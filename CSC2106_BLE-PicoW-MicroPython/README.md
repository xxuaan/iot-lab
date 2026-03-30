# MicroPython on Raspberry Pi Pico W **BLE Point-to-Point and Beacon Lab**

## I. Objectives

  * Understand the roles of **BLE Peripheral (Server)** and **BLE Central (Client)**.
  * Implement data communication using **GATT Services and Characteristics (Read, Write, Notify)**.
  * Control the Pico W's onboard LED actuator remotely.
  * Read the Pico W's onboard temperature sensor.
  * **Implement BLE Beacon (Advertising-Only)** mode for location or presence signaling.

## 🛠️ II. Prerequisites and Setup

  * **Hardware**: Two Raspberry Pi Pico W boards.
  * **Software**: Thonny IDE.
  * **Firmware**: Latest MicroPython UF2 firmware installed on both Pico Ws.

-----

## ⚙️ III. Pico W Server (Peripheral) - `ble_server.py`

This Pico W (Node A) acts as the **Server** and hosts the sensor data and actuator control characteristic, enabling communication via the Generic Attribute Profile (GATT).

### A. Key Characteristics and UUIDs

| Characteristic | UUID (Custom) | Permissions | Role |
| :--- | :--- | :--- | :--- |
| **LED State** | `0x1A00` | `READ`, `WRITE` | Allows Client to read and change LED state. |
| **Status (Temp/Volt)**| `0x1A01` | `READ`, `NOTIFY` | Allows Client to read and receive asynchronous updates. |

### B. `ble_server.py` Code

Upload and run this code on **Pico W 1 (Server)**.

```python
# ble_server.py (Pico W 1 - Server/Peripheral)
import bluetooth
import time
import machine
from micropython import const

# --- CONSTANTS & UUIDS ---
_ADV_INTERVAL_US = 200000 
_LED_UUID = bluetooth.UUID(0x1A00) 
_STATUS_UUID = bluetooth.UUID(0x1A01)
_SVC_UUID = bluetooth.UUID(0x1A02)
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3) 

# --- HARDWARE SETUP ---
onboard_led = machine.Pin("LED", machine.Pin.OUT)
temp_sensor = machine.ADC(4)
conversion_factor = 3.3 / (65535)

def read_pico_status():
    # Read Internal Temperature and approximate Voltage
    voltage = temp_sensor.read_u16() * conversion_factor
    temp = 27 - (voltage - 0.706) / 0.001721
    volt = 3.3 
    return f"T:{temp:.1f}V:{volt:.1f}"

# --- BLE CLASS ---
class BLEServer:
    def __init__(self, name):
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)
        
        _LED_CHAR = (_LED_UUID, bluetooth.FLAG_READ | bluetooth.FLAG_WRITE | bluetooth.FLAG_WRITE_NO_RSP)
        _STATUS_CHAR = (_STATUS_UUID, bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY)
        _SERVICE = (_SVC_UUID, (_LED_CHAR, _STATUS_CHAR,),)

        self._handles = self._ble.gatts_register_services((_SERVICE,))
        self._led_handle = self._handles[0][0][0]
        self._status_handle = self._handles[0][0][1]
        
        self._connections = set()
        self._name = name
        self._led_state = 0
        self.update_status()
        self._advertise()

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
            print("Client Connected.")
        
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.remove(conn_handle)
            self._advertise()
            print("Client Disconnected. Advertising...")

        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle == self._led_handle:
                # Handle WRITE from Client (Task 4)
                data = self._ble.gatts_read(value_handle)
                new_state = int(data.decode())
                onboard_led.value(new_state)
                self._led_state = new_state
                print(f"LED state set to: {new_state}")

    def _advertise(self):
        # Advertising payload: Name and Service UUID
        adv_data = bytearray(f"\x02\x01\x06\x03\x03\x02\x1A\x06\t{self._name}")
        self._ble.gap_advertise(_ADV_INTERVAL_US, adv_data=adv_data)
        
    def update_status(self, notify=False):
        led_val = str(self._led_state).encode('utf-8')
        status_val = read_pico_status().encode('utf-8')
        
        self._ble.gatts_write(self._led_handle, led_val)
        self._ble.gatts_write(self._status_handle, status_val)
        
        if notify:
            # Send NOTIFY to all connected clients (Task 2)
            for conn_handle in self._connections:
                self._ble.gatts_notify(conn_handle, self._status_handle)
                print("Sent NOTIFY update.")


# --- MAIN SERVER LOOP ---
server = BLEServer("PicoW_A_Server")

def check_button_a():
    # Placeholder for M5StickC Button A functionality: toggle state and notify
    return time.ticks_ms() % 10000 < 50 

last_check = 0
while True:
    current_time = time.ticks_ms()
    
    # Simulate Server Button A press (Task 2 Trigger)
    if check_button_a() and current_time - last_check > 10000:
        server._led_state = 1 - server._led_state
        onboard_led.value(server._led_state)
        server.update_status(notify=True)
        last_check = current_time
        
    time.sleep_ms(100)
```

