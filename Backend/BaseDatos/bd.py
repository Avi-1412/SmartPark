import sqlite3 as sql
import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR,"crud.db")

def conectar():
    conexion = sql.connect(DB_PATH)
    return conexion

def insert_historial(id_usuario,esp_asig,fecha_his):
    try:
        conexion = conectar()
    except sql.DatabaseError as e:
        print(f"Error en la base de datos {e}")
    cursor = conexion.cursor()
    sql = "INSERT INTO historial (idUsuario,espAsig,fechaHis) VALUES (?,?,?)"
    datos = (id_usuario,esp_asig,fecha_his)
    cursor.execute(sql,datos)
    conexion.commit()
    cursor.execute("SELECT idUsuario,espAsig,fechaHis,valido FROM historial ORDER BY idHis DESC LIMIT 1")
    resultado = cursor.fetchone()

    if resultado is None:
        cursor.close()
        conexion.close()
        return{
            "usuario_id" : id_usuario,
            "espacio_asignado": esp_asig,
            "hora_entrada": fecha_his.strftime("%H:%M:%S"),
        }
    return {
        "usuario_id" : resultado[0],
        "espacio_asignado" : resultado[1],
        "hora_entrada" : resultado[2],
    }

def cambiar_valido_historial(espacio):
    conexion = conectar()
    cursor = conexion.cursor()
    sql = "UPDATE historial SET valido = 0 WHERE idHis = (SELECT idHis FROM historial WHERE espAsig = ? AND valido = 1 ORDER BY idHis DESC LIMIT 1)"
    cursor.execute(sql,espacio)
    conexion.commit()
    conexion.close()

def get_historial():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT idHis, idUsuario, espAsig, fechaHis, valido from historial ORDER BY idHis DESC LIMIT 10")
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()

    historial = []
    for fila in resultados:
        historial.append({
            "historial_id" : fila[0],
            "usuario_id" : fila[1],
            "espacio_asignado": fila[2],
            "hora_entrada" : fila[3],
            "valido": fila[4]
        })
    return historial

def purgar_historial():
    fecha_limite = (datetime.now() - timedelta(days=2)).date()
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM historial WHERE fechaHis < ?", (fecha_limite,))
    conexion.commit()
    conexion.close()

def get_historial_por_usuario(user_id):
    """Obtener historial de un usuario específico"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT idHis, idUsuario, espAsig, fechaHis, valido, horaEntrada, horaSalida FROM historial WHERE idUsuario = ? ORDER BY idHis DESC", (user_id,))
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()

    historial = []
    for fila in resultados:
        historial.append({
            "historial_id": fila[0],
            "usuario_id": fila[1],
            "espacio_asignado": fila[2],
            "fecha_entrada": fila[3],
            "valido": fila[4],
            "hora_entrada": fila[5],
            "hora_salida": fila[6],
            "tipo": "automatico"
        })
    return historial

def get_historial_completo_usuario(user_id):
    """Obtener historial completo de un usuario (automático + manual)"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Obtener historial automático
    cursor.execute("SELECT idHis, idUsuario, espAsig, fechaHis, valido, horaEntrada, horaSalida FROM historial WHERE idUsuario = ? ORDER BY idHis DESC", (user_id,))
    resultados_auto = cursor.fetchall()
    
    # Obtener accesos manuales
    cursor.execute("SELECT id, id_usuario, fecha, tipo FROM accesos_manuales WHERE id_usuario = ? ORDER BY id DESC", (user_id,))
    resultados_manuales = cursor.fetchall()
    
    cursor.close()
    conexion.close()

    historial = []
    
    # Procesar historial automático
    for fila in resultados_auto:
        historial.append({
            "historial_id": fila[0],
            "usuario_id": fila[1],
            "espacio_asignado": fila[2],
            "fecha_entrada": fila[3],
            "valido": fila[4],
            "hora_entrada": fila[5],
            "hora_salida": fila[6],
            "tipo": "automático",
            "ordenar_por": fila[5]  # horaEntrada para ordenar
        })
    
    # Procesar accesos manuales
    for fila in resultados_manuales:
        historial.append({
            "historial_id": fila[0],
            "usuario_id": fila[1],
            "espacio_asignado": f"Manual ({fila[3].upper()})",
            "fecha_entrada": fila[2],
            "valido": 1,  # Los accesos manuales siempre son válidos
            "hora_entrada": fila[2],
            "hora_salida": None,
            "tipo": "manual",
            "ordenar_por": fila[2]  # fecha para ordenar
        })
    
    # Ordenar por fecha descendente (más recientes primero)
    historial.sort(key=lambda x: x.get("ordenar_por", ""), reverse=True)
    
    # Remover la clave de ordenamiento
    for item in historial:
        del item["ordenar_por"]
    
    return historial

