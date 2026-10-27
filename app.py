import base64
import os
import secrets
import threading
import time
import traceback
from collections import defaultdict, deque
from datetime import timedelta

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

from flask import (
    Flask,
    g,
    request,
    jsonify,
    session,
    redirect,
    url_for,
    render_template,
    flash
)
from flask_wtf.csrf import CSRFError, CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash, generate_password_hash

from conexion import obtener_conexion

try:
    import cv2
    import numpy as np
    vision_error = None
except Exception as e:
    cv2 = None
    np = None
    vision_error = str(e)

try:
    from ultralytics import YOLO
except Exception as e:
    YOLO = None
    yolo_import_error = str(e)
else:
    yolo_import_error = None


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# #region agent log
def _agent_log(hypothesis_id, location, message, data=None, run_id="pre-fix"):
    import json as _json
    try:
        with open(os.path.join(BASE_DIR, "debug-8a12b9.log"), "a", encoding="utf-8") as _f:
            _f.write(_json.dumps({
                "sessionId": "8a12b9",
                "runId": run_id,
                "hypothesisId": hypothesis_id,
                "location": location,
                "message": message,
                "data": data or {},
                "timestamp": int(time.time() * 1000),
            }) + "\n")
    except Exception:
        pass
# #endregion

try:
    from dotenv import load_dotenv
except ImportError:
    pass
else:
    load_dotenv(os.path.join(BASE_DIR, ".env"))

DATA_DIR = os.getenv("SIGIREC_DATA_DIR") or os.path.join(BASE_DIR, "instance")
ES_PRODUCCION = bool(
    os.getenv("RENDER")
    or os.getenv("SIGIREC_ENV", "").lower() == "production"
    or os.getenv("FLASK_ENV", "").lower() == "production"
)

PUNTOS_BASE = 50
PUNTOS_TAPA = 10
PUNTOS_ETIQUETA = 5
CONFIANZA_MINIMA = float(os.getenv("SIGIREC_MIN_CONFIDENCE", "0.40"))


class RateLimiter:
    def __init__(self, limite, ventana_segundos):
        self.limite = limite
        self.ventana = ventana_segundos
        self.eventos = defaultdict(deque)
        self.lock = threading.Lock()

    def permitido(self, clave):
        ahora = time.monotonic()
        with self.lock:
            eventos = self.eventos[clave]
            while eventos and ahora - eventos[0] >= self.ventana:
                eventos.popleft()
            if len(eventos) >= self.limite:
                return False
            eventos.append(ahora)
            return True


login_limiter = RateLimiter(10, 300)
scan_limiter = RateLimiter(20, 60)
register_limiter = RateLimiter(10, 60)


def cargar_secret_key():
    clave = os.getenv("SIGIREC_SECRET_KEY") or os.getenv("SECRET_KEY")
    if clave:
        return clave

    if ES_PRODUCCION:
        raise RuntimeError(
            "Configura SIGIREC_SECRET_KEY o SECRET_KEY en producción."
        )

    os.makedirs(DATA_DIR, exist_ok=True)
    ruta = os.path.join(DATA_DIR, "secret_key")

    try:
        descriptor = os.open(
            ruta,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600
        )
    except FileExistsError:
        with open(ruta, "r", encoding="utf-8") as archivo:
            clave = archivo.read().strip()
        if not clave:
            raise RuntimeError("El archivo de clave de sesión está vacío.")
        return clave

    try:
        clave = secrets.token_hex(32)
        with os.fdopen(descriptor, "w", encoding="utf-8") as archivo:
            archivo.write(clave)
    finally:
        try:
            os.chmod(ruta, 0o600)
        except OSError:
            pass

    return clave


def calcular_puntos(detecciones, confianza):
    if not detecciones.get("botella"):
        return 0, 0, 0, 0

    if confianza < CONFIANZA_MINIMA:
        return 0, 0, 0, 0

    puntos_base = PUNTOS_BASE
    puntos_tapa = PUNTOS_TAPA if detecciones.get("tapa") else 0
    puntos_etiqueta = PUNTOS_ETIQUETA if detecciones.get("etiqueta") else 0

    return (
        puntos_base,
        puntos_tapa,
        puntos_etiqueta,
        puntos_base + puntos_tapa + puntos_etiqueta
    )


model = None
model_error = None

if YOLO is None:
    model_error = "Ultralytics no está instalado: " + (yolo_import_error or "desconocido")
    print("======================================")
    print("ERROR CARGANDO MODELO:", model_error)
    print("======================================")
    # #region agent log
    _agent_log("B", "app.py:yolo-none", "YOLO import failed", {"error": model_error})
    # #endregion
else:
    try:
        model_path = os.path.join(
            BASE_DIR,
            'runs', 'detect',
            'train-5', 'weights',
            'best.pt'
        )

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                "Modelo no encontrado en: " + model_path
            )

        model = YOLO(model_path)

        print("======================================")
        print("MODELO SIGIREC CARGADO")
        print("RUTA:", model.ckpt_path)
        print("CLASES:", model.names)
        print("======================================")
        # #region agent log
        _agent_log("B", "app.py:model-ok", "YOLO model loaded", {"path": str(model.ckpt_path)})
        # #endregion

    except Exception as e:
        model_error = str(e)
        print("======================================")
        print("ERROR CARGANDO MODELO:", e)
        print("======================================")
        # #region agent log
        _agent_log("B", "app.py:model-fail", "YOLO model load failed", {"error": model_error})
        # #endregion

app = Flask(__name__)
# #region agent log
_agent_log("C", "app.py:flask-init", "Flask app created")
# #endregion
app.secret_key = cargar_secret_key()
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=ES_PRODUCCION,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    MAX_CONTENT_LENGTH=10 * 1024 * 1024,
    WTF_CSRF_TIME_LIMIT=8 * 60 * 60
)

if ES_PRODUCCION or os.getenv("TRUST_PROXY") == "1":
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1
    )

csrf = CSRFProtect(app)

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "https://sigirec.onrender.com"
    ).split(",")
    if origin.strip()
]


