import argparse
import getpass
import sys
from pathlib import Path

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

project_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_dir))
load_dotenv(project_dir / ".env")

from conexion import obtener_conexion


def main():
    parser = argparse.ArgumentParser(
        description="Asigna o restablece la contraseña de un usuario SIGIREC."
    )
    parser.add_argument("identificacion", help="Número de identificación del usuario")
    parser.add_argument(
        "--admin",
        action="store_true",
        help="Convierte al usuario en administrador"
    )
    args = parser.parse_args()

    clave = getpass.getpass("Nueva contraseña: ")
    confirmar = getpass.getpass("Confirmar contraseña: ")

    if len(clave) < 8 or len(clave) > 128:
        print("La contraseña debe tener entre 8 y 128 caracteres.")
        return 1

    if clave != confirmar:
        print("Las contraseñas no coinciden.")
        return 1

    conexion = obtener_conexion()
    if conexion is None:
        print("No fue posible conectar con la base de datos.")
        return 1

    cursor = conexion.cursor()

    try:
        campos = "clave_hash = %s"
        valores = [generate_password_hash(clave)]

        if args.admin:
            campos += ", tipo_usuario = 'ADMINISTRADOR'"

        valores.append(args.identificacion)

        cursor.execute(
            f"UPDATE usuarios SET {campos} WHERE numero_identificacion = %s",
            tuple(valores)
        )
        conexion.commit()

        if cursor.rowcount == 0:
            print("No existe un usuario con esa identificación.")
            return 1

        print("Contraseña actualizada correctamente.")
        return 0

    except Exception as e:
        conexion.rollback()
        print(f"No fue posible actualizar la contraseña: {e}")
        return 1

    finally:
        cursor.close()
        conexion.close()


if __name__ == "__main__":
    raise SystemExit(main())