# =====================================================
# FUNCIONES PARA REGISTRO DE USUARIOS
# =====================================================

def inicializar_bd():
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Tabla de usuarios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        idUsuario INTEGER PRIMARY KEY,
        nomUsuario TEXT,
        matrUsuario INTEGER,
        celular TEXT,
        placa1 TEXT,
        placa2 TEXT
    )
    """)
    
    # Tabla de login/credenciales
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS login (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE NOT NULL,
        contrasena TEXT NOT NULL,
        rol TEXT NOT NULL,
        id_usuario INTEGER,
        FOREIGN KEY (id_usuario) REFERENCES usuarios(idUsuario) ON DELETE CASCADE
    )
    """)
    
    # Tabla de autos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS autos (
        placa TEXT PRIMARY KEY,
        usuario_id TEXT,
        tipo_vehiculo INTEGER,
        color TEXT,
        marca TEXT,
        modelo TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(idUsuario) ON DELETE CASCADE
    )
    """)
    
    # Tabla de historial
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historial (
        idHis INTEGER PRIMARY KEY AUTOINCREMENT,
        idUsuario INTEGER,
        espAsig TEXT,
        fechaHis DATETIME,
        valido INTEGER DEFAULT 1,
        horaEntrada DATETIME,
        horaSalida DATETIME,
        FOREIGN KEY (idUsuario) REFERENCES usuarios(idUsuario) ON DELETE CASCADE
    )
    """)
    
    # Tabla de accesos manuales
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accesos_manuales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER,
        fecha DATETIME,
        tipo TEXT,
        FOREIGN KEY (id_usuario) REFERENCES usuarios(idUsuario) ON DELETE CASCADE
    )
    """)
    # Tabla de advertencias (vinculadas a entrada en historial)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS advertencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER,
        id_historial INTEGER,
        fecha DATETIME,
        motivo TEXT,
        FOREIGN KEY (id_usuario) REFERENCES usuarios(idUsuario) ON DELETE CASCADE,
        FOREIGN KEY (id_historial) REFERENCES historial(idHis) ON DELETE CASCADE
    )
    """)
    # Tabla de multas (vinculadas a entrada y concepto)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS multas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER,
        id_historial INTEGER,
        fecha DATETIME,
        concepto TEXT,
        monto REAL,
        pagado INTEGER DEFAULT 0,
        FOREIGN KEY (id_usuario) REFERENCES usuarios(idUsuario) ON DELETE CASCADE,
        FOREIGN KEY (id_historial) REFERENCES historial(idHis) ON DELETE CASCADE
    )
    """)
    
    conexion.commit()
    conexion.close()

# ===============================
# ACCESOS MANUALES (tarjeta digital)
# ===============================
def registrar_acceso_manual(id_usuario, tipo):
    """Registra un acceso manual (entrada o salida) para un usuario."""
    conexion = conectar()
    cursor = conexion.cursor()
    fecha = datetime.now()
    cursor.execute("""
        INSERT INTO accesos_manuales (id_usuario, fecha, tipo)
        VALUES (?, ?, ?)
    """, (id_usuario, fecha, tipo))
    conexion.commit()
    conexion.close()
    return {"mensaje": f"Acceso manual '{tipo}' registrado para usuario {id_usuario}"}

def contar_accesos_manuales_mes(id_usuario):
    """Cuenta los accesos manuales de ENTRADA de un usuario en el mes actual."""
    conexion = conectar()
    cursor = conexion.cursor()
    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    cursor.execute("""
        SELECT COUNT(*) FROM accesos_manuales
        WHERE id_usuario = ? AND tipo = 'entrada' AND fecha >= ?
    """, (id_usuario, inicio_mes))
    count = cursor.fetchone()[0]
    conexion.close()
    return count

def obtener_historial_accesos_manuales(id_usuario):
    """Devuelve el historial de accesos manuales de un usuario."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT fecha, tipo FROM accesos_manuales
        WHERE id_usuario = ?
        ORDER BY fecha DESC
    """, (id_usuario,))
    rows = cursor.fetchall()
    conexion.close()
    return [{"fecha": r[0], "tipo": r[1]} for r in rows]

def hay_entrada_activa(id_usuario):
    """Verifica si hay una entrada manual sin salida correspondiente (entrada activa)."""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Obtener el último acceso del usuario
    cursor.execute("""
        SELECT tipo, fecha FROM accesos_manuales
        WHERE id_usuario = ?
        ORDER BY fecha DESC
        LIMIT 1
    """, (id_usuario,))
    
    resultado = cursor.fetchone()
    conexion.close()
    
    # Si no hay accesos, no hay entrada activa
    if resultado is None:
        return False
    
    # Si el último acceso es una entrada, hay entrada activa
    # Si el último acceso es una salida, no hay entrada activa
    ultimo_tipo = resultado[0]
    return ultimo_tipo == "entrada"

# ===============================
# ADVERTENCIAS (vigilante)
# ===============================
def verificar_historial_usuario(id_usuario, id_historial):
    """Verifica si un ID de historial existe y pertenece al usuario especificado"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT idHis FROM historial 
        WHERE idHis = ? AND idUsuario = ?
    """, (id_historial, id_usuario))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado is not None

def enviar_advertencia(id_usuario, id_historial, motivo="Mal estacionado"):
    """Registra una advertencia para un usuario en una entrada específica."""
    conexion = conectar()
    cursor = conexion.cursor()
    fecha = datetime.now()
    cursor.execute("""
        INSERT INTO advertencias (id_usuario, id_historial, fecha, motivo)
        VALUES (?, ?, ?, ?)
    """, (id_usuario, id_historial, fecha, motivo))
    conexion.commit()
    conexion.close()
    return {"mensaje": f"Advertencia registrada para usuario {id_usuario}"}

def contar_advertencias_entrada(id_usuario, id_historial):
    """Cuenta advertencias en la entrada actual del usuario."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM advertencias
        WHERE id_usuario = ? AND id_historial = ?
    """, (id_usuario, id_historial))
    count = cursor.fetchone()[0]
    conexion.close()
    return count

def obtener_ultima_advertencia_entrada(id_usuario, id_historial):
    """Obtiene la fecha de la última advertencia de esta entrada."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT fecha FROM advertencias
        WHERE id_usuario = ? AND id_historial = ?
        ORDER BY fecha DESC
        LIMIT 1
    """, (id_usuario, id_historial))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado[0] if resultado else None

def obtener_advertencias_usuario(id_usuario):
    """Obtiene todas las advertencias de un usuario (históricas)."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT a.fecha, a.motivo, a.id_historial, h.fechaHis
        FROM advertencias a
        LEFT JOIN historial h ON a.id_historial = h.idHis
        WHERE a.id_usuario = ?
        ORDER BY a.fecha DESC
    """, (id_usuario,))
    rows = cursor.fetchall()
    conexion.close()
    return [{"fecha": r[0], "motivo": r[1], "id_historial": r[2], "fecha_entrada": r[3]} for r in rows]

def contar_advertencias_usuario(id_usuario):
    """Cuenta el total de advertencias de un usuario."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM advertencias WHERE id_usuario = ?", (id_usuario,))
    count = cursor.fetchone()[0]
    conexion.close()
    return count