@app.before_request
def validar_sesion():
    if request.endpoint in {"static", "index", "login", "register", "logout"}:
        return None

    if "id_usuario" not in session:
        return None

    es_api = request.path.startswith("/api/")
    conexion = obtener_conexion()

    if conexion is None:
        if es_api:
            return jsonify({"error": "Base de datos no disponible."}), 503
        session.clear()
        flash("No fue posible validar la sesión.", "danger")
        return redirect(url_for("login"))

    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                id_usuario,
                nombre_completo,
                numero_identificacion,
                tipo_usuario,
                rol
            FROM usuarios
            WHERE id_usuario = %s
            """,
            (session["id_usuario"],)
        )
        usuario = cursor.fetchone()

        if usuario is None:
            session.clear()
            if es_api:
                return jsonify({"error": "Sesión no válida."}), 401
            flash("La sesión ya no es válida.", "danger")
            return redirect(url_for("login"))

        session["nombre_completo"] = usuario["nombre_completo"]
        session["numero_identificacion"] = usuario["numero_identificacion"]
        session["tipo_usuario"] = usuario["tipo_usuario"]
        session["rol"] = usuario["rol"]
        g.usuario = usuario

    except Exception as e:
        print("ERROR VALIDANDO SESIÓN:", e)
        session.clear()
        if es_api:
            return jsonify({"error": "No fue posible validar la sesión."}), 503
        flash("No fue posible validar la sesión.", "danger")
        return redirect(url_for("login"))

    finally:
        cursor.close()
        conexion.close()

    return None


@app.after_request
def add_security_headers(response):
    origin = request.headers.get("Origin")

    if origin in cors_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, X-CSRFToken"
        )
        response.headers["Vary"] = "Origin"

    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    response.headers.setdefault(
        "Permissions-Policy",
        "camera=(self), microphone=(), geolocation=()"
    )
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; "
        "base-uri 'self'; "
        "frame-ancestors 'none'; "
        "form-action 'self'; "
        "img-src 'self' data: blob:; "
        "media-src 'self' blob:; "
        "connect-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'"
    )

    if request.path.startswith("/api/"):
        response.headers.setdefault("Cache-Control", "no-store")

    return response


@app.errorhandler(CSRFError)
def manejar_csrf_error(error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Token CSRF inválido o expirado."}), 400

    flash("La solicitud expiró. Intenta de nuevo.", "danger")
    if "id_usuario" in session:
        return redirect(url_for("admin_dashboard" if session.get("tipo_usuario") == "ADMINISTRADOR" else "dashboard"))
    return redirect(url_for("login"))


@app.errorhandler(413)
def manejar_archivo_grande(error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "La imagen supera el límite de 10 MB."}), 413

    flash("El archivo enviado es demasiado grande.", "danger")
    return redirect(url_for("login"))

# ==========================================
# INICIO
# ==========================================
@app.route("/")
def index():
    # #region agent log
    _agent_log("E", "app.py:index", "GET /", {"remote": request.remote_addr})
    # #endregion
    return redirect(url_for("login"))

# ==========================================
# LOGIN
# ==========================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not login_limiter.permitido(request.remote_addr or "desconocido"):
            flash(
                "Demasiados intentos. Espera unos minutos antes de volver a intentar.",
                "danger"
            )
            return render_template("auth/auth.html", modo="login"), 429

        numero_identificacion = request.form.get("numero_identificacion", "").strip()
        clave = request.form.get("clave", "")

        if not numero_identificacion or not clave:
            flash("Debes ingresar tu identificación y contraseña.", "danger")
            return redirect(url_for("login"))

        if len(clave) > 128:
            flash("La identificación o la contraseña no son correctas.", "danger")
            return redirect(url_for("login"))

        conexion = obtener_conexion()

        if conexion is None:
            flash("No fue posible conectar con la base de datos.", "danger")
            return redirect(url_for("login"))

        cursor = conexion.cursor(dictionary=True)

        try:
            consulta = """
                SELECT
                    id_usuario,
                    numero_identificacion,
                    nombre_completo,
                    correo,
                    telefono,
                    rol,
                    programa_formacion,
                    numero_ficha,
                    tipo_usuario,
                    clave_hash
                FROM usuarios
                WHERE numero_identificacion = %s
            """

            cursor.execute(
                consulta,
                (numero_identificacion,)
            )

            usuario = cursor.fetchone()

            if (
                usuario is None
                or not usuario.get("clave_hash")
                or not check_password_hash(usuario["clave_hash"], clave)
            ):
                flash("La identificación o la contraseña no son correctas.", "danger")
                return redirect(url_for("login"))

            session.clear()
            session.permanent = True
            session["id_usuario"] = usuario["id_usuario"]
            session["nombre_completo"] = usuario["nombre_completo"]
            session["numero_identificacion"] = usuario["numero_identificacion"]
            session["tipo_usuario"] = usuario["tipo_usuario"]
            session["rol"] = usuario["rol"]

            if usuario["tipo_usuario"] == "ADMINISTRADOR":
                return redirect(url_for("admin_dashboard"))

            return redirect(url_for("dashboard"))

        except Exception as e:
            print("ERROR LOGIN:", e)
            flash("No fue posible iniciar sesión. Intenta de nuevo.", "danger")
            return redirect(url_for("login"))

        finally:
            cursor.close()
            conexion.close()

    return render_template("auth/auth.html", modo="login")

# ==========================================
# REGISTER
# ==========================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not register_limiter.permitido(request.remote_addr or "desconocido"):
            flash("Demasiados intentos. Espera un momento.", "danger")
            return render_template("auth/auth.html", modo="register"), 429

        nombre_completo = request.form.get("nombre_completo", "").strip()
        numero_identificacion = request.form.get("numero_identificacion", "").strip()
        correo = request.form.get("correo", "").strip().lower()
        telefono = request.form.get("telefono", "").strip() or None
        rol = request.form.get("rol", "").strip()
        programa_formacion = request.form.get("programa_formacion", "").strip()
        numero_ficha = request.form.get("numero_ficha", "").strip()
        clave = request.form.get("clave", "")
        confirmar_clave = request.form.get("confirmar_clave", "")

        if not all([
            nombre_completo,
            numero_identificacion,
            correo,
            rol,
            programa_formacion,
            numero_ficha,
            clave,
            confirmar_clave
        ]):
            flash("Completa todos los campos obligatorios.", "danger")
            return redirect(url_for("register"))

        if len(clave) < 8 or len(clave) > 128:
            flash("La contraseña debe tener entre 8 y 128 caracteres.", "danger")
            return redirect(url_for("register"))

        if clave != confirmar_clave:
            flash("Las contraseñas no coinciden.", "danger")
            return redirect(url_for("register"))

        roles_validos = [
            "APRENDIZ",
            "INSTRUCTOR",
            "AREA_ADMINISTRATIVA",
            "EXTERNO"
        ]

        if rol not in roles_validos:
            flash("El rol seleccionado no es válido.", "danger")
            return redirect(url_for("register"))

        conexion = obtener_conexion()

        if conexion is None:
            flash("No fue posible conectar con la base de datos.", "danger")
            return redirect(url_for("register"))

        cursor = conexion.cursor()

        try:
            consulta = """
                INSERT INTO usuarios (
                    numero_identificacion,
                    nombre_completo,
                    correo,
                    telefono,
                    rol,
                    programa_formacion,
                    numero_ficha,
                    clave_hash
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            valores = (
                numero_identificacion,
                nombre_completo,
                correo,
                telefono,
                rol,
                programa_formacion,
                numero_ficha,
                generate_password_hash(clave)
            )

            cursor.execute(
                consulta,
                valores
            )

            conexion.commit()

            flash(
                "Cuenta creada correctamente. Ya puedes iniciar sesión.",
                "success"
            )

            return redirect(url_for("login"))

        except Exception as e:
            conexion.rollback()

            print("ERROR REGISTRO:", e)

            if "Duplicate entry" in str(e):
                flash(
                    "La identificación o el correo ya están registrados.",
                    "danger"
                )
            else:
                flash(
                    "No fue posible crear la cuenta. Intenta de nuevo.",
                    "danger"
                )

            return redirect(url_for("register"))

        finally:
            cursor.close()
            conexion.close()

    return render_template("auth/auth.html", modo="register")

# ==========================================
# DASHBOARD USUARIO
# ==========================================
@app.route("/dashboard")
def dashboard():

    if "id_usuario" not in session:
        return redirect(url_for("login"))

    if session.get("tipo_usuario") == "ADMINISTRADOR":
        return redirect(url_for("admin_dashboard"))

    conexion = obtener_conexion()

    if conexion is None:
        flash(
            "No fue posible conectar con la base de datos.",
            "danger"
        )
        return redirect(url_for("login"))

    cursor = conexion.cursor(dictionary=True)

    try:
        consulta = """
            SELECT
                u.id_usuario,
                u.nombre_completo,
                u.numero_identificacion,

                COALESCE(
                    (
                        SELECT SUM(mp1.puntos)
                        FROM movimientos_puntos mp1
                        WHERE mp1.id_usuario = u.id_usuario
                    ),
                    0
                ) AS puntos_totales,

                COALESCE(
                    (
                        SELECT COUNT(*)
                        FROM movimientos_puntos mp2
                        WHERE mp2.id_usuario = u.id_usuario
                        AND mp2.tipo_movimiento = 'RECICLAJE'
                    ),
                    0
                ) AS botellas_recicladas,

                COALESCE(
                    (
                        SELECT SUM(mp3.puntos)
                        FROM movimientos_puntos mp3
                        WHERE mp3.id_usuario = u.id_usuario
                        AND mp3.tipo_movimiento = 'RECICLAJE'
                    ),
                    0
                ) AS puntos_obtenidos,

                (
                    SELECT MAX(mp4.fecha_movimiento)
                    FROM movimientos_puntos mp4
                    WHERE mp4.id_usuario = u.id_usuario
                    AND mp4.tipo_movimiento = 'RECICLAJE'
                ) AS ultimo_reciclaje

            FROM usuarios u
            WHERE u.id_usuario = %s
        """

        cursor.execute(
            consulta,
            (session["id_usuario"],)
        )

        usuario = cursor.fetchone()

        if usuario is None:
            session.clear()

            flash(
                "El usuario no existe.",
                "danger"
            )

            return redirect(url_for("login"))

        return render_template(
            "usuario/dashboard.html",
            usuario=usuario
        )

    except Exception as e:
        print("ERROR DASHBOARD:", e)

        flash(
            "No fue posible cargar el dashboard.",
            "danger"
        )

        return redirect(url_for("login"))

    finally:
        cursor.close()
        conexion.close()

# ==========================================
# INFORMACIÓN SIGIREC
# ==========================================
@app.route("/informacion")
def informacion():

    if "id_usuario" not in session:
        return redirect(url_for("login"))

    if session.get("tipo_usuario") == "ADMINISTRADOR":
        return redirect(url_for("admin_dashboard"))

    return render_template(
        "usuario/informacion.html"
    )


@app.route("/escanear")
def escanear():

    if "id_usuario" not in session:
        return redirect(url_for("login"))

    if session.get("tipo_usuario") == "ADMINISTRADOR":
        return redirect(url_for("admin_dashboard"))

    conexion = obtener_conexion()

    if conexion is None:
        flash(
            "No fue posible conectar con la base de datos.",
            "danger"
        )

        return redirect(url_for("dashboard"))

    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT *
            FROM usuarios
            WHERE id_usuario = %s
            """,
            (session["id_usuario"],)
        )

        usuario = cursor.fetchone()

        if usuario is None:
            return redirect(url_for("logout"))

        return render_template(
            "usuario/escanear.html",
            usuario=usuario
        )

    finally:

        cursor.close()
        conexion.close()



# API DE ESCANEO Y REGISTRO DEL RECICLAJE

@app.route("/api/escanear", methods=["POST"])
def api_escanear():

    if "id_usuario" not in session:
        return jsonify({
            "error": "Sesión no válida."
        }), 401

    if not scan_limiter.permitido(f"usuario:{session['id_usuario']}"):
        return jsonify({
            "error": "Demasiados escaneos. Espera un momento."
        }), 429

    if "imagen" not in request.files:
        return jsonify({
            "error": "No se recibió ninguna imagen."
        }), 400

    if model is None:
        print("MODELO NO DISPONIBLE:", model_error)
        return jsonify({
            "error": "El modelo de IA no está disponible."
        }), 503

    if cv2 is None or np is None:
        print("VISIÓN NO DISPONIBLE:", vision_error)
        return jsonify({
            "error": "El procesamiento de imágenes no está disponible."
        }), 503

    archivo = request.files["imagen"]

    if archivo.filename == "":
        return jsonify({
            "error": "La imagen está vacía."
        }), 400

    if archivo.mimetype not in {"image/jpeg", "image/png", "image/webp"}:
        return jsonify({
            "error": "El formato de imagen no es válido."
        }), 415

    try:

        # =====================================================
        # LEER IMAGEN
        # =====================================================

        datos = archivo.read()

        if not datos:
            return jsonify({
                "error": "La imagen está vacía."
            }), 400

        print("TAMAÑO IMAGEN RECIBIDA:", len(datos), "bytes")

        imagen_array = np.frombuffer(
            datos,
            np.uint8
        )

        frame = cv2.imdecode(
            imagen_array,
            cv2.IMREAD_COLOR
        )

        if frame is None:
            print("ERROR: cv2.imdecode devolvió None")
            return jsonify({
                "error": "No fue posible procesar la imagen."
            }), 400

        if frame.shape[0] > 8000 or frame.shape[1] > 8000:
            return jsonify({
                "error": "Las dimensiones de la imagen no son válidas."
            }), 400

        print(
            "IMAGEN DECODED:",
            frame.shape[1], "x", frame.shape[0]
        )


        # =====================================================
        # REDIMENSIONAR PARA ACELERAR YOLO
        # =====================================================

        h_img, w_img = frame.shape[:2]
        max_dim = 640

        if max(h_img, w_img) > max_dim:
            scale = max_dim / max(h_img, w_img)
            frame = cv2.resize(
                frame,
                (int(w_img * scale), int(h_img * scale)),
                interpolation=cv2.INTER_AREA
            )


        # =====================================================
        # ANALIZAR CON YOLO
        # =====================================================

        try:
            resultados = model(
                frame,
                conf=0.15,
                imgsz=320,
                device="cpu",
                max_det=10,
                verbose=False
            )
        except Exception as yolo_err:
            print("ERROR YOLO INFERENCE:", yolo_err)
            return jsonify({
                "error": "No fue posible ejecutar el modelo de IA."
            }), 500

        resultado = resultados[0]

        clases_detectadas = []
        confianzas_por_clase = {}

        for box in resultado.boxes:

            clase_id = int(box.cls[0])

            confianza = float(box.conf[0])

            nombre_clase = (
                resultado.names[clase_id]
                .lower()
            )

            clases_detectadas.append({
                "clase": nombre_clase,
                "confianza": round(
                    confianza,
                    4
                )
            })

            confianzas_por_clase[nombre_clase] = max(
                confianza,
                confianzas_por_clase.get(nombre_clase, 0.0)
            )

        confianza_botella = confianzas_por_clase.get("botella", 0.0)
        confianza_maxima = max(confianzas_por_clase.values(), default=0.0)

        print("OBJETOS DETECTADOS:")
        print(clases_detectadas)


        # =====================================================
        # DETERMINAR OBJETOS
        # =====================================================

        botella_detectada = confianza_botella >= CONFIANZA_MINIMA

        tapa_detectada = (
            confianzas_por_clase.get("tapa", 0.0)
            >= CONFIANZA_MINIMA
        )

        etiqueta_detectada = (
            confianzas_por_clase.get("etiqueta", 0.0)
            >= CONFIANZA_MINIMA
        )


        # =====================================================
        # CALCULAR PUNTOS
        # =====================================================

        (
            puntos_base,
            puntos_tapa,
            puntos_etiqueta,
            puntos_totales
        ) = calcular_puntos(
            {
                "botella": botella_detectada,
                "tapa": tapa_detectada,
                "etiqueta": etiqueta_detectada
            },
            confianza_botella
        )


        # =====================================================
        # DIBUJAR RESULTADO YOLO
        # =====================================================

        annotated_frame = resultado.plot()


        # =====================================================
        # CONVERTIR IMAGEN A BASE64
        # =====================================================

        _, buffer = cv2.imencode(
            ".jpg",
            annotated_frame
        )

        imagen_base64 = base64.b64encode(
            buffer
        ).decode("utf-8")


        # =====================================================
        # GUARDAR ANÁLISIS EN MYSQL
        # =====================================================

        conexion = obtener_conexion()

        if conexion is None:
            return jsonify({
                "error": "No fue posible guardar el análisis."
            }), 503

        cursor = conexion.cursor()

        try:
            cursor.execute(
                """
                SELECT id_botella
                FROM botellas
                WHERE nombre = %s
                LIMIT 1
                """,
                ("Botella PET",)
            )
            fila_botella = cursor.fetchone()
            id_botella = fila_botella[0] if fila_botella else None

            cursor.execute(
                """
                INSERT INTO analisis_ia (
                    id_usuario,
                    id_botella,
                    imagen,
                    botella_detectada,
                    tapa_detectada,
                    etiqueta_detectada,
                    confianza,
                    puntos_base,
                    puntos_tapa,
                    puntos_etiqueta,
                    puntos_totales,
                    estado_analisis,
                    modelo_ia,
                    version_modelo
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s
                )
                """,
                (
                    session["id_usuario"],
                    id_botella,
                    None,
                    1 if botella_detectada else 0,
                    1 if tapa_detectada else 0,
                    1 if etiqueta_detectada else 0,
                    round(
                        (confianza_botella if botella_detectada else confianza_maxima) * 100,
                        2
                    ),
                    puntos_base,
                    puntos_tapa,
                    puntos_etiqueta,
                    puntos_totales,
                    "IDENTIFICADO" if botella_detectada else "NO_IDENTIFICADO",
                    "YOLO",
                    "train-5"
                )
            )
            id_analisis = cursor.lastrowid
            conexion.commit()

        except Exception as e:
            conexion.rollback()
            print("ERROR GUARDANDO ANÁLISIS:", e)
            return jsonify({
                "error": "No fue posible guardar el análisis."
            }), 500

        finally:
            cursor.close()
            conexion.close()


        # =====================================================
        # SI NO HAY BOTELLA
        # =====================================================

        if not botella_detectada:

            if confianza_botella > 0:
                titulo = "Confianza insuficiente"
                mensaje = (
                    "La botella no alcanzó la confianza mínima del "
                    f"{round(CONFIANZA_MINIMA * 100)}%."
                )
            else:
                titulo = "Botella no reconocida"
                mensaje = "No se detectó una botella válida."

            return jsonify({

                "success": False,

                "botella_detectada": False,

                "titulo": titulo,

                "mensaje": mensaje,

                "puntos": 0,

                "confianza":
                    confianza_maxima * 100,

                "detecciones":
                    clases_detectadas,

                "id_analisis": id_analisis,

                "scan_id": id_analisis,

                "imagen":
                    imagen_base64

            })


        # =====================================================
        # BOTELLA DETECTADA
        # =====================================================

        return jsonify({

            "success": True,

            "botella_detectada": True,

            "titulo":
                "Botella reconocida",

            "mensaje":
                "La botella fue reconocida correctamente.",

            "puntos":
                puntos_totales,

            "puntos_base":
                puntos_base,

            "puntos_tapa":
                puntos_tapa,

            "puntos_etiqueta":
                puntos_etiqueta,

            "confianza":
                confianza_botella * 100,

            "tapa_detectada":
                tapa_detectada,

            "etiqueta_detectada":
                etiqueta_detectada,

            "detecciones":
                clases_detectadas,

            "id_analisis": id_analisis,

            "scan_id": id_analisis,

            "imagen":
                imagen_base64

        })


    except Exception as e:

        print(
            "ERROR ANALIZANDO:",
            e
        )
        traceback.print_exc()

        return jsonify({
            "error": "No fue posible procesar el escaneo."
        }), 500



@app.route("/api/registrar-reciclaje", methods=["POST"])
def registrar_reciclaje():

    if "id_usuario" not in session:

        return jsonify({
            "error": "Sesión no válida."
        }), 401


    datos = request.get_json()

    if not datos:

        return jsonify({
            "error": "No se recibieron datos."
        }), 400


    if not scan_limiter.permitido(
        f"registro:{session['id_usuario']}"
    ):
        return jsonify({
            "error": "Demasiadas solicitudes. Espera un momento."
        }), 429

    try:
        scan_id = int(datos.get("scan_id", 0))
    except (TypeError, ValueError):
        scan_id = 0

    if scan_id <= 0:
        return jsonify({
            "error": "El escaneo no es válido."
        }), 400

    conexion = obtener_conexion()

    if conexion is None:
        return jsonify({
            "error": "No fue posible conectar con la base de datos."
        }), 503

    cursor = conexion.cursor(dictionary=True)


    try:

        conexion.start_transaction()

        cursor.execute(
            """
            SELECT
                id_analisis,
                id_usuario,
                botella_detectada,
                tapa_detectada,
                etiqueta_detectada,
                confianza,
                estado_analisis
            FROM analisis_ia
            WHERE id_analisis = %s
              AND id_usuario = %s
            FOR UPDATE
            """,
            (scan_id, session["id_usuario"])
        )

        analisis = cursor.fetchone()

        if analisis is None:
            conexion.rollback()
            return jsonify({
                "error": "El escaneo no existe o no pertenece a tu cuenta."
            }), 404

        if analisis["estado_analisis"] != "IDENTIFICADO":
            conexion.rollback()
            return jsonify({
                "error": "El escaneo no contiene una botella válida."
            }), 409

        cursor.execute(
            """
            SELECT id_movimiento
            FROM movimientos_puntos
            WHERE id_analisis = %s
              AND tipo_movimiento = 'RECICLAJE'
            LIMIT 1
            """,
            (scan_id,)
        )

        if cursor.fetchone() is not None:
            conexion.rollback()
            return jsonify({
                "error": "Este escaneo ya fue registrado."
            }), 409

        botella_detectada = bool(analisis["botella_detectada"])
        tapa_detectada = bool(analisis["tapa_detectada"])
        etiqueta_detectada = bool(analisis["etiqueta_detectada"])
        confianza = float(analisis["confianza"] or 0) / 100

        (
            puntos_base,
            puntos_tapa,
            puntos_etiqueta,
            puntos_totales
        ) = calcular_puntos(
            {
                "botella": botella_detectada,
                "tapa": tapa_detectada,
                "etiqueta": etiqueta_detectada
            },
            confianza
        )

        if not botella_detectada or puntos_totales <= 0:
            conexion.rollback()
            return jsonify({
                "error": "El escaneo no supera la confianza mínima."
            }), 409

        id_analisis = analisis["id_analisis"]


        # =================================================
        # OBTENER SALDO ACTUAL
        # =================================================

        cursor.execute(
            """
            SELECT COALESCE(
                SUM(puntos),
                0
            ) AS saldo
            FROM movimientos_puntos
            WHERE id_usuario = %s
            """,
            (
                session["id_usuario"],
            )
        )


        resultado_saldo = cursor.fetchone()

        saldo_anterior = int(
            (resultado_saldo or {}).get("saldo", 0) or 0
        )


        saldo_nuevo = (
            saldo_anterior
            + puntos_totales
        )


        # =================================================
        # MOVIMIENTO DE PUNTOS
        # =================================================

        motivo = (
            "Reciclaje detectado por IA: "
            "botella"
        )


        if tapa_detectada:

            motivo += " + tapa"


        if etiqueta_detectada:

            motivo += " + etiqueta"


        consulta_movimiento = """
            INSERT INTO movimientos_puntos (
                id_usuario,
                id_analisis,
                tipo_movimiento,
                puntos,
                motivo
            )
            VALUES (
                %s,
                %s,
                'RECICLAJE',
                %s,
                %s
            )
        """


        cursor.execute(
            consulta_movimiento,
            (
                session["id_usuario"],
                id_analisis,
                puntos_totales,
                motivo
            )
        )


        # =================================================
        # GENERAR COMPROBANTE
        # =================================================

        numero_comprobante = (
            "SIGI-"
            + str(id_analisis).zfill(6)
        )


        # =================================================
        # INSERTAR COMPROBANTE
        # =================================================

        consulta_comprobante = """
            INSERT INTO comprobantes_reciclaje (
                id_analisis,
                id_usuario,
                numero_comprobante,
                saldo_anterior,
                puntos_ganados,
                saldo_nuevo
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """


        cursor.execute(
            consulta_comprobante,
            (
                id_analisis,
                session["id_usuario"],
                numero_comprobante,
                saldo_anterior,
                puntos_totales,
                saldo_nuevo
            )
        )


        # =================================================
        # CONFIRMAR
        # =================================================

        conexion.commit()


        # =================================================
        # RESPUESTA
        # =================================================

        return jsonify({

            "success": True,

            "mensaje":
                "Botella registrada correctamente "
                "y puntos asignados.",

            "puntos":
                puntos_totales,

            "saldo_anterior":
                saldo_anterior,

            "saldo_nuevo":
                saldo_nuevo,

            "numero_comprobante":
                numero_comprobante

        })


    except Exception as e:

        conexion.rollback()

        print(
            "ERROR REGISTRANDO RECICLAJE:",
            e
        )

        return jsonify({
            "error": "No fue posible registrar el reciclaje."
        }), 500


    finally:

        cursor.close()

        conexion.close()



@app.route("/catalogo")
def catalogo():

    if "id_usuario" not in session:
        return redirect(url_for("login"))

    if session.get("tipo_usuario") == "ADMINISTRADOR":
        return redirect(url_for("admin_dashboard"))

    conexion = obtener_conexion()

    if conexion is None:
        flash(
            "No fue posible conectar con la base de datos.",
            "danger"
        )
        return redirect(url_for("dashboard"))

    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT *
            FROM usuarios
            WHERE id_usuario = %s
            """,
            (session["id_usuario"],)
        )

        usuario = cursor.fetchone()

        if usuario is None:
            flash(
                "No se encontró la información del usuario.",
                "danger"
            )
            return redirect(url_for("dashboard"))

        cursor.execute(
            """
            SELECT
                id_producto,
                nombre,
                descripcion,
                imagen,
                costo_puntos,
                stock
            FROM productos
            ORDER BY fecha_registro DESC
            """
        )

        productos = cursor.fetchall()

        return render_template(
            "usuario/catalogo.html",
            usuario=usuario,
            productos=productos
        )

    except Exception as e:

        print("ERROR CATÁLOGO:", e)

        flash(
            "No fue posible cargar el catálogo.",
            "danger"
        )

        return redirect(url_for("dashboard"))

    finally:

        cursor.close()
        conexion.close()


# ==========================================
# DASHBOARD ADMINISTRADOR
# ==========================================
@app.route("/admin")
def admin_dashboard():

    if "id_usuario" not in session:
        return redirect(url_for("login"))

    if session.get("tipo_usuario") != "ADMINISTRADOR":
        return redirect(url_for("dashboard"))

    conexion = obtener_conexion()

    if conexion is None:
        flash(
            "No fue posible conectar con la base de datos.",
            "danger"
        )
        return redirect(url_for("login"))

    cursor = conexion.cursor(dictionary=True)

    try:
        consulta = """
            SELECT
                (SELECT COUNT(*) FROM usuarios) AS usuarios_total,

                (SELECT COUNT(*) FROM analisis_ia) AS escaneos_ia,

                (
                    SELECT COALESCE(SUM(puntos), 0)
                    FROM movimientos_puntos
                    WHERE tipo_movimiento = 'RECICLAJE'
                ) AS puntos_entregados,

                (SELECT COUNT(*) FROM productos) AS productos_total
        """

        cursor.execute(consulta)

        estadisticas = cursor.fetchone()

        return render_template(
            "admin/dashboard.html",
            estadisticas=estadisticas
        )

    except Exception as e:
        print(
            "ERROR DASHBOARD ADMIN:",
            e
        )

        flash(
            "No fue posible cargar el dashboard administrativo.",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )

    finally:
        cursor.close()
        conexion.close()

# ==========================================
# GESTIÓN DE USUARIOS
# ==========================================
@app.route("/admin/usuarios")
def admin_usuarios():
    if "id_usuario" not in session:
        return redirect(url_for("login"))

    if session.get("tipo_usuario") != "ADMINISTRADOR":
        return redirect(url_for("dashboard"))

    conexion = obtener_conexion()

    if conexion is None:
        flash("No fue posible conectar con la base de datos.", "danger")
        return redirect(url_for("admin_dashboard"))

    cursor = conexion.cursor(dictionary=True)

    try:
        consulta = """
            SELECT
                u.id_usuario,
                u.nombre_completo,
                u.numero_identificacion,
                u.correo,
                u.telefono,
                u.rol,
                u.programa_formacion,
                u.numero_ficha,
                u.tipo_usuario,

                COALESCE(
                    (
                        SELECT SUM(mp.puntos)
                        FROM movimientos_puntos mp
                        WHERE mp.id_usuario = u.id_usuario
                    ),
                    0
                ) AS puntos_totales,

                (
                    SELECT COUNT(*)
                    FROM analisis_ia ai
                    WHERE ai.id_usuario = u.id_usuario
                ) AS escaneos_ia

            FROM usuarios u
            ORDER BY u.id_usuario DESC
        """

        cursor.execute(consulta)
        usuarios = cursor.fetchall()

        return render_template(
            "admin/usuarios.html",
            usuarios=usuarios
        )

    except Exception as e:
        print("ERROR GESTION USUARIOS:", e)
        flash("No fue posible cargar los usuarios.", "danger")
        return redirect(url_for("admin_dashboard"))

    finally:
        cursor.close()
        conexion.close()

# ==========================================
# EDITAR USUARIO
# ==========================================
@app.route(
    "/admin/usuarios/editar/<int:id_usuario>",
    methods=["GET", "POST"]
)
def admin_editar_usuario(id_usuario):

    if "id_usuario" not in session:
        return redirect(url_for("login"))

    if session.get("tipo_usuario") != "ADMINISTRADOR":
        return redirect(url_for("dashboard"))

    conexion = obtener_conexion()

    if conexion is None:
        flash(
            "No fue posible conectar con la base de datos.",
            "danger"
        )
        return redirect(
            url_for("admin_usuarios")
        )

    cursor = conexion.cursor(dictionary=True)

    try:

        if request.method == "GET":

            consulta = """
                SELECT
                    id_usuario,
                    numero_identificacion,
                    nombre_completo,
                    correo,
                    telefono,
                    rol,
                    programa_formacion,
                    numero_ficha,
                    tipo_usuario
                FROM usuarios
                WHERE id_usuario = %s
            """

            cursor.execute(
                consulta,
                (id_usuario,)
            )

            usuario = cursor.fetchone()

            if usuario is None:

                flash(
                    "El usuario no existe.",
                    "danger"
                )

                return redirect(
                    url_for("admin_usuarios")
                )

            return render_template(
                "admin/usuarios.html",
                usuarios=[usuario],
                editar=True,
                usuario_editar=usuario,
                busqueda=""
            )

        # ==================================
        # DATOS DEL FORMULARIO
        # ==================================

        nombre_completo = request.form.get(
            "nombre_completo",
            ""
        ).strip()

        numero_identificacion = request.form.get(
            "numero_identificacion",
            ""
        ).strip()

        correo = request.form.get(
            "correo",
            ""
        ).strip()

        telefono = request.form.get(
            "telefono",
            ""
        ).strip()

        rol = request.form.get(
            "rol",
            ""
        ).strip()

        programa_formacion = request.form.get(
            "programa_formacion",
            ""
        ).strip()

        numero_ficha = request.form.get(
            "numero_ficha",
            ""
        ).strip()

        tipo_usuario = request.form.get(
            "tipo_usuario",
            "USUARIO"
        ).strip()

        nueva_clave = request.form.get(
            "nueva_clave",
            ""
        )

        confirmar_clave = request.form.get(
            "confirmar_clave",
            ""
        )

        # ==================================
        # VALIDACIONES
        # ==================================

        if not all([
            nombre_completo,
            numero_identificacion,
            correo,
            rol,
            programa_formacion,
            numero_ficha
        ]):

            flash(
                "Completa todos los campos obligatorios.",
                "danger"
            )

            return redirect(
                url_for(
                    "admin_editar_usuario",
                    id_usuario=id_usuario
                )
            )

        roles_validos = [
            "APRENDIZ",
            "INSTRUCTOR",
            "AREA_ADMINISTRATIVA",
            "EXTERNO"
        ]

        if rol not in roles_validos:

            flash(
                "El rol seleccionado no es válido.",
                "danger"
            )

            return redirect(
                url_for(
                    "admin_editar_usuario",
                    id_usuario=id_usuario
                )
            )

        tipos_validos = [
            "USUARIO",
            "ADMINISTRADOR"
        ]

        if tipo_usuario not in tipos_validos:

            flash(
                "El tipo de usuario seleccionado no es válido.",
                "danger"
            )

            return redirect(
                url_for(
                    "admin_editar_usuario",
                    id_usuario=id_usuario
                )
            )

        if nueva_clave or confirmar_clave:
            if len(nueva_clave) < 8 or len(nueva_clave) > 128:
                flash(
                    "La nueva contraseña debe tener entre 8 y 128 caracteres.",
                    "danger"
                )
                return redirect(
                    url_for(
                        "admin_editar_usuario",
                        id_usuario=id_usuario
                    )
                )

            if nueva_clave != confirmar_clave:
                flash("Las contraseñas no coinciden.", "danger")
                return redirect(
                    url_for(
                        "admin_editar_usuario",
                        id_usuario=id_usuario
                    )
                )

        # ==================================
        # EVITAR QUE EL ADMIN SE ELIMINE
        # SU PROPIO ACCESO
        # ==================================

        if (
            id_usuario == session["id_usuario"]
            and tipo_usuario != "ADMINISTRADOR"
        ):

            flash(
                "No puedes quitarte a ti mismo el acceso de administrador.",
                "danger"
            )

            return redirect(
                url_for(
                    "admin_editar_usuario",
                    id_usuario=id_usuario
                )
            )

        # ==================================
        # ACTUALIZAR
        # ==================================

        campos = [
            "numero_identificacion = %s",
            "nombre_completo = %s",
            "correo = %s",
            "telefono = %s",
            "rol = %s",
            "programa_formacion = %s",
            "numero_ficha = %s",
            "tipo_usuario = %s"
        ]

        valores = [
            numero_identificacion,
            nombre_completo,
            correo,
            telefono or None,
            rol,
            programa_formacion,
            numero_ficha,
            tipo_usuario
        ]

        if nueva_clave:
            campos.append("clave_hash = %s")
            valores.append(generate_password_hash(nueva_clave))

        valores.append(id_usuario)

        consulta = (
            "UPDATE usuarios SET "
            + ", ".join(campos)
            + " WHERE id_usuario = %s"
        )

        cursor.execute(
            consulta,
            tuple(valores)
        )

        # ==================================
        # REGISTRAR AUDITORÍA
        # ==================================

        descripcion_auditoria = (
            f"Se modificaron los datos del usuario "
            f"{nombre_completo} "
            f"(ID: {id_usuario})."
        )

        if nueva_clave:
            descripcion_auditoria += " Contraseña actualizada."

        cursor.execute(
            """
            INSERT INTO auditoria
            (
                id_usuario,
                accion,
                tabla_afectada,
                id_registro,
                descripcion,
                ip
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                session.get("id_usuario"),
                "ACTUALIZAR",
                "usuarios",
                id_usuario,
                descripcion_auditoria,
                request.remote_addr
            )
        )

        conexion.commit()

        # Si el administrador editó su propia información,
        # actualizamos también la sesión.
        if id_usuario == session["id_usuario"]:

            session["nombre_completo"] = nombre_completo
            session["numero_identificacion"] = numero_identificacion
            session["tipo_usuario"] = tipo_usuario
            session["rol"] = rol

        flash(
            "Usuario actualizado correctamente.",
            "success"
        )

        return redirect(
            url_for("admin_usuarios")
        )

    except Exception as e:

        conexion.rollback()

        print(
            "ERROR EDITANDO USUARIO:",
            e
        )

        if "Duplicate entry" in str(e):

            flash(
                "La identificación o el correo ya pertenecen a otro usuario.",
                "danger"
            )

        else:

            flash(
                "No fue posible actualizar el usuario.",
                "danger"
            )

        return redirect(
            url_for("admin_usuarios")
        )

    finally:
        cursor.close()
        conexion.close()

# ==========================================
# ELIMINAR USUARIO
# ==========================================
@app.route(
    "/admin/usuarios/eliminar/<int:id_usuario>",
    methods=["POST"]
)
def admin_eliminar_usuario(id_usuario):

    if "id_usuario" not in session:
        return redirect(url_for("login"))

    if session.get("tipo_usuario") != "ADMINISTRADOR":
        return redirect(url_for("dashboard"))

    # ==================================
    # NO PERMITIR ELIMINARSE A SÍ MISMO
    # ==================================

    if id_usuario == session["id_usuario"]:

        flash(
            "No puedes eliminar tu propia cuenta de administrador.",
            "danger"
        )

        return redirect(
            url_for("admin_usuarios")
        )

    conexion = obtener_conexion()

    if conexion is None:
        flash(
            "No fue posible conectar con la base de datos.",
            "danger"
        )
        return redirect(
            url_for("admin_usuarios")
        )

    cursor = conexion.cursor()

    try:

        consulta = """
            DELETE FROM usuarios
            WHERE id_usuario = %s
        """

        cursor.execute(
            consulta,
            (id_usuario,)
        )

        if cursor.rowcount == 0:

            conexion.rollback()
            flash(
                "El usuario no existe.",
                "danger"
            )

            return redirect(
                url_for("admin_usuarios")
            )

        cursor.execute("""
            INSERT INTO auditoria (
                id_usuario,
                accion,
                tabla_afectada,
                id_registro,
                descripcion,
                ip
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            session["id_usuario"],
            "ELIMINAR",
            "usuarios",
            id_usuario,
            f"Se eliminó el usuario ID {id_usuario}.",
            request.remote_addr
        ))

        conexion.commit()

        flash(
            "Usuario eliminado correctamente.",
            "success"
        )

        return redirect(
            url_for("admin_usuarios")
        )

    except Exception as e:

        conexion.rollback()

        print(
            "ERROR ELIMINANDO USUARIO:",
            e
        )

        flash(
            "No se pudo eliminar el usuario. "
            "Es posible que tenga registros relacionados "
            "en otras tablas.",
            "danger"
        )

        return redirect(
            url_for("admin_usuarios")
        )

    finally:
        cursor.close()
        conexion.close()


# ==========================================
# AGREGAR PUNTOS
# ==========================================
@app.route("/admin/usuarios/puntos/agregar/<int:id_usuario>", methods=["POST"])
def agregar_puntos(id_usuario):
    if "id_usuario" not in session:
        return redirect(url_for("login"))

    if session.get("tipo_usuario") != "ADMINISTRADOR":
        return redirect(url_for("dashboard"))

    try:
        puntos = int(request.form.get("puntos", 0))
    except (ValueError, TypeError):
        puntos = 0

    motivo = request.form.get("motivo", "").strip()

    if puntos <= 0:
        flash("La cantidad de puntos debe ser mayor que 0.", "danger")
        return redirect(url_for("admin_usuarios"))

    conexion = obtener_conexion()

    if conexion is None:
        flash("No fue posible conectar con la base de datos.", "danger")
        return redirect(url_for("admin_usuarios"))

    cursor = conexion.cursor(dictionary=True)

    try:
        conexion.start_transaction()

        cursor.execute("""
            SELECT id_usuario
            FROM usuarios
            WHERE id_usuario = %s
            FOR UPDATE
        """, (id_usuario,))

        if cursor.fetchone() is None:
            conexion.rollback()
            flash("El usuario no existe.", "danger")
            return redirect(url_for("admin_usuarios"))

        consulta = """
            INSERT INTO movimientos_puntos (
                id_usuario,
                tipo_movimiento,
                puntos,
                motivo,
                id_usuario_admin
            )
            VALUES (%s, %s, %s, %s, %s)
        """

        valores = (
            id_usuario,
            "BONIFICACION",
            puntos,
            motivo if motivo else "Bonificación manual realizada por administrador",
            session["id_usuario"]
        )

        cursor.execute(consulta, valores)
        id_movimiento = cursor.lastrowid

        cursor.execute("""
            INSERT INTO auditoria (
                id_usuario,
                accion,
                tabla_afectada,
                id_registro,
                descripcion,
                ip
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            session["id_usuario"],
            "BONIFICACION",
            "movimientos_puntos",
            id_movimiento,
            f"Se agregaron {puntos} SIGIPUNTOS al usuario ID {id_usuario}.",
            request.remote_addr
        ))

        conexion.commit()

        flash(
            f"Se agregaron {puntos} SIGIPUNTOS correctamente.",
            "success"
        )

    except Exception as e:
        conexion.rollback()
        print("ERROR AGREGANDO PUNTOS:", e)
        flash("No fue posible agregar los puntos.", "danger")

    finally:
        cursor.close()
        conexion.close()

    return redirect(url_for("admin_usuarios"))


# ==========================================
# QUITAR PUNTOS
# ==========================================
@app.route("/admin/usuarios/puntos/quitar/<int:id_usuario>", methods=["POST"])
def quitar_puntos(id_usuario):
    if "id_usuario" not in session:
        return redirect(url_for("login"))

    if session.get("tipo_usuario") != "ADMINISTRADOR":
        return redirect(url_for("dashboard"))

    try:
        puntos = int(request.form.get("puntos", 0))
    except (ValueError, TypeError):
        puntos = 0

    motivo = request.form.get("motivo", "").strip()

    if puntos <= 0:
        flash("La cantidad de puntos debe ser mayor que 0.", "danger")
        return redirect(url_for("admin_usuarios"))

    conexion = obtener_conexion()

    if conexion is None:
        flash("No fue posible conectar con la base de datos.", "danger")
        return redirect(url_for("admin_usuarios"))

    cursor = conexion.cursor(dictionary=True)

    try:
        conexion.start_transaction()

        cursor.execute("""
            SELECT id_usuario
            FROM usuarios
            WHERE id_usuario = %s
            FOR UPDATE
        """, (id_usuario,))

        if cursor.fetchone() is None:
            conexion.rollback()
            flash("El usuario no existe.", "danger")
            return redirect(url_for("admin_usuarios"))

        consulta_saldo = """
            SELECT COALESCE(SUM(puntos), 0) AS saldo
            FROM movimientos_puntos
            WHERE id_usuario = %s
        """

        cursor.execute(consulta_saldo, (id_usuario,))
        resultado = cursor.fetchone()

        saldo_actual = int(resultado["saldo"] or 0)

        if puntos > saldo_actual:
            conexion.rollback()
            flash(
                f"El usuario solamente tiene {saldo_actual} SIGIPUNTOS.",
                "danger"
            )
            return redirect(url_for("admin_usuarios"))

        consulta = """
            INSERT INTO movimientos_puntos (
                id_usuario,
                tipo_movimiento,
                puntos,
                motivo,
                id_usuario_admin
            )
            VALUES (%s, %s, %s, %s, %s)
        """

        valores = (
            id_usuario,
            "PENALIZACION",
            -puntos,
            motivo if motivo else "Descuento manual realizado por administrador",
            session["id_usuario"]
        )

        cursor.execute(consulta, valores)
        id_movimiento = cursor.lastrowid

        cursor.execute("""
            INSERT INTO auditoria (
                id_usuario,
                accion,
                tabla_afectada,
                id_registro,
                descripcion,
                ip
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            session["id_usuario"],
            "PENALIZACION",
            "movimientos_puntos",
            id_movimiento,
            f"Se quitaron {puntos} SIGIPUNTOS al usuario ID {id_usuario}.",
            request.remote_addr
        ))

        conexion.commit()

        flash(
            f"Se quitaron {puntos} SIGIPUNTOS correctamente.",
            "success"
        )

    except Exception as e:
        conexion.rollback()
        print("ERROR QUITANDO PUNTOS:", e)
        flash("No fue posible quitar los puntos.", "danger")

    finally:
        cursor.close()
        conexion.close()

    return redirect(url_for("admin_usuarios"))


# ==========================================
# LOGOUT
# ==========================================
@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )



@app.route("/admin/reciclajes")
def admin_reciclajes():

    if "id_usuario" not in session:
        return redirect(url_for("login"))

    if session.get("tipo_usuario") != "ADMINISTRADOR":
        return redirect(url_for("dashboard"))

    conexion = obtener_conexion()

    if conexion is None:
        flash(
            "No fue posible conectar con la base de datos.",
            "danger"
        )
        return redirect(url_for("admin_dashboard"))

    cursor = conexion.cursor(dictionary=True)

    try:

        # ==========================================
        # ANÁLISIS IA REGISTRADOS
        # ==========================================

        cursor.execute("""
            SELECT
                a.id_analisis,
                a.id_usuario,
                a.botella_detectada,
                a.tapa_detectada,
                a.etiqueta_detectada,
                a.confianza,
                a.puntos_base,
                a.puntos_tapa,
                a.puntos_etiqueta,
                a.puntos_totales,
                a.estado_analisis,
                a.fecha_analisis,

                u.nombre_completo,
                u.numero_identificacion,

                cr.numero_comprobante,
                cr.saldo_anterior,
                cr.saldo_nuevo

            FROM analisis_ia a

            INNER JOIN usuarios u
                ON a.id_usuario = u.id_usuario

            LEFT JOIN comprobantes_reciclaje cr
                ON cr.id_analisis = a.id_analisis

            ORDER BY a.fecha_analisis DESC
        """)

        reciclajes = cursor.fetchall()


        # ==========================================
        # MOSTRAR VISTA
        # ==========================================

        return render_template(
            "admin/admin_reciclajes.html",
            reciclajes=reciclajes
        )


    except Exception as e:

        print("ERROR RECICLAJES ADMIN:", e)

        return render_template(
            "admin/admin_reciclajes.html",
            reciclajes=[]
        )


    finally:

        cursor.close()
        conexion.close()






