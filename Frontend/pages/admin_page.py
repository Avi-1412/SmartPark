import flet as ft
import requests

def admin_view(page: ft.Page, API_URL: str):
    page.clean()
    page.title = "SmartPark - Administrador"
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    salida = ft.Text("", size=14, color=ft.Colors.BLUE_GREY_900, selectable=True)

    def ver_historial(e):
        try:
            r = requests.get(f"{API_URL}/historial")
            data = r.json().get("historial", [])
            if data:
                salida.value = "\n".join(
                    [f"Usuario {h['usuario_id']} | Espacio {h['espacio_asignado']} | Entrada {h['hora_entrada']}" for h in data]
                )
            else:
                salida.value = "Sin registros."
        except Exception as ex:
            salida.value = f"Error: {ex}"
        page.update()

    def placeholder(e):
        salida.value = f"La función '{e.control.text}' aún no está disponible."
        page.update()

    def cerrar_aplicacion(e):
        page.window.close()

    titulo = ft.Text("Panel del Administrador", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    logo = ft.Text("SmartPark", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)

    def ver_datos(e):
        salida.value = ""  # limpia mensajes previos
        page.update()

        try:
            r = requests.get(f"{API_URL}/usuarios")
            usuarios = r.json().get("usuarios", [])

            if not usuarios:
                salida.value = "No hay usuarios registrados."
                page.update()
                return

            # Creamos una tabla visual
            tabla = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID")),
                    ft.DataColumn(ft.Text("Nombre")),
                    ft.DataColumn(ft.Text("Celular")),
                    ft.DataColumn(ft.Text("Matrícula")),
                    ft.DataColumn(ft.Text("Placa")),
                    ft.DataColumn(ft.Text("Marca")),
                    ft.DataColumn(ft.Text("Modelo")),
                    ft.DataColumn(ft.Text("Acciones")),
                ],
                rows=[],
            )

            def editar_usuario(ev, usuario):
                # Campos de edición
                nombre_edit = ft.TextField(value=usuario.get("nombre", ""), label="Nombre")
                celular_edit = ft.TextField(value=usuario.get("celular", ""), label="Celular")
                matricula_edit = ft.TextField(value=str(usuario.get("matricula", "")), label="Matrícula")
                placa1_edit = ft.TextField(value=usuario.get("placa1", ""), label="Placa 1")
                placa2_edit = ft.TextField(value=usuario.get("placa2", ""), label="Placa 2")
                
                mensaje_dialog = ft.Text("", size=12, color=ft.Colors.RED_700)

                def guardar_cambios(_):
                    # Validación básica
                    if not nombre_edit.value.strip():
                        mensaje_dialog.value = "❌ El nombre no puede estar vacío"
                        page.update()
                        return
                    
                    try:
                        # Validar que matrícula sea número si no está vacía
                        if matricula_edit.value.strip():
                            try:
                                int(matricula_edit.value)
                            except ValueError:
                                mensaje_dialog.value = "❌ La matrícula debe ser un número"
                                page.update()
                                return
                        
                        datos_actualizados = {
                            "nombre": nombre_edit.value.strip(),
                            "celular": celular_edit.value.strip(),
                            "matricula": matricula_edit.value.strip(),
                            "placa1": placa1_edit.value.strip(),
                            "placa2": placa2_edit.value.strip(),
                        }
                        r2 = requests.put(
                            f"{API_URL}/usuarios/{usuario['id']}", json=datos_actualizados
                        )
                        resultado = r2.json()
                        
                        if "error" in resultado:
                            mensaje_dialog.value = f"❌ {resultado['error']}"
                        else:
                            mensaje_dialog.value = "✅ Cambios guardados correctamente"
                            # Cerrar después de 1 segundo
                            import time
                            time.sleep(0.5)
                            dialog.open = False
                            page.update()
                            ver_datos(None)  # recarga la tabla
                            return
                    except Exception as ex:
                        mensaje_dialog.value = f"❌ Error: {str(ex)}"
                    page.update()

                dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Text(f"Editar usuario ID {usuario['id']}"),
                    content=ft.Column([
                        nombre_edit, 
                        celular_edit,
                        matricula_edit, 
                        placa1_edit, 
                        placa2_edit,
                        ft.Divider(height=10),
                        mensaje_dialog
                    ]),
                    actions=[
                        ft.TextButton("Guardar", on_click=guardar_cambios),
                        ft.TextButton("Cancelar", on_click=lambda _: cerrar_dialogo()),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )

                def cerrar_dialogo():
                    dialog.open = False
                    page.update()

                if dialog not in page.overlay:
                    page.overlay.append(dialog)

                dialog.open = True
                page.update()

            def eliminar_usuario(ev, usuario):
                """Mostrar diálogo de confirmación para eliminar usuario"""
                def confirmar_eliminar(_):
                    try:
                        r = requests.delete(f"{API_URL}/usuarios/{usuario['id']}")
                        resultado = r.json()
                        
                        if "error" in resultado:
                            salida.value = f"❌ {resultado['error']}"
                        else:
                            salida.value = f"✅ {resultado.get('mensaje', 'Usuario eliminado correctamente')}"
                            # Cerrar diálogo y recargar tabla
                            dialogo_confirmar.open = False
                            page.update()
                            ver_datos(None)  # recarga la tabla
                            return
                    except Exception as ex:
                        salida.value = f"❌ Error al eliminar: {str(ex)}"
                    
                    page.update()

                dialogo_confirmar = ft.AlertDialog(
                    modal=True,
                    title=ft.Text(f"⚠️ Eliminar usuario ID {usuario['id']}"),
                    content=ft.Text(
                        f"¿Estás seguro de que deseas eliminar a '{usuario.get('nombre', '')}' y todos sus datos asociados?\n\n"
                        f"Esta acción no se puede deshacer.",
                        size=12
                    ),
                    actions=[
                        ft.TextButton("Eliminar", on_click=confirmar_eliminar),
                        ft.TextButton("Cancelar", on_click=lambda _: cerrar_dialogo_confirmar()),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )

                def cerrar_dialogo_confirmar():
                    dialogo_confirmar.open = False
                    page.update()

                if dialogo_confirmar not in page.overlay:
                    page.overlay.append(dialogo_confirmar)

                dialogo_confirmar.open = True
                page.update()

            def registrar_auto(ev, usuario):
                """Registrar un nuevo auto para el usuario"""
                placa_input = ft.TextField(label="Placa *", width=250)
                marca_input = ft.TextField(label="Marca *", width=250)
                modelo_input = ft.TextField(label="Modelo *", width=250)
                mensaje_auto = ft.Text("", size=12, color=ft.Colors.RED_700)

                def guardar_auto(_):
                    # Validación
                    if not placa_input.value.strip():
                        mensaje_auto.value = "❌ La placa es obligatoria"
                        mensaje_auto.color = ft.Colors.RED_700
                        page.update()
                        return
                    
                    if not marca_input.value.strip():
                        mensaje_auto.value = "❌ La marca es obligatoria"
                        mensaje_auto.color = ft.Colors.RED_700
                        page.update()
                        return
                    
                    if not modelo_input.value.strip():
                        mensaje_auto.value = "❌ El modelo es obligatorio"
                        mensaje_auto.color = ft.Colors.RED_700
                        page.update()
                        return
                    
                    try:
                        mensaje_auto.value = "⏳ Registrando auto..."
                        mensaje_auto.color = ft.Colors.BLUE_700
                        page.update()
                        
                        data = {
                            "usuario_id": usuario['id'],
                            "placa": placa_input.value.strip().upper(),
                            "marca": marca_input.value.strip(),
                            "modelo": modelo_input.value.strip(),
                        }
                        
                        r = requests.post(f"{API_URL}/autos", json=data)
                        resultado = r.json()
                        
                        if "error" in resultado:
                            mensaje_auto.value = f"❌ {resultado['error']}"
                            mensaje_auto.color = ft.Colors.RED_700
                        else:
                            mensaje_auto.value = "✅ Auto registrado correctamente"
                            mensaje_auto.color = ft.Colors.GREEN_700
                            page.update()
                            
                            import time
                            time.sleep(1.5)
                            dialogo_auto.open = False
                            page.update()
                            ver_datos(None)  # recarga la tabla
                            return
                    except Exception as ex:
                        mensaje_auto.value = f"❌ Error: {str(ex)}"
                        mensaje_auto.color = ft.Colors.RED_700
                    
                    page.update()

                dialogo_auto = ft.AlertDialog(
                    modal=True,
                    title=ft.Text(f"Registrar Auto - Usuario {usuario['id']} ({usuario.get('nombre', '')})"),
                    content=ft.Column([
                        ft.Text("* Campos obligatorios", size=11, color=ft.Colors.ORANGE_700),
                        ft.Divider(height=5),
                        placa_input,
                        marca_input,
                        modelo_input,
                        ft.Divider(height=10),
                        mensaje_auto,
                    ], scroll=ft.ScrollMode.AUTO, tight=True),
                    actions=[
                        ft.TextButton("Registrar", on_click=guardar_auto),
                        ft.TextButton("Cancelar", on_click=lambda _: cerrar_dialogo_auto()),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )

                def cerrar_dialogo_auto():
                    dialogo_auto.open = False
                    page.update()

                if dialogo_auto not in page.overlay:
                    page.overlay.append(dialogo_auto)

                dialogo_auto.open = True
                page.update()
            for u in usuarios:
                autos = u.get("autos", [])
                
                if autos:
                    # Si hay vehículos, mostrar una fila por vehículo CON datos del usuario en cada fila
                    for idx, auto in enumerate(autos):
                        placa = auto.get("placa", "")
                        tabla.rows.append(
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text(str(u["id"]))),
                                    ft.DataCell(ft.Text(u.get("nombre", ""))),
                                    ft.DataCell(ft.Text(u.get("celular", ""))),
                                    ft.DataCell(ft.Text(str(u.get("matricula", "")))),
                                    ft.DataCell(ft.Text(placa)),
                                    ft.DataCell(ft.Text(auto.get("marca", ""))),
                                    ft.DataCell(ft.Text(auto.get("modelo", ""))),
                                    ft.DataCell(
                                        ft.Row([
                                            ft.ElevatedButton(
                                                "Editar",
                                                on_click=lambda ev, user=u: editar_usuario(ev, user),
                                                bgcolor=ft.Colors.BLUE_900,
                                                color=ft.Colors.WHITE,
                                                width=80,
                                                height=35
                                            ),
                                            ft.ElevatedButton(
                                                "Auto+",
                                                on_click=lambda ev, user=u: registrar_auto(ev, user),
                                                bgcolor=ft.Colors.GREEN_700,
                                                color=ft.Colors.WHITE,
                                                width=70,
                                                height=35,
                                                tooltip="Registrar nuevo auto"
                                            ),
                                            ft.IconButton(
                                                ft.Icons.DELETE,
                                                icon_color=ft.Colors.RED_700,
                                                tooltip="Eliminar usuario",
                                                on_click=lambda ev, user=u: eliminar_usuario(ev, user),
                                            )
                                        ], spacing=5) if idx == 0 else ft.Text("")
                                    ),
                                ]
                            )
                        )
                else:
                    # Si no hay vehículos, mostrar una fila sin datos de auto
                    tabla.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(u["id"]))),
                                ft.DataCell(ft.Text(u.get("nombre", ""))),
                                ft.DataCell(ft.Text(u.get("celular", ""))),
                                ft.DataCell(ft.Text(str(u.get("matricula", "")))),
                                ft.DataCell(ft.Text("—")),
                                ft.DataCell(ft.Text("—")),
                                ft.DataCell(ft.Text("—")),
                                ft.DataCell(
                                    ft.Row([
                                        ft.ElevatedButton(
                                            "Editar",
                                            on_click=lambda ev, user=u: editar_usuario(ev, user),
                                            bgcolor=ft.Colors.BLUE_900,
                                            color=ft.Colors.WHITE,
                                            width=80,
                                            height=35
                                        ),
                                        ft.ElevatedButton(
                                            "Auto+",
                                            on_click=lambda ev, user=u: registrar_auto(ev, user),
                                            bgcolor=ft.Colors.GREEN_700,
                                            color=ft.Colors.WHITE,
                                            width=70,
                                            height=35,
                                            tooltip="Registrar nuevo auto"
                                        ),
                                        ft.IconButton(
                                            ft.Icons.DELETE,
                                            icon_color=ft.Colors.RED_700,
                                            tooltip="Eliminar usuario",
                                            on_click=lambda ev, user=u: eliminar_usuario(ev, user),
                                        )
                                    ], spacing=5)
                                ),
                            ]
                        )
                    )

            # Mostrar la tabla
            page.clean()
            
            panel = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.ElevatedButton("VOLVER", on_click=lambda _: admin_view(page, API_URL), 
                                         bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=100, height=40),
                        ft.Text("VER/MODIFICAR USUARIOS", size=18, weight=ft.FontWeight.BOLD, 
                               color=ft.Colors.BLUE_900, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Container(width=100),
                    ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=15),
                    ft.Container(content=tabla, expand=True),
                    ft.Container(salida, expand=True),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, 
                   expand=True, scroll=ft.ScrollMode.AUTO),
                padding=20, expand=True, bgcolor=ft.Colors.GREY_200,
                border_radius=6, shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
            )
            page.add(panel)

        except Exception as ex:
            salida.value = f"❌ Error al obtener datos: {ex}"
            page.update()


    def crear_credenciales_para_usuario(usuario_id, nombre_usuario, tipo_id):
        """Diálogo para crear credenciales de login para el usuario recién registrado"""
        
        # Generar nombre de usuario sugerido (formato: nombre.apellido)
        nombres = nombre_usuario.split()
        nombre_sugerido = ""
        if len(nombres) >= 2:
            nombre_sugerido = f"{nombres[0].lower()}.{nombres[-1].lower()}"
        else:
            nombre_sugerido = nombres[0].lower() if nombres else ""
        
        usuario_login = ft.TextField(label="Nombre de usuario para login *", value=nombre_sugerido, width=250)
        contrasena = ft.TextField(label="Contraseña *", password=True, width=250)
        confirmar_contrasena = ft.TextField(label="Confirmar contraseña *", password=True, width=250)
        
        # Determinar rol según tipo_usuario
        rol_map = {"1": "usuario", "2": "admin", "3": "vigilante"}
        rol = rol_map.get(tipo_id, "usuario")
        
        mensaje_dialogo = ft.Text("", size=12)
        
        def cerrar_dialogo_cred(ev=None):
            dialog_cred.open = False
            page.update()
        
        def guardar_credenciales(ev):
            usuario_login_val = usuario_login.value.strip()
            contrasena_val = contrasena.value.strip()
            confirmar_val = confirmar_contrasena.value.strip()
            
            # Validaciones
            if not usuario_login_val:
                mensaje_dialogo.value = "❌ El nombre de usuario no puede estar vacío"
                mensaje_dialogo.color = ft.Colors.RED_700
                page.update()
                return
            
            if not contrasena_val:
                mensaje_dialogo.value = "❌ La contraseña no puede estar vacía"
                mensaje_dialogo.color = ft.Colors.RED_700
                page.update()
                return
            
            if contrasena_val != confirmar_val:
                mensaje_dialogo.value = "❌ Las contraseñas no coinciden"
                mensaje_dialogo.color = ft.Colors.RED_700
                page.update()
                return
            
            try:
                mensaje_dialogo.value = "⏳ Creando credenciales..."
                mensaje_dialogo.color = ft.Colors.BLUE_700
                page.update()
                
                data = {
                    "usuario_login": usuario_login_val,
                    "contrasena": contrasena_val,
                    "rol": rol,
                    "id_usuario": usuario_id
                }
                
                r = requests.post(f"{API_URL}/login/crear", json=data)
                resultado = r.json()
                
                if "error" in resultado:
                    mensaje_dialogo.value = f"❌ {resultado['error']}"
                    mensaje_dialogo.color = ft.Colors.RED_700
                else:
                    mensaje_dialogo.value = f"✅ Credenciales creadas: {resultado['usuario']} / {rol}"
                    mensaje_dialogo.color = ft.Colors.GREEN_700
                    page.update()
                    
                    import time
                    time.sleep(2)
                    dialog_cred.open = False
                    page.update()
                    return
                
            except Exception as ex:
                mensaje_dialogo.value = f"❌ Error: {str(ex)}"
                mensaje_dialogo.color = ft.Colors.RED_700
            
            page.update()
        
        dialog_cred = ft.AlertDialog(
            modal=True,
            title=ft.Text("Crear credenciales de acceso"),
            content=ft.Column(
                [
                    ft.Text(f"Usuario: {nombre_usuario} (ID: {usuario_id})", size=12, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=10),
                    ft.Text("* Campos obligatorios", size=11, color=ft.Colors.ORANGE_700),
                    usuario_login,
                    contrasena,
                    confirmar_contrasena,
                    ft.Divider(height=10),
                    mensaje_dialogo
                ],
                scroll=ft.ScrollMode.AUTO,
                tight=True,
            ),
            actions=[
                ft.TextButton("Crear", on_click=guardar_credenciales),
                ft.TextButton("Omitir", on_click=cerrar_dialogo_cred),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        if dialog_cred not in page.overlay:
            page.overlay.append(dialog_cred)
        
        dialog_cred.open = True
        page.update()

    def registrar_usuario(e):
        page.clean()
        
        # Campos del formulario (consistentes con los datos de usuarios)
        tipo_usuario = ft.Dropdown(
            label="Tipo de usuario *",
            options=[
                ft.dropdown.Option("1", "Alumno"),
                ft.dropdown.Option("2", "Administrativo"),
                ft.dropdown.Option("3", "Externo"),
            ],
            width=300,
        )
        nombre = ft.TextField(label="Nombre completo *", width=300)
        matricula = ft.TextField(label="Matrícula (números, si aplica)", width=300)
        celular = ft.TextField(label="Celular *", width=300)
        vigencia = ft.TextField(label="Vigencia (YYYY-MM-DD) *", width=300, value="2025-12-31")
        pago = ft.Dropdown(
            label="Estado de Pago (puede modificarse después) *",
            options=[
                ft.dropdown.Option("1", "Pagado"),
                ft.dropdown.Option("0", "No Pagado"),
            ],
            width=300,
            value="1"
        )
        
        mensaje_registro = ft.Text("", size=12, color=ft.Colors.RED_700)

        # Función para validar fecha
        def validar_fecha(fecha_str):
            """Valida que el formato sea YYYY-MM-DD"""
            if not fecha_str:
                return False
            try:
                partes = fecha_str.split("-")
                if len(partes) != 3:
                    return False
                año, mes, día = partes
                if len(año) != 4 or len(mes) != 2 or len(día) != 2:
                    return False
                int(año), int(mes), int(día)
                if not (1 <= int(mes) <= 12 and 1 <= int(día) <= 31):
                    return False
                return True
            except:
                return False

        # Función para validar celular
        def validar_celular(tel):
            """Valida que el celular sea números (al menos 7 dígitos)"""
            if not tel.strip():
                return False  # Obligatorio
            return tel.replace("+", "").replace(" ", "").replace("-", "").isdigit() and len(tel.replace("+", "").replace(" ", "").replace("-", "")) >= 7

        # Función para enviar los datos
        def enviar_datos(_):
            # Validación básica
            if not tipo_usuario.value:
                mensaje_registro.value = "❌ Selecciona un tipo de usuario"
                mensaje_registro.color = ft.Colors.RED_700
                page.update()
                return
            
            if not nombre.value.strip():
                mensaje_registro.value = "❌ El nombre no puede estar vacío"
                mensaje_registro.color = ft.Colors.RED_700
                page.update()
                return
            
            if not celular.value.strip():
                mensaje_registro.value = "❌ El celular es obligatorio"
                mensaje_registro.color = ft.Colors.RED_700
                page.update()
                return
            
            # Validar celular
            if not validar_celular(celular.value.strip()):
                mensaje_registro.value = "❌ Celular inválido (mínimo 7 dígitos)"
                mensaje_registro.color = ft.Colors.RED_700
                page.update()
                return
            
            # Validar vigencia
            if not validar_fecha(vigencia.value.strip()):
                mensaje_registro.value = "❌ Vigencia: usa formato YYYY-MM-DD (ej: 2025-12-31)"
                mensaje_registro.color = ft.Colors.RED_700
                page.update()
                return
            
            # Validar matrícula si se proporciona
            if matricula.value.strip() and not matricula.value.strip().isdigit():
                mensaje_registro.value = "❌ La matrícula debe contener solo números"
                mensaje_registro.color = ft.Colors.RED_700
                page.update()
                return
            
            try:
                mensaje_registro.value = "⏳ Registrando usuario..."
                mensaje_registro.color = ft.Colors.BLUE_700
                btn_registrar.disabled = True
                page.update()
                
                data = {
                    "tipo_id": tipo_usuario.value,
                    "nombre": nombre.value.strip(),
                    "matricula": matricula.value.strip() or "N/A",
                    "celular": celular.value.strip(),
                    "vigencia": vigencia.value.strip(),
                    "pago": int(pago.value or 0),
                }
                r = requests.post(f"{API_URL}/usuarios", json=data)
                resultado = r.json()
                
                if "error" in resultado:
                    mensaje_registro.value = f"❌ {resultado['error']}"
                    mensaje_registro.color = ft.Colors.RED_700
                    btn_registrar.disabled = False
                elif "mensaje" in resultado or "idUsuario" in resultado:
                    # Usuario registrado con éxito, obtener ID del usuario
                    usuario_id = resultado.get("idUsuario")
                    mensaje_registro.value = f"✅ Usuario registrado correctamente"
                    mensaje_registro.color = ft.Colors.GREEN_700
                    btn_registrar.disabled = True
                    page.update()
                    
                    import time
                    time.sleep(2)
                    
                    # Limpiar los campos del formulario
                    tipo_usuario.value = None
                    nombre.value = ""
                    matricula.value = ""
                    celular.value = ""
                    vigencia.value = "2025-12-31"
                    pago.value = "1"
                    mensaje_registro.value = ""
                    btn_registrar.disabled = False
                    page.update()
                    
                    # Mostrar diálogo para crear credenciales si tenemos el ID
                    if usuario_id:
                        crear_credenciales_para_usuario(usuario_id, nombre.value.strip(), tipo_usuario.value)
                    else:
                        # Si no tenemos ID, volver al menú admin
                        admin_view(page, API_URL)
                    return
                else:
                    mensaje_registro.value = "❌ Error al registrar usuario"
                    mensaje_registro.color = ft.Colors.RED_700
                    btn_registrar.disabled = False
                    
            except Exception as ex:
                mensaje_registro.value = f"❌ Error: {str(ex)}"
                mensaje_registro.color = ft.Colors.RED_700
                btn_registrar.disabled = False
            
            page.update()

        btn_registrar = ft.ElevatedButton(
            "REGISTRAR USUARIO",
            on_click=enviar_datos,
            disabled=False,
            height=45,
            width=300,
            bgcolor=ft.Colors.BLUE_900,
            color=ft.Colors.WHITE
        )
        
        panel = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.ElevatedButton("VOLVER", on_click=lambda _: admin_view(page, API_URL), 
                                     bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=100, height=40),
                    ft.Text("REGISTRAR NUEVO USUARIO", size=18, weight=ft.FontWeight.BOLD, 
                           color=ft.Colors.BLUE_900, expand=True, text_align=ft.TextAlign.CENTER),
                    ft.Container(width=100),
                ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=15),
                ft.Column([
                    ft.Text("* Campos obligatorios", size=11, color=ft.Colors.ORANGE_700),
                    ft.Divider(height=10),
                    tipo_usuario,
                    nombre,
                    celular,
                    matricula,
                    vigencia,
                    pago,
                    ft.Divider(height=10),
                    ft.Container(btn_registrar, alignment=ft.alignment.center),
                    ft.Divider(height=10),
                    mensaje_registro,
                ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
               expand=True, scroll=ft.ScrollMode.AUTO),
            padding=20, expand=True, bgcolor=ft.Colors.GREY_200,
            border_radius=6, shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
        )
        page.add(panel)

    def ver_reportes(e):
        """Muestra advertencias y multas del sistema"""
        page.clean()

        try:
            # Obtener todas las multas
            r = requests.get(f"{API_URL}/multas")
            multas_data = r.json().get("multas", [])
            
            if not multas_data:
                page.clean()
                panel = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.ElevatedButton("VOLVER", on_click=lambda _: admin_view(page, API_URL), 
                                             bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=100, height=40),
                            ft.Text("REPORTES DE MULTAS", size=18, weight=ft.FontWeight.BOLD, 
                                   color=ft.Colors.BLUE_900, expand=True, text_align=ft.TextAlign.CENTER),
                            ft.Container(width=100),
                        ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Divider(height=15),
                        ft.Column([
                            ft.Text("No hay multas registradas", size=14, color=ft.Colors.BLUE_GREY_700),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20, expand=True, bgcolor=ft.Colors.GREY_200,
                    border_radius=6, shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
                )
                page.add(panel)
                return
            
            # Crear tabla de multas
            tabla = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Usuario ID")),
                    ft.DataColumn(ft.Text("Nombre")),
                    ft.DataColumn(ft.Text("Fecha")),
                    ft.DataColumn(ft.Text("Concepto")),
                    ft.DataColumn(ft.Text("Monto")),
                    ft.DataColumn(ft.Text("Pagado")),
                ],
                rows=[],
            )
            
            for multa in multas_data:
                estado = "✅ SÍ" if multa.get("pagado") else "❌ NO"
                tabla.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(multa.get("id_usuario", "")))),
                            ft.DataCell(ft.Text(multa.get("usuario", ""))),
                            ft.DataCell(ft.Text(str(multa.get("fecha", ""))[:10])),
                            ft.DataCell(ft.Text(multa.get("concepto", ""))),
                            ft.DataCell(ft.Text(f"${multa.get('monto', 0)}")),
                            ft.DataCell(ft.Text(estado)),
                        ]
                    )
                )
            
            panel = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.ElevatedButton("VOLVER", on_click=lambda _: admin_view(page, API_URL), 
                                         bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=100, height=40),
                        ft.Text("REPORTES DE MULTAS", size=18, weight=ft.FontWeight.BOLD, 
                               color=ft.Colors.BLUE_900, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Container(width=100),
                    ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=15),
                    ft.Container(content=tabla, expand=True),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, 
                   expand=True, scroll=ft.ScrollMode.AUTO),
                padding=20, expand=True, bgcolor=ft.Colors.GREY_200,
                border_radius=6, shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
            )
            page.add(panel)
            
        except Exception as ex:
            page.clean()
            panel = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.ElevatedButton("VOLVER", on_click=lambda _: admin_view(page, API_URL), 
                                         bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=100, height=40),
                        ft.Text("REPORTES DE MULTAS", size=18, weight=ft.FontWeight.BOLD, 
                               color=ft.Colors.BLUE_900, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Container(width=100),
                    ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=15),
                    ft.Column([
                        ft.Text("Error", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700),
                        ft.Text(f"❌ {ex}", size=13, color=ft.Colors.RED_600),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20, expand=True, bgcolor=ft.Colors.GREY_200,
                border_radius=6, shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
            )
            page.add(panel)

    botones = [
        ft.ElevatedButton("VER/MODIFICAR DATOS DE USUARIO", on_click=ver_datos, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, expand=True, height=45, width=250),
        ft.ElevatedButton("REGISTRAR USUARIOS", on_click=registrar_usuario, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, expand=True, height=45, width=250),
        ft.ElevatedButton("VER REPORTES", on_click=ver_reportes, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, expand=True, height=45, width=250),
        ft.ElevatedButton("AJUSTES DE APLICACION", on_click=placeholder, bgcolor=ft.Colors.BLUE_GREY_700, color=ft.Colors.WHITE, expand=True, height=45, width=250),
        ft.ElevatedButton("CERRAR APLICACION", on_click=cerrar_aplicacion, bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE, expand=True, height=45, width=250),
    ]

    panel = ft.Container(
        content=ft.Column(
            [logo, titulo, ft.Divider(height=15, color=ft.Colors.TRANSPARENT)] + botones + [ft.Divider(height=15, color=ft.Colors.TRANSPARENT), salida],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        padding=40,
        width=500,
        bgcolor=ft.Colors.GREY_200,
        border_radius=6,
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
    )

    page.add(panel)