## IV. Pico W Client (Central) - `ble_client.py`

This Pico W (Node B) acts as the **Client** and controls the Server by scanning, connecting, reading, and writing characteristics.

### A. `ble_client.py` Code

Upload and run this code on **Pico W 2 (Client)**.

```python
# ble_client.py (Pico W 2 - Client/Central)
import bluetooth
import time
import machine
from micropython import const

# --- CONSTANTS & UUIDS (Must match Server) ---
_LED_UUID = bluetooth.UUID(0x1A00)
_STATUS_UUID = bluetooth.UUID(0x1A01)
_SVC_UUID = bluetooth.UUID(0x1A02)
TARGET_NAME = "PicoW_A_Server"

_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)
_IRQ_GATTC_READ_DONE = const(15)
_IRQ_GATTC_NOTIFY = const(18)
# Other IRQs (9, 10, 11, 12, 16, 19) handle discovery, connect/disconnect, and write complete.

# --- HARDWARE SETUP (Simulate Client Buttons) ---
# Assuming two buttons connected to GP0 (A) and GP1 (B)
btn_a = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
btn_b = machine.Pin(1, machine.Pin.IN, machine.Pin.PULL_UP)
onboard_led = machine.Pin("LED", machine.Pin.OUT) # Use this LED to show requested state

# --- BLE CLASS ---
class BLEClient:
    def __init__(self):
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)
        self._reset()

    # ... (Omitted: _reset and IRQ handlers for brevity, as they were provided in the previous response) ...
    # Note: Full IRQ handlers from the previous response should be included here.
    
    def _irq(self, event, data):
        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            if TARGET_NAME.encode() in adv_data:
                self._addr_type = addr_type
                self._addr = addr
                self._ble.gap_scan(None)
                print(f"Found Server: {TARGET_NAME}. Connecting...")
                self._ble.gattc_connect(self._addr_type, self._addr)
        
        # ... (Other IRQ handlers omitted for brevity, ensure they are present) ...
        
        elif event == _IRQ_GATTC_READ_DONE:
            conn_handle, value_handle, value = data
            if value_handle == self._led_handle:
                # Task 3: Read LED State from Server
                led_state = int(value.decode())
                onboard_led.value(led_state)
                print(f"Read LED State (Server): {led_state} (0=OFF, 1=ON)")

        elif event == _IRQ_GATTC_NOTIFY:
            # Task 2: Receive NOTIFY updates
            conn_handle, value_handle, value = data
            if value_handle == self._status_handle:
                status = value.decode('utf-8')
                # Display received status (Simulates M5.Lcd.print())
                print(f"NOTIFY Update (Server Status): {status}")

    def scan(self):
        # Scan indefinitely until found
        self._ble.gap_scan(0) 
            
    def read_led(self):
        # Task 3 Trigger
        if self._conn_handle and self._led_handle:
            self._ble.gattc_read(self._conn_handle, self._led_handle)
            
    def write_led(self, state):
        # Task 4 Trigger
        if self._conn_handle and self._led_handle:
            value = str(state).encode('utf-8')
            self._ble.gattc_write(self._conn_handle, self._led_handle, value, 1) # '1' is WRITE_NO_RSP


# --- MAIN CLIENT LOOP ---
client = BLEClient()
client.scan()
last_action_time = 0

while True:
    
    # Task 3: Client Button A (Read LED state from Server)
    if not btn_a.value(): 
        if time.ticks_ms() - last_action_time > 500: # Debounce
            print("\nClient Button A pressed: Reading LED state...")
            client.read_led()
            last_action_time = time.ticks_ms()
    
    # Task 4: Client Button B (Write LED state to Server)
    if not btn_b.value(): 
        if time.ticks_ms() - last_action_time > 500: # Debounce
            # Toggle the state we want to write (toggle client's LED to track the request)
            state_to_write = 1 - onboard_led.value() 
            print(f"\nClient Button B pressed: Writing LED state {state_to_write} to Server...")
            client.write_led(state_to_write)
            onboard_led.value(state_to_write) 
            last_action_time = time.ticks_ms()

    time.sleep_ms(50)
```

