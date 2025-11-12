import flet as ft
import requests

def vigilante_view(page: ft.Page, API_URL: str):
    page.clean()
    page.title = "SmartPark - Vigilante"
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    salida = ft.Text("", size=14, color=ft.Colors.BLUE_GREY_900, selectable=True)

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
                    ft.Text("DATOS DE USUARIOS", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                    ft.Container(content=tabla, width=1000, height=400),
                    ft.ElevatedButton("← Volver al Panel", on_click=lambda _: vigilante_view(page, API_URL), width=200),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border_radius=6,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
            )
            page.add(panel)

        except Exception as ex:
            salida.value = f"Error: {ex}"
            page.update()

    def registrar_acceso_manual(tipo):
        """Diálogo para registrar entrada o salida manual por ID de usuario"""
        id_input = ft.TextField(label="ID de usuario", width=250, keyboard_type=ft.KeyboardType.NUMBER)
        
        user_data = {"existe": False, "datos": {}}
        
        nombre_display = ft.Text("", size=12, color=ft.Colors.BLUE_GREY_700)
        celular_display = ft.Text("", size=12, color=ft.Colors.BLUE_GREY_700)
        vehiculos_display = ft.Text("", size=11, color=ft.Colors.BLUE_GREY_700)
        usos_restantes = ft.Text("", size=12, color=ft.Colors.BLUE_GREY_700)
        estado_entrada = ft.Text("", size=12, color=ft.Colors.ORANGE_700, weight=ft.FontWeight.BOLD)
        resultado = ft.Text("", size=12, weight=ft.FontWeight.BOLD)
        btn_registrar = ft.ElevatedButton(f"Registrar {tipo.upper()}", disabled=True, width=200)
        
        contenedor_datos = ft.Container(
            content=ft.Column([
                nombre_display,
                celular_display,
                vehiculos_display,
                usos_restantes,
                estado_entrada,
            ], spacing=4),
            visible=False,
            bgcolor=ft.Colors.BLUE_GREY_100,
            padding=10,
            border_radius=8
        )

        def buscar_usuario(_):
            """Busca el usuario en la BD y muestra sus datos"""
            user_id = id_input.value.strip()
            resultado.value = ""
            btn_registrar.disabled = True
            contenedor_datos.visible = False
            user_data["existe"] = False
            
            if not user_id or not user_id.isdigit():
                resultado.value = "⚠️ Ingresa un ID válido"
                page.update()
                return
            
            try:
                r = requests.get(f"{API_URL}/usuarios/{user_id}", timeout=5)
                
                if r.status_code != 200:
                    resultado.value = "❌ Usuario no encontrado en la BD"
                    page.update()
                    return
                
                usuario = r.json()
                
                if not usuario.get("nomUsuario"):
                    resultado.value = "❌ Usuario sin datos completos"
                    page.update()
                    return
                
                user_data["datos"] = usuario
                user_data["existe"] = True
                
                nombre_display.value = f"👤 Nombre: {usuario.get('nomUsuario', 'N/A')}"
                celular_display.value = f"📱 Celular: {usuario.get('celular', 'N/A')}"
                
                autos = usuario.get("autos", [])
                if autos:
                    autos_str = ", ".join([f"{a.get('marca')} {a.get('modelo')} ({a.get('placa')})" for a in autos])
                    vehiculos_display.value = f"🚗 Vehículos: {autos_str}"
                else:
                    vehiculos_display.value = "🚗 Vehículos: Sin registrar"
                
                r_accesos = requests.get(f"{API_URL}/acceso/manuales/{user_id}", timeout=5)
                data_accesos = r_accesos.json()
                
                r_entrada_activa = requests.get(f"{API_URL}/acceso/manuales/{user_id}/activa", timeout=5)
                data_activa = r_entrada_activa.json()
                entrada_activa = data_activa.get("entrada_activa", False)
                
                if tipo == "entrada":
                    if entrada_activa:
                        estado_entrada.value = "🚨 Este usuario tiene una ENTRADA ACTIVA sin salida correspondiente"
                        usos_restantes.value = "❌ Debe registrar salida primero"
                        btn_registrar.disabled = True
                        resultado.value = "❌ Operación bloqueada: hay entrada activa sin salida"
                    else:
                        usos = data_accesos.get("usos_mes", 0)
                        limite = data_accesos.get("limite", 3)
                        usos_restantes.value = f"📊 Entradas manuales: {usos}/{limite} usadas este mes"
                        estado_entrada.value = ""
                        
                        if usos >= limite:
                            resultado.value = f"❌ Límite de {limite} entradas manuales alcanzado"
                            btn_registrar.disabled = True
                        else:
                            resultado.value = f"✅ Usuario verificado. Accesos restantes: {limite - usos}"
                            btn_registrar.disabled = False
                else:
                    if not entrada_activa:
                        estado_entrada.value = "❌ No hay ENTRADA ACTIVA para este usuario"
                        usos_restantes.value = ""
                        btn_registrar.disabled = True
                        resultado.value = "❌ No se puede registrar salida sin entrada previa"
                    else:
                        estado_entrada.value = "✅ Hay una ENTRADA ACTIVA - Puedes registrar salida"
                        usos_restantes.value = ""
                        resultado.value = "✅ Usuario verificado"
                        btn_registrar.disabled = False
                
                contenedor_datos.visible = True
                    
            except requests.exceptions.Timeout:
                resultado.value = "❌ Tiempo de conexión agotado"
            except requests.exceptions.ConnectionError:
                resultado.value = "❌ No se puede conectar al servidor"
            except Exception as ex:
                resultado.value = f"❌ Error inesperado"
            
            page.update()

        def registrar(_):
            """Registra la entrada o salida manual"""
            if not user_data["existe"]:
                resultado.value = "❌ Debe verificar usuario primero"
                page.update()
                return
            
            user_id = id_input.value.strip()
            try:
                endpoint = f"/acceso/manual/{tipo}"
                r = requests.post(f"{API_URL}{endpoint}", json={"id_usuario": int(user_id)})
                data = r.json()
                
                if data.get("success"):
                    resultado.value = f"✅ {data.get('mensaje', 'Acceso registrado correctamente')}"
                    id_input.value = ""
                    contenedor_datos.visible = False
                else:
                    resultado.value = f"❌ {data.get('mensaje', 'Error al registrar')}"
                    
            except Exception as ex:
                resultado.value = f"❌ Error: {ex}"
            page.update()

        id_input.on_change = buscar_usuario
        btn_registrar.on_click = registrar

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Registrar {tipo.capitalize()} Manual", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text("Ingresa el ID del usuario:", size=12, weight=ft.FontWeight.W_600),
                id_input,
                ft.Divider(height=10),
                contenedor_datos,
                ft.Divider(height=10),
                btn_registrar,
                ft.Divider(height=10),
                resultado
            ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda _: cerrar_dialogo()),
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

    def enviar_advertencia(e):
        """Diálogo para enviar una advertencia a un usuario"""
        id_input = ft.TextField(label="ID de usuario", width=250, keyboard_type=ft.KeyboardType.NUMBER)
        id_historial_input = ft.TextField(label="ID de entrada (historial)", width=250, keyboard_type=ft.KeyboardType.NUMBER)
        
        user_data = {"existe": False, "datos": {}}
        
        nombre_display = ft.Text("", size=12, color=ft.Colors.BLUE_GREY_700)
        celular_display = ft.Text("", size=12, color=ft.Colors.BLUE_GREY_700)
        advertencias_display = ft.Text("", size=12, color=ft.Colors.BLUE_GREY_700)
        ids_disponibles = ft.Text("", size=11, color=ft.Colors.BLUE_900, weight=ft.FontWeight.BOLD)
        resultado = ft.Text("", size=12, weight=ft.FontWeight.BOLD)
        btn_enviar = ft.ElevatedButton("ENVIAR ADVERTENCIA", disabled=True, width=200)
        
        contenedor_datos = ft.Container(
            content=ft.Column([
                nombre_display,
                celular_display,
                ids_disponibles,
                advertencias_display,
            ], spacing=4),
            visible=False,
            bgcolor=ft.Colors.BLUE_GREY_100,
            padding=10,
            border_radius=8
        )

        def buscar_usuario_para_entrada(_):
            """Busca el usuario y muestra sus IDs de entrada disponibles"""
            user_id = id_input.value.strip()
            resultado.value = ""
            ids_disponibles.value = ""
            btn_enviar.disabled = True
            contenedor_datos.visible = False
            user_data["existe"] = False
            
            if not user_id or not user_id.isdigit():
                resultado.value = "⚠️ Ingresa un ID válido"
                page.update()
                return
            
            try:
                # Obtener datos del usuario
                r = requests.get(f"{API_URL}/usuarios/{user_id}", timeout=5)
                
                if r.status_code != 200:
                    resultado.value = "❌ Usuario no encontrado"
                    page.update()
                    return
                
                usuario = r.json()
                
                if not usuario.get("nomUsuario"):
                    resultado.value = "❌ Usuario sin datos completos"
                    page.update()
                    return
                
                user_data["datos"] = usuario
                
                nombre_display.value = f"👤 Nombre: {usuario.get('nomUsuario', 'N/A')}"
                celular_display.value = f"📱 Celular: {usuario.get('celular', 'N/A')}"
                
                # Obtener IDs de historial disponibles
                r_ids = requests.get(f"{API_URL}/historial/usuario/{user_id}/ids", timeout=5)
                data_ids = r_ids.json()
                ids_list = data_ids.get("ids", [])
                
                if not ids_list:
                    resultado.value = "❌ Este usuario no tiene entradas registradas"
                    contenedor_datos.visible = True
                    page.update()
                    return
                
                # Mostrar IDs disponibles
                ids_text = "📋 IDs de entrada disponibles: " + ", ".join([str(h["id"]) for h in ids_list])
                ids_disponibles.value = ids_text
                
                resultado.value = f"✅ Usuario encontrado ({len(ids_list)} entradas disponibles)"
                contenedor_datos.visible = True
                    
            except Exception as ex:
                resultado.value = f"❌ Error: {ex}"
            
            page.update()

        def buscar_usuario_y_entrada(_):
            """Busca el usuario y valida la entrada específica"""
            user_id = id_input.value.strip()
            id_hist = id_historial_input.value.strip()
            resultado.value = ""
            btn_enviar.disabled = True
            user_data["existe"] = False
            
            if not user_id or not user_id.isdigit():
                resultado.value = "⚠️ Ingresa un ID válido"
                page.update()
                return
            
            if not id_hist or not id_hist.isdigit():
                resultado.value = "⚠️ Ingresa ID de entrada válido"
                page.update()
                return
            
            try:
                r = requests.get(f"{API_URL}/usuarios/{user_id}", timeout=5)
                
                if r.status_code != 200:
                    resultado.value = "❌ Usuario no encontrado"
                    page.update()
                    return
                
                usuario = r.json()
                
                if not usuario.get("nomUsuario"):
                    resultado.value = "❌ Usuario sin datos"
                    page.update()
                    return
                
                # Validar que el ID de historial existe
                r_historial = requests.get(f"{API_URL}/historial/validar/{user_id}/{id_hist}", timeout=5)
                data_historial = r_historial.json()
                
                if not data_historial.get("valido"):
                    resultado.value = f"❌ {data_historial.get('mensaje', 'Entrada no válida')}"
                    page.update()
                    return
                
                user_data["datos"] = usuario
                user_data["existe"] = True
                
                nombre_display.value = f"👤 Nombre: {usuario.get('nomUsuario', 'N/A')}"
                celular_display.value = f"📱 Celular: {usuario.get('celular', 'N/A')}"
                
                r_adv = requests.get(f"{API_URL}/advertencias/entrada/{user_id}/{id_hist}", timeout=5)
                data_adv = r_adv.json()
                adv_entrada = data_adv.get("advertencias", 0)
                advertencias_display.value = f"⚠️ Advertencias en esta entrada: {adv_entrada}/3"
                
                resultado.value = "✅ Usuario y entrada validados"
                btn_enviar.disabled = False
                contenedor_datos.visible = True
                    
            except Exception as ex:
                resultado.value = f"❌ Error: {ex}"
            
            page.update()

        def enviar(_):
            """Envía la advertencia"""
            if not user_data["existe"]:
                resultado.value = "❌ Busca un usuario primero"
                page.update()
                return
            
            user_id = id_input.value.strip()
            id_hist = id_historial_input.value.strip()
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
                        resultado.value += " - ⚠️ PUEDE ENVIAR MULTA"
                else:
                    resultado.value = f"❌ {data.get('mensaje', 'Error')}"
                    
            except Exception as ex:
                resultado.value = f"❌ Error: {ex}"
            page.update()

        id_input.on_change = buscar_usuario_para_entrada
        id_historial_input.on_change = buscar_usuario_y_entrada
        btn_enviar.on_click = enviar

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Enviar Advertencia", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text("Ingresa el ID del usuario:", size=12, weight=ft.FontWeight.W_600),
                id_input,
                ft.Text("Ingresa el ID de la entrada (historial):", size=12, weight=ft.FontWeight.W_600),
                id_historial_input,
                ft.Divider(height=10),
                contenedor_datos,
                ft.Divider(height=10),
                btn_enviar,
                ft.Divider(height=10),
                resultado
            ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda _: cerrar_dialogo()),
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

    def enviar_multa(e):
        """Diálogo para enviar una multa (después de 3 advertencias)"""
        id_input = ft.TextField(label="ID de usuario", width=250, keyboard_type=ft.KeyboardType.NUMBER)
        id_historial_input = ft.TextField(label="ID de entrada (historial)", width=250, keyboard_type=ft.KeyboardType.NUMBER)
        monto_input = ft.TextField(label="Monto ($)", width=250, value="50.0", keyboard_type=ft.KeyboardType.NUMBER)
        
        user_data = {"existe": False}
        
        nombre_display = ft.Text("", size=12, color=ft.Colors.BLUE_GREY_700)
        advertencias_display = ft.Text("", size=12, color=ft.Colors.RED_700, weight=ft.FontWeight.BOLD)
        resultado = ft.Text("", size=12, weight=ft.FontWeight.BOLD)
        btn_enviar = ft.ElevatedButton("ENVIAR MULTA", disabled=True, width=200, bgcolor=ft.Colors.RED_900)
        
        contenedor_datos = ft.Container(
            content=ft.Column([
                nombre_display,
                advertencias_display,
            ], spacing=4),
            visible=False,
            bgcolor=ft.Colors.RED_100,
            padding=10,
            border_radius=8
        )

        def buscar_usuario(_):
            """Verifica usuario y advertencias"""
            user_id = id_input.value.strip()
            id_hist = id_historial_input.value.strip()
            resultado.value = ""
            btn_enviar.disabled = True
            contenedor_datos.visible = False
            user_data["existe"] = False
            
            if not user_id or not user_id.isdigit() or not id_hist or not id_hist.isdigit():
                resultado.value = "⚠️ Completa ID usuario e ID entrada"
                page.update()
                return
            
            try:
                r = requests.get(f"{API_URL}/usuarios/{user_id}", timeout=5)
                if r.status_code != 200:
                    resultado.value = "❌ Usuario no encontrado"
                    page.update()
                    return
                
                # Validar que el ID de historial existe
                r_historial = requests.get(f"{API_URL}/historial/validar/{user_id}/{id_hist}", timeout=5)
                data_historial = r_historial.json()
                
                if not data_historial.get("valido"):
                    resultado.value = f"❌ {data_historial.get('mensaje', 'Entrada no válida')}"
                    page.update()
                    return
                
                usuario = r.json()
                nombre_display.value = f"👤 {usuario.get('nomUsuario', 'N/A')}"
                
                r_adv = requests.get(f"{API_URL}/advertencias/entrada/{user_id}/{id_hist}", timeout=5)
                data_adv = r_adv.json()
                adv_count = data_adv.get("advertencias", 0)
                
                if adv_count < 3:
                    advertencias_display.value = f"⚠️ Solo {adv_count}/3 advertencias - NO PUEDE MULTAR"
                    btn_enviar.disabled = True
                else:
                    advertencias_display.value = f"🚨 {adv_count} ADVERTENCIAS - MULTA HABILITADA"
                    btn_enviar.disabled = False
                
                user_data["existe"] = True
                resultado.value = "✅ Usuario y entrada validados"
                contenedor_datos.visible = True
                    
            except Exception as ex:
                resultado.value = f"❌ Error: {ex}"
            
            page.update()

        def enviar(_):
            """Envía la multa"""
            if not user_data["existe"]:
                resultado.value = "❌ Busca usuario primero"
                page.update()
                return
            
            user_id = id_input.value.strip()
            id_hist = id_historial_input.value.strip()
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
                    resultado.value = f"❌ {data.get('mensaje', 'Error')}"
                    
            except ValueError:
                resultado.value = "❌ Monto inválido"
            except Exception as ex:
                resultado.value = f"❌ Error: {ex}"
            page.update()

        id_input.on_change = buscar_usuario
        id_historial_input.on_change = buscar_usuario
        btn_enviar.on_click = enviar

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Enviar Multa", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text("ID usuario:", size=12, weight=ft.FontWeight.W_600),
                id_input,
                ft.Text("ID entrada:", size=12, weight=ft.FontWeight.W_600),
                id_historial_input,
                ft.Divider(height=10),
                contenedor_datos,
                ft.Divider(height=10),
                ft.Text("Monto:", size=12, weight=ft.FontWeight.W_600),
                monto_input,
                ft.Divider(height=10),
                btn_enviar,
                ft.Divider(height=10),
                resultado
            ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda _: cerrar_dialogo()),
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

    def ver_accesos_recientes(e):
        """Ver los últimos accesos registrados en tiempo real"""
        page.clean()
        
        titulo_accesos = ft.Text("Accesos Recientes", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
        contenedor_accesos = ft.Column([], scroll=ft.ScrollMode.AUTO)
        btn_refrescar = ft.ElevatedButton("🔄 REFRESCAR", bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=250, height=40)
        
        def cargar_accesos():
            """Carga los accesos recientes desde el API"""
            try:
                r = requests.get(f"{API_URL}/accesos-recientes?limite=15")
                if r.status_code == 200:
                    accesos = r.json().get("accesos", [])
                    contenedor_accesos.controls.clear()
                    
                    if not accesos:
                        contenedor_accesos.controls.append(
                            ft.Text("No hay accesos registrados", size=14, color=ft.Colors.BLUE_GREY_700)
                        )
                    else:
                        for acceso in accesos:
                            estado = "🔵 ACTIVO" if acceso.get("activo") == 1 else "✅ CERRADO"
                            color_estado = ft.Colors.BLUE_600 if acceso.get("activo") == 1 else ft.Colors.GREEN_700
                            
                            tarjeta = ft.Container(
                                content=ft.Column([
                                    ft.Row([
                                        ft.Text(f"👤 {acceso.get('nombre_usuario')}", weight=ft.FontWeight.BOLD, size=13),
                                        ft.Text(f"ID: {acceso.get('usuario_id')}", size=11, color=ft.Colors.BLUE_GREY_700),
                                    ]),
                                    ft.Row([
                                        ft.Text(f"🅿️ Espacio: {acceso.get('espacio_asignado')}", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                                        ft.Text(estado, size=11, color=color_estado, weight=ft.FontWeight.BOLD),
                                    ]),
                                    ft.Row([
                                        ft.Text(f"📞 {acceso.get('celular')}", size=10, color=ft.Colors.BLUE_GREY_600),
                                        ft.Text(f"⏰ {str(acceso.get('fecha_hora_entrada', ''))[:19]}", size=10, color=ft.Colors.BLUE_GREY_600),
                                    ]),
                                    ft.Divider(height=1, color=ft.Colors.BLUE_GREY_200),
                                ], spacing=5),
                                padding=12,
                                bgcolor=ft.Colors.BLUE_GREY_50,
                                border_radius=6,
                                border=ft.border.all(1, ft.Colors.BLUE_GREY_300),
                            )
                            contenedor_accesos.controls.append(tarjeta)
                    
                    page.update()
                else:
                    contenedor_accesos.controls.clear()
                    contenedor_accesos.controls.append(
                        ft.Text(f"Error al cargar: {r.status_code}", color=ft.Colors.RED_700)
                    )
                    page.update()
            except Exception as ex:
                contenedor_accesos.controls.clear()
                contenedor_accesos.controls.append(
                    ft.Text(f"❌ Error: {str(ex)}", color=ft.Colors.RED_700)
                )
                page.update()
        
        def refrescar_click(e):
            cargar_accesos()
        
        btn_refrescar.on_click = refrescar_click
        
        # Cargar accesos al abrir
        cargar_accesos()
        
        # Panel con actualización automática cada 2 segundos
        panel_accesos = ft.Container(
            content=ft.Column([
                titulo_accesos,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row([btn_refrescar], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Container(
                    content=contenedor_accesos,
                    width=600,
                    height=450,
                    border_radius=6,
                    border=ft.border.all(1, ft.Colors.BLUE_GREY_300),
                ),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.ElevatedButton("← VOLVER AL PANEL", on_click=lambda _: vigilante_view(page, API_URL), bgcolor=ft.Colors.BLUE_GREY_700, color=ft.Colors.WHITE, width=250, height=40),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=30,
            bgcolor=ft.Colors.WHITE,
            border_radius=6,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
        )
        
        page.add(panel_accesos)
        
        # Actualizar cada 3 segundos
        import threading
        def auto_refresh():
            import time
            while page.overlay or True:
                time.sleep(3)
                try:
                    if page.session.get("actualizar_accesos", True):
                        cargar_accesos()
                except:
                    break
        
        threading.Thread(target=auto_refresh, daemon=True).start()

    # =====================================================
    # PANEL PRINCIPAL
    # =====================================================

    titulo = ft.Text("Panel del Vigilante", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    logo = ft.Text("SmartPark", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)

    botones = [
        ft.ElevatedButton("👀 VER ACCESOS RECIENTES", on_click=ver_accesos_recientes, bgcolor=ft.Colors.GREEN_900, color=ft.Colors.WHITE, width=250, height=45),
        ft.ElevatedButton("VER DATOS DE USUARIOS", on_click=ver_datos_usuarios, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=250, height=45),
        ft.ElevatedButton("REGISTRAR ENTRADA MANUAL", on_click=lambda e: registrar_acceso_manual("entrada"), bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=250, height=45),
        ft.ElevatedButton("REGISTRAR SALIDA MANUAL", on_click=lambda e: registrar_acceso_manual("salida"), bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=250, height=45),
        ft.ElevatedButton("ENVIAR ADVERTENCIA", on_click=enviar_advertencia, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=250, height=45),
        ft.ElevatedButton("ENVIAR MULTA", on_click=enviar_multa, bgcolor=ft.Colors.RED_900, color=ft.Colors.WHITE, width=250, height=45),
        ft.ElevatedButton("AJUSTES DE APLICACION", on_click=placeholder, bgcolor=ft.Colors.BLUE_GREY_700, color=ft.Colors.WHITE, width=250, height=45),
        ft.ElevatedButton("CERRAR APLICACION", on_click=cerrar_aplicacion, bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE, width=250, height=45),
    ]

    panel = ft.Container(
        content=ft.Column(
            [logo, titulo, ft.Divider(height=15, color=ft.Colors.TRANSPARENT)] + botones + [ft.Divider(height=15, color=ft.Colors.TRANSPARENT), salida],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        padding=40,
        width=420,
        bgcolor=ft.Colors.WHITE,
        border_radius=6,
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
    )

    page.add(panel)
