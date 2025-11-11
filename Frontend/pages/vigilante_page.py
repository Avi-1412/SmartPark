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

    def ver_datos_usuarios(e):
        """Mostrar tabla de todos los usuarios"""
        salida.value = ""
        page.update()

        try:
            r = requests.get(f"{API_URL}/usuarios")
            usuarios = r.json().get("usuarios", [])

            if not usuarios:
                salida.value = "No hay usuarios registrados."
                page.update()
                return

            # Crear tabla de usuarios
            tabla = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID")),
                    ft.DataColumn(ft.Text("Nombre")),
                    ft.DataColumn(ft.Text("Celular")),
                    ft.DataColumn(ft.Text("Matrícula")),
                    ft.DataColumn(ft.Text("Placa")),
                    ft.DataColumn(ft.Text("Marca")),
                    ft.DataColumn(ft.Text("Modelo")),
                ],
                rows=[],
            )

            # Agregar filas a la tabla
            for u in usuarios:
                autos = u.get("autos", [])
                
                if autos:
                    # Si hay vehículos, mostrar una fila por vehículo CON datos del usuario en cada fila
                    for auto in autos:
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
                            ]
                        )
                    )

            # Mostrar la tabla
            page.clean()
            
            boton_volver = ft.ElevatedButton(
                "← Volver al Menú",
                on_click=lambda _: vigilante_view(page, API_URL),
                bgcolor=ft.Colors.BLUE_GREY_700,
                color=ft.Colors.WHITE,
                width=260,
                height=40
            )
            
            page.add(
                ft.Column([
                    ft.Text("Datos de Usuarios", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                    ft.Divider(height=10),
                    tabla,
                    ft.Divider(height=20),
                    boton_volver,
                    ft.Divider(height=10),
                    salida
                ],
                scroll=ft.ScrollMode.AUTO,
                )
            )

        except Exception as ex:
            salida.value = f"❌ Error al obtener datos: {ex}"
            page.update()

    titulo = ft.Text("Panel del Vigilante", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    logo = ft.Text("SmartPark", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)

    botones = [
        ft.ElevatedButton("VER DATOS DE USUARIOS", on_click=ver_datos_usuarios, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=250, height=45),
        ft.ElevatedButton("ENVIAR ADVERTENCIA", on_click=placeholder, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=250, height=45),
        ft.ElevatedButton("ENVIAR MULTA", on_click=placeholder, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, width=250, height=45),
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
