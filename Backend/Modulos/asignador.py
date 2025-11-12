# asignador.py

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
    
    #espacios = {}
    ultima_valida = None
    for _ in range(reintentos):
        try:
            arduino.write(b'R')  # Solicita lectura
            linea = arduino.readline().decode().strip()
            print(f"[DEBUG] Línea recibida: {linea}")
            if not linea or "Asignado" in linea: #Lee que arduino este haciendo e/s
                continue
            valores = linea.split(',')
            if len(valores) != len(etiquetas):
                continue
            temporal = {etiquetas[i]: int(valores[i]) for i in range(len(etiquetas))}
            ultima_valida = temporal
        except Exception as e:
            print(f"{ERROR}, {MESSAGE}: {e}")
            break
    return ultima_valida if ultima_valida else {}

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
    libres = [espacio for espacio, estado in sensores.items() if estado == 1
              and espacio not in espacios_pendientes]
    if not libres:
        return None
    return min(libres, key=lambda x: distancias.get(x, float('inf')))

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

#Funcion principal que realiza todo el proceso
def asignar_espacio():
    global copia_grafo, grafo
    
    # Leer sensores (retorna simulados si no hay Arduino)
    sensores = leer_espacios()
    if not sensores:
        print(f"{INFO} No hay sensores disponibles")
        return None
    
    print(f"{INFO} Sensores: {sensores}")
    print(f"{INFO} Espacios pendientes: {espacios_pendientes}")
    
    # Calcular distancias usando Dijkstra
    distancias = dijkstra(copia_grafo, 'Entrada')
    print(f"{INFO} Distancias: {distancias}")
    
    espacio_objetivo = encontrar_espacio_libre(distancias, sensores)
    print(f"{INFO} Espacio seleccionado: {espacio_objetivo}")

    if espacio_objetivo:
        try:
            # Si Arduino está conectado, enviar comando
            if esta_conectado():
                arduino.write(espacio_objetivo.encode())
                espacios_pendientes.add(espacio_objetivo)
                print(f"{INFO} Espacio pendiente: {espacios_pendientes}")
            
            print(f"✅ Asignado: {espacio_objetivo}")
            
            # Actualizar el grafo para la siguiente asignación
            copia_grafo = simular_ocupacion(copia_grafo, espacio_objetivo)
            print(f"{INFO} Grafo actualizado")
            
            if esta_conectado():
                verificar_ocupacion_real_diferida(espacio_objetivo)
            
            return espacio_objetivo
        except Exception as e:
            print(f"{ERROR} Fallo: {e}")
            import traceback
            traceback.print_exc()
            return None
    else:
        print(f"{INFO} No hay espacios libres")
        # Resetear grafo si no hay espacios
        copia_grafo = copy.deepcopy(grafo_original)
        print(f"{INFO} Grafo reseteado")
    
    return None
