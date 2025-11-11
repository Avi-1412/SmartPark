# Flujo de Credenciales en Dos Pasos

## Resumen

El sistema SmartPark ahora implementa un **flujo de dos pasos** para la creación de usuarios con credenciales de login. Esto proporciona mayor control y flexibilidad al administrador.

## Pasos

### Paso 1: Registrar Usuario

1. Admin accede al panel: **"Registrar o agregar usuarios"**
2. Completa el formulario con:
   - **Tipo de usuario**: Alumno, Administrativo, Externo (Dropdown)
   - **Nombre completo** *
   - **Matrícula** (solo números, opcional)
   - **Vigencia** (formato YYYY-MM-DD, default: 2025-12-31)
   - **Pago**: Sí/No (Dropdown)
   - **Teléfono** (opcional)
3. Hace clic en **"Registrar"**
4. **Resultado**: Usuario creado en tabla `usuarios` con ID auto-generado

**Nota**: En este paso, el usuario NO tiene credenciales de acceso aún.

### Paso 2: Crear Credenciales

Después del registro exitoso, automáticamente aparece un diálogo: **"Crear credenciales de acceso"**

1. **Usuario** aparece pre-llenado con sugerencia auto-generada:
   - Formato: `nombre.apellido` (minúsculas)
   - Ejemplo: `juan.perez`
   - Admin puede modificar si lo desea
2. **Contraseña** *
3. **Confirmar contraseña** *
4. Hacer clic en **"Crear"** o **"Omitir"**

**Resultado del Crear**:
- Credenciales insertadas en tabla `login`
- Rol determinado automáticamente según tipo de usuario:
  - Tipo 1 (Alumno) → `usuario`
  - Tipo 2 (Administrativo) → `admin`
  - Tipo 3 (Externo) → `vigilante`

**Resultado del Omitir**:
- Usuario queda sin credenciales
- Admin puede crear credenciales más tarde accediendo a **Ver/modificar datos** (función pendiente)

## Flujo Técnico

```
┌──────────────────────────────────────────┐
│  Admin Panel - Opción: Registrar Usuario │
└──────────────────────────────────────────┘
                    │
                    ▼
        ┌─────────────────────────┐
        │  Formulario de Usuario  │
        │  - Tipo                 │
        │  - Nombre               │
        │  - Matrícula            │
        │  - Vigencia             │
        │  - Pago                 │
        │  - Teléfono             │
        └─────────────────────────┘
                    │
                    ▼
        ┌─────────────────────────┐
        │ POST /usuarios          │
        │ (Backend: app.py)       │
        └─────────────────────────┘
                    │
                    ▼
        ┌─────────────────────────┐
        │ INSERT en tabla usuarios│
        │ (Backend: bd.py)        │
        └─────────────────────────┘
                    │
                    ▼
        ┌─────────────────────────┐
        │ Retorna idUsuario       │
        └─────────────────────────┘
                    │
                    ▼
        ┌─────────────────────────┐
        │ Mostrar Diálogo:        │
        │ "Crear Credenciales"    │
        │ (Frontend: admin_page)  │
        │                         │
        │ - usuario_login         │
        │ - contrasena            │
        │ - confirmar_contrasena  │
        │                         │
        │ [Crear] [Omitir]        │
        └─────────────────────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
      [Crear]              [Omitir]
         │                     │
         ▼                     ▼
  POST /login/crear        Usuario sin
  (Backend: app.py)        credenciales
         │
         ▼
  INSERT en tabla login
  (Backend: bd.py)
         │
         ▼
  ✅ Credenciales Creadas
     Usuario puede hacer login
```

## Endpoints Utilizados

### Paso 1: Crear Usuario
```
POST /usuarios
{
  "tipo_id": "1",  // 1=Alumno, 2=Admin, 3=Vigilante
  "tipo": "Alumno",
  "nombre": "Juan Pérez",
  "matricula": "12345",
  "vigencia": "2025-12-31",
  "pago": 1,
  "telefono": "+5551234567"
}

Response (Exitoso):
{
  "mensaje": "Usuario registrado correctamente",
  "idUsuario": "010001"
}
```

