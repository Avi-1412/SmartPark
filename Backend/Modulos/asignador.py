# asignador.py
# Protocolo de comunicación: Solicitud-Respuesta (request-response)
# - Python envía comando 'S' al Arduino
# - Arduino responde solo con el estado de sensores: "1,1,0,1"
# - Arduino NO envía datos continuamente, solo cuando se solicita
# 
# Esto permite que asignador controle cuándo necesita los datos
# en lugar de Arduino enviando datos constantemente

import heapq
import time
import serial
import threading
import copy

etiquetas = ['A', 'B', 'C', 'D']
grafo_original = {
    'Entrada': {'A': 1},
    'A': {'C': 3},
    'B': {'A': 3},
    'C': {}
}
# Usar copia profunda para no modificar el original
grafo = copy.deepcopy(grafo_original)
copia_grafo = copy.deepcopy(grafo_original)
espacios_pendientes = set()

MESSAGE = "No hay conexion a Arduino"
INFO = "[INFO]"
ERROR = "[ERROR]"

#NOTA: Esta parte de código se debe adaptar para conexion wireless "POR VER"
# Inicializa Arduino solo una vez
# COMENTADO: El script Python (lector_rfid_backend.py) maneja la comunicación serial
# try:
#     arduino = serial.Serial('COM3', 9600)
#     time.sleep(2)
#     arduino.reset_input_buffer()
# #Depuracion de conexion serial
# except serial.SerialException as e:
#     print(f"{ERROR} No se pudo abrir el puerto COM3: {e}")
#     arduino = None

# Usar None directamente para evitar conflicto con script Python
arduino = None

#Funcion anticrash
def esta_conectado():
    return arduino is not None and arduino.is_open    
#-------------------------------------------------------------------

#Por medio de arduino, lee los sensores activos y no activos
def simular_ocupacion(grafo_original, espacio_ocupado):
    grafo_simulado = {nodo: dict(vecinos) for nodo, vecinos in grafo_original.items()}
    for nodo in grafo_simulado:
        if espacio_ocupado in grafo_simulado[nodo]:
            del grafo_simulado[nodo][espacio_ocupado]
    return grafo_simulado

def verificar_ocupacion_real_diferida(espacio_objetivo, espera=10):
    def tarea():
        time.sleep(espera)
        sensores = leer_espacios()
        if sensores.get(espacio_objetivo) == 0:
            print(f"{INFO} Confirmado: espacio {espacio_objetivo} fue ocupado")
            global grafo
            grafo = simular_ocupacion(grafo, espacio_objetivo)
        else:
            print(f"{INFO} Revertido: espacio {espacio_objetivo} no fue ocupado")
            espacios_pendientes.discard(espacio_objetivo)
            global copia_grafo
            copia_grafo = grafo.copy()
    threading.Thread(target=tarea).start()

def leer_espacios(reintentos=10):
    if not esta_conectado():
        print(f"{INFO} Arduino no conectado - Usando sensores simulados")
        # Retornar sensores simulados (todos libres: 1 = libre, 0 = ocupado)
        return {'A': 1, 'B': 1, 'C': 1, 'D': 1}
    
    # Solicitar estado de sensores enviando comando 'S'
    ultima_valida = None
    for intento in range(reintentos):
        try:
            # Enviar comando 'S' para solicitar sensores
            arduino.write(b'S')
            print(f"[DEBUG] Solicitud {intento + 1}: Enviando 'S' a Arduino...")
            
            # Leer respuesta (esperar respuesta con timeout)
            linea = arduino.readline().decode().strip()
            print(f"[DEBUG] Respuesta recibida: '{linea}'")
            
            if not linea:
                print(f"[DEBUG] Línea vacía, reintentando...")
                time.sleep(0.1)
                continue
            
            # Parsear valores: esperamos "1,1,0,1" etc
            valores = linea.split(',')
            if len(valores) != len(etiquetas):
                print(f"[DEBUG] Longitud incorrecta: {len(valores)} vs {len(etiquetas)}")
                time.sleep(0.1)
                continue
            
            # Convertir a diccionario
            temporal = {etiquetas[i]: int(valores[i]) for i in range(len(etiquetas))}
            print(f"[DEBUG] Sensores parseados correctamente: {temporal}")
            ultima_valida = temporal
            break
            
        except ValueError as ve:
            print(f"{ERROR} Error al parsear valores: {ve}")
            time.sleep(0.1)
            continue
        except Exception as e:
            print(f"{ERROR} {MESSAGE}: {e}")
            break
    
    if ultima_valida:
        return ultima_valida
    else:
        print(f"{ERROR} No se pudieron leer sensores después de {reintentos} intentos")
        return {}

#Algoritmo para asignar el espacio mas corto del grafo
def dijkstra(grafo, inicio):
    distancias = {nodo: float('inf') for nodo in grafo}
    distancias[inicio] = 0
    cola = [(0, inicio)]
    visitados = set()
    while cola:
        distancia_actual, nodo_actual = heapq.heappop(cola)
        if nodo_actual in visitados:
            continue
        visitados.add(nodo_actual)
        for vecino, peso in grafo[nodo_actual].items():
            nueva_distancia = distancia_actual + peso
            if nueva_distancia < distancias[vecino]:
                distancias[vecino] = nueva_distancia
                heapq.heappush(cola, (nueva_distancia, vecino))
    return distancias

