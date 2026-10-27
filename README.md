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
├── scripts/            # Utilidades de administración
├── yolov8n.pt          # Pesos base de YOLOv8n
├── runs/detect/        # Pesos del modelo entrenado (train-5/best.pt)
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

El servidor arranca en `http://127.0.0.1:5000`. El modelo de IA se carga desde `runs/detect/train-5/weights/best.pt`; si no está disponible, las funciones de escaneo quedan inhabilitadas con un mensaje de error.

La aplicación es exclusivamente web; no requiere instaladores de escritorio.

## Entrenamiento del modelo

```bash
python train.py
```

Entrena YOLOv8n con el dataset propio. Los pesos se guardan en `runs/detect/`. El modelo usado por la aplicación está en `runs/detect/train-5/weights/best.pt`.

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
