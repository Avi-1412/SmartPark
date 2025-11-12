"""
Script para leer RFID del Arduino y enviar al backend
Lee datos del puerto Serial COM3 (Arduino)
Envía al endpoint /registrar/rfid del backend
"""

import serial
import json
import requests
import time
from datetime import datetime

# CONFIGURACIÓN
PUERTO_SERIAL = "COM3"
VELOCIDAD_BAUD = 9600
BACKEND_URL = "http://127.0.0.1:8000/registrar/rfid"

# Colores para terminal
class Colores:
    VERDE = '\033[92m'
    ROJO = '\033[91m'
    AMARILLO = '\033[93m'
    AZUL = '\033[94m'
    RESET = '\033[0m'

def conectar_serial():
    """Conecta al puerto serial del Arduino"""
    try:
        puerto = serial.Serial(PUERTO_SERIAL, VELOCIDAD_BAUD, timeout=1)
        print(f"{Colores.VERDE}✓ Conectado a Arduino en {PUERTO_SERIAL}{Colores.RESET}")
        return puerto
    except serial.SerialException as e:
        print(f"{Colores.ROJO}✗ Error al conectar a {PUERTO_SERIAL}: {e}{Colores.RESET}")
        return None

def leer_tarjeta(puerto):
    """Lee una tarjeta del Arduino y extrae el ID usuario"""
    try:
        linea = puerto.readline().decode('utf-8').strip()
        
        if not linea:
            return None
        
        # Buscar la línea que contiene "JSON: "
        if "JSON:" in linea:
            # Extraer el JSON
            json_str = linea.split("JSON:")[1].strip()
            datos = json.loads(json_str)
            return datos.get("id_usuario")
        
        return None
    except Exception as e:
        print(f"{Colores.AMARILLO}⚠ Error al leer: {e}{Colores.RESET}")
        return None

def enviar_al_backend(id_usuario):
    """Envía el ID usuario al backend"""
    try:
        payload = {"id_usuario": id_usuario}
        
        print(f"{Colores.AZUL}→ Enviando al backend: {payload}{Colores.RESET}")
        
        response = requests.post(BACKEND_URL, json=payload, timeout=5)
        
        if response.status_code == 200:
            resultado = response.json()
            
            if resultado.get("success"):
                espacio = resultado.get("espacio")
                print(f"{Colores.VERDE}✓ ÉXITO - Espacio asignado: {espacio}{Colores.RESET}")
                return True
            else:
                mensaje = resultado.get("mensaje", "Error desconocido")
                print(f"{Colores.ROJO}✗ Error: {mensaje}{Colores.RESET}")
                return False
        else:
            print(f"{Colores.ROJO}✗ Error HTTP {response.status_code}: {response.text}{Colores.RESET}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"{Colores.ROJO}✗ Error: No se puede conectar al backend en {BACKEND_URL}{Colores.RESET}")
        return False
    except Exception as e:
        print(f"{Colores.ROJO}✗ Error al enviar: {e}{Colores.RESET}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("  LECTOR RFID → BACKEND")
    print("=" * 60)
    print(f"Puerto Serial: {PUERTO_SERIAL}")
    print(f"Backend: {BACKEND_URL}")
    print("=" * 60)
    print()
    
    # Conectar a Arduino
    puerto = conectar_serial()
    if not puerto:
        print(f"{Colores.ROJO}No se pudo conectar. Abortando...{Colores.RESET}")
        return
    
    # Esperar a que Arduino esté listo
    time.sleep(2)
    
    try:
        print(f"{Colores.VERDE}Sistema listo. Esperando tarjetas...{Colores.RESET}\n")
        
        while True:
            # Leer tarjeta del Arduino
            id_usuario = leer_tarjeta(puerto)
            
            if id_usuario is not None:
                print(f"{Colores.AZUL}[{datetime.now().strftime('%H:%M:%S')}] Tarjeta detectada → ID: {id_usuario}{Colores.RESET}")
                
                # Enviar al backend
                enviar_al_backend(id_usuario)
                print()
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print(f"\n{Colores.AMARILLO}Programa interrumpido por el usuario{Colores.RESET}")
    except Exception as e:
        print(f"{Colores.ROJO}Error inesperado: {e}{Colores.RESET}")
    finally:
        if puerto:
            puerto.close()
            print(f"{Colores.VERDE}✓ Puerto serial cerrado{Colores.RESET}")

if __name__ == "__main__":
    main()