### Paso 2: Crear Credenciales
```
POST /login/crear
{
  "usuario_login": "juan.perez",
  "contrasena": "mi_contraseña_123",
  "rol": "usuario",
  "id_usuario": "010001"
}

Response (Exitoso):
{
  "mensaje": "Credenciales creadas correctamente",
  "usuario": "juan.perez",
  "rol": "usuario",
  "id_usuario": "010001"
}

Response (Error - usuario existe):
{
  "error": "El nombre de usuario 'juan.perez' ya existe"
}

Response (Error - usuario_id no existe):
{
  "error": "Usuario con ID 010001 no existe"
}
```

## Validaciones

### Paso 1: Formulario de Usuario
- **Tipo de usuario**: Requerido (Dropdown)
- **Nombre**: Requerido, no puede estar vacío
- **Matrícula**: Opcional, si se proporciona debe ser solo números
- **Vigencia**: Formato YYYY-MM-DD (default: 2025-12-31)
- **Pago**: Sí/No (default: Sí)
- **Teléfono**: Opcional, si se proporciona debe tener mínimo 7 dígitos

### Paso 2: Diálogo de Credenciales
- **usuario_login**: Requerido, no puede estar vacío
- **contrasena**: Requerido, no puede estar vacía
- **confirmar_contrasena**: Debe coincidir con contrasena
- **Unicidad**: usuario_login no debe existir ya en tabla login

## Flujo Alternativo: Crear Credenciales Posteriormente

Si el admin hace clic en **"Omitir"** durante el Paso 2:

1. Usuario queda registrado pero sin credenciales
2. Más adelante, puede acceder a **"Ver/modificar datos"** (función a desarrollar)
3. Seleccionar el usuario
4. Opción: **"Crear Credenciales"** o **"Modificar Credenciales"**

*Esta funcionalidad está pendiente de implementación.*

## Casos de Uso

### Caso 1: Registro Completo en Tiempo Real
- Admin completa todo en una sesión
- Registra usuario
- Inmediatamente crea credenciales
- Usuario puede hacer login

### Caso 2: Registro sin Credenciales
- Admin solo registra el usuario
- Omite la creación de credenciales
- Más tarde (cuando usuario tiene más datos), crea las credenciales

### Caso 3: Credenciales Temporales
- Admin crea credenciales con contraseña temporal
- Usuario accede
- Sistema solicita cambiar contraseña en primer login (función pendiente)

## Base de Datos

### Tabla `usuarios`
```
idUsuario (PRIMARY KEY)  | nomUsuario | matrUsuario | placa1 | placa2
010001                   | Juan Pérez | 12345       | ABC123 | XYZ789
```

### Tabla `login`
```
id (AUTOINCREMENT PRIMARY KEY) | usuario    | contrasena | rol     | id_usuario (FK)
1                              | juan.perez | ***        | usuario | 010001
```

**Relación**: `login.id_usuario` → `usuarios.idUsuario`

## Validaciones de Integridad

1. ✅ No se permite crear credenciales para usuario_id que no existe
2. ✅ No se permite usuario_login duplicado
3. ✅ Rol se asigna automáticamente según tipo de usuario
4. ✅ Validaciones en frontend antes de enviar al backend
5. ✅ Validaciones en backend para mayor seguridad

## Respuestas de Error

| Error | Causa | Solución |
|-------|-------|----------|
| "Se requieren: usuario_login, contrasena, id_usuario" | Faltan campos | Completar todos los campos |
| "Usuario con ID XXX no existe" | usuario_id inválido | Verificar que el usuario fue registrado |
| "El nombre de usuario 'XXX' ya existe" | Duplicado | Usar otro nombre de usuario |
| "Error de integridad" | Problema en BD | Contactar administrador |

## Ventajas de Este Flujo

1. **Flexibilidad**: Admin decide si crear credenciales ahora o después
2. **Control**: Admin controla el nombre de usuario y contraseña
3. **Seguridad**: Credenciales separadas del registro de usuario
4. **Auditoría**: Registro de cuándo se crearon las credenciales
5. **Correcciones**: Fácil de cambiar usuario/contraseña sin afectar datos del usuario

## Próximas Mejoras

- [ ] Opción de cambiar credenciales para usuario existente
- [ ] Opción de deshabilitar/eliminar credenciales
- [ ] Auto-generación de contraseña temporal
- [ ] Envío de credenciales por email
- [ ] Encriptación de contraseñas (hashear con bcrypt)
- [ ] Cambio de contraseña en primer login
- [ ] Recuperación de contraseña olvidada
