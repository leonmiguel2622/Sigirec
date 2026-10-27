import os

import cv2
from ultralytics import YOLO

base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(
    base_dir,
    "runs",
    "detect",
    "train-5",
    "weights",
    "best.pt"
)
model = YOLO(model_path)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:
    ret, frame = cap.read()
    
    if not ret:
        break

    results = model(frame)
    annotated_frame = results[0].plot()
    cv2.imshow("SIGIREC IA", annotated_frame)
    tecla = cv2.waitKey(1)  

    if tecla == 27:  #La tecla 27 es ESC
        break

cap.release()
cv2.destroyAllWindows()