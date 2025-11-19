import flet as ft
import requests

def vigilante_view(page: ft.Page, API_URL: str):
    page.clean()
    page.title = "SmartPark - Vigilante"
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    salida = ft.Text("", size=14, color=ft.Colors.BLUE_GREY_900, selectable=True)
    
    # Contenedor para notificaciones en esquina
    notificaciones_container = ft.Column(
        controls=[],
        alignment=ft.MainAxisAlignment.START,
        spacing=10
    )

    # =====================================================
    # FUNCIONES DE NOTIFICACIONES
    # =====================================================
    
    def mostrar_notificacion(titulo, mensaje, tipo="info", duracion=5000):
        """Muestra una notificación flotante en la esquina superior derecha"""
        import threading
        import time
        
        # Color según tipo
        colores = {
            "exito": ft.Colors.GREEN_700,
            "error": ft.Colors.RED_700,
            "alerta": ft.Colors.ORANGE_700,
            "info": ft.Colors.BLUE_700
        }
        
        bgcolor = colores.get(tipo, ft.Colors.BLUE_700)
        icono = {"exito": "✅", "error": "❌", "alerta": "⚠️", "info": "ℹ️"}.get(tipo, "ℹ️")
        
        # Crear notificación
        notif = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"{icono} {titulo}", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, size=12),
                    ft.IconButton(
                        ft.icons.CLOSE,
                        icon_size=16,
                        icon_color=ft.Colors.WHITE,
                        on_click=lambda _: remover_notif()
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text(mensaje, color=ft.Colors.WHITE, size=11)
            ], spacing=5),
            padding=15,
            bgcolor=bgcolor,
            border_radius=8,
            width=320,
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK26),
        )
        
        def remover_notif():
            if notif in notificaciones_container.controls:
                notificaciones_container.controls.remove(notif)
            page.update()
        
        # Agregar a contenedor
        notificaciones_container.controls.append(notif)
        page.update()
        
        # Desaparecer automáticamente
        def auto_remove():
            time.sleep(duracion / 1000)
            remover_notif()
        
        threading.Thread(target=auto_remove, daemon=True).start()
    
    # =====================================================
    # MONITOR DE ALERTAS EN TIEMPO REAL
    # =====================================================
    
    # =====================================================
    # FUNCIONES PRINCIPALES
    # =====================================================
    
    def placeholder(e):
        salida.value = f"La función '{e.control.text}' aún no está disponible."
        page.update()

    def cerrar_aplicacion(e):
        page.window.close()

    def ver_datos_usuarios(e):
        """Ver tabla de todos los usuarios con botón para ver historial"""
        page.clean()  # Limpiar página primero
        
        try:
            r = requests.get(f"{API_URL}/usuarios")
            usuarios = r.json().get("usuarios", [])

            if not usuarios:
                salida.value = "No hay usuarios registrados."
                page.update()
                return

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

            def ver_historial_usuario_btn(ev, user_id):
                """Ver historial de un usuario específico"""
                try:
                    r = requests.get(f"{API_URL}/historial/usuario/{user_id}")
                    
                    if r.status_code == 200:
                        historial = r.json().get("historial", [])
                        
                        if not historial:
                            # Mostrar mensaje en diálogo
                            dialog_sin_datos = ft.AlertDialog(
                                modal=True,
                                title=ft.Text(f"Historial - Usuario {user_id}", size=16, weight=ft.FontWeight.BOLD),
                                content=ft.Text(f"No hay historial disponible para este usuario", size=14),
                            )
                            
                            def cerrar_dialog_sin_datos(_):
                                dialog_sin_datos.open = False
                                page.update()
                            
                            btn_cerrar = ft.TextButton("Cerrar", on_click=cerrar_dialog_sin_datos)
                            dialog_sin_datos.actions = [btn_cerrar]
                            
                            if dialog_sin_datos not in page.overlay:
                                page.overlay.append(dialog_sin_datos)
                            
                            dialog_sin_datos.open = True
                            page.update()
                            return
                        
                        tabla_historial = ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text("ID")),
                                ft.DataColumn(ft.Text("Tipo")),
                                ft.DataColumn(ft.Text("Espacio")),
                                ft.DataColumn(ft.Text("Entrada")),
                                ft.DataColumn(ft.Text("Salida")),
                                ft.DataColumn(ft.Text("OK")),
                            ],
                            rows=[],
                            vertical_lines=ft.BorderSide(1, ft.Colors.BLUE_GREY_200),
                            horizontal_lines=ft.BorderSide(1, ft.Colors.BLUE_GREY_200),
                        )
                        
                        for h in historial:
                            estado = "✅" if h.get("valido") else "❌"
                            entrada = str(h.get("hora_entrada", h.get("fecha_entrada", "")))[:19]
                            salida_h = str(h.get("hora_salida", ""))[:19] if h.get("hora_salida") else "—"
                            tipo = h.get("tipo", "automático")
                            tipo_badge = "🔵 Auto" if tipo == "automático" else "🟡 Manual"
                            
                            tabla_historial.rows.append(
                                ft.DataRow(
                                    cells=[
                                        ft.DataCell(ft.Text(str(h.get("historial_id", h.get("idHis", ""))), size=11)),
                                        ft.DataCell(ft.Text(tipo_badge, size=10)),
                                        ft.DataCell(ft.Text(str(h.get("espacio_asignado", "")), size=11)),
                                        ft.DataCell(ft.Text(entrada, size=10)),
                                        ft.DataCell(ft.Text(salida_h, size=10)),
                                        ft.DataCell(ft.Text(estado, size=11)),
                                    ]
                                )
                            )
                        
                        # Crear diálogo con scroll
                        dialog = ft.AlertDialog(
                            modal=True,
                            title=ft.Text(f"Historial Completo - Usuario {user_id}", size=16, weight=ft.FontWeight.BOLD),
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text("🔵 = Automático | 🟡 = Manual", size=11, color=ft.Colors.BLUE_GREY_700),
                                    ft.Divider(height=5),
                                    tabla_historial,
                                ], scroll=ft.ScrollMode.AUTO),
                                width=800,
                                height=480,
                            ),
                        )
                        
                        def cerrar_dialog(_):
                            dialog.open = False
                            page.update()
                        
                        btn_cerrar = ft.TextButton("Cerrar", on_click=cerrar_dialog)
                        dialog.actions = [btn_cerrar]
                        
                        # Mostrar el diálogo
                        if dialog not in page.overlay:
                            page.overlay.append(dialog)
                        
                        dialog.open = True
                        page.update()
                    else:
                        salida.value = f"Error en API: {r.status_code}"
                        page.update()
                except Exception as ex:
                    salida.value = f"❌ Error: {str(ex)}"
                    page.update()

            # Limpiar página ANTES de construir todo
            page.clean()
            
            # Ahora construir la tabla
            for u in usuarios:
                autos = u.get("autos", [])
                user_id = u.get("id", u.get("idUsuario", ""))
                user_nombre = u.get("nombre", u.get("nomUsuario", ""))
                user_matricula = u.get("matricula", u.get("matrUsuario", ""))
                
                if autos:
                    for idx, auto in enumerate(autos):
                        placa = auto.get("placa", "")
                        tabla.rows.append(
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text(str(user_id))),
                                    ft.DataCell(ft.Text(user_nombre)),
                                    ft.DataCell(ft.Text(u.get("celular", ""))),
                                    ft.DataCell(ft.Text(str(user_matricula))),
                                    ft.DataCell(ft.Text(placa)),
                                    ft.DataCell(ft.Text(auto.get("marca", ""))),
                                    ft.DataCell(ft.Text(auto.get("modelo", ""))),
                                    ft.DataCell(
                                        ft.Row([
                                            ft.ElevatedButton(
                                                "Ver Historial",
                                                on_click=lambda ev, uid=user_id: ver_historial_usuario_btn(ev, uid),
                                                bgcolor=ft.Colors.BLUE_900,
                                                color=ft.Colors.WHITE,
                                                width=120,
                                                height=35
                                            )
                                        ], spacing=5) if idx == 0 else ft.Text("")
                                    ),
                                ]
                            )
                        )
                else:
                    tabla.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(user_id))),
                                ft.DataCell(ft.Text(user_nombre)),
                                ft.DataCell(ft.Text(u.get("celular", ""))),
                                ft.DataCell(ft.Text(str(user_matricula))),
                                ft.DataCell(ft.Text("—")),
                                ft.DataCell(ft.Text("—")),
                                ft.DataCell(ft.Text("—")),
                                ft.DataCell(
                                    ft.Row([
                                        ft.ElevatedButton(
                                            "Ver Historial",
                                            on_click=lambda ev, uid=user_id: ver_historial_usuario_btn(ev, uid),
                                            bgcolor=ft.Colors.BLUE_900,
                                            color=ft.Colors.WHITE,
                                            width=120,
                                            height=35
                                        )
                                    ], spacing=5)
                                ),
                            ]
                        )
                    )
            
            panel = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.ElevatedButton("VOLVER", on_click=lambda _: vigilante_view(page, API_URL), bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=100, height=40),
                        ft.Text("DATOS DE USUARIOS", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Container(width=100),
                    ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=15),
                    ft.Container(content=tabla, expand=True),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, expand=True, scroll=ft.ScrollMode.AUTO),
                padding=20,
                expand=True,
                bgcolor=ft.Colors.GREY_200,
                border_radius=6,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
            )
            page.add(panel)

        except Exception as ex:
            salida.value = f"Error: {ex}"
            page.update()

    def registrar_acceso_manual(tipo):
        """Registrar entrada o salida manual"""
        page.clean()
        
        id_input = ft.TextField(label="ID de usuario", width=300, keyboard_type=ft.KeyboardType.NUMBER)
        
        nombre_display = ft.Text("", size=13, weight=ft.FontWeight.BOLD)
        celular_display = ft.Text("", size=12)
        vehiculos_display = ft.Text("", size=12)
        usos_restantes = ft.Text("", size=12)
        estado_entrada = ft.Text("", size=12, weight=ft.FontWeight.BOLD)
        resultado = ft.Text("", size=12, weight=ft.FontWeight.BOLD)
        btn_registrar = ft.ElevatedButton(f"REGISTRAR {tipo.upper()}", disabled=True, height=45, width=300, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE)
        
        contenedor_datos = ft.Container(
            content=ft.Column([
                nombre_display,
                celular_display,
                vehiculos_display,
                usos_restantes,
                estado_entrada,
            ], spacing=8),
            visible=False,
            bgcolor=ft.Colors.BLUE_GREY_100,
            padding=15,
            border_radius=8
        )

        def buscar_usuario(_):
            """Busca el usuario en la BD"""
            user_id = id_input.value.strip()
            resultado.value = ""
            btn_registrar.disabled = True
            contenedor_datos.visible = False
            
            if not user_id or not user_id.isdigit():
                resultado.value = "Ingresa un ID válido"
                page.update()
                return
            
            try:
                r = requests.get(f"{API_URL}/usuarios/{user_id}", timeout=5)
                if r.status_code != 200:
                    resultado.value = "Usuario no encontrado"
                    page.update()
                    return
                
                usuario = r.json()
                nombre_display.value = f"Nombre: {usuario.get('nomUsuario', 'N/A')}"
                celular_display.value = f"Celular: {usuario.get('celular', 'N/A')}"
                
                autos = usuario.get("autos", [])
                autos_text = ", ".join([f"{a.get('marca')} {a.get('modelo')}" for a in autos]) if autos else "Sin registrar"
                vehiculos_display.value = f"Vehículos: {autos_text}"
                
                r_accesos = requests.get(f"{API_URL}/acceso/manuales/{user_id}", timeout=5)
                data_accesos = r_accesos.json()
                
                r_entrada_activa = requests.get(f"{API_URL}/acceso/manuales/{user_id}/activa", timeout=5)
                data_activa = r_entrada_activa.json()
                entrada_activa = data_activa.get("entrada_activa", False)
                
                if tipo == "entrada":
                    if entrada_activa:
                        estado_entrada.value = "Entrada activa sin salida registrada"
                        resultado.value = "Debe registrar salida primero"
                        btn_registrar.disabled = True
                    else:
                        usos = data_accesos.get("usos_mes", 0)
                        limite = data_accesos.get("limite", 3)
                        usos_restantes.value = f"Entradas manuales: {usos}/{limite} usadas este mes"
                        if usos >= limite:
                            resultado.value = f"Límite de {limite} entradas alcanzado"
                            btn_registrar.disabled = True
                        else:
                            resultado.value = f"Usuario verificado. Accesos restantes: {limite - usos}"
                            btn_registrar.disabled = False
                else:
                    if not entrada_activa:
                        estado_entrada.value = "No hay entrada activa"
                        resultado.value = "No se puede registrar salida sin entrada"
                        btn_registrar.disabled = True
                    else:
                        estado_entrada.value = "Entrada activa disponible"
                        resultado.value = "Usuario verificado"
                        btn_registrar.disabled = False
                
                contenedor_datos.visible = True
            except Exception as ex:
                resultado.value = f"Error: {ex}"
            
            page.update()

        def registrar(_):
            """Registra entrada o salida"""
            user_id = id_input.value.strip()
            if not user_id:
                resultado.value = "Verifica usuario primero"
                page.update()
                return
            
            try:
                r = requests.post(f"{API_URL}/acceso/manual/{tipo}", json={"id_usuario": int(user_id)})
                data = r.json()
                
                if data.get("success"):
                    resultado.value = f"✅ {data.get('mensaje', 'Acceso registrado')}"
                    id_input.value = ""
                    contenedor_datos.visible = False
                else:
                    resultado.value = f"❌ {data.get('mensaje', 'Error')}"
            except Exception as ex:
                resultado.value = f"Error: {ex}"
            page.update()

        id_input.on_change = buscar_usuario
        btn_registrar.on_click = registrar

        panel = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.ElevatedButton("VOLVER", on_click=lambda _: vigilante_view(page, API_URL), bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=100, height=40),
                    ft.Text(f"REGISTRAR {tipo.upper()} MANUAL", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900, expand=True, text_align=ft.TextAlign.CENTER),
                    ft.Container(width=100),
                ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=15),
                ft.Text("ID de usuario:", size=13, weight=ft.FontWeight.BOLD),
                id_input,
                ft.Divider(height=10),
                contenedor_datos,
                ft.Divider(height=10),
                ft.Container(btn_registrar, alignment=ft.alignment.center),
                ft.Divider(height=10),
                ft.Container(resultado, alignment=ft.alignment.center),
            ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True, scroll=ft.ScrollMode.AUTO),
            padding=20,
            expand=True,
            bgcolor=ft.Colors.GREY_200,
            border_radius=6,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
        )
        
        page.add(panel)

    def enviar_advertencia(e):
        """Enviar advertencia a un usuario"""
        page.clean()
        
        id_input = ft.TextField(label="ID de usuario", width=300, keyboard_type=ft.KeyboardType.NUMBER)
        id_historial_input = ft.TextField(label="ID de entrada (historial)", width=300, keyboard_type=ft.KeyboardType.NUMBER)
        
        nombre_display = ft.Text("", size=13, weight=ft.FontWeight.BOLD)
        advertencias_display = ft.Text("", size=12, weight=ft.FontWeight.BOLD)
        ids_disponibles = ft.Text("", size=11)
        resultado = ft.Text("", size=12, weight=ft.FontWeight.BOLD)
        btn_enviar = ft.ElevatedButton("ENVIAR ADVERTENCIA", disabled=True, height=45, width=300, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE)
        
        contenedor_datos = ft.Container(
            content=ft.Column([
                nombre_display,
                ids_disponibles,
                advertencias_display,
            ], spacing=8),
            visible=False,
            bgcolor=ft.Colors.BLUE_GREY_100,
            padding=15,
            border_radius=8
        )

        def buscar_usuario_y_entrada(_):
            """Valida usuario e entrada"""
            user_id = id_input.value.strip()
            id_hist = id_historial_input.value.strip()
            resultado.value = ""
            btn_enviar.disabled = True
            contenedor_datos.visible = False
            
            if not user_id or not user_id.isdigit() or not id_hist or not id_hist.isdigit():
                resultado.value = "Completa ID usuario e ID entrada"
                page.update()
                return
            
            try:
                r = requests.get(f"{API_URL}/usuarios/{user_id}", timeout=5)
                if r.status_code != 200:
                    resultado.value = "Usuario no encontrado"
                    page.update()
                    return
                
                usuario = r.json()
                
                # Validar entrada
                r_historial = requests.get(f"{API_URL}/historial/validar/{user_id}/{id_hist}", timeout=5)
                data_historial = r_historial.json()
                
                if not data_historial.get("valido"):
                    resultado.value = f"Entrada no válida"
                    page.update()
                    return
                
                nombre_display.value = f"Usuario: {usuario.get('nomUsuario', 'N/A')}"
                
                r_adv = requests.get(f"{API_URL}/advertencias/entrada/{user_id}/{id_hist}", timeout=5)
                data_adv = r_adv.json()
                adv_entrada = data_adv.get("advertencias", 0)
                advertencias_display.value = f"Advertencias en esta entrada: {adv_entrada}/3"
                
                resultado.value = "Usuario y entrada validados"
                btn_enviar.disabled = False
                contenedor_datos.visible = True
                    
            except Exception as ex:
                resultado.value = f"Error: {ex}"
            
            page.update()

        def enviar(_):
            """Envía la advertencia"""
            user_id = id_input.value.strip()
            id_hist = id_historial_input.value.strip()
            if not user_id or not id_hist:
                resultado.value = "Verifica usuario e entrada primero"
                page.update()
                return
            
            try:
                r = requests.post(f"{API_URL}/advertencias", json={
                    "id_usuario": int(user_id), 
                    "id_historial": int(id_hist),
                    "motivo": "Mal estacionado"
                }, timeout=5)
                data = r.json()
                
                if data.get("success"):
                    adv_count = data.get("advertencias_entrada", 0)
                    resultado.value = f"✅ Advertencia enviada ({adv_count}/3)"
                    if adv_count >= 3:
                        resultado.value += " - Puede enviar multa"
                else:
                    resultado.value = f"Error: {data.get('mensaje', 'Error')}"
                    
            except Exception as ex:
                resultado.value = f"Error: {ex}"
            page.update()

        id_input.on_change = buscar_usuario_y_entrada
        id_historial_input.on_change = buscar_usuario_y_entrada
        btn_enviar.on_click = enviar

        panel = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.ElevatedButton("VOLVER", on_click=lambda _: vigilante_view(page, API_URL), bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=100, height=40),
                    ft.Text("ENVIAR ADVERTENCIA", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900, expand=True, text_align=ft.TextAlign.CENTER),
                    ft.Container(width=100),
                ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=15),
                ft.Text("ID de usuario:", size=13, weight=ft.FontWeight.BOLD),
                id_input,
                ft.Text("ID de entrada:", size=13, weight=ft.FontWeight.BOLD),
                id_historial_input,
                ft.Divider(height=10),
                contenedor_datos,
                ft.Divider(height=10),
                ft.Container(btn_enviar, alignment=ft.alignment.center),
                ft.Divider(height=10),
                ft.Container(resultado, alignment=ft.alignment.center),
            ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True, scroll=ft.ScrollMode.AUTO),
            padding=20,
            expand=True,
            bgcolor=ft.Colors.GREY_200,
            border_radius=6,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
        )
        
        page.add(panel)

    def enviar_multa(e):
        """Enviar multa a un usuario"""
        page.clean()
        
        id_input = ft.TextField(label="ID de usuario", width=300, keyboard_type=ft.KeyboardType.NUMBER)
        id_historial_input = ft.TextField(label="ID de entrada (historial)", width=300, keyboard_type=ft.KeyboardType.NUMBER)
        monto_input = ft.TextField(label="Monto ($)", width=300, value="50.0", keyboard_type=ft.KeyboardType.NUMBER)
        
        nombre_display = ft.Text("", size=13, weight=ft.FontWeight.BOLD)
        advertencias_display = ft.Text("", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700)
        resultado = ft.Text("", size=12, weight=ft.FontWeight.BOLD)
        btn_enviar = ft.ElevatedButton("ENVIAR MULTA", disabled=True, height=45, width=300, bgcolor=ft.Colors.RED_900, color=ft.Colors.WHITE)
        
        contenedor_datos = ft.Container(
            content=ft.Column([
                nombre_display,
                advertencias_display,
            ], spacing=8),
            visible=False,
            bgcolor=ft.Colors.RED_100,
            padding=15,
            border_radius=8
        )

        def buscar_usuario(_):
            """Verifica usuario y advertencias"""
            user_id = id_input.value.strip()
            id_hist = id_historial_input.value.strip()
            resultado.value = ""
            btn_enviar.disabled = True
            contenedor_datos.visible = False
            
            if not user_id or not user_id.isdigit() or not id_hist or not id_hist.isdigit():
                resultado.value = "Completa ID usuario e ID entrada"
                page.update()
                return
            
            try:
                r = requests.get(f"{API_URL}/usuarios/{user_id}", timeout=5)
                if r.status_code != 200:
                    resultado.value = "Usuario no encontrado"
                    page.update()
                    return
                
                # Validar entrada
                r_historial = requests.get(f"{API_URL}/historial/validar/{user_id}/{id_hist}", timeout=5)
                data_historial = r_historial.json()
                
                if not data_historial.get("valido"):
                    resultado.value = "Entrada no válida"
                    page.update()
                    return
                
                usuario = r.json()
                nombre_display.value = f"Usuario: {usuario.get('nomUsuario', 'N/A')}"
                
                r_adv = requests.get(f"{API_URL}/advertencias/entrada/{user_id}/{id_hist}", timeout=5)
                data_adv = r_adv.json()
                adv_count = data_adv.get("advertencias", 0)
                
                if adv_count < 3:
                    advertencias_display.value = f"Solo {adv_count}/3 advertencias - NO PUEDE MULTAR"
                    btn_enviar.disabled = True
                    resultado.value = "Se requieren 3 advertencias para multar"
                else:
                    advertencias_display.value = f"{adv_count} ADVERTENCIAS - MULTA HABILITADA"
                    btn_enviar.disabled = False
                    resultado.value = "Usuario y entrada validados"
                
                contenedor_datos.visible = True
                    
            except Exception as ex:
                resultado.value = f"Error: {ex}"
            
            page.update()

        def enviar(_):
            """Envía la multa"""
            user_id = id_input.value.strip()
            id_hist = id_historial_input.value.strip()
            if not user_id or not id_hist:
                resultado.value = "Verifica usuario e entrada primero"
                page.update()
                return
            
            try:
                monto = float(monto_input.value) if monto_input.value else 50.0
                r = requests.post(f"{API_URL}/multas", json={
                    "id_usuario": int(user_id),
                    "id_historial": int(id_hist),
                    "concepto": "Mal estacionado",
                    "monto": monto
                }, timeout=5)
                data = r.json()
                
                if data.get("success"):
                    resultado.value = f"✅ Multa de ${monto} registrada"
                    btn_enviar.disabled = True
                else:
                    resultado.value = f"Error: {data.get('mensaje', 'Error')}"
                    
            except ValueError:
                resultado.value = "Monto inválido"
            except Exception as ex:
                resultado.value = f"Error: {ex}"
            page.update()

        id_input.on_change = buscar_usuario
        id_historial_input.on_change = buscar_usuario
        btn_enviar.on_click = enviar

        panel = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.ElevatedButton("VOLVER", on_click=lambda _: vigilante_view(page, API_URL), bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=100, height=40),
                    ft.Text("ENVIAR MULTA", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900, expand=True, text_align=ft.TextAlign.CENTER),
                    ft.Container(width=100),
                ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=15),
                ft.Text("ID de usuario:", size=13, weight=ft.FontWeight.BOLD),
                id_input,
                ft.Text("ID de entrada:", size=13, weight=ft.FontWeight.BOLD),
                id_historial_input,
                ft.Divider(height=10),
                contenedor_datos,
                ft.Divider(height=10),
                ft.Text("Monto de la multa ($):", size=13, weight=ft.FontWeight.BOLD),
                monto_input,
                ft.Divider(height=10),
                ft.Container(btn_enviar, alignment=ft.alignment.center),
                ft.Divider(height=10),
                ft.Container(resultado, alignment=ft.alignment.center),
            ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True, scroll=ft.ScrollMode.AUTO),
            padding=20,
            expand=True,
            bgcolor=ft.Colors.GREY_200,
            border_radius=6,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
        )
        
        page.add(panel)

    def ver_accesos_recientes(e):
        """Ver los últimos accesos registrados en tiempo real"""
        page.clean()
        
        try:
            r = requests.get(f"{API_URL}/accesos-recientes?limite=15")
            if r.status_code == 200:
                accesos = r.json().get("accesos", [])
                
                if not accesos:
                    # Si no hay accesos, mostrar mensaje
                    contenido = ft.Column([
                        ft.Text("No hay accesos registrados", size=14, color=ft.Colors.BLUE_GREY_700),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
                else:
                    tarjetas = []
                    for acceso in accesos:
                        estado = "ACTIVO" if acceso.get("activo") == 1 else "CERRADO"
                        color_estado = ft.Colors.BLUE_600 if acceso.get("activo") == 1 else ft.Colors.GREEN_700
                        
                        tarjeta = ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(f"{acceso.get('nombre_usuario')}", weight=ft.FontWeight.BOLD, size=13),
                                    ft.Text(f"ID: {acceso.get('usuario_id')}", size=11, color=ft.Colors.BLUE_GREY_700),
                                ]),
                                ft.Row([
                                    ft.Text(f"Espacio: {acceso.get('espacio_asignado')}", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                                    ft.Text(estado, size=11, color=color_estado, weight=ft.FontWeight.BOLD),
                                ]),
                                ft.Row([
                                    ft.Text(f"{acceso.get('celular')}", size=10, color=ft.Colors.BLUE_GREY_600),
                                    ft.Text(f"{str(acceso.get('fecha_hora_entrada', ''))[:19]}", size=10, color=ft.Colors.BLUE_GREY_600),
                                ]),
                            ], spacing=5),
                            padding=12,
                            bgcolor=ft.Colors.BLUE_GREY_50,
                            border_radius=6,
                            border=ft.border.all(1, ft.Colors.BLUE_GREY_300),
                        )
                        tarjetas.append(tarjeta)
                    
                    contenido = ft.Column(tarjetas, scroll="adaptive", spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                
                resultado = ft.Text("", size=12, color=ft.Colors.GREEN_700)
                
                def refrescar_accesos(_):
                    ver_accesos_recientes(None)
                
                panel = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.ElevatedButton("VOLVER", on_click=lambda _: vigilante_view(page, API_URL), bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=100, height=40),
                            ft.Text("ACCESOS RECIENTES", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900, expand=True, text_align=ft.TextAlign.CENTER),
                            ft.ElevatedButton("REFRESCAR", on_click=refrescar_accesos, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=120, height=40),
                        ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Divider(height=15),
                        contenido,
                        ft.Divider(height=10),
                        resultado,
                    ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True, scroll=ft.ScrollMode.AUTO),
                    padding=20,
                    expand=True,
                    bgcolor=ft.Colors.GREY_200,
                    border_radius=6,
                    shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
                )
                
                page.add(panel)
            
        except Exception as ex:
            resultado = ft.Text(f"Error: {str(ex)}", size=12, color=ft.Colors.RED_700)

    def ver_alertas_sensores(e):
        """Ver alertas no autorizadas"""
        page.clean()
        
        try:
            r = requests.get(f"{API_URL}/sensores/alertas")
            data = r.json()
            alertas = data.get("alertas", [])
            
            # Crear tabla de alertas
            tabla_alertas = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Espacio", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Hora", weight=ft.FontWeight.BOLD)),
                ],
                rows=[],
                vertical_lines=ft.BorderSide(1, ft.Colors.BLUE_GREY_200),
                horizontal_lines=ft.BorderSide(1, ft.Colors.BLUE_GREY_200),
            )
            
            # Llenar tabla
            for alerta in alertas:
                espacio = alerta.get("espacio", "?")
                estado = "⚠️ Ocupado sin asignación"
                hora = str(alerta.get("fecha", ""))[:19]
                
                tabla_alertas.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(espacio, weight=ft.FontWeight.BOLD, size=14)),
                            ft.DataCell(ft.Text(estado, size=12)),
                            ft.DataCell(ft.Text(hora, size=11)),
                        ]
                    )
                )
            
            def borrar_todas_alertas(_):
                """Borra todas las alertas pendientes"""
                try:
                    for alerta in alertas:
                        alerta_id = alerta.get("id")
                        requests.post(f"{API_URL}/sensores/alertas/{alerta_id}/resolver")
                    # Recargar tabla
                    ver_alertas_sensores(None)
                except Exception as ex:
                    resultado.value = f"❌ Error: {str(ex)}"
                    page.update()
            
            if not alertas:
                # Si no hay alertas, mostrar mensaje
                contenido = ft.Column([
                    ft.Text("✅ No hay alertas pendientes", size=14, color=ft.Colors.GREEN_700, weight=ft.FontWeight.BOLD),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
            else:
                contenido = ft.Column([
                    ft.Text(f"⚠️ {len(alertas)} Alerta(s) Pendiente(s)", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700),
                    ft.Divider(height=10),
                    tabla_alertas,
                ], scroll="adaptive", spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            
            resultado = ft.Text("", size=12, color=ft.Colors.GREEN_700)
            
            # Botón para borrar alertas (fijo en la parte superior)
            btn_borrar = ft.ElevatedButton(
                "🗑️ BORRAR",
                on_click=borrar_todas_alertas,
                bgcolor=ft.Colors.RED_700,
                color=ft.Colors.WHITE,
                width=120,
                height=40
            ) if alertas else ft.Container()
            
            # Envolver tabla en contenedor con altura máxima y scroll
            tabla_container = ft.Container(
                content=tabla_alertas,
                expand=True,
                border_radius=6,
            )
            
            panel = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.ElevatedButton("⬅️ Volver", on_click=lambda _: vigilante_view(page, API_URL), bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=100, height=40),
                        ft.Text("ALERTAS NO AUTORIZADAS", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.ElevatedButton("🔄", on_click=lambda _: ver_alertas_sensores(None), bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=50, height=40),
                        btn_borrar,
                    ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=15),
                    contenido,
                    ft.Divider(height=10),
                    resultado,
                ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True, scroll=ft.ScrollMode.AUTO),
                padding=20,
                expand=True,
                bgcolor=ft.Colors.GREY_200,
                border_radius=6,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
            )
            
            page.add(panel)
            
        except Exception as ex:
            resultado = ft.Text(f"❌ Error: {str(ex)}", size=12, color=ft.Colors.RED_700)
            page.add(resultado)

    # =====================================================
    # PANEL PRINCIPAL
    # =====================================================

    titulo = ft.Text("Panel del Vigilante", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    logo = ft.Text("SmartPark", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)

    botones = [
        ft.ElevatedButton("VER ACCESOS RECIENTES", on_click=ver_accesos_recientes, bgcolor=ft.Colors.GREEN_900, color=ft.Colors.WHITE, expand=True, height=45, width=250),
        ft.ElevatedButton("VER ALERTAS NO AUTORIZADAS", on_click=ver_alertas_sensores, bgcolor=ft.Colors.ORANGE_900, color=ft.Colors.WHITE, expand=True, height=45, width=250),
        ft.ElevatedButton("VER DATOS DE USUARIOS", on_click=ver_datos_usuarios, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, expand=True, height=45, width=250),
        ft.ElevatedButton("REGISTRAR ENTRADA MANUAL", on_click=lambda e: registrar_acceso_manual("entrada"), bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, expand=True, height=45, width=250),
        ft.ElevatedButton("REGISTRAR SALIDA MANUAL", on_click=lambda e: registrar_acceso_manual("salida"), bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, expand=True, height=45, width=250),
        ft.ElevatedButton("ENVIAR ADVERTENCIA", on_click=enviar_advertencia, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, expand=True, height=45, width=250),
        ft.ElevatedButton("ENVIAR MULTA", on_click=enviar_multa, bgcolor=ft.Colors.RED_900, color=ft.Colors.WHITE, expand=True, height=45, width=250),
        ft.ElevatedButton("AJUSTES DE APLICACION", on_click=placeholder, bgcolor=ft.Colors.BLUE_GREY_700, color=ft.Colors.WHITE, expand=True, height=45, width=250),
        ft.ElevatedButton("CERRAR APLICACION", on_click=cerrar_aplicacion, bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE, expand=True, height=45, width=250),
    ]

    panel = ft.Container(
        content=ft.Column(
            [logo, titulo, ft.Divider(height=15, color=ft.Colors.TRANSPARENT)] + botones + [ft.Divider(height=15, color=ft.Colors.TRANSPARENT), salida],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=40,
        width=500,
        bgcolor=ft.Colors.GREY_200,
        border_radius=6,
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
    )

    # Crear layout con notificaciones en esquina superior derecha
    # Las notificaciones se agregan como overlay para aparecer encima de todo
    page.overlay.append(notificaciones_container)
    
    # Posicionar notificaciones en esquina superior derecha
    notificaciones_container.left = 20
    notificaciones_container.top = 20
    notificaciones_container.width = 340
    
    page.add(ft.Container(
        content=panel,
        alignment=ft.alignment.center,
        expand=True,
    ))