@app.route("/admin/catalogo")
def admin_catalogo():

    if "id_usuario" not in session:
        return redirect(url_for("login"))

    if session.get("tipo_usuario") != "ADMINISTRADOR":
        return redirect(url_for("dashboard"))

    conexion = obtener_conexion()

    if conexion is None:
        flash(
            "No fue posible conectar con la base de datos.",
            "danger"
        )
        return redirect(url_for("login"))

    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id_producto,
                nombre,
                descripcion,
                imagen,
                costo_puntos,
                stock,
                fecha_registro
            FROM productos
            ORDER BY fecha_registro DESC
        """)

        productos = cursor.fetchall()

        print("PRODUCTOS CATALOGO:", productos)

        return render_template(
            "admin/admin_catalogo.html",
            productos=productos
        )

    except Exception as e:

        print("ERROR CATALOGO ADMIN:", e)

        flash(
            "No fue posible cargar el catálogo.",
            "danger"
        )

        return render_template(
            "admin/admin_catalogo.html",
            productos=[]
        )

    finally:

        cursor.close()
        conexion.close()





# ==========================================
# AUDITORÍAS
# ==========================================
@app.route("/admin/auditorias")
def admin_auditorias():

    if "id_usuario" not in session:
        return redirect(url_for("login"))

    if session.get("tipo_usuario") != "ADMINISTRADOR":
        return redirect(url_for("dashboard"))

    conexion = None
    cursor = None

    try:

        conexion = obtener_conexion()

        if conexion is None:
            flash(
                "No fue posible conectar con la base de datos.",
                "danger"
            )
            return redirect(url_for("admin_dashboard"))

        cursor = conexion.cursor(dictionary=True)

        # ==========================================
        # AUDITORÍAS (REGISTRO DEL SISTEMA)
        # ==========================================

        cursor.execute("""
            SELECT
                a.id_auditoria,
                a.id_usuario,
                a.accion,
                a.tabla_afectada,
                a.id_registro,
                a.descripcion,
                a.ip,
                a.fecha,

                u.nombre_completo,
                u.numero_identificacion

            FROM auditoria a

            LEFT JOIN usuarios u
                ON a.id_usuario = u.id_usuario

            ORDER BY a.fecha DESC

            LIMIT 100
        """)

        auditorias = cursor.fetchall()

        # ==========================================
        # USUARIOS RECIENTES
        # ==========================================

        cursor.execute("""
            SELECT
                u.id_usuario,
                u.numero_identificacion,
                u.nombre_completo,
                u.correo,
                u.numero_ficha,
                u.rol,

                COALESCE(
                    (
                        SELECT SUM(mp.puntos)
                        FROM movimientos_puntos mp
                        WHERE mp.id_usuario = u.id_usuario
                    ),
                    0
                ) AS puntos_totales

            FROM usuarios u

            WHERE u.tipo_usuario = 'USUARIO'

            ORDER BY u.id_usuario DESC

            LIMIT 10
        """)

        usuarios_nuevos = cursor.fetchall()

        # ==========================================
        # CANJES RECIENTES
        # ==========================================

        cursor.execute("""
            SELECT
                c.id_canje,
                c.total_puntos,
                c.fecha_canje,

                u.nombre_completo,
                u.numero_identificacion,

                (
                    SELECT mp.motivo
                    FROM movimientos_puntos mp
                    WHERE mp.id_canje = c.id_canje
                    LIMIT 1
                ) AS descripcion_canje

            FROM canjes c

            LEFT JOIN usuarios u
                ON c.id_usuario = u.id_usuario

            ORDER BY c.fecha_canje DESC

            LIMIT 15
        """)

        canjes_recientes = cursor.fetchall()

        # ==========================================
        # ANÁLISIS IA RECIENTES
        # ==========================================

        cursor.execute("""
            SELECT
                ai.id_analisis,
                ai.fecha_analisis,
                ai.botella_detectada,
                ai.tapa_detectada,
                ai.etiqueta_detectada,
                ai.puntos_totales,
                ai.confianza,
                ai.estado_analisis,

                u.nombre_completo,
                u.numero_identificacion

            FROM analisis_ia ai

            LEFT JOIN usuarios u
                ON ai.id_usuario = u.id_usuario

            ORDER BY ai.fecha_analisis DESC

            LIMIT 15
        """)

        analisis_recientes = cursor.fetchall()

        # ==========================================
        # MOVIMIENTOS DE PUNTOS RECIENTES
        # ==========================================

        cursor.execute("""
            SELECT
                mp.id_movimiento,
                mp.tipo_movimiento,
                mp.puntos,
                mp.motivo,
                mp.fecha_movimiento,

                u.nombre_completo,
                u.numero_identificacion

            FROM movimientos_puntos mp

            LEFT JOIN usuarios u
                ON mp.id_usuario = u.id_usuario

            ORDER BY mp.fecha_movimiento DESC

            LIMIT 20
        """)

        movimientos_recientes = cursor.fetchall()

        # ==========================================
        # RANKING - TOP USUARIOS CON MÁS PUNTOS
        # ==========================================

        cursor.execute("""
            SELECT
                u.id_usuario,
                u.numero_identificacion,
                u.nombre_completo,

                COALESCE(SUM(mp.puntos), 0) AS puntos_totales,

                (
                    SELECT COUNT(*)
                    FROM analisis_ia ai
                    WHERE ai.id_usuario = u.id_usuario
                ) AS total_analisis,

                (
                    SELECT COUNT(*)
                    FROM canjes c
                    WHERE c.id_usuario = u.id_usuario
                ) AS total_canjes

            FROM usuarios u

            LEFT JOIN movimientos_puntos mp
                ON mp.id_usuario = u.id_usuario

            WHERE u.tipo_usuario = 'USUARIO'

            GROUP BY
                u.id_usuario,
                u.numero_identificacion,
                u.nombre_completo

            HAVING puntos_totales > 0

            ORDER BY puntos_totales DESC

            LIMIT 20
        """)

        ranking = cursor.fetchall()

        # ==========================================
        # ESTADÍSTICAS
        # ==========================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM auditoria
        """)

        total_acciones = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM usuarios
            WHERE tipo_usuario = 'USUARIO'
        """)

        total_usuarios = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM canjes
        """)

        total_canjes = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM analisis_ia
        """)

        total_analisis_ia = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM movimientos_puntos
        """)

        total_movimientos = cursor.fetchone()["total"]

        estadisticas = {
            "total_acciones": total_acciones,
            "total_usuarios": total_usuarios,
            "total_canjes": total_canjes,
            "total_analisis_ia": total_analisis_ia,
            "total_movimientos": total_movimientos
        }

        return render_template(
            "admin/admin_auditoria.html",
            auditorias=auditorias,
            usuarios_nuevos=usuarios_nuevos,
            canjes_recientes=canjes_recientes,
            analisis_recientes=analisis_recientes,
            movimientos_recientes=movimientos_recientes,
            ranking=ranking,
            estadisticas=estadisticas
        )

    except Exception as e:

        print("ERROR AUDITORIAS ADMIN:", e)

        return render_template(
            "admin/admin_auditoria.html",
            auditorias=[],
            usuarios_nuevos=[],
            canjes_recientes=[],
            analisis_recientes=[],
            movimientos_recientes=[],
            ranking=[],
            estadisticas={
                "total_acciones": 0,
                "total_usuarios": 0,
                "total_canjes": 0,
                "total_analisis_ia": 0,
                "total_movimientos": 0
            }
        )

    finally:

        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


