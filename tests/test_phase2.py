import os
import re
import sys
from pathlib import Path

import pytest
from werkzeug.security import generate_password_hash

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SIGIREC_SECRET_KEY", "clave-de-prueba-suficientemente-larga")

import app as sigirec


class FakeCursor:
    def __init__(self, usuario=None):
        self.usuario = usuario
        self.resultado = None
        self.ultima_consulta = ""
        self.lastrowid = 0
        self.rowcount = 0

    def execute(self, consulta, parametros=None):
        self.ultima_consulta = consulta
        if "FROM usuarios" in consulta and self.usuario is not None:
            self.resultado = self.usuario

    def fetchone(self):
        return self.resultado

    def close(self):
        pass


class FakeConnection:
    def __init__(self, usuario=None):
        self.usuario = usuario
        self.cerrada = False

    def cursor(self, dictionary=False):
        return FakeCursor(self.usuario)

    def start_transaction(self):
        pass

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        self.cerrada = True


@pytest.fixture
def client():
    sigirec.app.config.update(TESTING=True)
    return sigirec.app.test_client()


def csrf_token(client):
    respuesta = client.get("/login")
    coincidencia = re.search(
        rb'name="csrf_token"\s+value="([^"]+)"',
        respuesta.data
    )
    assert coincidencia
    return coincidencia.group(1).decode("utf-8")


def test_calcular_puntos_aplica_umbral_y_topes_del_servidor():
    assert sigirec.calcular_puntos(
        {"botella": True, "tapa": True, "etiqueta": True},
        0.90
    ) == (50, 10, 5, 65)

    assert sigirec.calcular_puntos(
        {"botella": True, "tapa": True, "etiqueta": False},
        0.39
    ) == (0, 0, 0, 0)

    assert sigirec.calcular_puntos(
        {"botella": False, "tapa": True, "etiqueta": True},
        0.99
    ) == (0, 0, 0, 0)


def test_login_exige_csrf(client):
    respuesta = client.post(
        "/login",
        data={
            "numero_identificacion": "123",
            "clave": "clave-segura"
        }
    )
    assert respuesta.status_code == 302
    with client.session_transaction() as sesion:
        assert "id_usuario" not in sesion


def test_login_valido_inicia_sesion(client):
    usuario = {
        "id_usuario": 7,
        "numero_identificacion": "123",
        "nombre_completo": "Usuario de prueba",
        "correo": "usuario@example.invalid",
        "telefono": None,
        "rol": "APRENDIZ",
        "programa_formacion": "ADSO",
        "numero_ficha": "3139687",
        "tipo_usuario": "USUARIO",
        "clave_hash": generate_password_hash("clave-segura")
    }
    conexion = FakeConnection(usuario)

    with sigirec.app.app_context():
        with pytest.MonkeyPatch.context() as monkeypatch:
            monkeypatch.setattr(sigirec, "obtener_conexion", lambda: conexion)
            respuesta = client.post(
                "/login",
                data={
                    "csrf_token": csrf_token(client),
                    "numero_identificacion": "123",
                    "clave": "clave-segura"
                }
            )

    assert respuesta.status_code == 302
    assert respuesta.headers["Location"].endswith("/dashboard")
    with client.session_transaction() as sesion:
        assert sesion["id_usuario"] == 7


def test_login_invalido_no_inicia_sesion(client):
    usuario = {
        "id_usuario": 7,
        "numero_identificacion": "123",
        "nombre_completo": "Usuario de prueba",
        "correo": "usuario@example.invalid",
        "telefono": None,
        "rol": "APRENDIZ",
        "programa_formacion": "ADSO",
        "numero_ficha": "3139687",
        "tipo_usuario": "USUARIO",
        "clave_hash": generate_password_hash("clave-segura")
    }
    conexion = FakeConnection(usuario)

    with sigirec.app.app_context():
        with pytest.MonkeyPatch.context() as monkeypatch:
            monkeypatch.setattr(sigirec, "obtener_conexion", lambda: conexion)
            respuesta = client.post(
                "/login",
                data={
                    "csrf_token": csrf_token(client),
                    "numero_identificacion": "123",
                    "clave": "clave-incorrecta"
                }
            )

    assert respuesta.status_code == 302
    with client.session_transaction() as sesion:
        assert "id_usuario" not in sesion


def test_registro_no_confia_en_puntos_del_cliente(client):
    with client.session_transaction() as sesion:
        sesion["id_usuario"] = 7

    with sigirec.app.app_context():
        with pytest.MonkeyPatch.context() as monkeypatch:
            monkeypatch.setattr(
                sigirec,
                "obtener_conexion",
                lambda: FakeConnection({
                    "id_usuario": 7,
                    "nombre_completo": "Usuario de prueba",
                    "numero_identificacion": "123",
                    "tipo_usuario": "USUARIO",
                    "rol": "APRENDIZ"
                })
            )
            respuesta = client.post(
                "/api/registrar-reciclaje",
                json={
                    "puntos": 999999,
                    "botella_detectada": True
                },
                headers={"X-CSRFToken": csrf_token(client)}
            )

    assert respuesta.status_code == 400
    assert "escaneo" in respuesta.get_json()["error"].lower()


def test_plantilla_admin_escapa_datos_de_usuario():
    usuario = {
        "id_usuario": 9,
        "nombre_completo": '<script>alert("xss")</script>',
        "numero_identificacion": '"><img src=x>',
        "correo": "usuario@example.invalid",
        "telefono": None,
        "rol": "APRENDIZ",
        "tipo_usuario": "USUARIO",
        "programa_formacion": "ADSO",
        "numero_ficha": "3139687",
        "puntos_totales": 0,
        "escaneos_ia": 0
    }

    with sigirec.app.test_request_context("/admin/usuarios"):
        from flask import render_template, session

        session["id_usuario"] = 1
        session["nombre_completo"] = "Administrador"
        html = render_template("admin/usuarios.html", usuarios=[usuario])

    assert "<script>alert" not in html
    assert "&lt;script&gt;alert" in html
    assert 'onclick="abrirModalUsuario({' not in html
