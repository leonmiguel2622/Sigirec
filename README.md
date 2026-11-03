# SigiRec

Sistema de gestión de reciclaje inteligente con inteligencia artificial. Detecta botellas PET, tapas y etiquetas mediante YOLOv8 y asigna puntos de reciclaje (SIGIPUNTOS) a los usuarios, quienes pueden canjearlos por productos ecológicos del catálogo.

Desarrollado por el equipo **SigiDev's** para la comunidad educativa SENA (aprendices, instructores y área administrativa) y público externo.

## Funcionalidades

### Usuario
- **Registro e inicio de sesión** con número de identificación, contraseña y roles (Aprendiz, Instructor, Área Administrativa, Externo)
- **Detección IA**: escanea botellas PET mediante la cámara usando un modelo YOLOv8 entrenado con dataset propio; identifica botella, tapa y etiqueta
- **Sistema de SIGIPUNTOS**: asigna puntos automáticamente según lo detectado (50 base + 10 tapa + 5 etiqueta)
- **Comprobantes de reciclaje**: genera automáticamente un comprobante numerado (SIGI-XXXXXX) por cada reciclaje registrado
- **Catálogo / Tienda**: canjea SIGIPUNTOS por productos ecológicos
- **Dashboard**: saldo de puntos, botellas recicladas, puntos obtenidos y último reciclaje
- **Comprobantes de canje**: numeración CANJ-XXXXXX

### Administrador
- **Panel administrativo** con estadísticas globales (usuarios, escaneos IA, puntos entregados, productos)
- **Gestión de usuarios**: crear, editar y eliminar usuarios; asignar rol y tipo de cuenta
- **Gestión de puntos**: agregar (bonificación) o quitar (penalización) SIGIPUNTOS manualmente
- **Gestión de productos / catálogo**: administrar catálogo de canje
- **Registro de reciclajes**: historial completo de análisis IA y comprobantes
- **Movimientos y canjes**: gestionar el intercambio de puntos por productos desde el panel
- **Auditoría**: registro de todas las acciones administrativas (quién, qué, cuándo e IP), usuarios nuevos, canjes recientes, análisis IA recientes, movimientos de puntos y **ranking** de recicladores
- **Ranking**: top de usuarios con más SIGIPUNTOS

## Tecnologías

### Backend
- Python 3.11 / Flask
- MySQL (gestionado en Clever Cloud)
- gunicorn (servidor de producción)

### IA / Visión
- YOLOv8 (Ultralytics)
- OpenCV
- PyTorch (CPU)

### Frontend
- HTML / CSS / JavaScript (DOM)
- Jinja2 (motor de plantillas)

### Despliegue
- Render (Web Service, configurado con `render.yaml` y `Procfile`)
- Clever Cloud (base de datos MySQL)

## Estructura del proyecto

```
SigiRec/
├── app.py              # Aplicación principal Flask (rutas, API, lógica)
├── conexion.py         # Conexión a MySQL (Clever Cloud)
├── train.py            # Entrenamiento del modelo YOLO
├── camara.py           # Prueba local de cámara en tiempo real
├── requirements.txt    # Dependencias Python
├── runtime.txt         # Versión de Python para despliegue
├── Procfile            # Comando de inicio en Render
├── render.yaml         # Configuración del despliegue en Render
├── .env.example        # Variables de entorno requeridas
├── migrations/         # Migraciones SQL
├── scripts/            # Utilidades de administración y verificación
├── dataset/            # Export de Roboflow en formato YOLOv8 (local)
├── models/             # Modelo estable usado por la app (best.pt)
├── yolov8n.pt          # Pesos base de YOLOv8n
├── runs/detect/        # Resultados de entrenamientos anteriores
├── static/             # Archivos estáticos (CSS, JS, imágenes)
└── templates/          # Plantillas Jinja2
    ├── auth/           # Login y registro
    ├── usuario/        # Dashboard, escaneo, catálogo, comprobantes
    └── admin/          # Panel administrativo
```

## Requisitos

- Python 3.11+
- MySQL 8.0+
- pip

## Instalación

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd SigiRec

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

## Configuración

1. Crear la base de datos e importar el esquema:

```sql
CREATE DATABASE sigirec;
```

2. Importar el esquema (`sigirec (3).sql`) y ejecutar la migración de seguridad:

```bash
mysql -u root -p sigirec < "sigirec (3).sql"
mysql -u root -p sigirec < migrations/001_phase2_security.sql
```

3. Copiar `.env.example` a `.env` y completar las variables:

```env
SIGIREC_SECRET_KEY=una-clave-larga-y-aleatoria
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=sigirec
CORS_ORIGINS=http://127.0.0.1:5000
```

4. Asignar la contraseña inicial de un administrador existente:

```bash
python scripts/set_password.py 0000000000 --admin
```

## Ejecución en modo web

```bash
python app.py
```

El servidor arranca en `http://127.0.0.1:5000`. El modelo de IA se resuelve en este orden: `SIGIREC_MODEL_PATH`, `models/best.pt`, el `runs/detect/<run>/weights/best.pt` más reciente y, por compatibilidad, `runs/detect/train-5/weights/best.pt`. Si no hay ningún modelo disponible, las funciones de escaneo quedan inhabilitadas con un mensaje de error.

La aplicación es exclusivamente web; no requiere instaladores de escritorio.

## Dataset de Roboflow y entrenamiento del modelo

1. En Roboflow abre el proyecto, entra a **Download Dataset** y elige el formato **YOLOv8** (también aparece como *YOLOv8 PyTorch TXT*). Descarga el `.zip`.
2. Descomprime el contenido dentro de `dataset/`, de modo que quede `dataset/data.yaml`.
3. Verifica el export antes de entrenar:

```bash
python scripts/verificar_dataset.py
```

4. Entrena con los pesos base de YOLOv8n:

```bash
python train.py
```

`train.py` lee `dataset/data.yaml`, guarda el entrenamiento en `runs/detect/` y publica una copia del mejor modelo en `models/best.pt`, que es la ruta estable que usa la aplicación. Las rutas y parámetros se pueden cambiar con las variables `SIGIREC_DATA_YAML`, `SIGIREC_EPOCHS`, `SIGIREC_IMGSZ`, `SIGIREC_BATCH`, `SIGIREC_DEVICE` y `SIGIREC_RUN_NAME`.

Si ya entrenaste en Roboflow y solo quieres usar esos pesos, descarga el `best.pt` del proyecto y colócalo en `models/best.pt` (o define `SIGIREC_MODEL_PATH`).

Las clases del dataset deben representar `botella`, `tapa` y `etiqueta`. El código también reconoce alias en inglés como `bottle`, `cap` y `label`.

## Despliegue en Render

Definido en `render.yaml` y `Procfile`. La conexión a la base de datos se realiza mediante variables de entorno cuando está disponible, y Render redespliega automáticamente con cada push a la rama principal.

- **URL de producción:** `https://sigirec.onrender.com`
- **CORS:** configura los orígenes permitidos con la variable de entorno `CORS_ORIGINS` (por defecto incluye el dominio de Render).

## Roles de usuario

| Rol | Descripción |
|-----|-------------|
| USUARIO | Acceso al dashboard, escaneo, catálogo y canje |
| ADMINISTRADOR | Gestión completa del sistema (usuarios, puntos, catálogo, canjes, auditoría) |

Los perfiles de registro (Aprendiz, Instructor, Área Administrativa y Externo) permiten identificar el tipo de usuario dentro de la institución.
