import glob
import os

import cv2
from ultralytics import YOLO

base_dir = os.path.dirname(os.path.abspath(__file__))


def resolver_modelo():
    ruta_env = (os.getenv("SIGIREC_MODEL_PATH") or "").strip()
    if ruta_env and os.path.isfile(ruta_env):
        return ruta_env

    candidatos = [os.path.join(base_dir, "models", "best.pt")]

    runs = glob.glob(
        os.path.join(base_dir, "runs", "detect", "*", "weights", "best.pt")
    )
    runs.sort(key=os.path.getmtime, reverse=True)
    candidatos.extend(runs)

    candidatos.append(
        os.path.join(base_dir, "runs", "detect", "train-5", "weights", "best.pt")
    )

    for ruta in candidatos:
        if os.path.isfile(ruta):
            return ruta

    raise SystemExit(
        "No se encontro un modelo. Coloca best.pt en models/best.pt "
        "o define SIGIREC_MODEL_PATH."
    )


model_path = resolver_modelo()
model = YOLO(model_path)
print("Modelo:", model_path)
print("Clases:", model.names)
cap = cv2.VideoCapture(int(os.getenv("SIGIREC_CAMERA_INDEX", "0")), cv2.CAP_DSHOW)
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