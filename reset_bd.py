"""
Script para resetear la base de datos
Borra la BD actual y crea una nueva con datos iniciales
"""

import sys
import os

sys.path.insert(0, r'c:\Users\Avi\Documents\GitHub\SmartPark')

from Backend.BaseDatos import bd

print("🔄 Reseteando base de datos...")

# Borrar archivo BD si existe
db_path = r'c:\Users\Avi\Documents\GitHub\SmartPark\Backend\BaseDatos\crud.db'

if os.path.exists(db_path):
    os.remove(db_path)
    print(f"✅ Archivo BD eliminado: {db_path}")

# Crear BD nueva
bd.inicializar_bd()
print("✅ Base de datos inicializada")

# Insertar datos iniciales
bd.seed_datos_iniciales()
print("✅ Datos iniciales insertados")

# Verificar
conn = bd.conectar()
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM usuarios")
users = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM login")
logins = c.fetchone()[0]
conn.close()

print(f"\n📊 BD reseteada correctamente")
print(f"   - Usuarios: {users}")
print(f"   - Credenciales: {logins}")
