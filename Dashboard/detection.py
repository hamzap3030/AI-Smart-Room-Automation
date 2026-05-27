from torchgen.executorch.api.et_cpp import return_names
from ultralytics import YOLO
import cv2
import cvzone
import math
import time
import requests
import threading
import json

esp32_ip = ""  # your esp32 ip
url = esp32_ip + "/data"
headers = {
    "Content-Type": "application/json"
}
bulb1Loc = (300, 400)
bulb2Loc = (1000, 400)
bulb1 = False
bulb2 = False
fan = False
bulb1LastOn = time.time()
bulb2LastOn = time.time()
is_person = False

cap = cv2.VideoCapture("../video/classroom_video.mp4")
# cap = cv2.VideoCapture(0)

cap.set(3, 1280)
cap.set(4, 720)

# model = YOLO('../Yolo-Weights/yolov8l.pt')
model = YOLO('../Yolo-Weights/yolov8s.pt')
# model.to('cuda')
prev_time = time.time()
current_time = time.time()
lastRequest = time.time()


classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush"
              ]


def sendData(data):
    global lastRequest
    global current_time
    try:
        if(current_time-lastRequest > 2):
            response = requests.post(url, data=json.dumps(data), headers=headers)
            lastRequest = current_time
            # cvzone.putTextRect(img,f'StatusCode{response.status_code}, Response:{response.text} ',(0, 35), scale=1, thickness=1)
    except Exception as e:
        pass

def get_states():
    global bulb1, bulb2, fan
    return bulb1, bulb2, fan


def isPerson():
    global prev_time, current_time
    if(current_time - prev_time > 10) and not is_person:
        return False
    else:
        return True



def generate_frames():
    global bulb1, bulb2, bulb1LastOn, bulb2LastOn, prev_time, current_time, fan
    while True:
        success, img = cap.read()
        if not success:
            break

        results = model(img, stream=True)

        cv2.circle(img, center=bulb1Loc, radius=5, color=(0, 255, 0), thickness=6)
        cv2.circle(img, center=bulb2Loc, radius=5, color=(0, 255, 0), thickness=6)
        cv2.line(img, pt1=(650, 10), pt2=(650, 1000), color=(0, 255, 0), thickness=2)

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                w, h = x2 - x1, y2 - y1

                conf = math.ceil((box.conf[0] * 100)) / 100
                cls = int(box.cls[0])

                if conf > 0.8 and classNames[cls] == "person":
                    is_person = True
                    center = (int((x1 + (w / 2))), int((y1 + (h / 2))))
                    distFromBulb1 = abs(center[0] - bulb1Loc[0])
                    distFromBulb2 = abs(center[0] - bulb2Loc[0])

                    cv2.circle(img, center=center, radius=5, color=(0, 255, 0), thickness=3, )
                    cvzone.cornerRect(img, (x1, y1, w, h))
                    # cvzone.putTextRect(img, f'{classNames[cls]} {conf}', (max(0, x1), max(35, y1)), scale=1, thickness=1)


                    if (distFromBulb1 < distFromBulb2):
                        if bulb1:
                            bulb1LastOn = current_time
                        if not bulb1:
                            bulb1 = True
                        if bulb2 and (current_time - bulb2LastOn > 10):
                            bulb2 = False
                    else:
                        if bulb2:
                            bulb2LastOn = current_time
                        if not bulb2:
                            bulb2 = True
                        if bulb1 and (current_time - bulb1LastOn > 10):
                            bulb1 = False

                    cvzone.putTextRect(img, f'FanState: {fan}, bulb1State: {bulb1}, bulb2State: {bulb2} time1:{(current_time-bulb1LastOn):.2f}, time2:{(current_time-bulb2LastOn):.2f}', (max(0, x1), max(35, y1)), scale=1, thickness=1)
                elif conf > 0.8 and classNames[cls] != "person":
                    is_person = False

        fan = True if(isPerson()) else False
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time
        cvzone.putTextRect(img, f'FPS: {int(fps)}', (20, 40), scale=2, thickness=2)

        data = {
            "bulb1": bulb1,
            "bulb2": bulb2,
            "fan": fan
        }
        threading.Thread(target=sendData, args=[data]).start()


        #-----------------------live video streaming--------------------
        _, buffer = cv2.imencode('.jpg', img)
        # cv2.imencode('.jpg', img) encodes the OpenCV image (img) as a JPEG image in memory (not saved to disk).
        frame = buffer.tobytes()
        # Converts the encoded image into raw bytes that can be sent over HTTP.
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

























