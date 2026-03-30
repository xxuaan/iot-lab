# ble_client.py  –– Pico W 2  (Client / Central)
# CSC2106 BLE Lab
#
# Scans for "PicoW_A_Server", connects, discovers the GATT service and its two
# characteristics, then:
#   Button A (GP0) → Task 3: READ LED State from server
#   Button B (GP1) → Task 4: WRITE new LED State to server
#   NOTIFY events  → Task 2: prints received temperature/voltage string
# ─────────────────────────────────────────────────────────────────────────────

import bluetooth
import time
import machine
from micropython import const

# ── UUIDs (must match server) ─────────────────────────────────────────────────
_SVC_UUID    = bluetooth.UUID(0x1A02)
_LED_UUID    = bluetooth.UUID(0x1A00)
_STATUS_UUID = bluetooth.UUID(0x1A01)
TARGET_NAME  = "LX_SERVER"

# ── BLE IRQ event codes ───────────────────────────────────────────────────────
_IRQ_SCAN_RESULT               = const(5)
_IRQ_SCAN_DONE                 = const(6)
_IRQ_PERIPHERAL_CONNECT        = const(7)
_IRQ_PERIPHERAL_DISCONNECT     = const(8)
_IRQ_GATTC_SERVICE_RESULT      = const(9)
_IRQ_GATTC_SERVICE_DONE        = const(10)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_CHARACTERISTIC_DONE   = const(12)
_IRQ_GATTC_DESCRIPTOR_RESULT   = const(13)
_IRQ_GATTC_DESCRIPTOR_DONE     = const(14)
_IRQ_GATTC_READ_RESULT         = const(15)   # Carries the value we asked for
_IRQ_GATTC_READ_DONE           = const(16)   # Signals read transaction complete
_IRQ_GATTC_WRITE_DONE          = const(17)
_IRQ_GATTC_NOTIFY              = const(18)
_IRQ_GATTC_INDICATE            = const(19)

# ── Hardware ──────────────────────────────────────────────────────────────────
btn_a       = machine.Pin(20, machine.Pin.IN, machine.Pin.PULL_UP)   # GP20
btn_b       = machine.Pin(21, machine.Pin.IN, machine.Pin.PULL_UP)   # GP21
onboard_led = machine.Pin("LED", machine.Pin.OUT)


