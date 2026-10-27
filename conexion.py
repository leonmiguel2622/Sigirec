import os


def _configuracion():
    faltantes = [
        nombre
        for nombre in ("DB_HOST", "DB_USER", "DB_NAME")
        if not os.getenv(nombre)
    ]
    if faltantes:
        print(
            "Faltan variables de entorno de base de datos: "
            + ", ".join(faltantes)
        )
        return None

    try:
        puerto = int(os.getenv("DB_PORT", "3306"))
        timeout = int(os.getenv("DB_CONNECT_TIMEOUT", "10"))
    except ValueError:
        print("DB_PORT y DB_CONNECT_TIMEOUT deben ser números válidos.")
        return None

    return {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME"),
        "port": puerto,
        "connection_timeout": timeout,
        "autocommit": False,
        "charset": "utf8mb4"
    }


def obtener_conexion():
    configuracion = _configuracion()
    if configuracion is None:
        return None

    try:
        import mysql.connector
    except ImportError:
        print("Falta instalar mysql-connector-python.")
        return None

    try:
        return mysql.connector.connect(**configuracion)
    except Exception as e:
        print(f"Error al conectar con MySQL: {e}")
        return None
