from machine import Pin, PWM
import network
import socket
import time

# Servo configuration
servo = PWM(Pin(13))  # GPIO13 for servo control
servo.freq(50)  # Standard 50Hz frequency for servos

# WiFi credentials
SSID = "MikroTik-2GHz"
PASSWORD = "5BNX9PA73S"

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
    
def web_page():
    html = """
    <html>
        <head>
            <title>ESP32 Servo Control</title>
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
            <h1>ESP32 Servo Control</h1>
            <p>
                <a href="/?angle=0"><button class="button">0°</button></a>
                <a href="/?angle=90"><button class="button">90°</button></a>
                <a href="/?angle=180"><button class="button">180°</button></a>
            </p>
            <p>
                <form action="/" method="get">
                    <input type="range" name="angle" min="0" max="180" value="90" 
                           oninput="this.nextElementSibling.value = this.value">
                    <output>90</output>
                    <input type="submit" value="Set Angle" class="button">
                </form>
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
            
            # Parse angle from request
            angle = None
            if 'GET /?angle=' in request:
                angle_str = request.split('GET /?angle=')[1].split(' ')[0]
                try:
                    angle = int(angle_str)
                    if 0 <= angle <= 180:
                        set_servo_angle(angle)
                        print(f'Setting angle to {angle}°')
                except ValueError:
                    pass
            
            # Send response
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
