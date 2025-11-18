# 🚗 SmartPark - Sistema de Gestión de Estacionamiento Inteligente

Sistema completo e integrado de gestión de estacionamiento con **RFID, sensores IR, Arduino y detección de ocupación no autorizada**. Desarrollado con Python FastAPI (Backend) y Flet (Frontend).

## 📋 Descripción

SmartPark automatiza completamente la gestión de estacionamiento:
- **Entrada/Salida automática**: Lectura RFID sin contacto
- **Asignación inteligente**: Algoritmo Dijkstra para el espacio más cercano
- **Detección de ocupación**: Sensores IR detectan autos no autorizados
- **3 Roles diferenciados**: Usuario, Vigilante, Admin con permisos específicos
- **Historial completo**: Registro de todas las entradas/salidas con horas exactas

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

### Configuración Inicial

```bash
# 1. Clonar proyecto
git clone https://github.com/Avi-1412/SmartPark.git
cd SmartPark

# 2. Crear ambiente virtual
python -m venv venv
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r Backend/Modulos/requirements.txt
pip install flet
```

### Iniciar Sistema (4 Terminales)

**Terminal 1: Backend (API)**
```bash
uvicorn Backend.Modulos.app:app --reload
# Corre en: http://127.0.0.1:8000
```

**Terminal 2: RFID Reader (Lee tarjetas del Arduino)**
```bash
python Scripts/lector_rfid_backend.py
# Conecta Arduino COM3 (entrada) y COM4 (salida)
```

**Terminal 3: Reset BD (Opcional - Solo primera vez)**
```bash
python reset_bd.py
# Crea BD con usuarios de prueba
```

**Terminal 4: Frontend (GUI)**
```bash
cd Frontend
python Main.py
```

### Credenciales de Prueba

| Usuario | Contraseña | Rol | ID |
|---------|-----------|-----|-----|
| carlos.mendoza | 1234 | usuario | 100 |
| sandra.ruiz | admin123 | admin | 200 |
| david.ortega | vigilante123 | vigilante | 300 |

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                      ENTRADA Y SALIDA                        │
│  Arduino Nano            Arduino UNO                        │
│     (COM3)                  (COM4)                         │
│  ┌──────────────┐       ┌──────────────┐                   │
│  │ ENTRADA      │       │ SALIDA       │                   │
│  │ RC522 RFID   │       │ RC522 RFID   │                   │
│  │ 4x Sensores  │       │              │                   │
│  │ IR (A,B,C,D) │       │              │                   │
│  └──────┬───────┘       └──────┬───────┘                   │
│         │ Serial 9600          │ Serial 9600               │
└─────────┼──────────────────────┼────────────────────────────┘
          │                      │
          └──────────┬───────────┘
                     │
          ┌──────────▼──────────┐
          │  lector_rfid_       │
          │  backend.py         │
          │  (Python Script)    │
          │                     │
          │ Lee RFID x2         │
          │ Envía JSON al API   │
          └──────────┬──────────┘
                     │ HTTP POST
        ┌────────────▼────────────┐
        │   FastAPI Backend       │
        │  (app.py en puerto 8000)│
        │                         │
        │ POST /registrar/entrada │
        │ POST /registrar/salida  │
        │ GET /historial/usuario  │
        │ POST /sensores/alertas  │
        └────────────┬────────────┘
                     │ SQLite
        ┌────────────▼────────────┐
        │   Base de Datos         │
        │      (crud.db)          │
        │                         │
        │ Tablas:                 │
        │ - usuarios              │
        │ - login                 │
        │ - historial             │
        │ - estado_sensores       │
        │ - alertas_sensor        │
        │ - advertencias          │
        │ - multas                │
        └─────────────────────────┘
        
        ┌─────────────────────────┐
        │  Frontend Flet (GUI)    │
        │   (Main.py)             │
        │                         │
        │ ├─ Login Page           │
        │ ├─ Admin Page           │
        │ ├─ Usuario Page         │
        │ └─ Vigilante Page       │
        └─────────────────────────┘
```

### Componentes Principales

| Componente | Archivo | Función |
|-----------|---------|---------|
| **Backend API** | `Backend/Modulos/app.py` | FastAPI endpoints (439 líneas) |
| **Base de Datos** | `Backend/BaseDatos/bd.py` | Lógica SQL y operaciones (1119 líneas) |
| **Asignador** | `Backend/Modulos/asignador.py` | Algoritmo Dijkstra (250 líneas) |
| **Lector RFID** | `Scripts/lector_rfid_backend.py` | Lee 2 Arduinos en paralelo (191 líneas) |
| **Frontend** | `Frontend/Main.py` | GUI Flet login (156 líneas) |
| **Rol Admin** | `Frontend/pages/admin_page.py` | Panel administrador |
| **Rol Vigilante** | `Frontend/pages/vigilante_page.py` | Panel vigilante (1093 líneas) |
| **Rol Usuario** | `Frontend/pages/usuario_page.py` | Panel usuario |

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

## ✅ Estado de Funcionalidades

### COMPLETO Y FUNCIONANDO

| Funcionalidad | Estado | Detalles |
|---------------|--------|----------|
| **Login** | ✅ | Autenticación con 3 roles (usuario/admin/vigilante) |
| **RFID Entrada** | ✅ | Lee tarjetas, valida usuario, asigna espacio |
| **RFID Salida** | ✅ | Lee tarjetas, valida acceso activo, libera espacio |
| **Asignación Espacios** | ✅ | Algoritmo Dijkstra - espacio más cercano |
| **Detección Ocupación** | ✅ | Sensores IR detectan ocupación ilegal |
| **Historial** | ✅ | Registro con hora entrada/salida exacta |
| **Admin - CRUD Usuarios** | ✅ | Crear, leer, editar, eliminar usuarios |
| **Vigilante - Ver Datos** | ✅ | Tabla de usuarios con historial por usuario |
| **Advertencias** | ✅ | Sistema de escalation (3 advertencias → multa) |
| **Multas** | ✅ | Generación automática tras 3 advertencias |
| **Base de Datos** | ✅ | SQLite con 7 tablas normalizadas |
| **API Endpoints** | ✅ | 20+ endpoints REST documentados |

### PENDIENTE

| Funcionalidad | Requisito | Prioridad |
|---------------|-----------|-----------|
| **Servomotor/Pluma** | Módulo relay 2 canales | ALTA |
| **Notificaciones Real-Time** | WebSocket o polling optimizado | MEDIA |
| **Boleto Digital** | Frontend usuario_page | MEDIA |

---

**Archivos clave para entender:**
- `Backend/Modulos/asignador.py` - Algoritmo Dijkstra (solo 250 líneas, muy legible)
- `Backend/BaseDatos/bd.py` - Todas las queries SQL (bien documentadas)
- `Scripts/lector_rfid_backend.py` - Lectura paralela de 2 puertos (threading)
- `Frontend/pages/vigilante_page.py` - UI más compleja pero bien estructurada

---

**Última actualización**: Noviembre 2025 | **Versión**: 0.0.6 
