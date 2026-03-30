# main.py
import network
import socket
import machine
import time
from web_server import serve_client

# WiFi Credentials (CHANGE THESE!)
SSID = "xuan"
PASSWORD = "xuan1234"

# Pico W Peripherals
onboard_led = machine.Pin("LED", machine.Pin.OUT)
temp_sensor = machine.ADC(4)
conversion_factor = 3.3 / (65535)

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError('Network connection failed')
    else:
        status = wlan.ifconfig()
        print('Connected! IP Address:', status[0])
        return status[0]

def read_temperature():
    # Pico W internal temperature sensor reading logic
    voltage = temp_sensor.read_u16() * conversion_factor
    temperature = 27 - (voltage - 0.706) / 0.001721
    return temperature

# --- Main Program ---
try:
    ip_address = wifi_connect()
except Exception as e:
    print(f"Error connecting to WiFi: {e}")
    # Flash LED to indicate failure
    for i in range(5):
        onboard_led.toggle()
        time.sleep(0.2)
    raise

# Create Socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print('Listening on:', addr)

# Server Loop
while True:
    try:
        # Check for client connection
        client_conn, client_addr = s.accept()
        print('Client connected from', client_addr)

        # Get current temperature before serving
        current_temp_c = read_temperature()

        # NEW: Read the actual hardware state of the LED
        current_led_value = onboard_led.value()

        # UPDATED: Pass the LED value as the 3rd argument 
        new_led_state = serve_client(client_conn, current_temp_c, current_led_value)

        # Apply actuator change if requested
        if new_led_state == 0:
            onboard_led.value(0) # LED OFF
        elif new_led_state == 1:
            onboard_led.value(1) # LED ON

    except OSError as e:
        # Catch connection errors and continue loop
        if e.args[0] == 110: # ETIMEDOUT (non-blocking socket)
            pass
        else:
            print('Connection error:', e)
            continue