#Busca que el espacio este libre en los sensores y en la lista temporal
def encontrar_espacio_libre(distancias, sensores):
    # Filtrar solo espacios que están REALMENTE libres (sensor = 1) 
    # Y que NO están en la lista de espacios pendientes
    libres = [
        espacio for espacio, estado in sensores.items() 
        if estado == 1 and espacio not in espacios_pendientes
    ]
    
    if not libres:
        print(f"{INFO} No hay espacios realmente libres (todos asignados o ocupados)")
        return None
    
    # Seleccionar el más cercano según Dijkstra
    espacio_seleccionado = min(libres, key=lambda x: distancias.get(x, float('inf')))
    print(f"{INFO} Espacios libres disponibles: {libres}")
    print(f"{INFO} Espacio seleccionado (más cercano): {espacio_seleccionado}")
    return espacio_seleccionado

#Toma un tiempo para leer que el espacio este ocupado
def esperar_ocupacion(espacio_objetivo):
    while True:
        sensores = leer_espacios()
        if sensores.get(espacio_objetivo) == 0:
            return True
        time.sleep(1)

#Toma un tiempo para leer que el espacio este desocupado
def esperar_desocupacion(espacio_objetivo):
    sensores = leer_espacios()
    if sensores.get(espacio_objetivo) == 1:
        return
    while True:
        sensores = leer_espacios()
        if sensores.get(espacio_objetivo) == 1:
            return
        time.sleep(0.2)

#Función para limpiar un espacio cuando se libera
def liberar_espacio(espacio_a_liberar):
    global copia_grafo, espacios_pendientes
    
    if espacio_a_liberar in espacios_pendientes:
        espacios_pendientes.discard(espacio_a_liberar)
        print(f"{INFO} Espacio {espacio_a_liberar} removido de pendientes")
    
    # Reconstruir el grafo: remover SOLO los espacios que están asignados actualmente
    # (los que están en espacios_pendientes)
    copia_grafo = copy.deepcopy(grafo_original)
    
    # Remover del grafo solo los espacios actualmente asignados
    for espacio_asignado in espacios_pendientes:
        copia_grafo = simular_ocupacion(copia_grafo, espacio_asignado)
    
    print(f"{INFO} Grafo reconstruido - removidos espacios asignados: {espacios_pendientes}")
    print(f"{INFO} Espacios disponibles para asignar: {[nodo for nodo in grafo_original if nodo not in ['Entrada'] and nodo not in espacios_pendientes]}")
    return True

#Funcion principal que realiza todo el proceso
def asignar_espacio():
    global copia_grafo, grafo
    
    # Leer sensores (retorna simulados si no hay Arduino)
    sensores = leer_espacios()
    if not sensores:
        print(f"{INFO} No hay sensores disponibles")
        return None
    
    print(f"{INFO} Estado actual de sensores: {sensores}")
    print(f"{INFO} Espacios pendientes (asignados pero no ocupados): {espacios_pendientes}")
    
    # Validar que no hay asignaciones duplicadas
    for espacio_pendiente in espacios_pendientes:
        if sensores.get(espacio_pendiente) == 0:
            print(f"{INFO} Espacio {espacio_pendiente} está ocupado (confirmado)")
        else:
            print(f"⚠️ ALERTA: Espacio {espacio_pendiente} aún pendiente (sin ocupar)")
    
    # Calcular distancias usando Dijkstra
    distancias = dijkstra(copia_grafo, 'Entrada')
    print(f"{INFO} Distancias desde Entrada: {distancias}")
    
    espacio_objetivo = encontrar_espacio_libre(distancias, sensores)
    
    if not espacio_objetivo:
        print(f"{INFO} No hay espacios libres disponibles")
        # Resetear grafo si no hay espacios
        copia_grafo = copy.deepcopy(grafo_original)
        print(f"{INFO} Grafo reseteado")
        return None

    try:
        print(f"✅ ASIGNANDO ESPACIO: {espacio_objetivo}")
        
        # Marcar espacio como pendiente
        espacios_pendientes.add(espacio_objetivo)
        print(f"{INFO} Espacio {espacio_objetivo} marcado como pendiente")
        
        # Actualizar el grafo para que NO se asigne de nuevo
        copia_grafo = simular_ocupacion(copia_grafo, espacio_objetivo)
        print(f"{INFO} Grafo actualizado (espacio {espacio_objetivo} removido de opciones)")
        
        # Verificar ocupación real con delay (20 seg)
        verificar_ocupacion_real_diferida(espacio_objetivo, espera=20)
        
        return espacio_objetivo
        
    except Exception as e:
        print(f"{ERROR} Fallo al asignar: {e}")
        import traceback
        traceback.print_exc()
        espacios_pendientes.discard(espacio_objetivo)
        return None
