# FastAPI Backend - Estacionamiento (Entrada COM3, Salida COM4)

from fastapi import Body
from fastapi import FastAPI
from Backend.Modulos.asignador import (
    asignar_espacio,
    leer_espacios,
    espacios_pendientes,
    liberar_espacio
)
from Backend.BaseDatos import bd
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException

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

@app.post("/registrar/entrada")
def registrar_entrada(datos: dict = Body(...)):
    """Registra entrada por RFID - recibe id_usuario del Arduino"""
    id_usuario = datos.get("id_usuario")
    
    if not id_usuario:
        return {"success": False, "mensaje": "❌ Falta id_usuario"}
    
    # VALIDACIÓN: Verificar que el usuario existe
    usuario = bd.get_usuario(str(id_usuario))
    if not usuario or usuario.get("error"):
        return {
            "success": False, 
            "mensaje": f"❌ Usuario {id_usuario} no registrado en el sistema",
            "codigo_error": "USUARIO_NO_EXISTE"
        }
    
    # VALIDACIÓN: Verificar si el usuario ya tiene un acceso activo
    acceso_activo = bd.verificar_acceso_activo(str(id_usuario))
    if acceso_activo.get("tiene_acceso_activo"):
        return {
            "success": False,
            "mensaje": f"❌ Usuario {id_usuario} ya tiene un acceso activo",
            "espacio_activo": acceso_activo.get("espacio_asignado"),
            "fecha_entrada": str(acceso_activo.get("fecha_entrada")),
            "codigo_error": "ACCESO_ACTIVO_EXISTENTE"
        }
    
    # Asignar espacio
    espacio = asignar_espacio()
    hora_entrada = datetime.now()
    
    if espacio:
        # Registrar en historial
        entrada = bd.insert_historial(id_usuario, espacio, hora_entrada)
        print(f"✅ ENTRADA REGISTRADA: Usuario {id_usuario} ({usuario.get('nomUsuario')}) → Espacio {espacio}")
        return {
            "success": True, 
            "espacio": espacio,
            "id_usuario": id_usuario,
            "nombre_usuario": usuario.get("nomUsuario"),
            "mensaje": f"✅ Espacio {espacio} asignado"
        }
    else:
        print(f"❌ No hay espacios disponibles para usuario {id_usuario}")
        return {
            "success": False, 
            "mensaje": "❌ No hay espacios disponibles",
            "codigo_error": "SIN_ESPACIOS"
        }

@app.get("/historial")
def obtener_historial():
    historial = bd.get_historial()
    return {"historial": historial}

@app.get("/accesos-recientes")
def obtener_accesos_recientes(limite: int = 10):
    """Obtiene los últimos accesos registrados (para panel vigilante)"""
    accesos = bd.get_accesos_recientes(limite)
    return {"accesos": accesos}

@app.post("/registrar/salida")
def registrar_salida(datos: dict = Body(...)):
    """Registra salida de un usuario - cierra su acceso activo"""
    id_usuario = datos.get("id_usuario")
    
    if not id_usuario:
        return {"success": False, "mensaje": "❌ Falta id_usuario"}
    
    # Verificar que el usuario existe
    usuario = bd.get_usuario(str(id_usuario))
    if not usuario:
        return {"success": False, "mensaje": f"❌ Usuario {id_usuario} no encontrado"}
    
    # Verificar si tiene acceso activo
    acceso_activo = bd.verificar_acceso_activo(str(id_usuario))
    if not acceso_activo.get("tiene_acceso_activo"):
        return {"success": False, "mensaje": f"❌ Usuario {id_usuario} no tiene acceso activo"}
    
    # Cerrar el acceso
    resultado = bd.cerrar_acceso(str(id_usuario))
    
    if resultado.get("exito"):
        espacio_liberado = acceso_activo.get("espacio_asignado")
        # Liberar el espacio y restaurar el grafo
        liberar_espacio(espacio_liberado)
        print(f"✅ SALIDA REGISTRADA: Usuario {id_usuario}")
        return {
            "success": True,
            "mensaje": f"✅ Salida registrada para usuario {id_usuario}",
            "espacio_liberado": espacio_liberado
        }
    else:
        return {"success": False, "mensaje": resultado.get("mensaje", "Error desconocido")}

@app.get("/historial/usuario/{user_id}")
def obtener_historial_usuario(user_id: int):
    """Obtener historial completo de un usuario (automático + manual)"""
    try:
        historial = bd.get_historial_completo_usuario(user_id)
        return {"historial": historial}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/historial/validar/{id_usuario}/{id_historial}")
def validar_historial(id_usuario: int, id_historial: int):
    """Valida si un ID de historial existe y pertenece al usuario"""
    existe = bd.verificar_historial_usuario(id_usuario, id_historial)
    if existe:
        return {"valido": True, "mensaje": "✅ Entrada válida"}
    else:
        return {"valido": False, "mensaje": "❌ Entrada no encontrada para este usuario"}