# ==========================================
# MOVIMIENTOS (INTERCAMBIO DE PUNTOS)
# ==========================================
@app.route("/admin/movimientos")
def admin_movimientos():

    if "id_usuario" not in session:
        return redirect(url_for("login"))

    if session.get("tipo_usuario") != "ADMINISTRADOR":
        return redirect(url_for("dashboard"))

    conexion = obtener_conexion()

    if conexion is None:
        flash(
            "No fue posible conectar con la base de datos.",
            "danger"
        )
        return redirect(url_for("admin_dashboard"))

    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id_producto,
                nombre,
                descripcion,
                costo_puntos,
                stock
            FROM productos
            WHERE stock > 0
            ORDER BY costo_puntos ASC
        """)

        productos = cursor.fetchall()

        cursor.execute("""
            SELECT
                u.id_usuario,
                u.numero_identificacion,
                u.nombre_completo,

                COALESCE(
                    (
                        SELECT SUM(mp.puntos)
                        FROM movimientos_puntos mp
                        WHERE mp.id_usuario = u.id_usuario
                    ),
                    0
                ) AS puntos_totales

            FROM usuarios u
            WHERE u.tipo_usuario = 'USUARIO'
            ORDER BY u.nombre_completo ASC
        """)

        usuarios = cursor.fetchall()

        return render_template(
            "admin/movimientos.html",
            productos=productos,
            usuarios=usuarios
        )

    except Exception as e:

        print("ERROR MOVIMIENTOS:", e)
        flash(
            "No fue posible cargar los movimientos.",
            "danger"
        )
        return redirect(url_for("admin_dashboard"))

    finally:
        cursor.close()
        conexion.close()


@app.route("/admin/api/usuario/<identificacion>")
def api_buscar_usuario(identificacion):

    if "id_usuario" not in session:
        return jsonify({"error": "Sesión no válida."}), 401

    if session.get("tipo_usuario") != "ADMINISTRADOR":
        return jsonify({"error": "No autorizado."}), 403

    conexion = obtener_conexion()

    if conexion is None:
        return jsonify({"error": "Error de conexión."}), 500

    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                u.id_usuario,
                u.numero_identificacion,
                u.nombre_completo,
                u.correo,
                u.rol,

                COALESCE(
                    (
                        SELECT SUM(mp.puntos)
                        FROM movimientos_puntos mp
                        WHERE mp.id_usuario = u.id_usuario
                    ),
                    0
                ) AS puntos_totales

            FROM usuarios u
            WHERE u.numero_identificacion = %s
        """, (identificacion,))

        usuario = cursor.fetchone()

        if usuario is None:
            return jsonify({
                "error": "No se encontró un usuario con esa identificación."
            }), 404

        return jsonify(usuario)

    except Exception:
        return jsonify({"error": "No fue posible buscar el usuario."}), 500

    finally:
        cursor.close()
        conexion.close()


