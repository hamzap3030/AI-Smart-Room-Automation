# AI Smart Room Automation

> A Mini Project submitted for **Bachelor of Technology in Computer Science & Engineering (AIML)**  
> Ramrao Adik Institute of Technology, D.Y. Patil Deemed to be University — April 2025

---

## Team — Group 20

| Name | Email |
|------|---------|
| Bhide Armaan Amit | armaanbhide13@gmail.com  |
| Bhosale Harshwardhan Santosh | har.bho.rt23@dypatil.edu |
| Devkar Siddharth Nitin | sid.dev.rt23@dypatil.edu |
| Patel Hamza M. Zaid | hamzap3030@gmail.com |

**Supervisor:** Dr. Gargi Phadke

---

## About The Project

**AI Smart Room Automation** is an intelligent, energy-efficient room automation system that uses **computer vision (YOLOv8)** and **IoT (ESP32)** to automatically control room appliances like lights and fans based on real-time human presence detection.

The system divides the room into **left and right zones** — if a person is detected on the left, only the left bulb turns on. If detected on both sides, all appliances activate. The fan also turns on based on temperature (threshold: 33°C) from a DHT11 sensor.

---

## Features

- **Real-time human detection** using YOLOv8 + OpenCV
- **Zone-based appliance control** (Left / Right / Both sides)
- **Temperature-based fan control** via DHT11 sensor
- **Live web dashboard** with video feed and device status
- **ESP32 IoT control** over local Wi-Fi using HTTP
- **Energy saving** — appliances turn OFF automatically when room is empty
- **Multi-threaded** — detection and HTTP requests run in parallel

---

## Project Structure

```
AI-Smart-Room-Automation/
│
├── Dashboard/                  # Python backend (Flask server)
│   ├── app.py                  # Flask app — routes & temperature handling
│   ├── detection.py            # YOLOv8 human detection logic
│   ├── static/
│   │   └── style.css           # Web dashboard styles
│   └── templates/
│       └── index.html          # Web dashboard UI
│
├── esp32/
│   └── esp32.ino               # Arduino code for ESP32 microcontroller
│
└── README.md
```

---

## Tech Stack

### Software
| Tool | Purpose |
|------|---------|
| Python 3.10 | Main programming language |
| Flask | Web server & dashboard |
| YOLOv8 (Ultralytics) | Human detection model |
| OpenCV (cv2) | Video capture & frame processing |
| cvzone | Bounding box drawing |
| requests | HTTP communication to ESP32 |
| threading | Parallel processing |
| ArduinoIDE | ESP32 programming |

### Hardware
| Component | Role |
|-----------|------|
| ESP32 Microcontroller | Receives commands, controls relays via Wi-Fi |
| USB Webcam | Captures live room video feed |
| DHT11 Sensor | Measures room temperature |
| 4-Channel Relay Module | Switches lights and fan ON/OFF |
| Bulbs (x2) | Left and right zone lights |
| Fan | Activated when temperature > 33°C |

---

## How It Works

```
Camera → YOLOv8 detects person → Check zone (Left/Right)
    → Flask sends HTTP POST to ESP32
        → ESP32 controls relay → Bulb/Fan ON or OFF

DHT11 → Temperature reading → ESP32 sends to Flask → Fan logic applied
```

1. The webcam captures live video, processed frame-by-frame using YOLOv8
2. If a person (confidence > 80%) is detected, their position determines zone
3. Flask server sends `{bulb1, bulb2, fan}` as JSON to the ESP32 every 2 seconds
4. ESP32 receives commands and toggles relay pins (GPIO 23, 22, 21)
5. DHT11 reads temperature every 2 seconds and sends it back to Flask
6. Fan activates only if person is present **AND** temperature > 33°C
7. Bulb turns OFF after 10 seconds of no detection in that zone

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- Arduino IDE
- YOLOv8 weights file (`yolov8s.pt`) — download from [Ultralytics](https://github.com/ultralytics/assets/releases)

---

### 1. Clone the Repository

```bash
git clone https://github.com/hamzap3030/AI-Smart-Room-Automation.git
cd AI-Smart-Room-Automation
```

### 2. Install Python Dependencies

```bash
pip install flask ultralytics opencv-python cvzone requests
```

### 3. Set Up YOLOv8 Weights

Download `yolov8s.pt` and place it in a folder called `Yolo-Weights/` at the root:

```
AI-Smart-Room-Automation/
├── Yolo-Weights/
│   └── yolov8s.pt
├── Dashboard/
...
```

### 4. Configure ESP32

Open `esp32/esp32.ino` in Arduino IDE and fill in:

```cpp
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
```

Also update the Flask server URL (your PC's local IP):

```cpp
String serverUrl = "http://192.168.X.X:5000/sendTemp";
```

**Required Arduino Libraries** (install via Library Manager):
- `ArduinoJson`
- `DHT sensor library` by Adafruit
- `WiFi` (built-in for ESP32)
- `WebServer` (built-in for ESP32)
- `HTTPClient` (built-in for ESP32)

Upload the code to your ESP32. Note the **IP address** printed in Serial Monitor.

### 5. Configure detection.py

Open `Dashboard/detection.py` and set your ESP32's IP:

```python
esp32_ip = "http://192.168.X.X"  # Replace with your ESP32's IP from Serial Monitor
```

Also update the video source — use webcam or a video file:

```python
cap = cv2.VideoCapture(0)                        # For live webcam
# cap = cv2.VideoCapture("path/to/video.mp4")   # For video file
```

### 6. Run the Flask Server

```bash
cd Dashboard
python app.py
```

Open your browser and go to: `http://localhost:5000`

---

## System States

| Case | Detection | Result |
|------|-----------|--------|
| Person on Left | Left zone occupied | Bulb 1 ON, Bulb 2 OFF |
| Person on Right | Right zone occupied | Bulb 1 OFF, Bulb 2 ON |
| Both sides | Both zones occupied | Bulb 1 ON, Bulb 2 ON |
| No one present | No detection for 10s | All bulbs OFF |
| Temp > 33°C + Person present | Temperature threshold crossed | Fan ON |

---

## Demo

> Project tested in a real classroom environment at RAIT, Navi Mumbai.

- Zone-based detection working in real time at ~14–17 FPS
- ESP32 responding to HTTP commands with negligible latency
- DHT11 successfully controlling fan based on room temperature

---

## Future Scope

- Multi-room support with multiple cameras
- Mobile app for remote monitoring
- Predictive automation using ML (learning user habits)
- Integration with smart home platforms (Google Home, Alexa)
- Extension to smart parking management using the same YOLO + IoT architecture

---

## License

This project was developed for academic purposes at **Ramrao Adik Institute of Technology, DYPU**.  
Feel free to use or build upon this work with proper credit.

---

## Acknowledgements

Special thanks to **Dr. Gargi Phadke** (Supervisor & Project Coordinator), **Dr. Sangita Chaudhari** (HoD), and **Dr. Mukesh Patil** (Principal) for their guidance and support throughout this project.