@app.get("/historial/usuario/{user_id}/ids")
def obtener_ids_historial_usuario(user_id: int):
    """Obtiene lista de IDs de historial disponibles para un usuario (solo automáticos)"""
    conexion = bd.conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT idHis, espAsig, horaEntrada FROM historial WHERE idUsuario = ? ORDER BY idHis DESC", (user_id,))
    rows = cursor.fetchall()
    conexion.close()
    
    ids_historial = [{"id": row[0], "espacio": row[1], "fecha": str(row[2])[:10]} for row in rows]
    return {"ids": ids_historial, "total": len(ids_historial)}

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

# =====================================================
# ENDPOINTS ACCESOS MANUALES (tarjeta digital)
# =====================================================

@app.post("/acceso/manual/entrada")
def registrar_entrada_manual(datos: dict = Body(...)):
    """Registrar entrada manual (tarjeta digital) con límite mensual."""
    id_usuario = datos.get("id_usuario")
    if not id_usuario:
        raise HTTPException(status_code=400, detail="Falta id_usuario")
    # Validar límite mensual (3)
    usos = bd.contar_accesos_manuales_mes(id_usuario)
    if usos >= 3:
        return {"success": False, "mensaje": "Límite de 3 accesos manuales alcanzado este mes"}
    bd.registrar_acceso_manual(id_usuario, "entrada")
    return {"success": True, "mensaje": f"Entrada manual registrada. Usos este mes: {usos+1}/3"}

@app.post("/acceso/manual/salida")
def registrar_salida_manual(datos: dict = Body(...)):
    """Registrar salida manual (tarjeta digital). No tiene límite."""
    id_usuario = datos.get("id_usuario")
    if not id_usuario:
        raise HTTPException(status_code=400, detail="Falta id_usuario")
    bd.registrar_acceso_manual(id_usuario, "salida")
    return {"success": True, "mensaje": "Salida manual registrada"}

@app.get("/acceso/manuales/{id_usuario}")
def obtener_historial_accesos_manuales(id_usuario: int):
    """Obtener historial y conteo de accesos manuales del mes para un usuario."""
    historial = bd.obtener_historial_accesos_manuales(id_usuario)
    usos_mes = bd.contar_accesos_manuales_mes(id_usuario)
    return {"historial": historial, "usos_mes": usos_mes, "limite": 3}

@app.get("/acceso/manuales/{id_usuario}/activa")
def verificar_entrada_activa(id_usuario: int):
    """Verifica si hay una entrada manual sin salida correspondiente."""
    hay_activa = bd.hay_entrada_activa(id_usuario)
    return {"entrada_activa": hay_activa}

# =====================================================
# ENDPOINTS ADVERTENCIAS (vigilante)
# =====================================================

@app.post("/advertencias")
def registrar_advertencia(datos: dict = Body(...)):
    """Registra una advertencia para un usuario en una entrada específica."""
    id_usuario = datos.get("id_usuario")
    id_historial = datos.get("id_historial")
    motivo = datos.get("motivo", "Mal estacionado")
    
    if not id_usuario or not id_historial:
        return {"success": False, "mensaje": "Faltan datos (id_usuario, id_historial)"}
    
    try:
        # Verificar que el ID de historial existe y pertenece al usuario
        if not bd.verificar_historial_usuario(id_usuario, id_historial):
            return {"success": False, "mensaje": "❌ ID de entrada no válido para este usuario"}
        
        # Verificar si ya hay 3 advertencias en esta entrada
        count = bd.contar_advertencias_entrada(id_usuario, id_historial)
        if count >= 3:
            return {"success": False, "mensaje": "Límite de 3 advertencias alcanzado en esta entrada"}
        
        # Verificar bloqueo de 2 minutos
        ultima_adv = bd.obtener_ultima_advertencia_entrada(id_usuario, id_historial)
        if ultima_adv:
            tiempo_transcurrido = (datetime.now() - datetime.fromisoformat(ultima_adv)).total_seconds() / 60
            if tiempo_transcurrido < 2:
                return {"success": False, "mensaje": f"Debe esperar 2 minutos entre advertencias ({int(2 - tiempo_transcurrido)} min restantes)"}
        
        result = bd.enviar_advertencia(id_usuario, id_historial, motivo)
        new_count = bd.contar_advertencias_entrada(id_usuario, id_historial)
        return {"success": True, "mensaje": f"Advertencia registrada ({new_count}/3)", "advertencias_entrada": new_count}
    except Exception as e:
        return {"success": False, "mensaje": f"Error al registrar: {str(e)}"}

@app.get("/advertencias/{id_usuario}")
def obtener_advertencias(id_usuario: int):
    """Obtiene todas las advertencias de un usuario"""
    advertencias = bd.obtener_advertencias_usuario(id_usuario)
    total = bd.contar_advertencias_usuario(id_usuario)
    return {"advertencias": advertencias, "total": total}

