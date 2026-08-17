from ultralytics import YOLO
import cv2
from gtts import gTTS
import pygame
import os
import time

# Initialize pygame mixer
pygame.mixer.init()

# Models
pothole_model = YOLO("runs/detect/pothole_yolo26/weights/best.pt")
coco_model = YOLO("yolo26n.pt")

class_for_coco = ['person', 'bicycle', 'motorcycle', 'car', 'bus', 'truck', 'traffic light', 'stop sign']

messages = {
    "clear": "വഴി ശൂന്യമാണ്",
    "left": "അല്പം വലത്തേക്ക് നീങ്ങുക",
    "right": "അല്പം ഇത്തേക്ക് നീങ്ങുക",
    "stop": "മുന്നിൽ തടസ്സം ഉണ്ട്, നിർത്തുക",
    "pothole_left": "ഇടത്ത് കുഴി ഉണ്ട്, അല്പം വലത്തേക്ക് നീങ്ങുക",
    "pothole_right": "വലത്ത് കുഴി ഉണ്ട്, അല്പം ഇത്തേക്ക് നീങ്ങുക",
    "pothole_ahead": "മുന്നിൽ കുഴി ഉണ്ട്, നിർത്തുക"
}

last_spoken = ""
last_speak_time = 0
cooldown = 6
frame_count = 0

def speak(text):
    global last_spoken, last_speak_time
    current_time = time.time()

    if text != last_spoken or (current_time - last_speak_time) > cooldown:
        try:
            tts = gTTS(text=text, lang='ml')
            tts.save("alert.mp3")

            pygame.mixer.music.load("alert.mp3")
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            os.remove("alert.mp3")
            last_spoken = text
            last_speak_time = current_time
        except Exception as e:
            print("Voice Error:", e)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    if frame_count % 3 != 0:          # process every 3rd frame (less lag)
        continue

    frame = cv2.resize(frame, (512, 384))   # smaller = faster

    coco_results = coco_model(frame, conf=0.5, verbose=False, imgsz=416)[0]
    pothole_result = pothole_model(frame, conf=0.7, verbose=False, imgsz=416)[0]

    ano_frame = frame.copy()
    frame_height, frame_width = frame.shape[:2]

    guidance = "Path Clear"
    voice_text = messages["clear"]

    # COCO
    for box in coco_results.boxes:
        cls_id = int(box.cls[0])
        class_name = coco_model.names[cls_id]
        if class_name in class_for_coco:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cv2.rectangle(ano_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(ano_frame, f"{class_name} {conf:.2f}", (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            center_x = (x1 + x2) // 2
            if center_x < frame_width // 3:
                voice_text = messages["left"]
            elif center_x > (frame_width * 2) // 3:
                voice_text = messages["right"]
            else:
                voice_text = messages["stop"]

    # Pothole
    for box in pothole_result.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        cv2.rectangle(ano_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(ano_frame, f"pothole {conf:.2f}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        center_x = (x1 + x2) // 2
        if center_x < frame_width // 3:
            voice_text = messages["pothole_left"]
        elif center_x > (frame_width * 2) // 3:
            voice_text = messages["pothole_right"]
        else:
            voice_text = messages["pothole_ahead"]

    speak(voice_text)
    cv2.imshow("Nethra Vazhi", ano_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()