# vcpmctool/ui/tabs/settings_tab.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QCheckBox, QPushButton, QComboBox,
    QSpinBox, QFormLayout, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from services.settings import Settings


class SettingsTab(QWidget):
    """Tab cài đặt"""
    
    def __init__(self, settings: Settings, main_window):
        super().__init__()
        self.settings = settings
        self.main_window = main_window
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Thiết lập giao diện"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("⚙️ Cài đặt ứng dụng")
        title.setFont(QFont("", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Appearance settings
        appearance_group = self._create_appearance_group()
        layout.addWidget(appearance_group)
        
        # Processing settings
        processing_group = self._create_processing_group()
        layout.addWidget(processing_group)
        
        # Advanced settings
        advanced_group = self._create_advanced_group()
        layout.addWidget(advanced_group)
        
        # About section
        about_group = self._create_about_group()
        layout.addWidget(about_group)
        
        layout.addStretch()
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("🔄 Khôi phục mặc định")
        self.reset_btn.clicked.connect(self._reset_settings)
        button_layout.addWidget(self.reset_btn)
        
        button_layout.addStretch()
        
        self.apply_btn = QPushButton("✅ Áp dụng")
        self.apply_btn.clicked.connect(self._apply_settings)
        self.apply_btn.setProperty("class", "primary")
        button_layout.addWidget(self.apply_btn)
        
        layout.addLayout(button_layout)
        
    def _create_appearance_group(self) -> QGroupBox:
        """Tạo nhóm cài đặt giao diện"""
        group = QGroupBox("🎨 Giao diện")
        layout = QFormLayout(group)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Sáng", "Tối"])
        self.theme_combo.setCurrentText("Tối" if self.settings.theme_mode == "dark" else "Sáng")
        layout.addRow("Chế độ hiển thị:", self.theme_combo)
        
        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 16)
        self.font_size_spin.setValue(9)
        self.font_size_spin.setSuffix(" pt")
        layout.addRow("Kích thước font:", self.font_size_spin)
        
        return group
        
    def _create_processing_group(self) -> QGroupBox:
        """Tạo nhóm cài đặt xử lý"""
        group = QGroupBox("⚙️ Xử lý dữ liệu")
        layout = QFormLayout(group)
        
        # Auto proper case
        self.auto_proper_cb = QCheckBox("Tự động định dạng tên riêng")
        self.auto_proper_cb.setChecked(self.settings.auto_propercase)
        self.auto_proper_cb.setToolTip("Tự động viết hoa chữ cái đầu của từng từ")
        layout.addRow(self.auto_proper_cb)
        
        # Auto backup
        self.auto_backup_cb = QCheckBox("Tự động sao lưu file gốc")
        self.auto_backup_cb.setChecked(True)
        self.auto_backup_cb.setToolTip("Tạo bản sao lưu trước khi xử lý")
        layout.addRow(self.auto_backup_cb)
        
        # Default terms
        self.default_initial_spin = QSpinBox()
        self.default_initial_spin.setRange(1, 10)
        self.default_initial_spin.setValue(2)
        self.default_initial_spin.setSuffix(" năm")
        layout.addRow("Thời hạn ban đầu mặc định:", self.default_initial_spin)
        
        self.default_ext_spin = QSpinBox()
        self.default_ext_spin.setRange(1, 10)
        self.default_ext_spin.setValue(2)
        self.default_ext_spin.setSuffix(" năm")
        layout.addRow("Thời hạn gia hạn mặc định:", self.default_ext_spin)
        
        return group
        
    def _create_advanced_group(self) -> QGroupBox:
        """Tạo nhóm cài đặt nâng cao"""
        group = QGroupBox("🔧 Nâng cao")
        layout = QFormLayout(group)
        
        # Max preview rows
        self.max_preview_spin = QSpinBox()
        self.max_preview_spin.setRange(10, 1000)
        self.max_preview_spin.setValue(50)
        self.max_preview_spin.setSuffix(" dòng")
        layout.addRow("Số dòng xem trước tối đa:", self.max_preview_spin)
        
        # Log level
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        layout.addRow("Mức độ log:", self.log_level_combo)
        
        # Clear log button
        clear_log_btn = QPushButton("🗑️ Xóa log")
        clear_log_btn.clicked.connect(self._clear_log)
        layout.addRow("Quản lý log:", clear_log_btn)
        
        return group
        
    def _create_about_group(self) -> QGroupBox:
        """Tạo nhóm thông tin"""
        group = QGroupBox("ℹ️ Thông tin")
        layout = QVBoxLayout(group)
        
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setMaximumHeight(120)
        about_text.setHtml("""
        <h3>VCPMC Tool v2.0</h3>
        <p><b>Công cụ xử lý dữ liệu tác phẩm âm nhạc</b></p>
        <p>🔹 Xử lý file Excel tác phẩm<br>
        🔹 Tính toán nhuận bút tự động<br>
        🔹 Tạo link YouTube với timestamp<br>
        🔹 Quản lý thời hạn và gia hạn</p>
        <p><i>Phát triển với Python + PySide6</i></p>
        """)
        layout.addWidget(about_text)
        
        return group
        
    def _apply_settings(self):
        """Áp dụng cài đặt"""
        # Update theme
        new_theme = "dark" if self.theme_combo.currentText() == "Tối" else "light"
        if new_theme != self.settings.theme_mode:
            self.settings.theme_mode = new_theme
            self.main_window.toggle_theme()
            
        # Update other settings
        self.settings.auto_propercase = self.auto_proper_cb.isChecked()
        
        QMessageBox.information(self, "Thành công", "Đã áp dụng cài đặt!")
        
    def _reset_settings(self):
        """Khôi phục cài đặt mặc định"""
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc muốn khôi phục tất cả cài đặt về mặc định?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset to defaults
            self.theme_combo.setCurrentText("Sáng")
            self.font_size_spin.setValue(9)
            self.auto_proper_cb.setChecked(True)
            self.auto_backup_cb.setChecked(True)
            self.default_initial_spin.setValue(2)
            self.default_ext_spin.setValue(2)
            self.max_preview_spin.setValue(50)
            self.log_level_combo.setCurrentText("INFO")
            
            QMessageBox.information(self, "Thành công", "Đã khôi phục cài đặt mặc định!")
            
    def _clear_log(self):
        """Xóa file log"""
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc muốn xóa file log?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                import os
                if os.path.exists("vcpmctool.log"):
                    os.remove("vcpmctool.log")
                QMessageBox.information(self, "Thành công", "Đã xóa file log!")
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể xóa file log: {e}")