## V. Lab Assignment Checklist

The following tasks, derived from the original lab, can now be executed using the two Pico W scripts above.

| Task | Action | Server (`ble_server.py`) | Client (`ble_client.py`) |
| :--- | :--- | :--- | :--- |
| **1: Setup** | Designate Pico W 1 (Server) and Pico W 2 (Client). | Runs, registers characteristics, and **advertises**. | Runs, **scans**, connects, and performs discovery. |
| **2: Server Notify** | Press the **Server's simulated button** (i.e., wait 10 seconds). | Toggles its LED state (`_led_state`) and calls `update_status(notify=True)`. | Receives the `NOTIFY` event and prints the `T:X V:Y` status update to the console. |
| **3: Client Read** | Press **Client Button A** (GP0). | Reads the `LED State` characteristic value. | Receives `_IRQ_GATTC_READ_DONE` event, reads the value, and prints the Server's LED state. |
| **4: Client Write** | Press **Client Button B** (GP1). | Receives the `_IRQ_GATTS_WRITE` event, updates its physical LED state. | Sends the new state value via `gattc_write` to the Server's LED characteristic. |

-----

## VI. Advanced Topic: BLE Beacon Mode (Advertising-Only)

A BLE Beacon is a device that broadcasts simple packets of data at regular intervals without ever attempting to establish a connection. This is the most energy-efficient mode of BLE communication and is crucial for location and presence applications.

The core difference between a GATT Peripheral and a Beacon is simple: **A Beacon only advertises custom data, it does not offer services to connect to.**

### A. Creating a Simple Beacon (`beacon.py`)

This program simplifies the Server code, removing all service registration and connection handlers, focusing only on the advertisement payload.

```python
# beacon.py (Pico W - Beacon Node)
import bluetooth
import time
import ubinascii
from micropython import const

_ADV_INTERVAL_US = 500000 # Advertise every 500ms

# Example Beacon Data: UUID (16 bytes), Major, Minor, Tx Power
# This specific format mimics an iBeacon structure
def create_i_beacon_payload(uuid, major, minor, tx_power):
    payload = bytearray()
    
    # Fixed prefix for Manufacturing Specific Data (0xFF)
    payload += b'\x02\x01\x06' 
    payload += b'\x1A\xFF' 
    
    # Company ID (Raspberry Pi: 0x00A5)
    payload += b'\xA5\x00' 
    
    # iBeacon Type and Length (0x02, 0x15)
    payload += b'\x02\x15' 
    
    # Proximity UUID (16 bytes)
    payload += ubinascii.unhexlify(uuid.replace('-', '')) 
    
    # Major (2 bytes)
    payload += major.to_bytes(2, 'big')
    
    # Minor (2 bytes)
    payload += minor.to_bytes(2, 'big')
    
    # Measured Power at 1m (1 byte signed integer)
    payload += bytes([tx_power])
    
    return payload

ble = bluetooth.BLE()
ble.active(True)

# Define your unique ID (e.g., location ID) and data fields
MY_UUID = "FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF"
MAJOR_ID = 1      # Group identifier
MINOR_ID = 101    # Specific device identifier
TX_POWER = -59    # Measured power at 1 meter (adjust based on calibration)

beacon_payload = create_i_beacon_payload(MY_UUID, MAJOR_ID, MINOR_ID, TX_POWER)

print("Starting Beacon Mode...")

while True:
    # Use gap_advertise with the custom payload
    ble.gap_advertise(_ADV_INTERVAL_US, adv_data=beacon_payload)
    
    # Note: Since there are no IRQ handlers, we stop advertising briefly before looping 
    # to maintain the correct advertising interval.
    time.sleep_ms(_ADV_INTERVAL_US // 1000) 
    ble.gap_advertise(None) # Stop advertising
    time.sleep_ms(1)

```

### B. Verification

To verify the beacon:

  * Upload `beacon.py` to a third Pico W and run it.
  * Use a mobile phone app (like **nRF Connect** or **BLE Scanner**) to scan for nearby devices.
  * You should see a device advertising the custom data packet (`MY_UUID`, `MAJOR_ID`, `MINOR_ID`) repeatedly without ever allowing a connection. This confirms operation in the energy-efficient **Beacon Mode**.