@app.get("/advertencias/entrada/{id_usuario}/{id_historial}")
def obtener_advertencias_entrada(id_usuario: int, id_historial: int):
    """Obtiene advertencias de una entrada específica"""
    count = bd.contar_advertencias_entrada(id_usuario, id_historial)
    return {"id_usuario": id_usuario, "id_historial": id_historial, "advertencias": count}

# =====================================================
# ENDPOINTS MULTAS (vigilante/admin)
# =====================================================

@app.post("/multas")
def registrar_multa(datos: dict = Body(...)):
    """Registra una multa para un usuario (solo después de 3 advertencias)"""
    id_usuario = datos.get("id_usuario")
    id_historial = datos.get("id_historial")
    concepto = datos.get("concepto", "Mal estacionado")
    monto = datos.get("monto", 50.0)  # Monto por defecto
    
    if not id_usuario or not id_historial:
        return {"success": False, "mensaje": "Faltan datos (id_usuario, id_historial)"}
    
    try:
        # Verificar que el ID de historial existe y pertenece al usuario
        if not bd.verificar_historial_usuario(id_usuario, id_historial):
            return {"success": False, "mensaje": "❌ ID de entrada no válido para este usuario"}
        
        # Verificar que hay 3 advertencias en esta entrada
        adv_count = bd.contar_advertencias_entrada(id_usuario, id_historial)
        if adv_count < 3:
            return {"success": False, "mensaje": f"Debe tener 3 advertencias para multa (actual: {adv_count})"}
        
        result = bd.enviar_multa(id_usuario, id_historial, concepto, monto)
        return {"success": True, "mensaje": f"Multa de ${monto} registrada"}
    except Exception as e:
        return {"success": False, "mensaje": f"Error al registrar multa: {str(e)}"}

@app.get("/multas/{id_usuario}")
def obtener_multas(id_usuario: int):
    """Obtiene todas las multas de un usuario"""
    multas = bd.obtener_multas_usuario(id_usuario)
    return {"multas": multas}

@app.get("/multas")
def obtener_todas_multas():
    """Obtiene todas las multas del sistema (para admin/reportes)"""
    multas = bd.obtener_todas_multas()
    return {"multas": multas}

@app.put("/multas/{id_multa}/pagada")
def marcar_multa_pagada(id_multa: int, estado: dict = Body(...)):
    """Marca una multa como pagada o no pagada (admin)"""
    pagada = estado.get("pagada", False)
    try:
        result = bd.marcar_multa_pagada(id_multa, pagada)
        return {"success": True, "mensaje": "Estado actualizado"}
    except Exception as e:
        return {"success": False, "mensaje": f"Error: {str(e)}"}

# =====================================================
# ENDPOINTS SENSORES (Arduino)
# =====================================================

@app.post("/sensores/actualizar")
def actualizar_sensores(datos: dict = Body(...)):
    """Recibe estado de sensores del Arduino y detecta ocupación ilegal"""
    datos_sensores = datos.get("sensores")  # {'A': 1, 'B': 0, 'C': 1, 'D': 0}
    
    if not datos_sensores:
        return {"success": False, "mensaje": "❌ Falta dato 'sensores'"}
    
    try:
        # Actualizar estado en BD
        bd.actualizar_estado_sensores(datos_sensores)
        
        # Detectar ocupación ilegal
        ocupacion_ilegal = bd.detectar_ocupacion_ilegal()
        
        # Crear alertas para espacios ilegales
        for espacio in ocupacion_ilegal:
            bd.crear_alerta_sensor(espacio, 0, None)  # 0 = ocupado
        
        print(f"✅ SENSORES ACTUALIZADOS: {datos_sensores}")
        if ocupacion_ilegal:
            print(f"⚠️  OCUPACIÓN ILEGAL DETECTADA: {ocupacion_ilegal}")
        
        return {
            "success": True,
            "sensores_recibidos": datos_sensores,
            "ocupacion_ilegal": ocupacion_ilegal,
            "mensaje": f"✅ Sensores actualizados. Alertas: {len(ocupacion_ilegal)}"
        }
    except Exception as e:
        return {"success": False, "mensaje": f"❌ Error: {str(e)}"}

@app.get("/sensores/estado")
def obtener_estado_sensores():
    """Obtiene el estado actual de todos los espacios"""
    estado = bd.obtener_estado_espacios()
    return {
        "estado": estado,
        "espacios": list(estado.keys())
    }

@app.get("/sensores/alertas")
def obtener_alertas_pendientes():
    """Obtiene todas las alertas de sensores sin resolver (para vigilante)"""
    alertas = bd.obtener_alertas_sensor_pendientes()
    return {
        "alertas": alertas,
        "total_pendientes": len(alertas)
    }

@app.post("/sensores/alertas/{alerta_id}/resolver")
def resolver_alerta(alerta_id: int):
    """Marca una alerta como resuelta"""
    try:
        bd.resolver_alerta_sensor(alerta_id)
        return {"success": True, "mensaje": f"✅ Alerta {alerta_id} resuelta"}
    except Exception as e:
        return {"success": False, "mensaje": f"❌ Error: {str(e)}"}