# ===============================
# MULTAS (vigilante/admin)
# ===============================
def enviar_multa(id_usuario, id_historial, concepto, monto):
    """Registra una multa para un usuario."""
    conexion = conectar()
    cursor = conexion.cursor()
    fecha = datetime.now()
    cursor.execute("""
        INSERT INTO multas (id_usuario, id_historial, fecha, concepto, monto, pagado)
        VALUES (?, ?, ?, ?, ?, 0)
    """, (id_usuario, id_historial, fecha, concepto, monto))
    conexion.commit()
    conexion.close()
    return {"mensaje": f"Multa registrada para usuario {id_usuario}"}

def obtener_multas_usuario(id_usuario):
    """Obtiene todas las multas de un usuario."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT fecha, concepto, monto, pagado FROM multas
        WHERE id_usuario = ?
        ORDER BY fecha DESC
    """, (id_usuario,))
    rows = cursor.fetchall()
    conexion.close()
    return [{"fecha": r[0], "concepto": r[1], "monto": r[2], "pagado": r[3]} for r in rows]

def obtener_todas_multas():
    """Obtiene todas las multas del sistema (para admin)."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT m.id, m.id_usuario, u.nomUsuario, m.fecha, m.concepto, m.monto, m.pagado
        FROM multas m
        LEFT JOIN usuarios u ON m.id_usuario = u.idUsuario
        ORDER BY m.fecha DESC
    """)
    rows = cursor.fetchall()
    conexion.close()
    return [{"id": r[0], "id_usuario": r[1], "usuario": r[2], "fecha": r[3], "concepto": r[4], "monto": r[5], "pagado": r[6]} for r in rows]

