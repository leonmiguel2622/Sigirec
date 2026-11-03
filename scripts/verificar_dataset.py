import argparse
import os
import sys

try:
    import yaml
except ImportError:
    print("Falta PyYAML. Instala las dependencias con: pip install -r requirements.txt")
    sys.exit(2)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_DEFECTO = os.path.join(BASE_DIR, "dataset", "data.yaml")

EXTENSIONES_IMAGEN = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
CLASES_ESPERADAS = {"botella", "tapa", "etiqueta"}
ALIAS_CLASES = {
    "botella": "botella",
    "botellas": "botella",
    "bottle": "botella",
    "bottles": "botella",
    "botella pet": "botella",
    "pet bottle": "botella",
    "plastic bottle": "botella",
    "tapa": "tapa",
    "tapas": "tapa",
    "cap": "tapa",
    "caps": "tapa",
    "bottle cap": "tapa",
    "etiqueta": "etiqueta",
    "etiquetas": "etiqueta",
    "label": "etiqueta",
    "labels": "etiqueta",
}


def normalizar(nombre):
    limpio = str(nombre).strip().lower().replace("_", " ").replace("-", " ")
    limpio = " ".join(limpio.split())

    if limpio in ALIAS_CLASES:
        return ALIAS_CLASES[limpio]

    for alias, canonico in ALIAS_CLASES.items():
        if limpio.startswith(alias + " "):
            return canonico

    return limpio


def obtener_nombres(data):
    names = data.get("names", [])
    if isinstance(names, list):
        return [str(n) for n in names]
    if isinstance(names, dict):
        def clave(orden):
            return int(orden) if str(orden).isdigit() else str(orden)

        return [str(names[k]) for k in sorted(names, key=clave)]
    return []


def resolver_ruta(base, valor):
    if not valor:
        return None
    valor = str(valor).replace("\\", os.sep).replace("/", os.sep)
    if os.path.isabs(valor):
        return valor
    return os.path.abspath(os.path.join(base, valor))


def contar_imagenes(directorio):
    if not directorio or not os.path.isdir(directorio):
        return 0
    total = 0
    for actual, _, archivos in os.walk(directorio):
        for archivo in archivos:
            if os.path.splitext(archivo)[1].lower() in EXTENSIONES_IMAGEN:
                total += 1
    return total


def contar_etiquetas(directorio):
    if not directorio or not os.path.isdir(directorio):
        return 0
    total = 0
    for actual, _, archivos in os.walk(directorio):
        for archivo in archivos:
            if archivo.lower().endswith(".txt"):
                total += 1
    return total


def main():
    parser = argparse.ArgumentParser(
        description="Verifica un dataset exportado de Roboflow en formato YOLOv8."
    )
    parser.add_argument(
        "data_yaml",
        nargs="?",
        default=RUTA_DEFECTO,
        help=f"Ruta al data.yaml (por defecto: {RUTA_DEFECTO})",
    )
    args = parser.parse_args()

    errores = []
    advertencias = []

    if not os.path.isfile(args.data_yaml):
        print(f"ERROR: no existe el archivo {args.data_yaml}")
        return 1

    with open(args.data_yaml, "r", encoding="utf-8") as archivo:
        data = yaml.safe_load(archivo) or {}

    base = os.path.dirname(os.path.abspath(args.data_yaml))
    raiz = resolver_ruta(base, data.get("path")) or base
    nombres = obtener_nombres(data)

    print("=" * 60)
    print("VERIFICACION DE DATASET YOLOV8 / ROBOFLOW")
    print("=" * 60)
    print("data.yaml:", os.path.abspath(args.data_yaml))
    print("raiz:", raiz)
    print("nombres:", nombres)

    if not nombres:
        errores.append("data.yaml no contiene la lista 'names'.")
    else:
        normalizados = [normalizar(n) for n in nombres]
        encontradas = set(normalizados)
        faltantes = CLASES_ESPERADAS - encontradas
        inesperadas = encontradas - CLASES_ESPERADAS

        if faltantes:
            errores.append(
                "Faltan clases esperadas: " + ", ".join(sorted(faltantes))
            )
        if inesperadas:
            advertencias.append(
                "Hay clases que SIGIREC no usa: " + ", ".join(sorted(inesperadas))
            )

        nc = data.get("nc")
        if nc is not None and int(nc) != len(nombres):
            advertencias.append(
                f"nc={nc} no coincide con la cantidad de names ({len(nombres)})."
            )

    for split in ("train", "val"):
        if not data.get(split):
            errores.append(f"data.yaml no define el split '{split}'.")
            continue

        ruta = resolver_ruta(raiz, data.get(split))
        imagenes = contar_imagenes(ruta)
        etiquetas = contar_etiquetas(
            os.path.join(os.path.dirname(ruta), "labels")
        )
        print(f"{split}: {ruta}")
        print(f"  imagenes: {imagenes} | etiquetas: {etiquetas}")

        if not os.path.isdir(ruta):
            errores.append(f"No existe la carpeta de imagenes de '{split}': {ruta}")
        elif imagenes == 0:
            errores.append(f"El split '{split}' no contiene imagenes.")

    if data.get("test"):
        ruta_test = resolver_ruta(raiz, data.get("test"))
        print(f"test: {ruta_test}")
        print(f"  imagenes: {contar_imagenes(ruta_test)}")

    print("-" * 60)

    for advertencia in advertencias:
        print("ADVERTENCIA:", advertencia)

    for error in errores:
        print("ERROR:", error)

    if errores:
        print("RESULTADO: el dataset NO esta listo para entrenar.")
        return 1

    print("RESULTADO: el dataset esta listo para entrenar con train.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
