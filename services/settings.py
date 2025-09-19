# vcpmctool/services/settings.py
from flet import ThemeMode


class Settings:
    def __init__(self):
        self.theme_mode = ThemeMode.LIGHT
        self.auto_propercase = True
