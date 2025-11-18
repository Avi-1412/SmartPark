# 🚗 SmartPark - Sistema de Gestión de Estacionamiento

Sistema completo de gestión de estacionamiento con roles de usuario (Admin, Vigilante, Usuario) desarrollado en Python con FastAPI y Flet.

## 📋 Descripción

SmartPark es una aplicación de escritorio para gestionar:
- **Usuarios**: Registro, visualización de datos personales y tarjeta digital
- **Vehículos**: Registro de placas, marcas y modelos
- **Administradores**: Gestión completa de usuarios y datos
- **Vigilantes**: Visualización de usuarios y vehículos registrados

## 🛠️ Requisitos

- Python 3.8+
- pip
- Conda (opcional)

## 📦 Instalación

```bash
# Clonar o descargar el proyecto
cd SmartPark

# Crear ambiente virtual (opcional pero recomendado)
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r Backend/Modulos/requirements.txt
pip install flet
```

## 🚀 Inicio Rápido

### Terminal 1: Backend
```bash
cd Backend/Modulos
python -m uvicorn app:app --reload
```
El backend se inicia en: `http://localhost:8000`

### Terminal 2: Monitor de Sensores (Opcional - si hay Arduino)
```bash
cd Scripts
python monitor_sensores_backend.py
```

### Terminal 3: RFID Backend (Opcional - si hay Arduino)
```bash
cd Scripts
python lector_rfid_backend.py
```

### Terminal 4: Frontend
```bash
cd Frontend
python main.py
```

## 🔐 Credenciales de Prueba

Al iniciar por primera vez, el sistema crea automáticamente 3 usuarios:

| Usuario | Contraseña | Rol | ID |
|---------|-----------|-----|-----|
| carlos.mendoza | 1234 | usuario | 100 |
| sandra.ruiz | admin123 | admin | 200 |
| david.ortega | vigilante123 | vigilante | 300 |

## 📁 Estructura del Proyecto

```
SmartPark/
├── Backend/
│   ├── BaseDatos/
│   │   ├── bd.py                 # Funciones de BD y lógica
│   │   ├── crud.db               # Base de datos SQLite
│   │   └── __init__.py
│   ├── Modulos/
│   │   ├── app.py                # API FastAPI
│   │   ├── requirements.txt      # Dependencias
│   │   └── __init__.py
│   └── __init__.py
├── Frontend/
│   ├── main.py                   # Punto de entrada
│   ├── GUIPrincipal.py           # Interfaz principal
│   ├── pages/
│   │   ├── admin_page.py         # Panel Admin
│   │   ├── usuario_page.py       # Panel Usuario
│   │   ├── vigilante_page.py     # Panel Vigilante
│   │   └── __pycache__/
│   └── __pycache__/
├── reset_bd.py                   # Script para resetear la BD
└── README.md                     # Este archivo
```

## 🎯 Funcionalidades por Rol

### 👨‍💼 Administrador (ID: 200-299)
- ✅ Ver/modificar datos de todos los usuarios
- ✅ Registrar nuevos usuarios
- ✅ Crear credenciales de acceso (2 pasos)
- ✅ Editar información de usuarios
- ✅ Eliminar usuarios con confirmación
- ✅ Ver historial de entradas

### 🚨 Vigilante (ID: 300-399)
- ✅ Ver datos de todos los usuarios
- ✅ Visualizar vehículos registrados (placa, marca, modelo)
- ✅ Ver números telefónicos de usuarios
- ⏳ Enviar advertencias y multas (en desarrollo)

### 👤 Usuario (ID: 100-199)
- ✅ Ver tarjeta digital con su información
- ✅ Visualizar vehículos registrados
- ✅ Ver número telefónico
- ✅ Ver historial de entradas
- ⏳ Ver boleto digital (en desarrollo)
- ⏳ Ver notificaciones/multas (en desarrollo)

## 🗄️ Base de Datos

**Tablas principales:**

### `usuarios`
```sql
- idUsuario (INTEGER PRIMARY KEY)
- nomUsuario (TEXT)
- matrUsuario (INTEGER)
- celular (TEXT)
- placa1 (TEXT)
- placa2 (TEXT)
```

