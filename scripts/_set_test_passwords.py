from pathlib import Path
import json
import time

from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash

project_dir = Path(__file__).resolve().parents[1]
load_dotenv(project_dir / ".env")

from conexion import obtener_conexion

clave = "Prueba1234"
h = generate_password_hash(clave)
c = obtener_conexion()
cur = c.cursor(dictionary=True)
cur.execute(
    "UPDATE usuarios SET clave_hash = %s "
    "WHERE clave_hash IS NULL OR clave_hash = ''",
    (h,),
)
c.commit()
updated = cur.rowcount
cur.execute(
    "SELECT numero_identificacion, tipo_usuario, rol FROM usuarios ORDER BY id_usuario"
)
rows = cur.fetchall()
cur.execute(
    "SELECT clave_hash FROM usuarios WHERE numero_identificacion = %s",
    ("3000000003",),
)
row = cur.fetchone()
ok = bool(row) and check_password_hash(row["clave_hash"], clave)
print("updated", updated)
print("verify_user3", ok)
for r in rows:
    print(r)
log = {
    "sessionId": "8a12b9",
    "runId": "pre-fix",
    "hypothesisId": "A",
    "location": "scripts/_set_test_passwords.py",
    "message": "test passwords assigned",
    "data": {
        "updated": updated,
        "verify_admin": ok,
        "users": [r["numero_identificacion"] for r in rows],
    },
    "timestamp": int(time.time() * 1000),
}
with open(project_dir / "debug-8a12b9.log", "a", encoding="utf-8") as f:
    f.write(json.dumps(log) + "\n")
cur.close()
c.close()
