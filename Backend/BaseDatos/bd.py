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
    
    conexion.commit()
    conexion.close()


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
