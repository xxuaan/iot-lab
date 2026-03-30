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
        
        # Added trailing commas to ensure they are treated as tuples
        _LED_CHAR = (_LED_UUID, bluetooth.FLAG_READ | bluetooth.FLAG_WRITE | bluetooth.FLAG_WRITE_NO_RESPONSE,)
        _STATUS_CHAR = (_STATUS_UUID, bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,)
        _SERVICE = (_SVC_UUID, (_LED_CHAR, _STATUS_CHAR,),)

        # Handle Unpacking Fix
        self._handles = self._ble.gatts_register_services((_SERVICE,))
        self._led_handle = self._handles[0][0]
        self._status_handle = self._handles[0][1]
        
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
            if conn_handle in self._connections:
                self._connections.remove(conn_handle)
            self._advertise()
            print("Client Disconnected. Advertising...")

        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle == self._led_handle:
                data_rx = self._ble.gatts_read(value_handle)
                try:
                    new_state = int(data_rx.decode())
                    onboard_led.value(new_state)
                    self._led_state = new_state
                    print(f"LED state set to: {new_state}")
                except:
                    pass

    def _advertise(self):
        name_bytes = self._name.encode('utf-8')
        # Standard BLE Advertising structure: [Length, Type, Data]
        adv_data = bytearray(b"\x02\x01\x06\x03\x03\x02\x1A") + bytearray([len(name_bytes) + 1, 0x09]) + bytearray(name_bytes)
        self._ble.gap_advertise(_ADV_INTERVAL_US, adv_data=adv_data)
        
    def update_status(self, notify=False):
        led_val = str(self._led_state).encode('utf-8')
        status_val = read_pico_status().encode('utf-8')
        
        self._ble.gatts_write(self._led_handle, led_val)
        self._ble.gatts_write(self._status_handle, status_val)
        
        if notify:
            for conn_handle in self._connections:
                self._ble.gatts_notify(conn_handle, self._status_handle)
                print("Sent NOTIFY update.")

# --- MAIN SERVER LOOP ---
print("Starting BLE Server...")
server = BLEServer("LX_SERVER")
print("Advertising as LX_SERVER")

last_check = 0
while True:
    current_time = time.ticks_ms()
    if time.ticks_diff(current_time, last_check) > 10000:
        server._led_state = 1 - server._led_state
        onboard_led.value(server._led_state)
        server.update_status(notify=True)
        last_check = current_time
    time.sleep_ms(100)