def marcar_multa_pagada(id_multa, pagada):
    """Marca una multa como pagada o no (admin)."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("UPDATE multas SET pagado = ? WHERE id = ?", (1 if pagada else 0, id_multa))
    conexion.commit()
    conexion.close()
    return {"mensaje": "Estado de multa actualizado"}

def generar_id(tipo_usuario):
    """
    Genera un ID único para usuario basado en tipo
    Rango de IDs por tipo:
    - Tipo 1 (Alumno): 100-199
    - Tipo 2 (Administrativo): 200-299
    - Tipo 3 (Externo): 300-399
    """
    rangos = {1: (100, 199), 2: (200, 299), 3: (300, 399)}
    rango = rangos.get(tipo_usuario)
    
    if not rango:
        raise ValueError("Tipo de usuario inválido")
    
    min_id, max_id = rango
    
    conexion = conectar()
    cursor = conexion.cursor()
    # Obtener el ID más alto para este rango
    cursor.execute("SELECT MAX(idUsuario) FROM usuarios WHERE idUsuario >= ? AND idUsuario <= ?", 
                   (min_id, max_id))
    resultado = cursor.fetchone()
    ultimo_id = resultado[0] if resultado[0] else min_id - 1
    conexion.close()
    
    nuevo_id = ultimo_id + 1
    return nuevo_id


def insert_usuario(usuario):
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            INSERT INTO usuarios (idUsuario, nomUsuario, matrUsuario, celular, placa1, placa2)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            usuario["idUsuario"],
            usuario["nombre"],
            usuario.get("matricula", "N/A"),
            usuario.get("celular", "N/A"),
            "",  # placa1 vacía al inicio
            ""   # placa2 vacía al inicio
        ))
        conexion.commit()
        conexion.close()
        return {
            "mensaje": f"Usuario {usuario['idUsuario']} registrado correctamente",
            "idUsuario": usuario["idUsuario"]
        }
    except sql.IntegrityError as e:
        conexion.close()
        return {"error": f"Error de integridad: {str(e)}"}
    except Exception as e:
        conexion.close()
        return {"error": f"Error al registrar usuario: {str(e)}"}


def get_usuario(usuario_id):
    """Obtener datos completos de un usuario con información de autos"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Obtener datos del usuario
    cursor.execute("SELECT idUsuario, nomUsuario, matrUsuario, celular, placa1, placa2 FROM usuarios WHERE idUsuario = ?", (usuario_id,))
    data = cursor.fetchone()
    
    if not data:
        conexion.close()
        return {"error": "Usuario no encontrado"}
    
    # Obtener datos de los autos asociados
    cursor.execute("SELECT placa, marca, modelo FROM autos WHERE usuario_id = ?", (usuario_id,))
    autos = cursor.fetchall()
    
    conexion.close()
    
    # Construir respuesta
    respuesta = {
        "idUsuario": data[0],
        "nomUsuario": data[1],
        "matrUsuario": data[2],
        "celular": data[3],
        "placa1": data[4],
        "placa2": data[5],
        "autos": []
    }
    
    # Agregar información de autos
    for auto in autos:
        respuesta["autos"].append({
            "placa": auto[0],
            "marca": auto[1],
            "modelo": auto[2]
        })
    
    return respuesta


