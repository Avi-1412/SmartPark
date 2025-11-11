"""
Script manual para reinicializar la base de datos.

NOTA: Este script es OPCIONAL. La BD se inicializa automáticamente cuando
inicia el backend si está vacía.

Uso: python seed_usuarios.py

Este script:
1. Crea las tablas si no existen
2. LIMPIA todos los datos (usuarios, credenciales, historial)
3. Inserta usuarios de prueba

ADVERTENCIA: ¡Borrará todos los datos existentes!
"""

import sqlite3 as sql
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "crud.db")

def conectar():
    conexion = sql.connect(DB_PATH)
    return conexion

def main():
    """Función principal: reinicializar BD completamente"""
    print("=" * 60)
    print("⚠️  SmartPark - Reinicializador Manual de Base de Datos")
    print("=" * 60)
    print("\n⚠️  ADVERTENCIA: Esto BORRARÁ todos los datos existentes")
    confirmacion = input("\n¿Estás seguro? Escribe 'SI' para continuar: ").strip().upper()
    
    if confirmacion != "SI":
        print("❌ Operación cancelada")
        return
    
    from bd import inicializar_bd, seed_datos_iniciales
    
    try:
        # Paso 1: Crear tablas
        print("\n📋 Paso 1: Inicializando tablas...")
        inicializar_bd()
        
        # Paso 2: Limpiar datos
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM login")
        cursor.execute("DELETE FROM autos")
        cursor.execute("DELETE FROM usuarios")
        cursor.execute("DELETE FROM historial")
        conexion.commit()
        conexion.close()
        print("🗑️  Base de datos limpia")
        
        # Paso 3: Poblar con datos de prueba
        print("\n📋 Paso 2: Poblando base de datos...")
        seed_datos_iniciales()
        
        print("\n" + "=" * 60)
        print("✨ Base de datos reinicializada correctamente")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        exit(1)

if __name__ == "__main__":
    main()