@app.route("/admin/movimientos/canjar", methods=["POST"])
def admin_canjar_puntos():

    if "id_usuario" not in session:
        return redirect(url_for("login"))

    if session.get("tipo_usuario") != "ADMINISTRADOR":
        return redirect(url_for("dashboard"))

    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({"error": "No se recibieron datos."}), 400

    try:
        id_usuario = int(datos.get("id_usuario", 0))
        id_producto = int(datos.get("id_producto", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Los datos del canje no son válidos."}), 400

    if id_usuario <= 0 or id_producto <= 0:
        return jsonify({
            "error": "Faltan datos: id_usuario e id_producto son obligatorios."
        }), 400

    conexion = obtener_conexion()

    if conexion is None:
        return jsonify({"error": "Error de conexión."}), 500

    cursor = conexion.cursor(dictionary=True)

    try:

        conexion.start_transaction()

        # ==========================================
        # 1. BLOQUEAR USUARIO Y VALIDAR EXISTENCIA
        # ==========================================

        cursor.execute("""
            SELECT id_usuario
            FROM usuarios
            WHERE id_usuario = %s
            FOR UPDATE
        """, (id_usuario,))

        if cursor.fetchone() is None:
            conexion.rollback()
            return jsonify({
                "error": "El usuario no existe."
            }), 404

        # ==========================================
        # 2. BLOQUEAR PRODUCTO Y VALIDAR STOCK
        # ==========================================

        cursor.execute("""
            SELECT id_producto, nombre, costo_puntos, stock
            FROM productos
            WHERE id_producto = %s
            FOR UPDATE
        """, (id_producto,))

        producto = cursor.fetchone()

        if producto is None:
            conexion.rollback()
            return jsonify({
                "error": "El producto no existe."
            }), 404

        if producto["stock"] <= 0:
            conexion.rollback()
            return jsonify({
                "error": "El producto no tiene stock disponible."
            }), 400

        # ==========================================
        # 3. OBTENER SALDO DEL USUARIO
        # ==========================================

        cursor.execute("""
            SELECT COALESCE(SUM(puntos), 0) AS saldo
            FROM movimientos_puntos
            WHERE id_usuario = %s
        """, (id_usuario,))

        resultado = cursor.fetchone()
        saldo_actual = int(resultado["saldo"] or 0)

        costo = int(producto["costo_puntos"])

        if saldo_actual < costo:
            conexion.rollback()
            return jsonify({
                "error": (
                    f"El usuario tiene {saldo_actual} SIGIPUNTOS "
                    f"pero el producto cuesta {costo}. "
                    f"Faltan {costo - saldo_actual} puntos."
                )
            }), 400

        # ==========================================
        # 4. INSERTAR CANJE
        # ==========================================

        cursor.execute("""
            INSERT INTO canjes (id_usuario, id_producto, total_puntos)
            VALUES (%s, %s, %s)
        """, (id_usuario, id_producto, costo))

        id_canje = cursor.lastrowid

        # ==========================================
        # 5. INSERTAR MOVIMIENTO DE PUNTOS
        # ==========================================

        motivo = (
            f"Canje de {costo} SIGIPUNTOS "
            f"por producto: {producto['nombre']}"
        )

        cursor.execute("""
            INSERT INTO movimientos_puntos (
                id_usuario,
                id_canje,
                tipo_movimiento,
                puntos,
                motivo,
                id_usuario_admin
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            id_usuario,
            id_canje,
            "CANJE",
            -costo,
            motivo,
            session["id_usuario"]
        ))

        # ==========================================
        # 6. ACTUALIZAR STOCK DEL PRODUCTO
        # ==========================================

        cursor.execute("""
            UPDATE productos
            SET stock = stock - 1
            WHERE id_producto = %s
              AND stock > 0
        """, (id_producto,))

        if cursor.rowcount != 1:
            conexion.rollback()
            return jsonify({
                "error": "El producto no tiene stock disponible."
            }), 409

        # ==========================================
        # 7. REGISTRAR AUDITORÍA
        # ==========================================

        cursor.execute("""
            INSERT INTO auditoria (
                id_usuario,
                accion,
                tabla_afectada,
                id_registro,
                descripcion,
                ip
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            session["id_usuario"],
            "CANJE",
            "productos",
            id_producto,
            (
                f"Canje de {costo} SIGIPUNTOS por "
                f"'{producto['nombre']}' "
                f"(Usuario ID: {id_usuario})."
            ),
            request.remote_addr
        ))

        # ==========================================
        # 8. CONFIRMAR
        # ==========================================

        conexion.commit()

        saldo_nuevo = saldo_actual - costo

        return jsonify({
            "success": True,
            "mensaje": (
                f"Canje exitoso: {producto['nombre']} "
                f"por {costo} SIGIPUNTOS."
            ),
            "saldo_anterior": saldo_actual,
            "saldo_nuevo": saldo_nuevo,
            "puntos_gastados": costo,
            "producto": producto["nombre"],
            "numero_canje": f"CANJ-{str(id_canje).zfill(6)}"
        })

    except Exception as e:

        conexion.rollback()
        print("ERROR CANJANDO:", e)
        return jsonify({
            "error": "No fue posible procesar el canje."
        }), 500

    finally:
        cursor.close()
        conexion.close()


# ==========================================
# EJECUTAR
# ==========================================
if __name__ == "__main__":
    # #region agent log
    db_ok = obtener_conexion() is not None
    _agent_log(
        "A",
        "app.py:main",
        "Starting Flask",
        {
            "db_ok": db_ok,
            "model_ok": model is not None,
            "model_error": model_error,
            "debug": os.getenv("FLASK_DEBUG") == "1",
            "cwd": os.getcwd(),
        },
    )
    # #endregion
    app.run(
        debug=os.getenv("FLASK_DEBUG") == "1"
    )

