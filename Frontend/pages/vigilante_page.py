import flet as ft
import requests

def vigilante_view(page: ft.Page, API_URL: str):
    page.clean()
    page.title = "SmartPark - Vigilante"
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    salida = ft.Text("", size=14, color=ft.Colors.BLUE_GREY_900, selectable=True)

    # --- Funciones ---
    def placeholder(e):
        salida.value = f"La función '{e.control.text}' aún no está disponible."
        page.update()

    def cerrar_aplicacion(e):
        page.window.close()

    titulo = ft.Text("Panel del Vigilante", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    logo = ft.Text("SmartPark", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)

    botones = [
        ft.ElevatedButton("Ver datos de usuarios", on_click=placeholder, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=250, height=45),
        ft.ElevatedButton("Enviar advertencia", on_click=placeholder, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=250, height=45),
        ft.ElevatedButton("Enviar multa", on_click=placeholder, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=250, height=45),
        ft.ElevatedButton("Ajustes", on_click=placeholder, bgcolor=ft.Colors.BLUE_GREY_700, color=ft.Colors.WHITE, width=250, height=45),
        ft.ElevatedButton("Cerrar aplicación", on_click=cerrar_aplicacion, bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE, width=250, height=45),
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
