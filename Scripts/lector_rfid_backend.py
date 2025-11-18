# Lee RFID de 2 Arduinos (COM3 entrada, COM4 salida) y envía al backend
import serial
import json
import requests
import time
from datetime import datetime
import threading

# CONFIGURACIÓN - 2 ARDUINOS
SENSORES = {
    "ENTRADA": {"puerto": "COM3", "velocidad": 9600},
    "SALIDA": {"puerto": "COM4", "velocidad": 9600}
}
BACKEND_URL = "http://127.0.0.1:8000"

# Colores para terminal
class Colores:
    VERDE = '\033[92m'
    ROJO = '\033[91m'
    AMARILLO = '\033[93m'
    AZUL = '\033[94m'
    RESET = '\033[0m'

def conectar_serial(tipo_sensor, puerto_com, velocidad_baud):
    """Conecta al puerto serial del Arduino"""
    try:
        puerto = serial.Serial(puerto_com, velocidad_baud, timeout=1)
        print(f"{Colores.VERDE}✓ Conectado a Arduino [{tipo_sensor}] en {puerto_com}{Colores.RESET}")
        return puerto
    except serial.SerialException as e:
        print(f"{Colores.ROJO}✗ Error al conectar a {puerto_com} [{tipo_sensor}]: {e}{Colores.RESET}")
        return None

def leer_tarjeta(puerto, tipo_sensor):
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
            return {
                "id_usuario": datos.get("id_usuario"),
                "tipo": tipo_sensor  # ENTRADA o SALIDA según el sensor
            }
        
        return None
    except Exception as e:
        print(f"{Colores.AMARILLO}⚠ Error al leer [{tipo_sensor}]: {e}{Colores.RESET}")
        return None


def enviar_al_backend(id_usuario, tipo="ENTRADA"):
    """Envía el ID usuario al backend con el tipo de transacción"""
    try:
        # Determinar endpoint según tipo
        if tipo.upper() == "SALIDA":
            endpoint = f"{BACKEND_URL}/registrar/salida"
        else:
            endpoint = f"{BACKEND_URL}/registrar/entrada"
        
        payload = {"id_usuario": id_usuario}
        
        tipo_color = Colores.VERDE if tipo.upper() == "ENTRADA" else Colores.AMARILLO
        print(f"{tipo_color}→ [SENSOR: {tipo.upper()}]{Colores.RESET}")
        print(f"{Colores.AZUL}→ Enviando al backend: {payload}{Colores.RESET}")
        
        response = requests.post(endpoint, json=payload, timeout=5)
        
        if response.status_code == 200:
            resultado = response.json()
            
            if resultado.get("success"):
                if tipo.upper() == "ENTRADA":
                    espacio = resultado.get("espacio")
                    print(f"{Colores.VERDE}✓ ENTRADA EXITOSA - Espacio asignado: {espacio}{Colores.RESET}")
                else:
                    espacio = resultado.get("espacio_liberado")
                    print(f"{Colores.VERDE}✓ SALIDA EXITOSA - Espacio liberado: {espacio}{Colores.RESET}")
                return True
            else:
                mensaje = resultado.get("mensaje", "Error desconocido")
                print(f"{Colores.ROJO}✗ Error: {mensaje}{Colores.RESET}")
                return False
        else:
            print(f"{Colores.ROJO}✗ Error HTTP {response.status_code}: {response.text}{Colores.RESET}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"{Colores.ROJO}✗ Error: No se puede conectar al backend{Colores.RESET}")
        return False
    except Exception as e:
        print(f"{Colores.ROJO}✗ Error al enviar: {e}{Colores.RESET}")
        return False

def procesar_sensor(tipo_sensor, config_sensor):
    """Procesa continuamente un sensor RFID en un hilo separado"""
    puerto_com = config_sensor["puerto"]
    velocidad_baud = config_sensor["velocidad"]
    
    print(f"{Colores.AZUL}[{tipo_sensor}] Iniciando thread...{Colores.RESET}")
    
    # Conectar a Arduino
    puerto = conectar_serial(tipo_sensor, puerto_com, velocidad_baud)
    if not puerto:
        print(f"{Colores.ROJO}[{tipo_sensor}] No se pudo conectar. Abortando...{Colores.RESET}")
        return
    
    # Esperar a que Arduino esté listo
    time.sleep(2)
    
    try:
        print(f"{Colores.VERDE}[{tipo_sensor}] Esperando tarjetas...{Colores.RESET}\n")
        
        while True:
            # Leer tarjeta del Arduino
            datos_tarjeta = leer_tarjeta(puerto, tipo_sensor)
            
            if datos_tarjeta is not None:
                id_usuario = datos_tarjeta.get("id_usuario")
                tipo = datos_tarjeta.get("tipo", tipo_sensor)
                print(f"{Colores.AZUL}[{datetime.now().strftime('%H:%M:%S')}] [{tipo_sensor}] Tarjeta detectada → ID: {id_usuario}{Colores.RESET}")
                
                # Enviar al backend
                enviar_al_backend(id_usuario, tipo)
                print()
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"{Colores.ROJO}[{tipo_sensor}] Error: {e}{Colores.RESET}")
    finally:
        if puerto:
            puerto.close()
            print(f"{Colores.VERDE}[{tipo_sensor}] Puerto serial cerrado{Colores.RESET}")

def main():
    """Función principal - Inicia 2 threads para 2 sensores"""
    print("=" * 70)
    print("  LECTOR RFID - DUAL (2 SENSORES)")
    print("=" * 70)
    for nombre, config in SENSORES.items():
        print(f"  {nombre:8} → {config['puerto']} ({config['velocidad']} baud)")
    print(f"  Backend: {BACKEND_URL}")
    print("=" * 70)
    print()
    
    # Crear threads para cada sensor
    threads = []
    for tipo_sensor, config_sensor in SENSORES.items():
        thread = threading.Thread(
            target=procesar_sensor,
            args=(tipo_sensor, config_sensor),
            daemon=True
        )
        threads.append(thread)
        thread.start()
    
    try:
        print(f"{Colores.VERDE}Sistema listo. Ambos sensores activos...{Colores.RESET}\n")
        # Mantener el programa corriendo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Colores.AMARILLO}Programa interrumpido por el usuario{Colores.RESET}")


if __name__ == "__main__":
    main()
