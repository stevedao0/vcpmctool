# vcpmctool/main.py - PySide6 Version
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont
from ui.main_window import MainWindow
from services.settings import Settings
from services.logger import Logger


def main():
    # Tạo QApplication
    app = QApplication(sys.argv)
    
    # Cấu hình ứng dụng
    app.setApplicationName("VCPMC Tool")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("VCPMC")
    
    # Thiết lập font mặc định
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    # Thiết lập style
    app.setStyle("Fusion")
    
    # Khởi tạo services
    settings = Settings()
    logger = Logger("vcpmctool.log")
    
    # Tạo và hiển thị cửa sổ chính
    window = MainWindow(settings, logger)
    window.show()
    
    # Chạy ứng dụng
    sys.exit(app.exec())


if __name__ == "__main__":
    main()