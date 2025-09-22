# vcpmctool/ui/main_window.py - Premium Glass Morphism UI
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
    """Cửa sổ chính với Premium Glass Morphism UI"""
    
    def __init__(self, settings: Settings, logger: Logger):
        super().__init__()
        self.settings = settings
        self.logger = logger
        
        self.setWindowTitle("VCPMC Tool v2.0 - Premium Edition")
        self.setMinimumSize(1000, 700)
        self.resize(1300, 850)
        
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_status_bar()
        self._apply_premium_theme()
        
    def _setup_ui(self):
        """Thiết lập giao diện chính"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Tab widget với glass effect
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setMovable(True)
        
        # Tạo các tab
        self.main_tab = MainProcessingTab(self.settings, self.logger)
        self.royalty_tab = RoyaltyTab(self.logger)
        self.settings_tab = SettingsTab(self.settings, self)
        self.help_tab = HelpTab()
        
        # Thêm các tab với icons
        self.tab_widget.addTab(self.main_tab, "🏠 Xử lý chính")
        self.tab_widget.addTab(self.royalty_tab, "💎 Nhuận bút")
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
        
    def _setup_status_bar(self):
        """Thiết lập status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("🚀 Premium Edition - Sẵn sàng")
        
    def _apply_premium_theme(self):
        """Áp dụng Premium Glass Morphism Theme"""
        premium_stylesheet = """
        /* === PREMIUM GLASS MORPHISM UI === */
        QMainWindow {
            background: qradialgradient(cx:0.3, cy:0.3, radius:1.2,
                stop:0 #667eea, stop:0.3 #764ba2, stop:0.6 #f093fb, stop:1 #f5576c);
            color: #ffffff;
        }
        
        QWidget {
            background-color: transparent;
            color: #ffffff;
            font-family: 'SF Pro Display', 'Segoe UI Variable', 'Inter', sans-serif;
            font-size: 14px;
            font-weight: 400;
        }
        
        /* === GLASS MORPHISM TABS === */
        QTabWidget::pane {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 24px;
            margin-top: 8px;
        }
        
        QTabBar::tab {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            color: rgba(255, 255, 255, 0.7);
            padding: 16px 32px;
            margin-right: 4px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-bottom: none;
            border-radius: 16px 16px 0 0;
            font-weight: 600;
            font-size: 15px;
            min-width: 140px;
        }
        
        QTabBar::tab:selected {
            background: rgba(255, 255, 255, 0.25);
            backdrop-filter: blur(30px);
            color: #ffffff;
            border-color: rgba(255, 255, 255, 0.3);
            font-weight: 700;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        QTabBar::tab:hover:!selected {
            background: rgba(255, 255, 255, 0.12);
            color: rgba(255, 255, 255, 0.9);
        }
        
        /* === GLASS GROUPBOX === */
        QGroupBox {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 20px;
            margin-top: 20px;
            padding-top: 24px;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.95);
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 20px;
            padding: 8px 20px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(255, 255, 255, 0.3), stop:1 rgba(255, 255, 255, 0.1));
            backdrop-filter: blur(15px);
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            font-weight: 700;
            font-size: 13px;
        }
        
        /* === PREMIUM BUTTONS === */
        QPushButton {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(15px);
            color: rgba(255, 255, 255, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 14px 28px;
            border-radius: 12px;
            font-weight: 600;
            min-height: 20px;
        }
        
        QPushButton:hover {
            background: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }
        
        QPushButton:pressed {
            background: rgba(255, 255, 255, 0.05);
            transform: translateY(0px);
        }
        
        QPushButton:disabled {
            background: rgba(255, 255, 255, 0.03);
            color: rgba(255, 255, 255, 0.3);
            border-color: rgba(255, 255, 255, 0.1);
        }
        
        /* === PREMIUM PRIMARY BUTTON === */
        QPushButton[class="primary"] {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(99, 102, 241, 0.8), stop:1 rgba(139, 92, 246, 0.8));
            backdrop-filter: blur(20px);
            color: #ffffff;
            border-color: rgba(255, 255, 255, 0.3);
            font-weight: 700;
            box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3);
        }
        
        QPushButton[class="primary"]:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(99, 102, 241, 0.9), stop:1 rgba(139, 92, 246, 0.9));
            box-shadow: 0 8px 30px rgba(99, 102, 241, 0.4);
        }
        
        /* === PREMIUM SUCCESS BUTTON === */
        QPushButton[class="success"] {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(16, 185, 129, 0.8), stop:1 rgba(5, 150, 105, 0.8));
            backdrop-filter: blur(20px);
            color: #ffffff;
            border-color: rgba(255, 255, 255, 0.3);
            font-weight: 700;
            box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3);
        }
        
        QPushButton[class="success"]:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(16, 185, 129, 0.9), stop:1 rgba(5, 150, 105, 0.9));
            box-shadow: 0 8px 30px rgba(16, 185, 129, 0.4);
        }
        
        /* === GLASS INPUTS === */
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(15px);
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 14px;
            min-height: 22px;
        }
        
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
            border-color: rgba(255, 255, 255, 0.4);
            background: rgba(255, 255, 255, 0.12);
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
        }
        
        QLineEdit::placeholder {
            color: rgba(255, 255, 255, 0.5);
        }
        
        /* === GLASS TABLES === */
        QTableWidget {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            color: #ffffff;
            gridline-color: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 16px;
            selection-background-color: rgba(255, 255, 255, 0.2);
            selection-color: #ffffff;
        }
        
        QTableWidget::item {
            padding: 12px 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        QTableWidget::item:alternate {
            background-color: rgba(255, 255, 255, 0.03);
        }
        
        QHeaderView::section {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(15px);
            color: #ffffff;
            padding: 12px 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            font-weight: 700;
            font-size: 13px;
        }
        
        /* === GLASS LISTS === */
        QListWidget {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(15px);
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            padding: 8px;
        }
        
        QListWidget::item {
            padding: 12px 16px;
            border-radius: 8px;
            margin: 2px 0;
        }
        
        QListWidget::item:selected {
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            color: #ffffff;
        }
        
        QListWidget::item:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        /* === GLASS TEXT EDIT === */
        QTextEdit {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(15px);
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            padding: 12px;
            font-family: 'JetBrains Mono', 'Consolas', monospace;
            font-size: 13px;
        }
        
        /* === PREMIUM PROGRESS BAR === */
        QProgressBar {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            text-align: center;
            color: #ffffff;
            font-weight: 600;
            height: 28px;
        }
        
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(16, 185, 129, 0.8), 
                stop:0.5 rgba(59, 130, 246, 0.8), 
                stop:1 rgba(139, 92, 246, 0.8));
            backdrop-filter: blur(15px);
            border-radius: 11px;
            margin: 1px;
        }
        
        /* === PREMIUM CHECKBOX === */
        QCheckBox {
            color: #ffffff;
            spacing: 12px;
            font-weight: 500;
        }
        
        QCheckBox::indicator {
            width: 20px;
            height: 20px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
        }
        
        QCheckBox::indicator:checked {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(59, 130, 246, 0.8), stop:1 rgba(99, 102, 241, 0.8));
            border-color: rgba(255, 255, 255, 0.5);
        }
        
        /* === PREMIUM MENU BAR === */
        QMenuBar {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(20px);
            color: #ffffff;
            border-bottom: 1px solid rgba(255, 255, 255, 0.15);
            padding: 8px 0;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 10px 20px;
            border-radius: 8px;
            margin: 0 4px;
        }
        
        QMenuBar::item:selected {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            color: #ffffff;
        }
        
        QMenu {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(30px);
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 8px;
        }
        
        QMenu::item {
            padding: 10px 20px;
            border-radius: 8px;
            margin: 2px;
        }
        
        QMenu::item:selected {
            background: rgba(255, 255, 255, 0.2);
            color: #ffffff;
        }
        
        /* === PREMIUM STATUS BAR === */
        QStatusBar {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(20px);
            color: rgba(255, 255, 255, 0.9);
            border-top: 1px solid rgba(255, 255, 255, 0.15);
            padding: 8px 16px;
            font-weight: 500;
        }
        
        /* === SCROLLBARS === */
        QScrollBar:vertical {
            background: rgba(255, 255, 255, 0.05);
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        """
        self.setStyleSheet(premium_stylesheet)
        
    def _show_about(self):
        """Hiển thị dialog giới thiệu"""
        from PySide6.QtWidgets import QMessageBox
        
        QMessageBox.about(
            self,
            "VCPMC Tool - Premium Edition",
            """
            <h3>🚀 VCPMC Tool v2.0 - Premium Edition</h3>
            <p><b>Công cụ xử lý dữ liệu tác phẩm âm nhạc cao cấp</b></p>
            <p><b>✨ Tính năng Premium:</b></p>
            <ul>
                <li>🎨 Glass Morphism UI Design</li>
                <li>📊 Xử lý file Excel thông minh</li>
                <li>💎 Tính toán nhuận bút tự động</li>
                <li>🔗 Tạo link YouTube với timestamp</li>
                <li>⏰ Quản lý thời hạn và gia hạn</li>
                <li>🌈 Giao diện hiện đại với backdrop blur</li>
            </ul>
            <p><b>Phiên bản:</b> 2.0.0 Premium</p>
            <p><b>Công nghệ:</b> Python + PySide6 + Glass Morphism</p>
            <p>© 2024 VCPMC Tool Premium Edition</p>
            """
        )
        
    def update_status(self, message: str):
        """Cập nhật status bar"""
        self.status_bar.showMessage(f"🚀 {message}")
        
    def toggle_theme(self):
        """Chuyển đổi theme (Premium luôn dùng Glass Morphism)"""
        self._apply_premium_theme()