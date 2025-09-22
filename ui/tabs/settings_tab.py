# vcpmctool/ui/tabs/settings_tab.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QCheckBox, QPushButton, QComboBox,
    QSpinBox, QFormLayout, QTextEdit, QMessageBox,
    QSlider, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from services.settings import Settings


class SettingsTab(QWidget):
    """Tab cài đặt"""
    
    # Signals để thông báo thay đổi
    theme_changed = Signal(str)
    font_size_changed = Signal(int)
    
    def __init__(self, settings: Settings, main_window):
        super().__init__()
        self.settings = settings
        self.main_window = main_window
        
        self._setup_ui()
        self._load_current_settings()
        
    def _setup_ui(self):
        """Thiết lập giao diện"""
        # Main scroll area để tránh vỡ layout khi thu nhỏ
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Content widget
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        
        # Main layout cho scroll area
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        
        # Layout cho content
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("⚙️ Cài đặt ứng dụng")
        title.setFont(QFont("", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("margin-bottom: 20px;")
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
        group.setMinimumWidth(300)
        group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout = QFormLayout(group)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumWidth(150)
        self.theme_combo.addItems(["Sáng (Light)", "Tối (Dark)", "Premium Glass"])
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        layout.addRow("Chế độ hiển thị:", self.theme_combo)
        
        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 16)
        self.font_size_spin.setMinimumWidth(80)
        self.font_size_spin.setSuffix(" pt")
        self.font_size_spin.valueChanged.connect(self._on_font_size_changed)
        layout.addRow("Kích thước font:", self.font_size_spin)
        
        # UI Scale
        self.ui_scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.ui_scale_slider.setRange(80, 150)
        self.ui_scale_slider.setValue(100)
        self.ui_scale_slider.setMinimumWidth(200)
        self.ui_scale_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.ui_scale_slider.setTickInterval(10)
        self.ui_scale_label = QLabel("100%")
        self.ui_scale_slider.valueChanged.connect(self._on_scale_changed)
        
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(self.ui_scale_slider)
        scale_layout.addWidget(self.ui_scale_label)
        layout.addRow("Tỷ lệ giao diện:", scale_layout)
        
        return group
        
    def _create_processing_group(self) -> QGroupBox:
        """Tạo nhóm cài đặt xử lý"""
        group = QGroupBox("⚙️ Xử lý dữ liệu")
        group.setMinimumWidth(300)
        group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout = QFormLayout(group)
        
        # Auto proper case
        self.auto_proper_cb = QCheckBox("Tự động định dạng tên riêng")
        self.auto_proper_cb.setToolTip("Tự động viết hoa chữ cái đầu của từng từ")
        layout.addRow(self.auto_proper_cb)
        
        # Auto backup
        self.auto_backup_cb = QCheckBox("Tự động sao lưu file gốc")
        self.auto_backup_cb.setChecked(True)
        self.auto_backup_cb.setToolTip("Tạo bản sao lưu trước khi xử lý")
        layout.addRow(self.auto_backup_cb)
        
        # Validate data
        self.validate_data_cb = QCheckBox("Kiểm tra dữ liệu đầu vào")
        self.validate_data_cb.setChecked(True)
        self.validate_data_cb.setToolTip("Kiểm tra tính hợp lệ của dữ liệu trước khi xử lý")
        layout.addRow(self.validate_data_cb)
        
        # Default terms
        self.default_initial_spin = QSpinBox()
        self.default_initial_spin.setRange(1, 10)
        self.default_initial_spin.setValue(2)
        self.default_initial_spin.setMinimumWidth(80)
        self.default_initial_spin.setSuffix(" năm")
        layout.addRow("Thời hạn ban đầu mặc định:", self.default_initial_spin)
        
        self.default_ext_spin = QSpinBox()
        self.default_ext_spin.setRange(1, 10)
        self.default_ext_spin.setValue(2)
        self.default_ext_spin.setMinimumWidth(80)
        self.default_ext_spin.setSuffix(" năm")
        layout.addRow("Thời hạn gia hạn mặc định:", self.default_ext_spin)
        
        return group
        
    def _create_advanced_group(self) -> QGroupBox:
        """Tạo nhóm cài đặt nâng cao"""
        group = QGroupBox("🔧 Nâng cao")
        group.setMinimumWidth(300)
        group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout = QFormLayout(group)
        
        # Max preview rows
        self.max_preview_spin = QSpinBox()
        self.max_preview_spin.setRange(10, 1000)
        self.max_preview_spin.setValue(50)
        self.max_preview_spin.setMinimumWidth(100)
        self.max_preview_spin.setSuffix(" dòng")
        layout.addRow("Số dòng xem trước tối đa:", self.max_preview_spin)
        
        # Log level
        self.log_level_combo = QComboBox()
        self.log_level_combo.setMinimumWidth(100)
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        layout.addRow("Mức độ log:", self.log_level_combo)
        
        # Performance settings
        self.multithread_cb = QCheckBox("Xử lý đa luồng")
        self.multithread_cb.setChecked(True)
        self.multithread_cb.setToolTip("Sử dụng nhiều luồng để xử lý nhanh hơn")
        layout.addRow(self.multithread_cb)
        
        # Clear log button
        clear_log_btn = QPushButton("🗑️ Xóa log")
        clear_log_btn.clicked.connect(self._clear_log)
        layout.addRow("Quản lý log:", clear_log_btn)
        
        # Export settings button
        export_btn = QPushButton("📤 Xuất cài đặt")
        export_btn.clicked.connect(self._export_settings)
        import_btn = QPushButton("📥 Nhập cài đặt")
        import_btn.clicked.connect(self._import_settings)
        
        settings_layout = QHBoxLayout()
        settings_layout.addWidget(export_btn)
        settings_layout.addWidget(import_btn)
        layout.addRow("Sao lưu cài đặt:", settings_layout)
        
        return group
        
    def _create_about_group(self) -> QGroupBox:
        """Tạo nhóm thông tin"""
        group = QGroupBox("ℹ️ Thông tin")
        group.setMinimumWidth(300)
        group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(group)
        
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setMaximumHeight(120)
        about_text.setMinimumWidth(280)
        about_text.setHtml("""
        <h3>🚀 VCPMC Tool v2.0 - Premium Edition</h3>
        <p><b>Công cụ xử lý dữ liệu tác phẩm âm nhạc</b></p>
        <p>🔹 Xử lý file Excel tác phẩm<br>
        🔹 Tính toán nhuận bút tự động<br>
        🔹 Tạo link YouTube với timestamp<br>
        🔹 Quản lý thời hạn và gia hạn<br>
        🔹 Glass Morphism UI Design</p>
        <p><i>Phát triển với Python + PySide6 + Premium UI</i></p>
        """)
        layout.addWidget(about_text)
        
        return group
        
    def _load_current_settings(self):
        """Tải cài đặt hiện tại"""
        # Theme
        if hasattr(self.settings, 'theme_mode'):
            if self.settings.theme_mode == "dark":
                self.theme_combo.setCurrentText("Tối (Dark)")
            elif self.settings.theme_mode == "light":
                self.theme_combo.setCurrentText("Sáng (Light)")
            else:
                self.theme_combo.setCurrentText("Premium Glass")
        else:
            self.theme_combo.setCurrentText("Premium Glass")
            
        # Font size
        if hasattr(self.settings, 'font_size'):
            self.font_size_spin.setValue(self.settings.font_size)
        else:
            self.font_size_spin.setValue(9)
            
        # Auto proper case
        if hasattr(self.settings, 'auto_propercase'):
            self.auto_proper_cb.setChecked(self.settings.auto_propercase)
        else:
            self.auto_proper_cb.setChecked(True)
            
    def _on_theme_changed(self, theme_text):
        """Xử lý khi thay đổi theme"""
        if "Sáng" in theme_text:
            theme_mode = "light"
        elif "Tối" in theme_text:
            theme_mode = "dark"
        else:
            theme_mode = "premium"
            
        self.theme_changed.emit(theme_mode)
        
    def _on_font_size_changed(self, size):
        """Xử lý khi thay đổi font size"""
        self.font_size_changed.emit(size)
        
    def _on_scale_changed(self, value):
        """Xử lý khi thay đổi UI scale"""
        self.ui_scale_label.setText(f"{value}%")
        
    def _apply_settings(self):
        """Áp dụng cài đặt"""
        try:
            # Update theme
            theme_text = self.theme_combo.currentText()
            if "Sáng" in theme_text:
                new_theme = "light"
            elif "Tối" in theme_text:
                new_theme = "dark"
            else:
                new_theme = "premium"
                
            self.settings.theme_mode = new_theme
            
            # Update font size
            self.settings.font_size = self.font_size_spin.value()
            
            # Update other settings
            self.settings.auto_propercase = self.auto_proper_cb.isChecked()
            
            # Apply theme to main window
            if hasattr(self.main_window, '_apply_theme'):
                self.main_window._apply_theme(new_theme)
            else:
                self.main_window._apply_premium_theme()
                
            QMessageBox.information(self, "Thành công", "Đã áp dụng cài đặt thành công!")
            
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể áp dụng cài đặt: {str(e)}")
        
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
            self.theme_combo.setCurrentText("Premium Glass")
            self.font_size_spin.setValue(9)
            self.auto_proper_cb.setChecked(True)
            self.auto_backup_cb.setChecked(True)
            self.validate_data_cb.setChecked(True)
            self.default_initial_spin.setValue(2)
            self.default_ext_spin.setValue(2)
            self.max_preview_spin.setValue(50)
            self.log_level_combo.setCurrentText("INFO")
            self.multithread_cb.setChecked(True)
            self.ui_scale_slider.setValue(100)
            
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
                 
    def _export_settings(self):
        """Xuất cài đặt ra file"""
        from PySide6.QtWidgets import QFileDialog
        import json
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Xuất cài đặt", "vcpmc_settings.json", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                settings_data = {
                    "theme_mode": self.theme_combo.currentText(),
                    "font_size": self.font_size_spin.value(),
                    "auto_propercase": self.auto_proper_cb.isChecked(),
                    "auto_backup": self.auto_backup_cb.isChecked(),
                    "validate_data": self.validate_data_cb.isChecked(),
                    "default_initial_term": self.default_initial_spin.value(),
                    "default_ext_term": self.default_ext_spin.value(),
                    "max_preview_rows": self.max_preview_spin.value(),
                    "log_level": self.log_level_combo.currentText(),
                    "multithread": self.multithread_cb.isChecked(),
                    "ui_scale": self.ui_scale_slider.value()
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(settings_data, f, indent=2, ensure_ascii=False)
                    
                QMessageBox.information(self, "Thành công", f"Đã xuất cài đặt ra: {file_path}")
                
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể xuất cài đặt: {e}")
                
    def _import_settings(self):
        """Nhập cài đặt từ file"""
        from PySide6.QtWidgets import QFileDialog
        import json
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Nhập cài đặt", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)
                    
                # Apply imported settings
                if "theme_mode" in settings_data:
                    self.theme_combo.setCurrentText(settings_data["theme_mode"])
                if "font_size" in settings_data:
                    self.font_size_spin.setValue(settings_data["font_size"])
                if "auto_propercase" in settings_data:
                    self.auto_proper_cb.setChecked(settings_data["auto_propercase"])
                if "auto_backup" in settings_data:
                    self.auto_backup_cb.setChecked(settings_data["auto_backup"])
                if "validate_data" in settings_data:
                    self.validate_data_cb.setChecked(settings_data["validate_data"])
                if "default_initial_term" in settings_data:
                    self.default_initial_spin.setValue(settings_data["default_initial_term"])
                if "default_ext_term" in settings_data:
                    self.default_ext_spin.setValue(settings_data["default_ext_term"])
                if "max_preview_rows" in settings_data:
                    self.max_preview_spin.setValue(settings_data["max_preview_rows"])
                if "log_level" in settings_data:
                    self.log_level_combo.setCurrentText(settings_data["log_level"])
                if "multithread" in settings_data:
                    self.multithread_cb.setChecked(settings_data["multithread"])
                if "ui_scale" in settings_data:
                    self.ui_scale_slider.setValue(settings_data["ui_scale"])
                    
                QMessageBox.information(self, "Thành công", "Đã nhập cài đặt thành công!")
                
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể nhập cài đặt: {e}")