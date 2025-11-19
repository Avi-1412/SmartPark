import flet as ft
import requests

def usuario_view(page: ft.Page, API_URL: str, id_usuario: int = None):
    page.clean()
    page.title = "SmartPark - Usuario"
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    salida = ft.Text("", size=14, color=ft.Colors.BLUE_GREY_900, selectable=True)

    # --- Funciones funcionales ---
    def ver_historial(e):
        """Ver historial de accesos del usuario actual"""
        page.clean()
        
        try:
            r = requests.get(f"{API_URL}/historial/usuario/{id_usuario}")
            
            if r.status_code == 200:
                historial = r.json().get("historial", [])
                
                if not historial:
                    salida.value = "No hay historial de accesos registrado."
                    page.update()
                    panel = ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.ElevatedButton("VOLVER", on_click=lambda _: usuario_view(page, API_URL, id_usuario), 
                                                 bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=100, height=40),
                                ft.Text("MI HISTORIAL DE ACCESOS", size=18, weight=ft.FontWeight.BOLD, 
                                       color=ft.Colors.BLUE_900, expand=True, text_align=ft.TextAlign.CENTER),
                                ft.Container(width=100),
                            ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Divider(height=15),
                            ft.Column([
                                ft.Text("No hay historial disponible", size=14, color=ft.Colors.BLUE_GREY_700),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=20, expand=True, bgcolor=ft.Colors.GREY_200,
                        border_radius=6, shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
                    )
                    page.add(panel)
                    return
                
                # Crear tabla de historial
                tabla_historial = ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("ID")),
                        ft.DataColumn(ft.Text("Tipo")),
                        ft.DataColumn(ft.Text("Espacio")),
                        ft.DataColumn(ft.Text("Entrada")),
                        ft.DataColumn(ft.Text("Salida")),
                        ft.DataColumn(ft.Text("Estado")),
                    ],
                    rows=[],
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
                                ft.DataCell(ft.Text(str(h.get("historial_id", h.get("idHis", ""))))),
                                ft.DataCell(ft.Text(tipo_badge)),
                                ft.DataCell(ft.Text(str(h.get("espacio_asignado", "")))),
                                ft.DataCell(ft.Text(entrada)),
                                ft.DataCell(ft.Text(salida_h)),
                                ft.DataCell(ft.Text(estado)),
                            ]
                        )
                    )
                
                # Mostrar tabla
                boton_volver = ft.ElevatedButton(
                    "VOLVER",
                    on_click=lambda _: usuario_view(page, API_URL, id_usuario),
                    bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=100, height=40
                )
                
                panel = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.ElevatedButton("VOLVER", on_click=lambda _: usuario_view(page, API_URL, id_usuario), 
                                             bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=100, height=40),
                            ft.Text("MI HISTORIAL DE ACCESOS", size=18, weight=ft.FontWeight.BOLD, 
                                   color=ft.Colors.BLUE_900, expand=True, text_align=ft.TextAlign.CENTER),
                            ft.Container(width=100),
                        ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Divider(height=15),
                        ft.Container(content=tabla_historial, expand=True),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, 
                       expand=True, scroll=ft.ScrollMode.AUTO),
                    padding=20, expand=True, bgcolor=ft.Colors.GREY_200,
                    border_radius=6, shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
                )
                page.add(panel)
            else:
                salida.value = f"Error en API: {r.status_code}"
                page.update()
        except Exception as ex:
            salida.value = f"❌ Error: {str(ex)}"
            page.update()

    def ver_tarjeta_digital(e):
        """Mostrar tarjeta digital con datos del usuario"""
        try:
            # Obtener datos del usuario
            r = requests.get(f"{API_URL}/usuarios/{id_usuario}")
            usuario_data = r.json()
            
            if "error" in usuario_data:
                salida.value = f"Error: {usuario_data['error']}"
                page.update()
                return
            
            # Obtener información de autos
            autos = usuario_data.get("autos", [])
            autos_info = []
            for auto in autos:
                autos_info.append(
                    ft.Row([
                        ft.Column([
                            ft.Text(auto.get("placa", "N/A"), size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                        ], spacing=2, expand=1),
                        ft.Column([
                            ft.Text(f"{auto.get('marca', 'N/A')} {auto.get('modelo', 'N/A')}", size=11),
                        ], spacing=2, expand=2),
                    ], spacing=5)
                )
            
            # Crear tarjeta digital estilo carné
            tarjeta = ft.Container(
                content=ft.Column([
                    # Encabezado de la tarjeta
                    ft.Container(
                        content=ft.Text("SMARTPARK", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.BLUE_900,
                        padding=10,
                        alignment=ft.alignment.center,
                    ),
                    
                    # Contenido principal con padding
                    ft.Container(
                        content=ft.Column([
                            # Nombre
                            ft.Column([
                                ft.Text("NOMBRE", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                                ft.Text(usuario_data.get("nomUsuario", "N/A"), size=14, weight=ft.FontWeight.BOLD),
                            ], spacing=2),
                            
                            ft.Divider(height=10),
                            
                            # Datos en dos columnas
                            ft.Row([
                                ft.Column([
                                    ft.Text("ID", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                                    ft.Text(str(usuario_data.get("idUsuario", "N/A")), size=12),
                                ], spacing=2, expand=True),
                                ft.Column([
                                    ft.Text("MATRÍCULA", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                                    ft.Text(str(usuario_data.get("matrUsuario", "N/A")), size=12),
                                ], spacing=2, expand=True),
                            ], spacing=10),
                            
                            ft.Divider(height=10),
                            
                            # Celular
                            ft.Column([
                                ft.Text("CELULAR", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                                ft.Text(usuario_data.get("celular", "N/A"), size=12),
                            ], spacing=2),
                            
                            ft.Divider(height=10),
                            
                            # Vehículos
                            ft.Column([
                                ft.Text("VEHÍCULOS", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                                ft.Column(autos_info if autos_info else [ft.Text("Sin vehículos registrados", size=11, color=ft.Colors.BLUE_GREY_700)], spacing=5),
                            ], spacing=2),
                            
                            ft.Divider(height=10),
                            
                            # Pie de página
                            ft.Container(
                                content=ft.Text(
                                    "Tarjeta Digital - Válida solo en caso de extravío de carné físico",
                                    size=9,
                                    color=ft.Colors.BLUE_GREY_700,
                                    text_align=ft.TextAlign.CENTER
                                ),
                                alignment=ft.alignment.center,
                            ),
                        ], spacing=5),
                        padding=15,
                    ),
                ]),
                bgcolor=ft.Colors.GREY_200,
                border_radius=10,
                shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.BLUE_GREY_300),
                padding=0,
                width=350,
            )
            
            # Mostrar tarjeta
            page.clean()
            
            panel = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.ElevatedButton("VOLVER", on_click=lambda _: usuario_view(page, API_URL, id_usuario), 
                                         bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=100, height=40),
                        ft.Text("MI TARJETA DIGITAL", size=18, weight=ft.FontWeight.BOLD, 
                               color=ft.Colors.BLUE_900, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Container(width=100),
                    ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=15),
                    ft.Container(tarjeta, alignment=ft.alignment.center),
                ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                   expand=True, scroll=ft.ScrollMode.AUTO),
                padding=20, expand=True, bgcolor=ft.Colors.GREY_200,
                border_radius=6, shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
            )
            page.add(panel)
            
        except Exception as ex:
            salida.value = f"❌ Error al obtener tarjeta: {ex}"
            page.update()

    def ver_boleto_digital(e):
        """Mostrar boleto digital con entrada actual"""
        try:
            # Obtener historial del usuario
            r = requests.get(f"{API_URL}/historial/usuario/{id_usuario}")
            historial = r.json().get("historial", [])
            
            # Buscar entrada activa (valido=1 sin hora_salida)
            entrada_activa = None
            for h in historial:
                if h.get("valido") == 1 and not h.get("hora_salida"):
                    entrada_activa = h
                    break
            
            if not entrada_activa:
                # Si no hay entrada activa, mostrar último acceso
                if historial:
                    entrada_activa = historial[0]
                else:
                    salida.value = "No hay accesos registrados"
                    page.update()
                    return
            
            # Obtener datos del usuario
            r_user = requests.get(f"{API_URL}/usuarios/{id_usuario}")
            usuario_data = r_user.json()
            
            # Formato de fechas
            fecha_entrada = str(entrada_activa.get("hora_entrada", entrada_activa.get("fecha_entrada", "")))
            hora_entrada = fecha_entrada[:16] if len(fecha_entrada) > 10 else fecha_entrada[:10]
            
            hora_salida = str(entrada_activa.get("hora_salida", ""))[:16] if entrada_activa.get("hora_salida") else "—"
            
            estado_acceso = "🟢 ACTIVO" if (entrada_activa.get("valido") == 1 and not entrada_activa.get("hora_salida")) else "✅ COMPLETADO"
            
            # Crear boleto
            boleto = ft.Container(
                content=ft.Column([
                    # Encabezado
                    ft.Container(
                        content=ft.Column([
                            ft.Text("SMARTPARK", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text("Boleto de Estacionamiento", size=12, color=ft.Colors.WHITE),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3),
                        bgcolor=ft.Colors.BLUE_900,
                        padding=15,
                        border_radius=ft.border_radius.only(top_left=10, top_right=10),
                    ),
                    
                    # Contenido principal
                    ft.Container(
                        content=ft.Column([
                            # Estado
                            ft.Container(
                                content=ft.Text(estado_acceso, size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                bgcolor=ft.Colors.GREEN_700 if "ACTIVO" in estado_acceso else ft.Colors.BLUE_700,
                                padding=8,
                                border_radius=5,
                                alignment=ft.alignment.center,
                            ),
                            
                            ft.Divider(height=15),
                            
                            # Datos del usuario
                            ft.Row([
                                ft.Column([
                                    ft.Text("USUARIO", size=9, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                                    ft.Text(usuario_data.get("nomUsuario", "N/A")[:20], size=11, weight=ft.FontWeight.BOLD),
                                ], spacing=2),
                                ft.Column([
                                    ft.Text("ID USUARIO", size=9, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                                    ft.Text(str(id_usuario), size=11, weight=ft.FontWeight.BOLD),
                                ], spacing=2),
                            ], spacing=15),
                            
                            ft.Divider(height=12),
                            
                            # Espacio asignado
                            ft.Column([
                                ft.Text("ESPACIO ASIGNADO", size=9, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                                ft.Text(str(entrada_activa.get("espacio_asignado", "N/A")), size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                            
                            ft.Divider(height=12),
                            
                            # Hora entrada
                            ft.Column([
                                ft.Text("HORA ENTRADA", size=9, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                                ft.Text(hora_entrada, size=12),
                            ], spacing=2),
                            
                            # Hora salida
                            ft.Column([
                                ft.Text("HORA SALIDA", size=9, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                                ft.Text(hora_salida, size=12),
                            ], spacing=2),
                            
                            ft.Divider(height=12),
                            
                            # Línea de separación visual
                            ft.Container(
                                height=2,
                                bgcolor=ft.Colors.BLUE_GREY_300,
                                border_radius=1,
                            ),
                            
                            # Pie de página
                            ft.Text(
                                "Guarda este boleto para consultas futuras",
                                size=9,
                                color=ft.Colors.BLUE_GREY_700,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ], spacing=5),
                        padding=15,
                    ),
                ], spacing=0),
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.BLUE_GREY_300),
                width=380,
            )
            
            # Mostrar boleto
            page.clean()
            
            panel = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.ElevatedButton("VOLVER", on_click=lambda _: usuario_view(page, API_URL, id_usuario), 
                                         bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=100, height=40),
                        ft.Text("MI BOLETO DIGITAL", size=18, weight=ft.FontWeight.BOLD, 
                               color=ft.Colors.BLUE_900, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Container(width=100),
                    ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=15),
                    ft.Container(boleto, alignment=ft.alignment.center),
                ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                   expand=True, scroll=ft.ScrollMode.AUTO),
                padding=20, expand=True, bgcolor=ft.Colors.GREY_200,
                border_radius=6, shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
            )
            page.add(panel)
            
        except Exception as ex:
            salida.value = f"❌ Error al obtener boleto: {ex}"
            page.update()

    def cerrar_aplicacion(e):
        page.window.close()

    def ver_advertencias_multas(e):
        """Ver advertencias y multas del usuario con diseño mejorado"""
        page.clean()
        
        try:
            # Obtener advertencias
            r_adv = requests.get(f"{API_URL}/advertencias/{id_usuario}")
            data_adv = r_adv.json()
            advertencias = data_adv.get("advertencias", [])
            
            # Obtener multas
            r_mul = requests.get(f"{API_URL}/multas/{id_usuario}")
            data_mul = r_mul.json()
            multas = data_mul.get("multas", [])
            
            # Construir contenido visual
            contenido = []
            
            # === ADVERTENCIAS ===
            if advertencias:
                contenido.append(ft.Text("⚠️ MIS ADVERTENCIAS", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_700))
                contenido.append(ft.Divider(height=10))
                
                for adv in advertencias:
                    fecha = str(adv.get("fecha", ""))[:10]
                    motivo = adv.get("motivo", "Sin especificar")
                    
                    tarjeta_adv = ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("⚠️", size=20),
                                ft.Column([
                                    ft.Text(motivo, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_800),
                                    ft.Text(fecha, size=10, color=ft.Colors.ORANGE_700),
                                ], expand=True),
                            ], spacing=10),
                        ], spacing=5),
                        bgcolor=ft.Colors.ORANGE_50,
                        padding=12,
                        border_radius=8,
                        border=ft.border.all(2, ft.Colors.ORANGE_300),
                    )
                    contenido.append(tarjeta_adv)
                
                contenido.append(ft.Divider(height=20))
            
            # === MULTAS ===
            if multas:
                contenido.append(ft.Text("🚨 MIS MULTAS", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700))
                contenido.append(ft.Divider(height=10))
                
                total_multas = 0
                multas_pendientes = 0
                
                for multa in multas:
                    fecha = str(multa.get("fecha", ""))[:10]
                    monto = multa.get("monto", 0)
                    concepto = multa.get("concepto", "Sin concepto")
                    pagado = multa.get("pagado", False)
                    total_multas += monto
                    
                    if not pagado:
                        multas_pendientes += monto
                    
                    estado_pago = "✅ PAGADA" if pagado else "❌ PENDIENTE"
                    color_estado = ft.Colors.GREEN_700 if pagado else ft.Colors.RED_700
                    color_bg = ft.Colors.GREEN_50 if pagado else ft.Colors.RED_50
                    color_border = ft.Colors.GREEN_300 if pagado else ft.Colors.RED_300
                    
                    tarjeta_multa = ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("🚨", size=20),
                                ft.Column([
                                    ft.Text(concepto, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_800),
                                    ft.Text(f"Fecha: {fecha}", size=10, color=ft.Colors.RED_700),
                                ], expand=True),
                                ft.Column([
                                    ft.Text(f"${monto}", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_800),
                                    ft.Text(estado_pago, size=10, weight=ft.FontWeight.BOLD, color=color_estado),
                                ], horizontal_alignment=ft.CrossAxisAlignment.END),
                            ], spacing=10),
                        ], spacing=5),
                        bgcolor=color_bg,
                        padding=12,
                        border_radius=8,
                        border=ft.border.all(2, color_border),
                    )
                    contenido.append(tarjeta_multa)
                
                contenido.append(ft.Divider(height=15))
                
                # Resumen de multas
                resumen = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Column([
                                ft.Text("TOTAL DE MULTAS", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ft.Text(f"${total_multas}", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ]),
                            ft.Column([
                                ft.Text("PENDIENTE DE PAGO", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ft.Text(f"${multas_pendientes}", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ]),
                        ], spacing=20),
                    ], spacing=5),
                    bgcolor=ft.Colors.RED_700,
                    padding=15,
                    border_radius=8,
                )
                contenido.append(resumen)
            
            # Si no hay advertencias ni multas
            if not advertencias and not multas:
                contenido.append(ft.Container(
                    content=ft.Column([
                        ft.Text("✅ ESTADO LIMPIO", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                        ft.Text("No tienes advertencias ni multas", size=13, color=ft.Colors.GREEN_600),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    bgcolor=ft.Colors.GREEN_50,
                    padding=30,
                    border_radius=8,
                    border=ft.border.all(2, ft.Colors.GREEN_300),
                ))
            
            # Panel wrapper con header
            panel = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.ElevatedButton("VOLVER", on_click=lambda _: usuario_view(page, API_URL, id_usuario), 
                                         bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=100, height=40),
                        ft.Text("ADVERTENCIAS Y MULTAS", size=18, weight=ft.FontWeight.BOLD, 
                               color=ft.Colors.BLUE_900, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Container(width=100),
                    ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=15),
                    ft.Column(contenido, spacing=10, scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
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
                        ft.ElevatedButton("VOLVER", on_click=lambda _: usuario_view(page, API_URL, id_usuario), 
                                         bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=100, height=40),
                        ft.Text("ADVERTENCIAS Y MULTAS", size=18, weight=ft.FontWeight.BOLD, 
                               color=ft.Colors.BLUE_900, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Container(width=100),
                    ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=15),
                    ft.Column([
                        ft.Text("Error", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700),
                        ft.Text(f"❌ {ex}", size=13, color=ft.Colors.RED_600),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                   expand=True),
                padding=20, expand=True, bgcolor=ft.Colors.GREY_200,
                border_radius=6, shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
            )
            page.add(panel)

    # --- UI ---
    titulo = ft.Text("Panel del Usuario", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    logo = ft.Text("SmartPark", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)

    botones = [
        ft.ElevatedButton("TARJETA DIGITAL", on_click=ver_tarjeta_digital, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, expand=True, height=50, width=400),
        ft.ElevatedButton("BOLETO DIGITAL", on_click=ver_boleto_digital, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, expand=True, height=50, width=400),
        ft.ElevatedButton("ADVERTENCIAS/MULTAS", on_click=ver_advertencias_multas, bgcolor=ft.Colors.ORANGE_700, color=ft.Colors.WHITE, expand=True, height=50, width=400),
        ft.ElevatedButton("HISTORIAL", on_click=ver_historial, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, expand=True, height=50, width=400),
        ft.ElevatedButton("AJUSTES DE APLICACION", on_click=lambda e: salida.update(f"La función '{e.control.text}' aún no está disponible.") or page.update(), bgcolor=ft.Colors.BLUE_GREY_700, color=ft.Colors.WHITE, expand=True, height=50, width=400),
        ft.ElevatedButton("CERRAR APLICACION", on_click=cerrar_aplicacion, bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE, expand=True, height=50, width=400),
    ]

    panel = ft.Container(
        content=ft.Column(
            [logo, titulo, ft.Divider(height=15, color=ft.Colors.TRANSPARENT)] + botones + [ft.Divider(height=15, color=ft.Colors.TRANSPARENT), salida],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        padding=40,
        width=420,
        bgcolor=ft.Colors.GREY_200,
        border_radius=6,
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLUE_GREY_100),
    )

    page.add(panel)
