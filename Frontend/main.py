import flet as ft
from pages.usuario_page import usuario_view
from pages.vigilante_page import vigilante_view
from pages.admin_page import admin_view

API_URL = "http://127.0.0.1:8000"

def main(page: ft.Page):
    page.title = "SmartPark - Ingreso"
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # --- UI Elements ---
    logo = ft.Text(
        "SmartPark",
        size=40,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE_900,
    )

    subtitulo = ft.Text(
        "Sistema de gestión de estacionamiento",
        size=16,
        color=ft.Colors.BLUE_GREY_700,
    )

    usuario_input = ft.TextField(
        label="Usuario",
        border_color=ft.Colors.BLUE_800,
        color=ft.Colors.BLUE_GREY_900,
        width=260,
    )

    password_input = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        border_color=ft.Colors.BLUE_800,
        color=ft.Colors.BLUE_GREY_900,
        width=260,
    )

    mensaje = ft.Text("", color=ft.Colors.RED_700, size=13)

    # --- Usuarios de prueba ---
    USUARIOS = {
        "usuario": {"password": "1234", "rol": "usuario"},
        "vigilante": {"password": "abcd", "rol": "vigilante"},
        "admin": {"password": "root", "rol": "admin"},
    }

    # --- Funciones ---
    def login_click(e):
        usuario = usuario_input.value.strip()
        password = password_input.value.strip()
        datos = USUARIOS.get(usuario)

        if datos and password == datos["password"]:
            rol = datos["rol"]
            if rol == "usuario":
                usuario_view(page, API_URL)
            elif rol == "vigilante":
                vigilante_view(page, API_URL)
            elif rol == "admin":
                admin_view(page, API_URL)
        else:
            mensaje.value = "Usuario o contraseña incorrectos."
            page.update()

    boton_login = ft.ElevatedButton(
        text="Iniciar sesión",
        bgcolor=ft.Colors.BLUE_900,
        color=ft.Colors.WHITE,
        width=180,
        height=45,
        on_click=login_click,
    )

    # --- Contenedor principal ---
    panel = ft.Container(
        content=ft.Column(
            [
                logo,
                subtitulo,
                ft.Divider(height=25, color=ft.Colors.TRANSPARENT),
                usuario_input,
                password_input,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                boton_login,
                mensaje,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=40,
        width=400,
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.BLUE_GREY_100),
    )

    page.add(panel)

ft.app(target=main)