def get_todos_usuarios():
    """Obtener lista de todos los usuarios con información de autos"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT idUsuario, nomUsuario, matrUsuario, celular, placa1, placa2 FROM usuarios")
    resultados = cursor.fetchall()
    
    usuarios = []
    for row in resultados:
        usuario_id = row[0]
        
        # Obtener datos de autos para este usuario
        cursor.execute("SELECT placa, marca, modelo FROM autos WHERE usuario_id = ?", (usuario_id,))
        autos = cursor.fetchall()
        
        # Detectar tipo basado en rango de IDs
        # 100-199: Alumno (1), 200-299: Administrativo (2), 300-399: Externo (3)
        if 100 <= usuario_id < 200:
            tipo_nombre = "Alumno"
        elif 200 <= usuario_id < 300:
            tipo_nombre = "Administrativo"
        elif 300 <= usuario_id < 400:
            tipo_nombre = "Externo"
        else:
            tipo_nombre = "Desconocido"
        
        usuario_dict = {
            "id": usuario_id,
            "nombre": row[1],
            "matricula": row[2],
            "celular": row[3],
            "tipo": tipo_nombre,
            "placa1": row[4],
            "placa2": row[5],
            "autos": []
        }
        
        # Agregar información de autos
        for auto in autos:
            usuario_dict["autos"].append({
                "placa": auto[0],
                "marca": auto[1],
                "modelo": auto[2]
            })
        
        usuarios.append(usuario_dict)
    
    conexion.close()
    return usuarios


def update_usuario(usuario_id, datos_actualizados):
    """Actualizar datos de un usuario"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Verificar que el usuario existe
    cursor.execute("SELECT idUsuario FROM usuarios WHERE idUsuario = ?", (usuario_id,))
    if not cursor.fetchone():
        conexion.close()
        return {"error": "Usuario no encontrado"}
    
    # Actualizar solo los campos proporcionados
    campos = []
    valores = []
    
    if "nombre" in datos_actualizados:
        campos.append("nomUsuario = ?")
        valores.append(datos_actualizados["nombre"])
    
    if "celular" in datos_actualizados:
        campos.append("celular = ?")
        valores.append(datos_actualizados["celular"])
    
    if "matricula" in datos_actualizados:
        campos.append("matrUsuario = ?")
        valores.append(datos_actualizados["matricula"])
    
    if "placa1" in datos_actualizados:
        campos.append("placa1 = ?")
        valores.append(datos_actualizados["placa1"])
    
    if "placa2" in datos_actualizados:
        campos.append("placa2 = ?")
        valores.append(datos_actualizados["placa2"])
    
    if not campos:
        conexion.close()
        return {"mensaje": "No hay campos para actualizar"}
    
    valores.append(usuario_id)
    sql = f"UPDATE usuarios SET {', '.join(campos)} WHERE idUsuario = ?"
    cursor.execute(sql, valores)
    conexion.commit()
    conexion.close()
    
    return {"mensaje": f"Usuario {usuario_id} actualizado correctamente"}


def delete_usuario(usuario_id):
    """Eliminar un usuario y todos sus datos asociados (autos, login, historial)"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    try:
        # Verificar que el usuario existe
        cursor.execute("SELECT nomUsuario FROM usuarios WHERE idUsuario = ?", (usuario_id,))
        usuario = cursor.fetchone()
        
        if not usuario:
            conexion.close()
            return {"error": "Usuario no encontrado"}
        
        # Las claves foráneas con ON DELETE CASCADE se encargarán de eliminar:
        # - Registros en login
        # - Registros en autos
        # - Registros en historial
        cursor.execute("DELETE FROM usuarios WHERE idUsuario = ?", (usuario_id,))
        conexion.commit()
        conexion.close()
        
        return {"mensaje": f"Usuario {usuario_id} ({usuario[0]}) eliminado correctamente"}
        
    except Exception as e:
        conexion.rollback()
        conexion.close()
        return {"error": f"Error al eliminar usuario: {str(e)}"}


# =====================================================
# FUNCIONES DE LOGIN Y AUTENTICACIÓN
# =====================================================

def validar_login(usuario, contrasena):
    """Validar credenciales de login"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT rol, id_usuario FROM login WHERE usuario = ? AND contrasena = ?", (usuario, contrasena))
    resultado = cursor.fetchone()
    conexion.close()
    
    if resultado:
        return {
            "autenticado": True,
            "rol": resultado[0],
            "id_usuario": resultado[1]
        }
    return {"autenticado": False}


