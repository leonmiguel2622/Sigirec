# Implementación del dataset de Roboflow en SigiRec

Fecha: 2026-11-03

Este documento registra el diagnóstico, los requisitos del dataset y cada cambio realizado para conectar el export de Roboflow con el proyecto.

## 1. Diagnóstico inicial

- La aplicación carga el modelo desde una ruta fija: `runs/detect/train-5/weights/best.pt` (`app.py`).
- El checkpoint `best.pt` existente sí contiene las clases `botella`, `tapa` y `etiqueta`, que son las que usa la lógica de puntos.
- La carpeta `dataset/` no existe, por lo que `train.py` no puede reentrenar todavía.
- Si se entrena de nuevo, Ultralytics crea `runs/detect/train-6`, `train-7`, etc. La app seguía apuntando a `train-5`, así que el modelo nuevo no se usaba.
- La lógica de detección busca los nombres exactos `botella`, `tapa` y `etiqueta`. Un export de Roboflow con nombres en inglés (`bottle`, `cap`, `label`) no funcionaba.

## 2. Qué archivo descargar de Roboflow

### Opción A: reentrenar en local (recomendada)

En Roboflow, dentro del proyecto:

1. **Download Dataset**.
2. Formato: **YOLOv8** (también aparece como **YOLOv8 PyTorch TXT**).
3. Descargar el `.zip`.

El `.zip` contiene una estructura similar a:

```text
dataset/
├── data.yaml
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```

Descomprimirlo directamente en `dataset/` para que quede `dataset/data.yaml`.

### Opción B: usar el modelo ya entrenado en Roboflow

En Roboflow, dentro de la versión entrenada:

1. **Deploy** o **Model**.
2. Formato **YOLOv8**.
3. Descargar `best.pt` (o los pesos del modelo).
4. Colocarlo en `models/best.pt` o indicar su ruta con `SIGIREC_MODEL_PATH`.

En esta opción no hace falta descargar el dataset para que la app funcione; solo se necesita el archivo de pesos.

## 3. Información necesaria del dataset

Para terminar la implementación se necesita confirmar:

- Contenido de `data.yaml`: `path`, `train`, `val`, `test`, `nc` y `names`.
- Orden y nombre exacto de las clases. Deben incluir botella, tapa y etiqueta (se aceptan alias en inglés).
- Cantidad de imágenes por split (`train`, `valid`, `test`).
- URL o nombre del proyecto y versión de Roboflow.
- Si se va a reentrenar en local o solo se usarán los pesos ya entrenados.
- Opcional: API key, workspace y project ID si se quiere automatizar la descarga con la API de Roboflow.

Con el `.zip` colocado en `dataset/`, el comando `python scripts/verificar_dataset.py` comprueba automáticamente clases, rutas y cantidad de imágenes.

## 4. Cambios realizados

### `app.py`

- Se agregó `SIGIREC_MODEL_PATH` para indicar una ruta de modelo personalizada.
- Se agregó `SIGIREC_MODEL_VERSION` para registrar la versión usada en la base de datos.
- Se implementó `resolver_modelo()`, que busca el modelo en este orden:
  1. `SIGIREC_MODEL_PATH`
  2. `models/best.pt`
  3. El `runs/detect/<run>/weights/best.pt` más reciente
  4. `runs/detect/train-5/weights/best.pt` por compatibilidad
- Se implementó `version_desde_modelo()` para guardar en `analisis_ia.version_modelo` la versión real del modelo utilizado.
- Se implementó `normalizar_clase()` con alias para `botella`/`bottle`, `tapa`/`cap` y `etiqueta`/`label`.
- Al cargar el modelo se comparan sus clases normalizadas contra `botella`, `tapa` y `etiqueta`, y se muestra una advertencia si falta alguna.
- La inserción en `analisis_ia` ya no usa `"train-5"` fijo; usa `model_version`.

### `camara.py`

- Se reemplazó la ruta fija de `train-5` por la misma búsqueda flexible de modelo que usa la app.
- El índice de cámara se puede cambiar con `SIGIREC_CAMERA_INDEX`.

### `train.py`

- Ahora lee el dataset desde `dataset/data.yaml` o desde `SIGIREC_DATA_YAML`.
- Parámetros configurables: `SIGIREC_EPOCHS`, `SIGIREC_IMGSZ`, `SIGIREC_BATCH`, `SIGIREC_DEVICE`, `SIGIREC_RUN_NAME` y `SIGIREC_BASE_MODEL`.
- Valida que existan el `data.yaml` y el modelo base antes de entrenar.
- Al finalizar, copia automáticamente el mejor modelo a `models/best.pt`, que es la ruta estable que consume la aplicación.

### `scripts/verificar_dataset.py` (nuevo)

- Verifica un export de Roboflow en formato YOLOv8.
- Revisa `data.yaml`, nombres de clases, `nc`, rutas de `train`/`val`, cantidad de imágenes y etiquetas.
- Acepta una ruta alternativa: `python scripts/verificar_dataset.py ruta/al/data.yaml`.

### `.env.example`

- Se documentaron las variables opcionales del modelo y del dataset.

### `requirements.txt` y `requirements-local.txt`

- Se agregó `PyYAML` de forma explícita porque lo usa `scripts/verificar_dataset.py` para leer `data.yaml`.

### `README.md`

- Se actualizó la estructura del proyecto.
- Se actualizó la explicación de la carga del modelo.
- Se agregó la sección de descarga del dataset de Roboflow, verificación y entrenamiento.

## 5. Cómo dejar el proyecto funcionando

1. Descargar el dataset en formato **YOLOv8** desde Roboflow.
2. Descomprimirlo en `dataset/` (debe existir `dataset/data.yaml`).
3. Verificarlo:

```bash
python scripts/verificar_dataset.py
```

4. Instalar dependencias si hace falta:

```bash
pip install -r requirements.txt
```

5. Entrenar y publicar el modelo:

```bash
python train.py
```

6. Arrancar la app:

```bash
python app.py
```

7. Probar el escaneo desde la interfaz web. El log de arranque debe mostrar `MODELO SIGIREC CARGADO`, `RUTA`, `VERSION` y `CLASES`.

## 6. Pendientes

- Colocar el export real de Roboflow en `dataset/` o indicar la ruta con `SIGIREC_DATA_YAML`.
- Confirmar el contenido de `data.yaml` y los nombres exactos de las clases.
- Ejecutar el entrenamiento y validar la precisión con imágenes reales.
- Si se usa solo el modelo ya entrenado en Roboflow, colocar `best.pt` en `models/best.pt`.
