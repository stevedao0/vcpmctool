# vcpmctool/ui/main_window.py
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, 
    QWidget, QSplitter, QStatusBar, QMenuBar, QToolBar
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon

from .tabs.main_processing_tab import MainProcessingTab
from .tabs.royalty_tab import RoyaltyTab
from .tabs.settings_tab import SettingsTab
from .tabs.help_tab import HelpTab
from services.settings import Settings
from services.logger import Logger


class MainWindow(QMainWindow):
    """Cửa sổ chính của ứng dụng VCPMC Tool"""
    
    def __init__(self, settings: Settings, logger: Logger):
        super().__init__()
        self.settings = settings
        self.logger = logger
        
        self.setWindowTitle("VCPMC Tool v2.0")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_tool_bar()
        self._setup_status_bar()
        self._apply_theme()
        
    def _setup_ui(self):
        """Thiết lập giao diện chính"""
        # Widget trung tâm
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout chính
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setMovable(True)
        
        # Tạo các tab
        self.main_tab = MainProcessingTab(self.settings, self.logger)
        self.royalty_tab = RoyaltyTab(self.logger)
        self.settings_tab = SettingsTab(self.settings, self)
        self.help_tab = HelpTab()
        
        # Thêm các tab
        self.tab_widget.addTab(self.main_tab, "📁 Xử lý chính")
        self.tab_widget.addTab(self.royalty_tab, "💰 Nhuận bút")
        self.tab_widget.addTab(self.settings_tab, "⚙️ Cài đặt")
        self.tab_widget.addTab(self.help_tab, "❓ Hướng dẫn")
        
        layout.addWidget(self.tab_widget)
        
    def _setup_menu_bar(self):
        """Thiết lập menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Mở file...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.main_tab.select_files)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Thoát", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        process_action = QAction("📁 &Xử lý file", self)
        process_action.setShortcut("F5")
        process_action.triggered.connect(self.main_tab.process_files)
        tools_menu.addAction(process_action)
        
        royalty_action = QAction("💰 &Tính nhuận bút", self)
        royalty_action.setShortcut("F6")
        royalty_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        tools_menu.addAction(royalty_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&Giới thiệu", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
    def _setup_tool_bar(self):
        """Thiết lập toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)
        
        # Open files action
        open_action = QAction("📂 Mở file", self)
        open_action.triggered.connect(self.main_tab.select_files)
        toolbar.addAction(open_action)
        
        toolbar.addSeparator()
        
        # Process action
        process_action = QAction("🚀 Xử lý", self)
        process_action.triggered.connect(self.main_tab.process_files)
        toolbar.addAction(process_action)
        
        toolbar.addSeparator()
        
        # Royalty action
        royalty_action = QAction("💵 Nhuận bút", self)
        royalty_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        toolbar.addAction(royalty_action)
        
    def _setup_status_bar(self):
        """Thiết lập status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Sẵn sàng")
        
    def _apply_theme(self):
        """Áp dụng theme"""
        if self.settings.theme_mode == "dark":
            self._apply_dark_theme()
        else:
            self._apply_light_theme()
            
    def _apply_dark_theme(self):
        """Áp dụng theme tối"""
        dark_stylesheet = """
        QMainWindow {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        QWidget {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        QTabWidget::pane {
            border: 1px solid #404040;
            background-color: #2d2d2d;
        }
        QTabBar::tab {
            background-color: #404040;
            color: #ffffff;
            padding: 10px 20px;
            margin-right: 2px;
            border: 1px solid #555555;
            border-bottom: none;
            border-radius: 8px 8px 0px 0px;
            font-weight: 500;
        }
        QTabBar::tab:selected {
            background-color: #0078d4;
            color: #ffffff;
            border-color: #0078d4;
        }
        QTabBar::tab:hover {
            background-color: #505050;
            color: #ffffff;
        }
        QGroupBox {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 2px solid #404040;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px 0 8px;
            color: #ffffff;
            background-color: #2d2d2d;
        }
        QPushButton {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 500;
        }
        QPushButton:hover {
            background-color: #505050;
            border-color: #666666;
        }
        QPushButton:pressed {
            background-color: #353535;
        }
        QPushButton:disabled {
            background-color: #2a2a2a;
            color: #666666;
            border-color: #333333;
        }
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 6px;
            border-radius: 4px;
        }
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
            border-color: #0078d4;
        }
        QTableWidget {
            background-color: #2d2d2d;
            color: #ffffff;
            gridline-color: #404040;
            border: 1px solid #404040;
            border-radius: 4px;
        }
        QTableWidget::item {
            background-color: #2d2d2d;
            color: #ffffff;
            padding: 8px;
        }
        QTableWidget::item:selected {
            background-color: #0078d4;
            color: #ffffff;
        }
        QTableWidget::item:alternate {
            background-color: #353535;
        }
        QHeaderView::section {
            background-color: #404040;
            color: #ffffff;
            padding: 8px;
            border: 1px solid #555555;
            font-weight: bold;
        }
        QListWidget {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #404040;
            border-radius: 4px;
        }
        QListWidget::item {
            color: #ffffff;
            padding: 4px;
        }
        QListWidget::item:selected {
            background-color: #0078d4;
        }
        QTextEdit {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #404040;
            border-radius: 4px;
        }
        QProgressBar {
            background-color: #404040;
            border: 1px solid #555555;
            border-radius: 4px;
            text-align: center;
            color: #ffffff;
        }
        QProgressBar::chunk {
            background-color: #0078d4;
            border-radius: 3px;
        }
        QCheckBox {
            color: #ffffff;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #555555;
            border-radius: 3px;
            background-color: #404040;
        }
        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border-color: #0078d4;
        }
        QLabel {
            color: #ffffff;
        }
        QMenuBar {
            background-color: #2d2d2d;
            color: #ffffff;
            border-bottom: 1px solid #404040;
        }
        QMenuBar::item {
            background-color: transparent;
            padding: 6px 12px;
        }
        QMenuBar::item:selected {
            background-color: #404040;
        }
        QMenu {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #404040;
        }
        QMenu::item {
            padding: 6px 20px;
        }
        QMenu::item:selected {
            background-color: #0078d4;
        }
        QToolBar {
            background-color: #2d2d2d;
            border: none;
            spacing: 4px;
        }
        QStatusBar {
            background-color: #2d2d2d;
            color: #ffffff;
            border-top: 1px solid #404040;
        }
        }
        """
        self.setStyleSheet(dark_stylesheet)
        
    def _apply_light_theme(self):
        """Áp dụng theme sáng"""
        light_stylesheet = """
        QMainWindow {
            background-color: #ffffff;
            color: #000000;
        }
        QWidget {
            background-color: #ffffff;
            color: #000000;
        }
        QTabWidget::pane {
            border: 1px solid #e0e0e0;
            background-color: #ffffff;
        }
        QTabBar::tab {
            background-color: #f8f9fa;
            color: #000000;
            padding: 10px 20px;
            margin-right: 2px;
            border: 1px solid #e0e0e0;
            border-bottom: none;
            border-radius: 8px 8px 0px 0px;
            font-weight: 500;
        }
        QTabBar::tab:selected {
            background-color: #0078d4;
            color: #ffffff;
            border-color: #0078d4;
        }
        QTabBar::tab:hover {
            background-color: #e9ecef;
            color: #000000;
        }
        QGroupBox {
            background-color: #ffffff;
            color: #000000;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px 0 8px;
            color: #000000;
            background-color: #ffffff;
        }
        QPushButton {
            background-color: #f8f9fa;
            color: #000000;
            border: 1px solid #dee2e6;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 500;
        }
        QPushButton:hover {
            background-color: #e9ecef;
            border-color: #adb5bd;
        }
        QPushButton:pressed {
            background-color: #dee2e6;
        }
        QPushButton:disabled {
            background-color: #f8f9fa;
            color: #6c757d;
            border-color: #dee2e6;
        }
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #ced4da;
            padding: 6px;
            border-radius: 4px;
        }
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
            border-color: #0078d4;
        }
        QTableWidget {
            background-color: #ffffff;
            color: #000000;
            gridline-color: #e0e0e0;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
        }
        QTableWidget::item {
            background-color: #ffffff;
            color: #000000;
            padding: 8px;
        }
        QTableWidget::item:selected {
            background-color: #0078d4;
            color: #ffffff;
        }
        QTableWidget::item:alternate {
            background-color: #f8f9fa;
        }
        QHeaderView::section {
            background-color: #f8f9fa;
            color: #000000;
            padding: 8px;
            border: 1px solid #dee2e6;
            font-weight: bold;
        }
        QListWidget {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
        }
        QListWidget::item {
            color: #000000;
            padding: 4px;
        }
        QListWidget::item:selected {
            background-color: #0078d4;
            color: #ffffff;
        }
        QTextEdit {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
        }
        QProgressBar {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            text-align: center;
            color: #000000;
        }
        QProgressBar::chunk {
            background-color: #0078d4;
            border-radius: 3px;
        }
        QCheckBox {
            color: #000000;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #ced4da;
            border-radius: 3px;
            background-color: #ffffff;
        }
        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border-color: #0078d4;
        }
        QLabel {
            color: #000000;
        }
        QMenuBar {
            background-color: #f8f9fa;
            color: #000000;
            border-bottom: 1px solid #e0e0e0;
        }
        QMenuBar::item {
            background-color: transparent;
            padding: 6px 12px;
        }
        QMenuBar::item:selected {
            background-color: #e9ecef;
        }
        QMenu {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #e0e0e0;
        }
        QMenu::item {
            padding: 6px 20px;
        }
        QMenu::item:selected {
            background-color: #0078d4;
            color: #ffffff;
        }
        QToolBar {
            background-color: #f8f9fa;
            border: none;
            spacing: 4px;
        }
        QStatusBar {
            background-color: #f8f9fa;
            color: #000000;
            border-top: 1px solid #e0e0e0;
        }
        """
        self.setStyleSheet(light_stylesheet)
        
    def _show_about(self):
        """Hiển thị dialog giới thiệu"""
        from PySide6.QtWidgets import QMessageBox
        
        QMessageBox.about(
            self,
            "Giới thiệu VCPMC Tool",
            """
            <h3>VCPMC Tool v2.0</h3>
            <p>Công cụ xử lý dữ liệu tác phẩm âm nhạc</p>
            <p><b>Tính năng:</b></p>
            <ul>
                <li>Xử lý file Excel tác phẩm</li>
                <li>Tính toán nhuận bút tự động</li>
                <li>Tạo link YouTube với timestamp</li>
                <li>Quản lý thời hạn và gia hạn</li>
            </ul>
            <p><b>Phiên bản:</b> 2.0.0</p>
            <p><b>Công nghệ:</b> Python + PySide6</p>
            <p>© 2024 VCPMC Tool</p>
            """
        )
        
    def update_status(self, message: str):
        """Cập nhật status bar"""
        self.status_bar.showMessage(message)
        
    def toggle_theme(self):
        """Chuyển đổi theme"""
        if self.settings.theme_mode == "light":
            self.settings.theme_mode = "dark"
        else:
            self.settings.theme_mode = "light"
        self._apply_theme()