def insertar_login(usuario, contrasena, rol, id_usuario=None):
    """Insertar credenciales de login"""
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            INSERT INTO login (usuario, contrasena, rol, id_usuario)
            VALUES (?, ?, ?, ?)
        """, (usuario, contrasena, rol, id_usuario))
        conexion.commit()
        conexion.close()
        return {"mensaje": f"Login para {usuario} creado correctamente"}
    except sql.IntegrityError:
        conexion.close()
        return {"error": f"El usuario {usuario} ya existe"}
    except Exception as e:
        conexion.close()
        return {"error": str(e)}


def seed_datos_iniciales():
    """Poblar la base de datos con usuarios de prueba (solo si está vacía)"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Datos de usuarios por tipo - UNO DE CADA TIPO
    # IDs: 100-199 (Alumno), 200-299 (Administrativo), 300-399 (Externo)
    usuarios = [
        # Tipo 1: Alumno (ID: 100-199)
        (100, "Carlos Mendoza Rodríguez", 202401, "3004567890", "ABC-1234", ""),
        
        # Tipo 2: Administrativo (ID: 200-299)
        (200, "Sandra Ruiz Gutiérrez", 202404, "3015678901", "GHI-1112", ""),
        
        # Tipo 3: Externo (ID: 300-399)
        (300, "David Ortega González", 999999, "3026789012", "MNO-1516", ""),
    ]
    
    # Datos de autos asociados a cada usuario
    autos = [
        # Autos del usuario 100 (Carlos)
        ("ABC-1234", 100, 1, "Blanco", "Hyundai", "Elantra"),
        ("DEF-5678", 100, 1, "Gris", "Toyota", "Corolla"),
        
        # Autos del usuario 200 (Sandra)
        ("GHI-1112", 200, 1, "Negro", "Honda", "Civic"),
        
        # Autos del usuario 300 (David)
        ("MNO-1516", 300, 1, "Rojo", "Nissan", "Sentra"),
    ]
    
    # Credenciales de login asociadas a los usuarios - UNA DE CADA TIPO
    credenciales = [
        ("carlos.mendoza", "1234", "usuario", 100),
        ("sandra.ruiz", "admin123", "admin", 200),
        ("david.ortega", "vigilante123", "vigilante", 300),
    ]
    
    try:
        # Insertar usuarios
        for usuario in usuarios:
            cursor.execute("""
                INSERT INTO usuarios (idUsuario, nomUsuario, matrUsuario, celular, placa1, placa2)
                VALUES (?, ?, ?, ?, ?, ?)
            """, usuario)
        
        # Insertar autos
        for auto in autos:
            cursor.execute("""
                INSERT INTO autos (placa, usuario_id, tipo_vehiculo, color, marca, modelo)
                VALUES (?, ?, ?, ?, ?, ?)
            """, auto)
        
        # Insertar credenciales de login
        for cred in credenciales:
            cursor.execute("""
                INSERT INTO login (usuario, contrasena, rol, id_usuario)
                VALUES (?, ?, ?, ?)
            """, cred)
        
        conexion.commit()
        print(f"✅ Se insertaron {len(usuarios)} usuarios, {len(autos)} autos y {len(credenciales)} credenciales")
        
    except sql.IntegrityError as e:
        print(f"⚠️  Datos ya existen o error de integridad: {e}")
        conexion.rollback()
    except Exception as e:
        print(f"❌ Error al insertar datos: {e}")
        conexion.rollback()
    finally:
        conexion.close()


