# asignador.py

import heapq
import time
import serial
import threading

etiquetas = ['A', 'B', 'C', 'D']
grafo = {
    'Entrada': {'A': 1},
    'A': {'C': 3},
    'B': {'A': 3},
    'C': {}
}
copia_grafo = grafo.copy()
espacios_pendientes = set()

MESSAGE = "No hay conexion a Arduino"
INFO = "[INFO]"
ERROR = "[ERROR]"

#NOTA: Esta parte de código se debe adaptar para conexion wireless "POR VER"
# Inicializa Arduino solo una vez
try:
    arduino = serial.Serial('COM3', 9600)
    time.sleep(2)
    arduino.reset_input_buffer()
#Depuracion de conexion serial
except serial.SerialException as e:
    print(f"{ERROR} No se pudo abrir el puerto COM10: {e}")
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
    if not esta_conectado:
        print(MESSAGE)
        return {}
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
    global copia_grafo
    if not esta_conectado():
        print(f"{ERROR} No se puede asignar espacio: {MESSAGE}")
        return None
    sensores = leer_espacios()
    if not sensores:
        print(f"{ERROR} No se pudieron leer sensores {MESSAGE}")
        return None
    distancias = dijkstra(copia_grafo, 'Entrada')
    espacio_objetivo = encontrar_espacio_libre(distancias, sensores)

    if espacio_objetivo:
        try:
            arduino.write(espacio_objetivo.encode())
            espacios_pendientes.add(espacio_objetivo)
            print(f"Espacio pendiente: {espacios_pendientes}")
            print(f"Asignado: {espacio_objetivo}")
            #global copia_grafo
            copia_grafo = simular_ocupacion(copia_grafo,espacio_objetivo)
            verificar_ocupacion_real_diferida(espacio_objetivo)
            return espacio_objetivo
        except Exception as e:
            print(f"{ERROR} Fallo al enviar datos al Arduino: {e}")
            return None
    else:
        print("{INFO} No hay espacios disponibles")
    return None
