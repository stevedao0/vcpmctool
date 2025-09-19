# vcpmctool/main.py
import flet as ft
from ui.app_layout import create_app_layout
from services.settings import Settings
from services.logger import Logger


def main(page: ft.Page):
    settings = Settings()
    logger = Logger("vcpmctool.log")  # Tạo file log
    page.title = "VCPMC Tool"
    page.theme_mode = settings.theme_mode
    page.add(create_app_layout(page, settings, logger))


if __name__ == "__main__":
    ft.app(target=main)