def crear_login_para_usuario(usuario_login, contrasena, rol, id_usuario):
    """
    Crear credenciales de login para un usuario existente
    
    Args:
        usuario_login: nombre de usuario para login (ej: juan.perez)
        contrasena: contraseña (sin encriptar, solo para demostración)
        rol: usuario, admin, vigilante
        id_usuario: ID del usuario en tabla usuarios
    
    Returns:
        dict con mensaje de éxito o error
    """
    conexion = conectar()
    cursor = conexion.cursor()
    
    try:
        # Verificar que el usuario existe en tabla usuarios
        cursor.execute("SELECT nomUsuario FROM usuarios WHERE idUsuario = ?", (id_usuario,))
        usuario_existe = cursor.fetchone()
        
        if not usuario_existe:
            conexion.close()
            return {"error": f"Usuario con ID {id_usuario} no existe"}
        
        # Verificar que el nombre de usuario no existe ya en login
        cursor.execute("SELECT id FROM login WHERE usuario = ?", (usuario_login,))
        usuario_login_existe = cursor.fetchone()
        
        if usuario_login_existe:
            conexion.close()
            return {"error": f"El nombre de usuario '{usuario_login}' ya existe"}
        
        # Insertar credenciales
        cursor.execute("""
            INSERT INTO login (usuario, contrasena, rol, id_usuario)
            VALUES (?, ?, ?, ?)
        """, (usuario_login, contrasena, rol, id_usuario))
        
        conexion.commit()
        conexion.close()
        
        return {
            "mensaje": f"Credenciales creadas correctamente",
            "usuario": usuario_login,
            "rol": rol,
            "id_usuario": id_usuario
        }
    
    except sql.IntegrityError as e:
        conexion.close()
        return {"error": f"Error de integridad: {str(e)}"}
    except Exception as e:
        conexion.close()
        return {"error": f"Error al crear credenciales: {str(e)}"}

# =====================================================
# NUEVAS FUNCIONES PARA VIGILANTE Y CONTROL DE ACCESO
# =====================================================

def get_accesos_recientes(limite=10):
    """Obtiene los últimos accesos registrados con información del usuario"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Obtener historial reciente con información de usuario
    cursor.execute("""
        SELECT 
            h.idHis,
            h.idUsuario,
            u.nomUsuario,
            u.celular,
            h.espAsig,
            h.fechaHis,
            h.valido
        FROM historial h
        JOIN usuarios u ON h.idUsuario = u.idUsuario
        ORDER BY h.idHis DESC
        LIMIT ?
    """, (limite,))
    
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()
    
    accesos = []
    for fila in resultados:
        accesos.append({
            "historial_id": fila[0],
            "usuario_id": fila[1],
            "nombre_usuario": fila[2],
            "celular": fila[3],
            "espacio_asignado": fila[4],
            "fecha_hora_entrada": fila[5],
            "activo": fila[6]  # 1 = acceso activo, 0 = cerrado
        })
    
    return accesos

def verificar_acceso_activo(id_usuario):
    """Verifica si el usuario tiene un acceso activo sin salida"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Buscar el último acceso del usuario que esté activo (valido = 1)
    cursor.execute("""
        SELECT idHis, espAsig, fechaHis
        FROM historial
        WHERE idUsuario = ? AND valido = 1
        ORDER BY idHis DESC
        LIMIT 1
    """, (id_usuario,))
    
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()
    
    if resultado:
        return {
            "tiene_acceso_activo": True,
            "historial_id": resultado[0],
            "espacio_asignado": resultado[1],
            "fecha_entrada": resultado[2]
        }
    else:
        return {"tiene_acceso_activo": False}

def cerrar_acceso(id_usuario):
    """Marca el último acceso activo del usuario como cerrado"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    try:
        # Actualizar el último acceso activo a valido = 0 (cerrado)
        cursor.execute("""
            UPDATE historial
            SET valido = 0
            WHERE idUsuario = ? AND valido = 1
            ORDER BY idHis DESC
            LIMIT 1
        """, (id_usuario,))
        
        conexion.commit()
        
        # Obtener el registro actualizado
        cursor.execute("""
            SELECT idHis, espAsig, fechaHis
            FROM historial
            WHERE idUsuario = ?
            ORDER BY idHis DESC
            LIMIT 1
        """, (id_usuario,))
        
        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()
        
        return {
            "exito": True,
            "mensaje": f"Acceso cerrado para usuario {id_usuario}",
            "historial_id": resultado[0] if resultado else None
        }
    except Exception as e:
        conexion.close()
        return {
            "exito": False,
            "mensaje": f"Error al cerrar acceso: {str(e)}"
        }
