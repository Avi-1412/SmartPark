# 📜 Scripts de SmartPark

Scripts auxiliares para el sistema SmartPark.

## 📋 Scripts Disponibles

### 1. `monitor_sensores_backend.py`
**Propósito:** Lee sensores IR del Arduino y envía datos al backend.

**Funciona:**
- Lee puerto serial (COM8 por defecto)
- Parsea formato: `SENSORES: A=1,B=0,C=1,D=0`
- Envía a: `POST /sensores/actualizar`
- Detecta ocupación ilegal automáticamente

**Uso:**
```bash
python monitor_sensores_backend.py
```

**Configuración (en el script):**
```python
PUERTO_SERIAL = "COM8"          # Cambiar si es otro puerto
VELOCIDAD_BAUD = 9600
BACKEND_URL = "http://127.0.0.1:8000/sensores/actualizar"
INTERVALO_LECTURA = 10          # Segundos entre lecturas
```

---

### 2. `lector_rfid_backend.py`
**Propósito:** Lee tarjetas RFID del Arduino y registra entrada de usuarios.

**Funciona:**
- Lee puerto serial (COM8 por defecto)
- Parsea formato: `JSON: {"id_usuario":100}`
- Envía a: `POST /registrar/rfid`
- Valida usuario y asigna espacio automáticamente

**Uso:**
```bash
python lector_rfid_backend.py
```

**Configuración (en el script):**
```python
PUERTO_SERIAL = "COM8"
VELOCIDAD_BAUD = 9600
BACKEND_URL = "http://127.0.0.1:8000/registrar/rfid"
```

---

## 🚀 Inicio Rápido

### Terminal 1: Backend
```bash
cd Backend/Modulos
python -m uvicorn app:app --reload
```

### Terminal 2: Monitor de Sensores
```bash
cd Scripts
python monitor_sensores_backend.py
```

### Terminal 3: RFID Backend (Opcional)
```bash
cd Scripts
python lector_rfid_backend.py
```

### Terminal 4: Frontend
```bash
cd Frontend
python main.py
```

---

## 🔌 Hardware Requerido

- Arduino Nano con código: `Arduino/rfid_y_sensores.ino`
- Lector RFID RC522
- 4x Sensores IR (A0-A3)
- Conexión USB a COM8 (o tu puerto)

---

## 🔧 Troubleshooting

| Problema | Solución |
|----------|----------|
| `SerialException: Port not found` | Cambiar `PUERTO_SERIAL` al correcto (COM3, COM4, etc.) |
| `Connection refused` | Asegurar backend corriendo en puerto 8000 |
| `No data from Arduino` | Verificar que Arduino tiene código `rfid_y_sensores.ino` |
| `Timeout` | Aumentar `timeout` en requests o revisar velocidad baud |

---

## 📝 Notas

- Los scripts corren en **loops infinitos**
- Presiona `Ctrl+C` para detener
- Se conectan automáticamente al backend
- Manejan errores y reconectan silenciosamente

---

**Última actualización:** Noviembre 2025