# ── Client class ──────────────────────────────────────────────────────────────
class BLEClient:
    def __init__(self):
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)
        self._reset()

    # ── Internal state reset ──────────────────────────────────────────────────
    def _reset(self):
        self._addr_type      = None
        self._addr           = None
        self._conn_handle    = None

        # Service handle range
        self._svc_start      = None
        self._svc_end        = None

        # Characteristic value handles
        self._led_handle     = None
        self._status_handle  = None
        self._cccd_handle    = None

        # Track number of characteristics discovered so we know when done
        self._chars_found    = 0
        self._connected      = False

    # ── IRQ handler ───────────────────────────────────────────────────────────
    def _irq(self, event, data):

        # ── Scanning ──────────────────────────────────────────────────────────
        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            if TARGET_NAME.encode() in bytes(adv_data):
                # Found the server – stop scanning and connect
                self._addr_type = addr_type
                self._addr      = bytes(addr)           # copy before it's garbage-collected
                print(f"[Client] Found '{TARGET_NAME}' (RSSI={rssi}). Stopping scan…")
                self._ble.gap_scan(None)                # stop scan

        elif event == _IRQ_SCAN_DONE:
            if self._addr:
                print("[Client] Connecting to server…")
                self._ble.gap_connect(self._addr_type, self._addr)
            else:
                print("[Client] Server not found. Rescanning…")
                self.scan()

        # ── Connection ────────────────────────────────────────────────────────
        elif event == _IRQ_PERIPHERAL_CONNECT:
            conn_handle, addr_type, addr = data
            self._conn_handle = conn_handle
            self._connected   = True
            print(f"[Client] Connected (handle={conn_handle}). Discovering services…")
            self._ble.gattc_discover_services(conn_handle)

        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            conn_handle, addr_type, addr = data
            print("[Client] Disconnected. Waiting before rescan…")
            self._reset()
            time.sleep_ms(2000)   # give server time to re-advertise
            self.scan()

        # ── Service discovery ─────────────────────────────────────────────────
        elif event == _IRQ_GATTC_SERVICE_RESULT:
            conn_handle, start_handle, end_handle, uuid = data
            if uuid == _SVC_UUID:
                self._svc_start = start_handle
                self._svc_end   = end_handle
                print(f"[Client] Service found: handles {start_handle}–{end_handle}")

        elif event == _IRQ_GATTC_SERVICE_DONE:
            conn_handle, status = data
            if self._svc_start is not None:
                print("[Client] Discovering characteristics…")
                self._ble.gattc_discover_characteristics(
                    conn_handle, self._svc_start, self._svc_end
                )
            else:
                print("[Client] Target service not found! Disconnecting to retry…")
                self._ble.gap_disconnect(conn_handle)

        # ── Characteristic discovery ──────────────────────────────────────────
        elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
            conn_handle, def_handle, value_handle, properties, uuid = data
            if uuid == _LED_UUID:
                self._led_handle = value_handle
                self._chars_found += 1
                print(f"[Client] LED characteristic  → value handle {value_handle}")
            elif uuid == _STATUS_UUID:
                self._status_handle = value_handle
                self._chars_found  += 1
                print(f"[Client] Status characteristic → value handle {value_handle}")

        elif event == _IRQ_GATTC_CHARACTERISTIC_DONE:
            conn_handle, status = data
            if self._led_handle and self._status_handle:
                print("[Client] All characteristics found. Discovering descriptors…")
                # Discover descriptors to find the real CCCD handle
                self._ble.gattc_discover_descriptors(
                    conn_handle, self._svc_start, self._svc_end
                )
            else:
                print("[Client] Warning: not all characteristics discovered.")

        elif event == _IRQ_GATTC_DESCRIPTOR_RESULT:
            conn_handle, dsc_handle, uuid = data
            # CCCD UUID is 0x2902
            if uuid == bluetooth.UUID(0x2902):
                self._cccd_handle = dsc_handle
                print(f"[Client] CCCD found at handle {dsc_handle}")

        elif event == _IRQ_GATTC_DESCRIPTOR_DONE:
            conn_handle, status = data
            if hasattr(self, '_cccd_handle') and self._cccd_handle:
                print("[Client] Enabling notifications via CCCD…")
                # mode=0 → WRITE with response, ensures subscription is confirmed
                self._ble.gattc_write(conn_handle, self._cccd_handle,
                                      b'\x01\x00', 0)
            else:
                # Fallback: assume CCCD is status_handle + 1
                print("[Client] CCCD not found via discovery, using fallback handle…")
                self._ble.gattc_write(conn_handle, self._status_handle + 1,
                                      b'\x01\x00', 0)

        # ── Read response (Task 3) ────────────────────────────────────────────
        elif event == _IRQ_GATTC_READ_RESULT:
            conn_handle, value_handle, value = data
            raw = bytes(value)
            print(f"[Client] READ_RESULT: handle={value_handle} (led_handle={self._led_handle}) raw={raw}")
            try:
                led_state = int(raw.decode().strip())
                onboard_led.value(led_state)
                print(f"[Client] Task 3 – Server LED is: {'ON' if led_state else 'OFF'} ({led_state})")
            except Exception as e:
                print(f"[Client] READ_RESULT parse error: {e}, raw={raw}")

        elif event == _IRQ_GATTC_READ_DONE:
            conn_handle, value_handle, status = data
            print(f"[Client] READ_DONE: handle={value_handle} status={status}")
            if status != 0:
                print(f"[Client] Read FAILED (status={status})")

        # ── Write acknowledgement ─────────────────────────────────────────────
        elif event == _IRQ_GATTC_WRITE_DONE:
            conn_handle, value_handle, status = data
            if hasattr(self, '_cccd_handle') and value_handle == self._cccd_handle:
                if status == 0:
                    print("[Client] Notifications ENABLED. Ready – Button A = Read LED, Button B = Write LED")
                else:
                    print(f"[Client] Failed to enable notifications (status={status})")
            else:
                if status == 0:
                    print(f"[Client] Task 4 – WRITE acknowledged by server.")
                else:
                    print(f"[Client] Write failed (status={status})")

        # ── Notify from server (Task 2) ───────────────────────────────────────
        elif event == _IRQ_GATTC_NOTIFY:
            conn_handle, value_handle, notify_data = data
            if value_handle == self._status_handle:
                status_str = bytes(notify_data).decode("utf-8")
                print(f"[Client] Task 2 – NOTIFY from server: {status_str}")

    # ── Public helpers ────────────────────────────────────────────────────────
    def scan(self):
        """Start a passive BLE scan indefinitely (stops when server is found)."""
        print("[Client] Scanning for BLE peripherals…")
        # duration_ms=0 → scan indefinitely; interval/window in 0.625 ms units
        self._ble.gap_scan(0, 30_000, 30_000)

    def read_led(self):
        """Task 3 – issue a GATTC read for the LED characteristic."""
        print(f"[Client] read_led() called – conn={self._conn_handle} led_handle={self._led_handle}")
        if self._conn_handle is not None and self._led_handle is not None:
            self._ble.gattc_read(self._conn_handle, self._led_handle)
        else:
            print("[Client] Not connected or LED handle unknown.")

    def write_led(self, state: int):
        """Task 4 – issue a GATTC write to change the server's LED state."""
        if self._conn_handle is not None and self._led_handle is not None:
            value = str(state).encode("utf-8")
            # 1 → WRITE_NO_RSP (faster; use 0 for WRITE with response)
            self._ble.gattc_write(self._conn_handle, self._led_handle, value, 1)
        else:
            print("[Client] Not connected or LED handle unknown.")


# ── Main loop ─────────────────────────────────────────────────────────────────
client = BLEClient()
client.scan()

_last_action_ms = 0
_DEBOUNCE_MS    = 500

while True:
    now = time.ticks_ms()

    # Task 3: Button A pressed → READ LED state from server
    if not btn_a.value():                                   # active-low
        if time.ticks_diff(now, _last_action_ms) > _DEBOUNCE_MS:
            print("\n[Client] Button A pressed → Reading LED state from server…")
            client.read_led()
            _last_action_ms = now

    # Task 4: Button B pressed → WRITE new LED state to server
    if not btn_b.value():                                   # active-low
        if time.ticks_diff(now, _last_action_ms) > _DEBOUNCE_MS:
            new_state = 1 - onboard_led.value()            # toggle local LED as indicator
            print(f"\n[Client] Button B pressed → Writing LED={new_state} to server…")
            client.write_led(new_state)
            onboard_led.value(new_state)                    # reflect the requested state locally
            _last_action_ms = now

    time.sleep_ms(50)