### `login`
```sql
- id (INTEGER PRIMARY KEY AUTOINCREMENT)
- usuario (TEXT UNIQUE)
- contrasena (TEXT)
- rol (TEXT)
- id_usuario (INTEGER FK)
```

### `autos`
```sql
- placa (TEXT PRIMARY KEY)
- usuario_id (INTEGER FK)
- tipo_vehiculo (INTEGER)
- color (TEXT)
- marca (TEXT)
- modelo (TEXT)
```

### `historial`
```sql
- idHis (INTEGER PRIMARY KEY)
- idUsuario (INTEGER FK)
- espAsig (TEXT)
- fechaHis (DATETIME)
- valido (INTEGER)
```

## 🔧 Resetear la Base de Datos

Para borrar todos los datos y reiniciar con datos de prueba:

```bash
python reset_bd.py
```

Esto:
- ✅ Elimina la BD actual
- ✅ Crea una nueva BD
- ✅ Inserta 3 usuarios de prueba con sus vehículos
- ✅ Crea sus credenciales de acceso

## 📡 API Endpoints

### Autenticación
- `POST /login` - Login con usuario y contraseña

### Usuarios
- `GET /usuarios` - Obtener todos los usuarios
- `GET /usuarios/{usuario_id}` - Obtener datos de un usuario
- `POST /usuarios` - Registrar nuevo usuario
- `PUT /usuarios/{usuario_id}` - Editar usuario
- `DELETE /usuarios/{usuario_id}` - Eliminar usuario

### Credenciales
- `POST /login/crear` - Crear credenciales para un usuario

### Historial
- `GET /historial` - Obtener historial de entradas

## 📝 Flujo de Registro (2 Pasos)

### Paso 1: Registrar Usuario
1. Admin accede a "Registrar o agregar usuarios"
2. Completa: Tipo, Nombre, Matrícula (opcional), Celular
3. El sistema genera automáticamente un ID único

### Paso 2: Crear Credenciales
1. Aparece diálogo automático
2. Admin ingresa contraseña
3. Se crea credencial de acceso (usuario puede hacer login)

## 🐛 Solución de Problemas

### "El proceso no tiene acceso al archivo crud.db"
**Solución**: El backend está usando la BD. Cierra el uvicorn y ejecuta:
```bash
python reset_bd.py
```

### "Connection refused" al conectar al backend
**Solución**: Asegúrate que el backend esté corriendo:
```bash
python -m uvicorn Backend.Modulos.app:app --reload
```

### Error en frontend: "unexpected keyword argument"
**Solución**: Actualiza Flet:
```bash
pip install --upgrade flet
```

## 👨‍💻 Desarrollo

El proyecto utiliza:
- **Backend**: FastAPI + SQLite
- **Frontend**: Flet (interfaz gráfica en Python)
- **Base de datos**: SQLite (crud.db)
- **Hardware**: Arduino Nano + MFRC522 (RFID) + Sensores IR

## 🔌 Integración con Arduino

### Hardware Requerido
- Arduino Nano (ATmega328P)
- **2x Lector RFID RC522** (Uno para ENTRADA, otro para SALIDA)
- 4x Sensores IR (MH Sensor Series)

### Conexiones Arduino
**Lector RFID ENTRADA:**
- SS (Chip Select) → Pin 10
- RST (Reset) → Pin 9
- SCK → Pin 13
- MOSI → Pin 11
- MISO → Pin 12

**Lector RFID SALIDA:**
- SS (Chip Select) → Pin 8
- RST (Reset) → Pin 7
- SCK → Pin 13 (compartido)
- MOSI → Pin 11 (compartido)
- MISO → Pin 12 (compartido)

**Sensores IR:**
- Sensor A → Pin 2
- Sensor B → Pin 3
- Sensor C → Pin 4
- Sensor D → Pin 5

### Funcionalidades
- **RFID Entry**: Lectura de tarjetas para registro de entrada
- **RFID Exit**: Lectura de tarjetas para registro de salida (solo con entrada activa)
- **Space Assignment**: Algoritmo Dijkstra para asignar espacios automáticamente
- **Occupancy Detection**: Sensores IR detectan ocupación en tiempo real
- **Illegal Parking Detection**: Sistema de alertas para ocupación sin asignación

