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
        try:
            r = requests.get(f"{API_URL}/historial")
            data = r.json().get("historial", [])
            if data:
                salida.value = "\n".join(
                    [f"Espacio {h['espacio_asignado']} — {h['hora_entrada']}" for h in data]
                )
            else:
                salida.value = "Sin historial registrado."
        except Exception as ex:
            salida.value = f"Error: {ex}"
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

    # --- UI ---
    titulo = ft.Text("Panel del Usuario", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    logo = ft.Text("SmartPark", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)

    botones = [
        ft.ElevatedButton("TARJETA DIGITAL", on_click=ver_tarjeta_digital, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=250, height=45),
        ft.ElevatedButton("BOLETO DIGITAL", on_click=placeholder, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=250, height=45),
        ft.ElevatedButton("NOTIFICACIONES/MULTAS", on_click=placeholder, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=250, height=45),
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
