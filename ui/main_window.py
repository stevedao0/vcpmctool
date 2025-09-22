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
        self.tab_widget.addTab(self.main_tab, "Xử lý chính")
        self.tab_widget.addTab(self.royalty_tab, "Nhuận bút")
        self.tab_widget.addTab(self.settings_tab, "Cài đặt")
        self.tab_widget.addTab(self.help_tab, "Hướng dẫn")
        
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
        
        process_action = QAction("&Xử lý file", self)
        process_action.setShortcut("F5")
        process_action.triggered.connect(self.main_tab.process_files)
        tools_menu.addAction(process_action)
        
        royalty_action = QAction("&Tính nhuận bút", self)
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
        # Không tạo toolbar để tránh trùng lặp với tabs
        pass
        
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
        /* === MODERN DARK THEME - DISCORD/VS CODE INSPIRED === */
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                stop:0 #1a1a2e, stop:1 #16213e);
            color: #e2e8f0;
        }
        
        QWidget {
            background-color: transparent;
            color: #e2e8f0;
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 13px;
        }
        
        /* === TABS - MODERN DARK === */
        QTabWidget::pane {
            border: 1px solid #334155;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1e293b, stop:1 #0f172a);
            border-radius: 12px;
            margin-top: 2px;
        }
        
        QTabBar::tab {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #374151, stop:1 #1f2937);
            color: #9ca3af;
            padding: 14px 28px;
            margin-right: 2px;
            border: 1px solid #4b5563;
            border-bottom: none;
            border-radius: 12px 12px 0 0;
            font-weight: 600;
            font-size: 14px;
            min-width: 120px;
        }
        
        QTabBar::tab:selected {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #3b82f6, stop:0.5 #6366f1, stop:1 #8b5cf6);
            color: #ffffff;
            border-color: #3b82f6;
            font-weight: 700;
        }
        
        QTabBar::tab:hover:!selected {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4b5563, stop:1 #374151);
            color: #d1d5db;
        }
        
        /* === GROUPBOX - ELEGANT DARK === */
        QGroupBox {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1e293b, stop:1 #0f172a);
            border: 1px solid #334155;
            border-radius: 12px;
            margin-top: 16px;
            padding-top: 20px;
            font-weight: 600;
            color: #cbd5e1;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 16px;
            padding: 6px 16px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #6366f1, stop:1 #8b5cf6);
            color: #ffffff;
            border-radius: 6px;
            font-weight: 700;
            font-size: 12px;
        }
        
        /* === BUTTONS - COLORFUL ACCENTS === */
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #374151, stop:1 #1f2937);
            color: #e2e8f0;
            border: 1px solid #4b5563;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            min-height: 18px;
        }
        
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4b5563, stop:1 #374151);
            border-color: #6b7280;
            transform: translateY(-1px);
        }
        
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1f2937, stop:1 #111827);
            transform: translateY(0px);
        }
        
        QPushButton:disabled {
            background: #1f2937;
            color: #6b7280;
            border-color: #374151;
        }
        
        /* === PRIMARY BUTTON - BLUE GRADIENT === */
        QPushButton[class="primary"] {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #3b82f6, stop:1 #1d4ed8);
            color: #ffffff;
            border-color: #3b82f6;
            font-weight: 700;
        }
        
        QPushButton[class="primary"]:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #2563eb, stop:1 #1e40af);
            border-color: #2563eb;
        }
        
        /* === SUCCESS BUTTON - GREEN GRADIENT === */
        QPushButton[class="success"] {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #10b981, stop:1 #059669);
            color: #ffffff;
            border-color: #10b981;
            font-weight: 700;
        }
        
        QPushButton[class="success"]:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #059669, stop:1 #047857);
            border-color: #059669;
        }
        
        /* === INPUTS - MODERN DARK === */
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1e293b, stop:1 #0f172a);
            color: #e2e8f0;
            border: 1px solid #475569;
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 13px;
        }
        
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
            border-color: #64748b;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #334155, stop:1 #1e293b);
            box-shadow: 0 0 0 2px rgba(100, 116, 139, 0.2);
        }
        
        /* === TABLES - ELEGANT DARK === */
        QTableWidget {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1e293b, stop:1 #0f172a);
            color: #e2e8f0;
            gridline-color: #334155;
            border: 1px solid #334155;
            border-radius: 8px;
            selection-background-color: #3b82f6;
            selection-color: #ffffff;
        }
        
        QTableWidget::item {
            padding: 12px 8px;
            border-bottom: 1px solid #1e293b;
            border-right: 1px solid #334155;
        }
        
        QTableWidget::item:alternate {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #334155, stop:1 #1e293b);
        }
        
        QTableWidget::item:selected {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #475569, stop:1 #64748b);
            color: #ffffff;
        }
        
        /* === TABLE INPUT CELLS === */
        QTableWidget QLineEdit, QTableWidget QSpinBox {
            background: transparent;
            border: none;
            padding: 8px 12px;
            color: #e2e8f0;
            font-size: 13px;
            border-radius: 4px;
        }
        
        QTableWidget QLineEdit:focus, QTableWidget QSpinBox:focus {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #334155, stop:1 #475569);
            border: 1px solid #64748b;
            box-shadow: none;
        }
        
        QHeaderView::section {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #6366f1, stop:1 #8b5cf6);
            color: #ffffff;
            padding: 12px 8px;
            border: 1px solid #4c1d95;
            font-weight: 700;
            font-size: 12px;
        }
        
        /* === LISTS === */
        QListWidget {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1e293b, stop:1 #0f172a);
            color: #e2e8f0;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 4px;
        }
        
        QListWidget::item {
            padding: 10px 14px;
            border-radius: 6px;
            margin: 2px 0;
        }
        
        QListWidget::item:selected {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #3b82f6, stop:1 #6366f1);
            color: #ffffff;
        }
        
        QListWidget::item:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #334155, stop:1 #1e293b);
        }
        
        /* === TEXT EDIT === */
        QTextEdit {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1e293b, stop:1 #0f172a);
            color: #e2e8f0;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 8px;
            font-family: 'Consolas', 'JetBrains Mono', monospace;
            font-size: 12px;
        }
        
        /* === PROGRESS BAR - COLORFUL === */
        QProgressBar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1e293b, stop:1 #0f172a);
            border: 1px solid #334155;
            border-radius: 8px;
            text-align: center;
            color: #e2e8f0;
            font-weight: 600;
            height: 24px;
        }
        
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #10b981, stop:0.5 #3b82f6, stop:1 #8b5cf6);
            border-radius: 7px;
            margin: 1px;
        }
        
        /* === CHECKBOX - MODERN === */
        QCheckBox {
            color: #e2e8f0;
            spacing: 10px;
            font-weight: 500;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #475569;
            border-radius: 4px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1e293b, stop:1 #0f172a);
        }
        
        QCheckBox::indicator:checked {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #3b82f6, stop:1 #6366f1);
            border-color: #3b82f6;
        }
        
        /* === MENU BAR === */
        QMenuBar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1e293b, stop:1 #0f172a);
            color: #e2e8f0;
            border-bottom: 1px solid #334155;
            padding: 4px 0;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 8px 16px;
            border-radius: 6px;
            margin: 0 2px;
        }
        
        QMenuBar::item:selected {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #3b82f6, stop:1 #6366f1);
            color: #ffffff;
        }
        
        QMenu {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1e293b, stop:1 #0f172a);
            color: #e2e8f0;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 4px;
        }
        
        QMenu::item {
            padding: 8px 16px;
            border-radius: 6px;
            margin: 1px;
        }
        
        QMenu::item:selected {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #3b82f6, stop:1 #6366f1);
            color: #ffffff;
        }
        
        /* === STATUS BAR === */
        QStatusBar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1e293b, stop:1 #0f172a);
            color: #94a3b8;
            border-top: 1px solid #334155;
            padding: 6px 12px;
        }
        """
        self.setStyleSheet(dark_stylesheet)
        
    def _apply_light_theme(self):
        """Áp dụng theme sáng"""
        light_stylesheet = """
        /* === CLEAN MINIMAL DESIGN === */
        QMainWindow {
            background-color: #f8f9fa;
            color: #212529;
        }
        
        QWidget {
            background-color: transparent;
            color: #212529;
            font-family: 'Segoe UI', sans-serif;
            font-size: 13px;
        }
        
        /* === TABS - CLEAN & MINIMAL === */
        QTabWidget::pane {
            border: 1px solid #dee2e6;
            background-color: #ffffff;
            border-radius: 8px;
            margin-top: 2px;
        }
        
        QTabBar::tab {
            background-color: #ffffff;
            color: #6c757d;
            padding: 12px 24px;
            margin-right: 2px;
            border: 1px solid #dee2e6;
            border-bottom: none;
            border-radius: 8px 8px 0 0;
            font-weight: 500;
            min-width: 100px;
        }
        
        QTabBar::tab:selected {
            background-color: #0d6efd;
            color: #ffffff;
            border-color: #0d6efd;
            font-weight: 600;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #e9ecef;
            color: #495057;
        }
        
        /* === GROUPBOX - SIMPLE & CLEAN === */
        QGroupBox {
            background-color: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 16px;
            font-weight: 600;
            color: #495057;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 4px 12px;
            background-color: #0d6efd;
            color: #ffffff;
            border-radius: 4px;
            font-weight: 600;
            font-size: 12px;
        }
        
        /* === BUTTONS - CONSISTENT DESIGN === */
        QPushButton {
            background-color: #ffffff;
            color: #495057;
            border: 1px solid #ced4da;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: 500;
            min-height: 16px;
        }
        
        QPushButton:hover {
            background-color: #f8f9fa;
            border-color: #adb5bd;
        }
        
        QPushButton:pressed {
            background-color: #e9ecef;
        }
        
        QPushButton:disabled {
            background-color: #f8f9fa;
            color: #adb5bd;
            border-color: #e9ecef;
        }
        
        /* === PRIMARY BUTTON === */
        QPushButton[class="primary"] {
            background-color: #0d6efd;
            color: #ffffff;
            border-color: #0d6efd;
            font-weight: 600;
        }
        
        QPushButton[class="primary"]:hover {
            background-color: #0b5ed7;
            border-color: #0a58ca;
        }
        
        /* === SUCCESS BUTTON === */
        QPushButton[class="success"] {
            background-color: #198754;
            color: #ffffff;
            border-color: #198754;
            font-weight: 600;
        }
        
        QPushButton[class="success"]:hover {
            background-color: #157347;
            border-color: #146c43;
        }
        
        /* === INPUTS - CLEAN & CONSISTENT === */
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background-color: #ffffff;
            color: #212529;
            border: 1px solid #ced4da;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 13px;
        }
        
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
            border-color: #86b7fe;
            box-shadow: 0 0 0 2px rgba(13, 110, 253, 0.25);
        }
        
        /* === TABLES - CLEAN DESIGN === */
        QTableWidget {
            background-color: #ffffff;
            color: #212529;
            gridline-color: #dee2e6;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            selection-background-color: #0d6efd;
            selection-color: #ffffff;
        }
        
        QTableWidget::item {
            padding: 12px 8px;
            border-bottom: 1px solid #f8f9fa;
        }
        
        QTableWidget::item:alternate {
            background-color: #f8f9fa;
        }
        
        QHeaderView::section {
            background-color: #e9ecef;
            color: #495057;
            padding: 12px 8px;
            border: 1px solid #dee2e6;
            font-weight: 600;
            font-size: 12px;
        }
        
        /* === LISTS === */
        QListWidget {
            background-color: #ffffff;
            color: #212529;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 4px;
        }
        
        QListWidget::item {
            padding: 8px 12px;
            border-radius: 4px;
            margin: 1px 0;
        }
        
        QListWidget::item:selected {
            background-color: #0d6efd;
            color: #ffffff;
        }
        
        QListWidget::item:hover {
            background-color: #f8f9fa;
        }
        
        /* === TEXT EDIT === */
        QTextEdit {
            background-color: #ffffff;
            color: #212529;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 8px;
            font-family: 'Consolas', monospace;
            font-size: 12px;
        }
        
        /* === PROGRESS BAR === */
        QProgressBar {
            background-color: #e9ecef;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            text-align: center;
            color: #495057;
            font-weight: 500;
            height: 20px;
        }
        
        QProgressBar::chunk {
            background-color: #0d6efd;
            border-radius: 5px;
            margin: 1px;
        }
        
        /* === CHECKBOX === */
        QCheckBox {
            color: #212529;
            spacing: 8px;
            font-weight: 500;
        }
        
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            background-color: #ffffff;
        }
        
        QCheckBox::indicator:checked {
            background-color: #0d6efd;
            border-color: #0d6efd;
        }
        
        /* === MENU BAR === */
        QMenuBar {
            background-color: #ffffff;
            color: #495057;
            border-bottom: 1px solid #dee2e6;
            padding: 4px 0;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 8px 16px;
            border-radius: 4px;
            margin: 0 2px;
        }
        
        QMenuBar::item:selected {
            background-color: #f8f9fa;
            color: #0d6efd;
        }
        
        QMenu {
            background-color: #ffffff;
            color: #212529;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 4px;
        }
        
        QMenu::item {
            padding: 8px 16px;
            border-radius: 4px;
            margin: 1px;
        }
        
        QMenu::item:selected {
            background-color: #0d6efd;
            color: #ffffff;
        }
        
        /* === STATUS BAR === */
        QStatusBar {
            background-color: #ffffff;
            color: #6c757d;
            border-top: 1px solid #dee2e6;
            padding: 4px 12px;
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