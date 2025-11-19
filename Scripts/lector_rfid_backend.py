# Lee RFID de 1 Arduino (COM3 dual: ENTRADA/SALIDA) y envía al backend
import serial
import json
import requests
import time
from datetime import datetime

# CONFIGURACIÓN - 1 ARDUINO DUAL
PUERTO_ARDUINO = "COM3"
VELOCIDAD_BAUD = 9600
BACKEND_URL = "http://127.0.0.1:8000"

# Colores para terminal
class Colores:
    VERDE = '\033[92m'
    ROJO = '\033[91m'
    AMARILLO = '\033[93m'
    AZUL = '\033[94m'
    RESET = '\033[0m'

def conectar_serial(puerto_com, velocidad_baud):
    """Conecta al puerto serial del Arduino"""
    try:
        puerto = serial.Serial(puerto_com, velocidad_baud, timeout=1)
        print(f"{Colores.VERDE}✓ Conectado a Arduino en {puerto_com}{Colores.RESET}")
        return puerto
    except serial.SerialException as e:
        print(f"{Colores.ROJO}✗ Error al conectar a {puerto_com}: {e}{Colores.RESET}")
        return None

def leer_datos_arduino(puerto):
    """Lee datos del Arduino (RFID o sensores) y retorna JSON parseado"""
    try:
        linea = puerto.readline().decode('utf-8').strip()
        
        if not linea:
            return None
        
        # Arduino envía JSON directamente
        datos = json.loads(linea)
        return datos
        
    except json.JSONDecodeError:
        # Ignorar líneas que no sean JSON válido
        return None
    except Exception as e:
        print(f"{Colores.AMARILLO}⚠ Error al leer Arduino: {e}{Colores.RESET}")
        return None


def enviar_al_backend(id_usuario, tipo="ENTRADA"):
    """Envía el ID usuario al backend con el tipo de transacción"""
    try:
        # Determinar endpoint según tipo
        if tipo.upper() == "SALIDA":
            endpoint = f"{BACKEND_URL}/registrar/salida"
            color = Colores.AMARILLO
        else:
            endpoint = f"{BACKEND_URL}/registrar/entrada"
            color = Colores.VERDE
        
        payload = {"id_usuario": id_usuario}
        
        print(f"{color}→ [SENSOR: {tipo.upper()}]{Colores.RESET}")
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


def enviar_comando_servo(tipo_acceso):
    """Envía comando al Arduino para abrir servo"""
    try:
        # Este método se llamaría desde una respuesta del backend
        # Pero el Arduino recibe comandos vía Serial
        pass
    except Exception as e:
        print(f"{Colores.ROJO}✗ Error al enviar comando servo: {e}{Colores.RESET}")

def procesar_arduino(puerto):
    """Procesa continuamente datos del Arduino (RFID y sensores)"""
    print(f"{Colores.VERDE}Esperando datos del Arduino...{Colores.RESET}\n")
    
    try:
        while True:
            # Leer datos del Arduino
            datos = leer_datos_arduino(puerto)
            
            if datos is None:
                continue
            
            # Procesar según tipo de evento
            tipo_evento = datos.get("tipo")
            
            if tipo_evento == "ENTRADA":
                id_usuario = datos.get("id_usuario")
                print(f"{Colores.VERDE}[{datetime.now().strftime('%H:%M:%S')}] ENTRADA detectada → ID: {id_usuario}{Colores.RESET}")
                enviar_al_backend(id_usuario, "ENTRADA")
                print()
            
            elif tipo_evento == "SALIDA":
                id_usuario = datos.get("id_usuario")
                print(f"{Colores.AMARILLO}[{datetime.now().strftime('%H:%M:%S')}] SALIDA detectada → ID: {id_usuario}{Colores.RESET}")
                enviar_al_backend(id_usuario, "SALIDA")
                print()
            
            elif tipo_evento == "SENSOR":
                sensor = datos.get("sensor")
                ocupado = datos.get("ocupado")
                
                estado = "OCUPADO" if ocupado else "LIBRE"
                color = Colores.ROJO if ocupado else Colores.VERDE
                print(f"{color}[{datetime.now().strftime('%H:%M:%S')}] Sensor {sensor}: {estado}{Colores.RESET}")
                
                # Enviar estado del sensor al backend para que detecte ocupación ilegal
                try:
                    # Crear diccionario de sensores (por ahora solo enviamos el sensor actual)
                    sensores_dict = {sensor: (1 if ocupado else 0)}
                    
                    response = requests.post(
                        f"{BACKEND_URL}/sensores/actualizar",
                        json={"sensores": sensores_dict},
                        timeout=5
                    )
                    resultado = response.json()
                    
                    # Si hay ocupación ilegal detectada, mostrar alerta
                    if resultado.get("ocupacion_ilegal"):
                        espacios_ilegal = resultado.get("ocupacion_ilegal", [])
                        print(f"{Colores.ROJO}⚠️ OCUPACIÓN ILEGAL DETECTADA EN: {espacios_ilegal}{Colores.RESET}")
                        
                except Exception as ex:
                    print(f"{Colores.AMARILLO}⚠ Error enviando estado sensor: {ex}{Colores.RESET}")
            
            elif tipo_evento == "SERVO_ABIERTO_ENTRADA":
                print(f"{Colores.AZUL}[{datetime.now().strftime('%H:%M:%S')}] 🔓 SERVO ABIERTO (ENTRADA){Colores.RESET}")
            
            elif tipo_evento == "SERVO_ABIERTO_SALIDA":
                print(f"{Colores.AZUL}[{datetime.now().strftime('%H:%M:%S')}] 🔓 SERVO ABIERTO (SALIDA){Colores.RESET}")
            
            elif tipo_evento == "SERVO_CERRADO":
                print(f"{Colores.AZUL}[{datetime.now().strftime('%H:%M:%S')}] 🔒 SERVO CERRADO{Colores.RESET}")
            
            elif tipo_evento == "SISTEMA_INICIADO":
                print(f"{Colores.VERDE}[{datetime.now().strftime('%H:%M:%S')}] Arduino iniciado correctamente{Colores.RESET}")
    
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"{Colores.ROJO}Error: {e}{Colores.RESET}")
    finally:
        if puerto:
            puerto.close()
            print(f"{Colores.VERDE}Puerto serial cerrado{Colores.RESET}")

def main():
    """Función principal - Inicia lectura del Arduino único"""
    print("=" * 70)
    print("  LECTOR RFID - ARDUINO ÚNICO (DUAL RFID + SERVO)")
    print("=" * 70)
    print(f"  Puerto: {PUERTO_ARDUINO} ({VELOCIDAD_BAUD} baud)")
    print(f"  Backend: {BACKEND_URL}")
    print("=" * 70)
    print()
    
    # Conectar a Arduino
    puerto = conectar_serial(PUERTO_ARDUINO, VELOCIDAD_BAUD)
    if not puerto:
        print(f"{Colores.ROJO}No se pudo conectar al Arduino. Abortando...{Colores.RESET}")
        return
    
    # Esperar a que Arduino esté listo
    time.sleep(2)
    
    try:
        print(f"{Colores.VERDE}Sistema listo. Arduino activo...{Colores.RESET}\n")
        # Procesar datos continuamente
        procesar_arduino(puerto)
    except KeyboardInterrupt:
        print(f"\n{Colores.AMARILLO}Programa interrumpido por el usuario{Colores.RESET}")


if __name__ == "__main__":
    main()
