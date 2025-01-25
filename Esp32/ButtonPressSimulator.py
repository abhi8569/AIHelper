from machine import Pin, PWM
import network
import socket
import time

# Servo configuration
servo = PWM(Pin(13))  # GPIO13 for servo control
servo.freq(50)  # Standard 50Hz frequency for servos

# WiFi credentials
SSID = "-----------------"
PASSWORD = "-------------------"

# Static IP configuration
STATIC_IP = "192.168.88.225"  # Replace with your desired static IP
GATEWAY = "192.168.88.1"      # Replace with your network gateway
SUBNET = "255.255.255.0"     # Replace with your subnet mask

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
    return wlan.ifconfig()[0]

def set_servo_angle(angle):
    # Convert angle (0-180) to duty cycle (20-120)
    # 20 = 0 degrees, 120 = 180 degrees
    duty = int(((angle / 180) * 100) + 20)
    servo.duty(duty)

def simulate_button_press():
    # Move to 182° (slightly beyond normal range to simulate press)
    set_servo_angle(184)
    time.sleep(0.5)  # Hold for half second
    # Return to 180°
    set_servo_angle(180)
    time.sleep(0.5)  # Wait before next press

def web_page():
    html = """
    <html>
        <head>
            <title>Button Press Simulator</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { text-align: center; font-family: Arial; }
                .button {
                    background-color: #4CAF50;
                    border: none;
                    color: white;
                    padding: 15px 32px;
                    text-align: center;
                    display: inline-block;
                    font-size: 16px;
                    margin: 4px 2px;
                    cursor: pointer;
                    border-radius: 4px;
                }
            </style>
        </head>
        <body>
            <h1>Button Press Simulator</h1>
            <p>
                <a href="/press"><button class="button">Simulate Button Press</button></a>
            </p>
        </body>
    </html>
    """
    return html

def main():
    ip = connect_to_wifi()
    
    # Create socket server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    
    print(f'Server running at http://{ip}/')
    
    while True:
        try:
            conn, addr = s.accept()
            request = conn.recv(1024).decode()
            
            # Check for button press request
            if 'GET /press' in request:
                simulate_button_press()
                print('Simulated button press')
                response = 'Button press simulated'
            else:
                # Send web page for all other requests
                response = web_page()
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
            conn.close()
            
        except Exception as e:
            print('Error:', e)
            conn.close()

if __name__ == '__main__':
    main()
