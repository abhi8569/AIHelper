import network
import socket
import machine
import esp32

# WiFi credentials
SSID = "---------------"
PASSWORD = "------------"

# Static IP configuration
STATIC_IP = "192.168.88.225"  # Replace with your desired static IP
GATEWAY = "192.168.88.1"      # Replace with your network gateway
SUBNET = "255.255.255.0"     # Replace with your subnet mask

# LED Configuration
GPIO_PIN = 14  # Change this to your desired GPIO pin number
ACTIVE_LOW = False  # Set to True if LED turns on with LOW signal (0), False if LED turns on with HIGH signal (1)

# Initialize LED pin
led = machine.Pin(GPIO_PIN, machine.Pin.OUT)

# Helper function to set LED considering active-low/active-high configuration
def set_led(turn_on):
    """Set LED state considering active-low/active-high configuration
    Args:
        turn_on (bool): True to turn LED on, False to turn LED off
    """
    if ACTIVE_LOW:
        led.value(0 if turn_on else 1)  # Active low: 0 = ON, 1 = OFF
    else:
        led.value(1 if turn_on else 0)  # Active high: 1 = ON, 0 = OFF

# Load last state from NVS
try:
    nvs = esp32.NVS('storage')
    last_state = nvs.get_i32('led_state')
    led.value(last_state)  # Restore last state
except:
    # If no saved state exists, default to OFF
    led.value(1)  # LED off (active low)
    nvs = esp32.NVS('storage')
    nvs.set_i32('led_state', 1)
    nvs.commit()

def save_state(state):
    """Save LED state to NVS"""
    try:
        nvs.set_i32('led_state', state)
        nvs.commit()
    except:
        pass

# Connect to WiFi with static IP
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.ifconfig((STATIC_IP, SUBNET, GATEWAY, GATEWAY))  # Set static IP
    wlan.connect(SSID, PASSWORD)
    print("Connecting to WiFi with static IP...")
    while not wlan.isconnected():
        pass
    print("Connected to WiFi")
    print("IP Address:", wlan.ifconfig()[0])

# Start HTTP server
def start_server():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(5)
    print("Listening on", addr)

    while True:
        conn, addr = s.accept()
        print("Connection from", addr)
        request = conn.recv(1024).decode()
        print("Request:", request)

        # Parse HTTP request
        if "GET /on" in request:
            set_led(True)  # Turn LED on
            save_state(0 if ACTIVE_LOW else 1)  # Save appropriate pin state
            response = f"HTTP/1.1 200 OK\nContent-Type: text/html\n\n{get_html('ON')}"
        elif "GET /off" in request:
            set_led(False)  # Turn LED off
            save_state(1 if ACTIVE_LOW else 0)  # Save appropriate pin state
            response = f"HTTP/1.1 200 OK\nContent-Type: text/html\n\n{get_html('OFF')}"
        else:
            # Serve the main page
            current_state = led.value()
            state = "ON" if ((current_state == 0) if ACTIVE_LOW else (current_state == 1)) else "OFF"
            response = f"HTTP/1.1 200 OK\nContent-Type: text/html\n\n{get_html(state)}"

        conn.send(response)
        conn.close()

def get_html(state):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ESP32 LED Control</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                text-align: center; 
                margin-top: 50px;
            }}
            .button {{
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 4px;
            }}
            .button-on {{
                background-color: #44ff44;
            }}
            .button-off {{
                background-color: #ff4444;
            }}
            .current-button {{
                opacity: 0.5;
                cursor: default;
            }}
        </style>
    </head>
    <body>
        <h1>ESP32 LED Control</h1>
        <p>LED is currently {state}</p>
        <div>
            <a href="/on" class="button button-on{' current-button' if state == 'ON' else ''}">Turn ON</a>
            <a href="/off" class="button button-off{' current-button' if state == 'OFF' else ''}">Turn OFF</a>
        </div>
    </body>
    </html>
    """

# Main
try:
    connect_to_wifi()
    start_server()
except KeyboardInterrupt:
    print("Server stopped")
