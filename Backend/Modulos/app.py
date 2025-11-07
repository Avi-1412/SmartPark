# Backend/Modulos/app.py

from fastapi import FastAPI
from Backend.Modulos.asignador import (
    esta_conectado,
    asignar_espacio,
    leer_espacios,
    espacios_pendientes
)
from Backend.BaseDatos import bd
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API Estacionamiento")

# Permitir que el frontend Flet se comunique con este backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # o pon tu IP/local si quieres limitarlo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/estado")
def obtener_estado_espacios():
    sensores = leer_espacios()
    return {
        "sensores": sensores,
        "pendientes": list(espacios_pendientes)
    }

@app.post("/registrar")
def registrar_acceso():
    usuario_id = 1  # Simulado, luego puedes reemplazarlo con login real
    espacio = asignar_espacio()
    conectado = esta_conectado()
    hora_entrada = datetime.now()

    if espacio and conectado:
        entrada = bd.insert_historial(usuario_id, espacio, hora_entrada)
        return {"success": True, "data": entrada}
    elif not espacio and conectado:
        return {"success": False, "mensaje": "No hay espacios disponibles"}
    else:
        return {"success": False, "mensaje": "[ERROR] No hay conexión a Arduino"}

@app.get("/historial")
def obtener_historial():
    historial = bd.get_historial()
    return {"historial": historial}

@app.delete("/historial")
def borrar_historial():
    bd.purgar_historial()
    return {"mensaje": "Historial purgado correctamente"}
