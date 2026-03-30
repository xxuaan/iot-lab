import network, time
from umqtt.simple import MQTTClient
from machine import Pin

# ==== EDIT THESE ====
SSID = "xuan"
PASSWORD = "xuan1234"
BROKER = "172.20.10.2"
CLIENT_ID = b"NodeB"
# ====================

# Hardware setup
BUTTON_PIN = 21        # GP21 -> button to GND
LED_PIN = 20        # Onboard LED (use "LED" for Pico W, or 25 for regular Pico)

# MQTT Topics
CMD_TO_A_TOPIC = b"csc2106/nodeA/led/cmd"  # Node B publishes here to control Node A
CMD_TO_B_TOPIC = b"csc2106/nodeB/led/cmd"  # Node B subscribes here (controlled by Node A)
STATUS_TOPIC = b"csc2106/nodeB/status"

# Initialize hardware
btn = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
led = Pin(LED_PIN, Pin.OUT, value=0)

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        time.sleep(0.2)
    print("WiFi:", wlan.ifconfig())

def on_msg(topic, msg):
    """Callback for incoming MQTT messages"""
    if topic == CMD_TO_B_TOPIC and msg == b"TOGGLE":
        # Toggle LED state
        led.value(0 if led.value() else 1)
        state = "ON" if led.value() else "OFF"
        print(f"Node B LED toggled -> {state}")

def make_client():
    c = MQTTClient(CLIENT_ID, BROKER, keepalive=30)
    c.set_last_will(STATUS_TOPIC, b"offline", retain=True, qos=1)
    c.connect()
    
    # Set callback and subscribe to control topic
    c.set_callback(on_msg)
    c.subscribe(CMD_TO_B_TOPIC, qos=1)
    
    # Publish online status
    c.publish(STATUS_TOPIC, b"online", retain=True, qos=1)
    print("Node B: MQTT connected, subscribed to control topic, status=online")
    return c

def publish_toggle(client):
    """Publish TOGGLE command to Node A"""
    try:
        client.publish(CMD_TO_A_TOPIC, b"TOGGLE", qos=1)
        print("Node B: Published TOGGLE to Node A")
        return client
    except Exception as e:
        print("Publish failed, reconnecting...", e)
        try:
            client.disconnect()
        except:
            pass
        return make_client()

def main():
    wifi_connect()
    client = make_client()
    
    # Button state tracking
    last_btn = btn.value()
    
    while True:
        # Check for button press
        v = btn.value()
        if v != last_btn:
            last_btn = v
            if v == 0:  # Button pressed (pulled to GND)
                print("Node B: Button pressed -> sending TOGGLE to Node A")
                client = publish_toggle(client)
        
        # Check for incoming MQTT messages
        try:
            client.check_msg()
        except Exception as e:
            print("MQTT error, reconnecting...", e)
            try:
                client.disconnect()
            except:
                pass
            time.sleep(1)
            client = make_client()
        
        time.sleep(0.02)

main()

