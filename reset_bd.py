"""
Script para resetear la base de datos
Borra la BD actual y crea una nueva con datos iniciales
"""

import sys
import os
import time

# Detectar automáticamente la ruta del proyecto
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from Backend.BaseDatos import bd

print("🔄 Reseteando base de datos...")

# Obtener la ruta de la BD de forma dinámica
db_path = os.path.join(script_dir, "Backend", "BaseDatos", "crud.db")

print(f"📁 Ubicación BD: {db_path}")

# Borrar archivo BD si existe
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        time.sleep(0.5)  # Esperar a que se libere el archivo
        print(f"✅ Archivo BD eliminado")
    except Exception as e:
        print(f"⚠️  Error al eliminar BD: {e}")
        print("⏳ Intentando de todas formas...")

# Crear BD nueva
try:
    bd.inicializar_bd()
    print("✅ Base de datos inicializada")
except Exception as e:
    print(f"❌ Error al inicializar BD: {e}")
    sys.exit(1)

# Insertar datos iniciales
try:
    bd.seed_datos_iniciales()
    print("✅ Datos iniciales insertados")
except Exception as e:
    print(f"⚠️  Advertencia al insertar datos: {e}")

# Verificar
try:
    conn = bd.conectar()
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM usuarios")
    users = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM login")
    logins = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM historial")
    historial = c.fetchone()[0]
    
    conn.close()
    
    print(f"\n📊 BD reseteada correctamente")
    print(f"   - Usuarios: {users}")
    print(f"   - Credenciales: {logins}")
    print(f"   - Registros historial: {historial}")
    print(f"\n✅ Sistema listo para usar")
    
except Exception as e:
    print(f"❌ Error al verificar BD: {e}")
