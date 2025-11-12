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
                    page.add(
                        ft.Column([
                            ft.Text("Mi Historial de Accesos", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                            ft.Divider(height=20),
                            ft.Text("No hay historial disponible", size=14, color=ft.Colors.BLUE_GREY_700),
                            ft.Divider(height=20),
                            ft.ElevatedButton(
                                "← Volver al Menú",
                                on_click=lambda _: usuario_view(page, API_URL, id_usuario),
                                bgcolor=ft.Colors.BLUE_GREY_700,
                                color=ft.Colors.WHITE,
                                width=260,
                                height=40
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=15,
                        )
                    )
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
                    "← Volver al Menú",
                    on_click=lambda _: usuario_view(page, API_URL, id_usuario),
                    bgcolor=ft.Colors.BLUE_GREY_700,
                    color=ft.Colors.WHITE,
                    width=260,
                    height=40
                )
                
                page.add(
                    ft.Column([
                        ft.Text("Mi Historial de Accesos", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                        ft.Divider(height=10),
                        ft.Container(content=tabla_historial, width=800, height=400),
                        ft.Divider(height=20),
                        boton_volver,
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                    )
                )
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
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.BLUE_GREY_300),
                padding=0,
                width=350,
            )
            
            # Mostrar tarjeta
            page.clean()
            
            boton_volver = ft.ElevatedButton(
                "← Volver al Menú",
                on_click=lambda _: usuario_view(page, API_URL, id_usuario),
                bgcolor=ft.Colors.BLUE_GREY_700,
                color=ft.Colors.WHITE,
                width=260,
                height=40
            )
            
            page.add(
                ft.Column([
                    ft.Text("Mi Tarjeta Digital", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                    ft.Divider(height=20),
                    tarjeta,
                    ft.Divider(height=20),
                    boton_volver,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
                )
            )
            
        except Exception as ex:
            salida.value = f"❌ Error al obtener tarjeta: {ex}"
            page.update()

    # --- Funciones futuras (sin implementación aún) ---
    def placeholder(e):
        salida.value = f"La función '{e.control.text}' aún no está disponible."
        page.update()

    def cerrar_aplicacion(e):
        page.window.close()

    def ver_advertencias_multas(e):
        """Ver advertencias y multas del usuario"""
        salida.value = ""
        page.update()

        try:
            # Obtener advertencias
            r_adv = requests.get(f"{API_URL}/advertencias/{id_usuario}")
            data_adv = r_adv.json()
            advertencias = data_adv.get("advertencias", [])
            
            # Obtener multas
            r_mul = requests.get(f"{API_URL}/multas/{id_usuario}")
            data_mul = r_mul.json()
            multas = data_mul.get("multas", [])
            
            # Construir contenido
            contenido = []
            
            if advertencias:
                contenido.append(ft.Text("⚠️ MIS ADVERTENCIAS", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_700))
                for adv in advertencias:
                    fecha = str(adv.get("fecha", ""))[:10]
                    contenido.append(ft.Text(f"  • {fecha} - {adv.get('motivo', '')}", size=11))
                contenido.append(ft.Divider(height=10))
            
            if multas:
                contenido.append(ft.Text("🚨 MIS MULTAS", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700))
                total_multas = 0
                for multa in multas:
                    fecha = str(multa.get("fecha", ""))[:10]
                    monto = multa.get("monto", 0)
                    pagado = "✅ PAGADA" if multa.get("pagado") else "❌ PENDIENTE"
                    total_multas += monto
                    contenido.append(ft.Text(
                        f"  • {fecha} | ${monto} | {multa.get('concepto', '')} | {pagado}",
                        size=11
                    ))
                contenido.append(ft.Divider(height=10))
                contenido.append(ft.Text(f"TOTAL A PAGAR: ${total_multas}", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700))
            
            if not advertencias and not multas:
                contenido.append(ft.Text("✅ No tienes advertencias ni multas", size=12, color=ft.Colors.GREEN_700))
            
            salida.value = ft.Column(contenido, scroll=ft.ScrollMode.AUTO, spacing=6)
            page.update()
            
        except Exception as ex:
            salida.value = f"Error: {ex}"
            page.update()

    # --- UI ---
    titulo = ft.Text("Panel del Usuario", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    logo = ft.Text("SmartPark", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)

    botones = [
        ft.ElevatedButton("TARJETA DIGITAL", on_click=ver_tarjeta_digital, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=250, height=45),
        ft.ElevatedButton("BOLETO DIGITAL", on_click=placeholder, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=250, height=45),
        ft.ElevatedButton("ADVERTENCIAS/MULTAS", on_click=ver_advertencias_multas, bgcolor=ft.Colors.ORANGE_700, color=ft.Colors.WHITE, width=250, height=45),
        ft.ElevatedButton("HISTORIAL", on_click=ver_historial, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=250, height=45),
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
