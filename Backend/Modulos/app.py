from fastapi import Body
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

# =====================================================
# INICIALIZACIÓN DE LA BASE DE DATOS
# =====================================================

# Inicializar tablas (solo crea si no existen)
bd.inicializar_bd()

# Poblar con datos iniciales si la BD está vacía
cursor = bd.conectar().cursor()
cursor.execute("SELECT COUNT(*) FROM login")
count = cursor.fetchone()[0]
cursor.close()

if count == 0:
    print("📋 BD vacía - Insertando datos iniciales...")
    bd.seed_datos_iniciales()
    print("✅ Datos iniciales insertados")

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

# =====================================================
# ENDPOINTS DE USUARIOS
# =====================================================

@app.post("/login")
def login(credentials: dict = Body(...)):
    """Autenticar usuario con credenciales"""
    usuario = credentials.get("usuario", "").strip()
    contrasena = credentials.get("contrasena", "").strip()
    
    if not usuario or not contrasena:
        return {"autenticado": False, "mensaje": "Usuario y contraseña requeridos"}
    
    resultado = bd.validar_login(usuario, contrasena)
    return resultado

@app.post("/login/crear")
def crear_credenciales(datos: dict = Body(...)):
    """Crear credenciales de login para un usuario existente (Administrador)"""
    usuario_login = datos.get("usuario_login", "").strip()
    contrasena = datos.get("contrasena", "").strip()
    rol = datos.get("rol", "usuario").strip()
    id_usuario = datos.get("id_usuario")
    
    # Validar que todos los campos requeridos estén presentes
    if not usuario_login or not contrasena or not id_usuario:
        return {
            "error": "Se requieren: usuario_login, contrasena, id_usuario"
        }
    
    # Llamar función de bd para crear las credenciales
    resultado = bd.crear_login_para_usuario(usuario_login, contrasena, rol, id_usuario)
    return resultado

@app.post("/usuarios")
def crear_usuario(usuario: dict = Body(...)):
    """Registrar un nuevo usuario (Administrador)"""
    usuario["idUsuario"] = bd.generar_id(int(usuario["tipo_id"]))
    return bd.insert_usuario(usuario)

@app.get("/usuarios")
def obtener_todos_usuarios():
    """Obtener lista de todos los usuarios"""
    usuarios = bd.get_todos_usuarios()
    return {"usuarios": usuarios}

@app.get("/usuarios/{usuario_id}")
def obtener_usuario(usuario_id: str):
    """Obtener datos completos de un usuario"""
    return bd.get_usuario(usuario_id)

@app.put("/usuarios/{usuario_id}")
def actualizar_usuario(usuario_id: str, datos: dict = Body(...)):
    """Actualizar datos de un usuario (Administrador)"""
    return bd.update_usuario(usuario_id, datos)

@app.delete("/usuarios/{usuario_id}")
def eliminar_usuario(usuario_id: str):
    """Eliminar un usuario y todos sus datos asociados (Administrador)"""
    return bd.delete_usuario(usuario_id)

# Inicializar BD (solo una vez)
bd.inicializar_bd()
