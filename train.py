import os
import shutil

from ultralytics import YOLO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_YAML = (
    os.getenv("SIGIREC_DATA_YAML")
    or os.path.join(BASE_DIR, "dataset", "data.yaml")
)
BASE_MODEL = (
    os.getenv("SIGIREC_BASE_MODEL")
    or os.path.join(BASE_DIR, "yolov8n.pt")
)
MODELOS_DIR = os.path.join(BASE_DIR, "models")
MODELO_FINAL = os.path.join(MODELOS_DIR, "best.pt")


def entero_env(nombre, defecto):
    try:
        return int(os.getenv(nombre, defecto))
    except (TypeError, ValueError):
        return defecto


def main():
    if not os.path.isfile(DATA_YAML):
        raise SystemExit(
            "No se encontro el data.yaml del dataset.\n"
            "Descarga el dataset de Roboflow en formato YOLOv8, "
            f"descomprimelo en {os.path.join(BASE_DIR, 'dataset')} "
            "o define SIGIREC_DATA_YAML con la ruta al data.yaml."
        )

    if not os.path.isfile(BASE_MODEL):
        raise SystemExit(f"No se encontro el modelo base: {BASE_MODEL}")

    print("Dataset:", DATA_YAML)
    print("Modelo base:", BASE_MODEL)

    model = YOLO(BASE_MODEL)
    model.train(
        data=DATA_YAML,
        epochs=entero_env("SIGIREC_EPOCHS", 100),
        imgsz=entero_env("SIGIREC_IMGSZ", 640),
        batch=entero_env("SIGIREC_BATCH", 16),
        device=os.getenv("SIGIREC_DEVICE", "cpu"),
        project=os.path.join(BASE_DIR, "runs", "detect"),
        name=os.getenv("SIGIREC_RUN_NAME", "train-sigirec"),
        exist_ok=False,
        verbose=True,
    )

    save_dir = getattr(getattr(model, "trainer", None), "save_dir", None)

    if not save_dir:
        raise SystemExit(
            "El entrenamiento termino, pero no se pudo ubicar la carpeta de resultados."
        )

    best = os.path.join(str(save_dir), "weights", "best.pt")

    if not os.path.isfile(best):
        raise SystemExit(
            f"El entrenamiento termino, pero no se genero el archivo {best}"
        )

    os.makedirs(MODELOS_DIR, exist_ok=True)
    shutil.copy2(best, MODELO_FINAL)

    print("Entrenamiento finalizado.")
    print("Mejor modelo:", best)
    print("Modelo publicado:", MODELO_FINAL)


if __name__ == "__main__":
    main()
