# vcpmctool/services/settings.py
class Settings:
    def __init__(self):
        self.theme_mode = "premium"  # "light", "dark", or "premium"
        self.font_size = 9
        self.auto_propercase = True
        self.auto_backup = True
        self.validate_data = True
        self.default_initial_term = 2
        self.default_ext_term = 2
        self.max_preview_rows = 50
        self.log_level = "INFO"
        self.multithread = True
        self.ui_scale = 100
