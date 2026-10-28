import mysql.connector

conn = mysql.connector.connect(host='127.0.0.1', user='root', password='', database='sigirec_web')
cursor = conn.cursor()

# Get all APRENDIZ users - using correct column names from earlier DESCRIBE
cursor.execute("SELECT id_usuario, numero_identificacion, nombre_completo, correo, telefono FROM usuarios WHERE rol = 'APRENDIZ'")
aprendices = cursor.fetchall()
print('Usuarios con rol APRENDIZ:')
for a in aprendices:
    print(' - ID_usuario:', a[0], '| Cédula:', a[1], '| Nombre:', a[2], '| Correo:', a[3], '| Tel:', a[4])

# Also show ALL users for reference
cursor.execute("SELECT id_usuario, numero_identificacion, nombre_completo, rol, tipo_usuario FROM usuarios")
all_users = cursor.fetchall()
print('\nTodos los usuarios:')
for u in all_users:
    print(' - ID_usuario:', u[0], '| Cédula:', u[1], '| Nombre:', u[2], '| Rol:', u[3], '| Tipo:', u[4])

cursor.close()
conn.close()