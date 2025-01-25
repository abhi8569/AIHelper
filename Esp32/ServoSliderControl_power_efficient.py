from machine import Pin, PWM, deepsleep, lightsleep
import network
import socket
import time

# Servo configuration
servo = PWM(Pin(13))  # GPIO13 for servo control
servo.freq(50)  # Standard 50Hz frequency for servos

# WiFi credentials
SSID = "----------------"
PASSWORD = "----------------"

# Static IP configuration
STATIC_IP = "192.168.88.225"  # Replace with your desired static IP
GATEWAY = "192.168.88.1"      # Replace with your network gateway
SUBNET = "255.255.255.0"     # Replace with your subnet mask

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # Set WiFi power mode to low (0 = no power saving, 1 = minimum power saving)
    wlan.config(pm=1)
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

# Global variables for angle movement
movement_active = False
start_angle = 0
end_angle = 0
pause_duration = 0

def execute_movement():
    global movement_active, start_angle, end_angle, pause_duration
    if movement_active:
        # Move to start angle
        set_servo_angle(start_angle)
        time.sleep(1)
        # Move to end angle
        set_servo_angle(end_angle)
        # Enter light sleep during pause
        lightsleep(pause_duration * 1000)
        # Return to start angle
        set_servo_angle(start_angle)
        movement_active = False

def enter_deep_sleep(duration_seconds):
    # Disable WiFi before deep sleep
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    # Configure deep sleep
    deepsleep(duration_seconds * 1000)

def web_page():
    html = """
    <html>
        <head>
            <title>Servo Control</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { text-align: center; font-family: Arial; }
                .slider-container {
                    margin: 20px auto;
                    width: 80%;
                    max-width: 400px;
                }
                .slider {
                    -webkit-appearance: none;
                    width: 100%;
                    height: 15px;
                    background: #ddd;
                    outline: none;
                    opacity: 0.7;
                    transition: opacity .2s;
                }
                .slider:hover {
                    opacity: 1;
                }
                .slider::-webkit-slider-thumb {
                    -webkit-appearance: none;
                    appearance: none;
                    width: 25px;
                    height: 25px;
                    background: #4CAF50;
                    cursor: pointer;
                    border-radius: 50%;
                }
            </style>
            <script>
                function updateServo(angle) {
                    // Only send updates every 500ms instead of continuous
                    if (!this.lastUpdate || Date.now() - this.lastUpdate > 500) {
                        fetch('/set_angle?angle=' + angle)
                            .then(response => response.text())
                            .then(data => console.log(data))
                            .catch(error => console.error('Error:', error));
                        this.lastUpdate = Date.now();
                    }
                }
            </script>
        </head>
        <body>
            <h1>Servo Motor Control</h1>
            <div class="slider-container">
                <input type="range" min="0" max="270" value="135" class="slider" 
                       oninput="updateServo(this.value)" 
                       onchange="updateServo(this.value)">
            </div>
            <p>Current Angle: <span id="angle-display">135</span>°</p>
            
            <h2>Angle Movement Control</h2>
            <div class="movement-control">
                <label>Start Angle: <input type="number" id="start-angle" min="0" max="270" value="0"></label><br>
                <label>End Angle: <input type="number" id="end-angle" min="0" max="270" value="90"></label><br>
                <label>Pause (seconds): <input type="number" id="pause-duration" min="1" max="60" value="2"></label><br>
                <button onclick="startMovement()">Start Movement</button>
            </div>
            <p>Movement Status: <span id="movement-status">Idle</span></p>
            <script>
                const slider = document.querySelector('.slider');
                const angleDisplay = document.getElementById('angle-display');
                
                slider.addEventListener('input', function() {
                    angleDisplay.textContent = this.value;
                });

                function startMovement() {
                    const startAngle = document.getElementById('start-angle').value;
                    const endAngle = document.getElementById('end-angle').value;
                    const pauseDuration = document.getElementById('pause-duration').value;
                    const statusDisplay = document.getElementById('movement-status');
                    
                    fetch('/start_movement?start=' + startAngle + '&end=' + endAngle + '&pause=' + pauseDuration)
                        .then(response => response.text())
                        .then(data => {
                            statusDisplay.textContent = 'Running';
                            console.log(data);
                        })
                        .catch(error => {
                            statusDisplay.textContent = 'Error';
                            console.error('Error:', error);
                        });
                }
            </script>
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
            
            # Handle angle setting requests
            if 'GET /set_angle' in request:
                angle = int(request.split('angle=')[1].split(' ')[0])
                set_servo_angle(angle)
                response = f'Servo set to {angle}°'
            # Handle movement start requests
            elif 'GET /start_movement' in request:
                try:
                    # Update global variables
                    global movement_active, start_angle, end_angle, pause_duration
                    movement_active = True
                    start_angle = int(request.split('start=')[1].split('&')[0])
                    end_angle = int(request.split('end=')[1].split('&')[0])
                    pause_duration = int(request.split('pause=')[1].split(' ')[0])
                    
                    response = 'Movement started'
                    execute_movement()
                except Exception as e:
                    response = f'Invalid movement parameters: {str(e)}'
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