### Endpoints de Sensores
```
POST /sensores/actualizar
  - Recibe: {"sensores": {"A": 1, "B": 0, "C": 1, "D": 0}}
  - Respuesta: {"success": true, "ocupacion_ilegal": ["C"]}

GET /sensores/estado
  - Obtiene estado actual de todos los espacios

GET /sensores/alertas
  - Obtiene alertas pendientes (para panel vigilante)

POST /sensores/alertas/{alerta_id}/resolver
  - Marca una alerta como resuelta
```

### Endpoints de RFID
```
POST /registrar/entrada
  - Recibe: {"id_usuario": 100}
  - Valida usuario y asigna espacio automáticamente

POST /registrar/salida
  - Recibe: {"id_usuario": 100}
  - Cierra entrada activa y libera espacio
  - Solo funciona si hay entrada activa sin cerrar
```

### Archivos Arduino
- `Arduino/rfid_y_sensores.ino` - Código principal (2x RFID + Sensores)

### Scripts Python
- `Scripts/monitor_sensores_backend.py` - Lee sensores cada 10s y envía al backend
- `Scripts/lector_rfid_backend.py` - Lee RFID (entrada/salida) del Arduino y registra

### Configuración de Puertos
En los scripts de Arduino (`monitor_sensores_backend.py`, `lector_rfid_backend.py`):
```python
PUERTO_SERIAL = "COM3"  # Cambiar según tu puerto
VELOCIDAD_BAUD = 9600
```

### Formato JSON del Arduino
**ENTRADA:**
```json
{"id_usuario": 100, "tipo": "ENTRADA"}
```

**SALIDA:**
```json
{"id_usuario": 100, "tipo": "SALIDA"}
```

### Flujo Completo

**ENTRADA:**
1. Usuario acerca tarjeta al lector de ENTRADA
2. Arduino lee y envía: `{"id_usuario": 100, "tipo": "ENTRADA"}`
3. `lector_rfid_backend.py` procesa y envía a `/registrar/entrada`
4. Backend valida usuario y asigna espacio (Dijkstra)
5. Usuario estaciona en espacio asignado

**SALIDA:**
1. Usuario acerca tarjeta al lector de SALIDA
2. Arduino lee y envía: `{"id_usuario": 100, "tipo": "SALIDA"}`
3. `lector_rfid_backend.py` procesa y envía a `/registrar/salida`
4. Backend verifica que hay entrada activa
5. Si válido: cierra entrada y libera espacio
6. Si error: muestra mensaje (no hay entrada activa, etc)

**SENSORES:**
- `monitor_sensores_backend.py` lee sensores cada 10s
- Backend detecta ocupación ilegal (espacio ocupado sin asignación)
- Crea alertas automáticamente
- Vigilante ve alertas en panel y puede resolver

## 📋 Estado de Funcionalidades

| Feature | Estado | Notas |
|---------|--------|-------|
| Login | ✅ Completo | Autenticación con 2FA pendiente |
| Registro de usuarios | ✅ Completo | Con validaciones |
| Gestión de autos | ✅ Completo | Marca y modelo incluidos |
| Tarjeta digital | ✅ Completo | Con datos de vehículos |
| Admin - CRUD usuarios | ✅ Completo | Incluye eliminar con confirmación |
| Vigilante - Ver usuarios | ✅ Completo | Tabla con todos los datos |
| Historial | ✅ Completo | Últimas 10 entradas |
| Multas/Advertencias | ✅ Completo | Sistema de escalation (3 adv → multa) |
| RFID Entry | ✅ Completo | Lectura de tarjetas y asignación automática |
| Space Assignment | ✅ Completo | Algoritmo Dijkstra |
| Occupancy Sensors | ✅ Completo | Detección de ocupación ilegal |
| Arduino Integration | ✅ Completo | RFID + Sensores IR |
| Boleto digital | ⏳ En desarrollo | |
| Notificaciones | ⏳ En desarrollo | |

## 📞 Soporte

Para reportar bugs o sugerencias, crea un issue en el repositorio.

---

**Última actualización**: Noviembre 2025
