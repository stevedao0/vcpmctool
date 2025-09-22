# vcpmctool/ui/tabs/royalty_tab.py - PySide6 Version
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget, 
    QTableWidgetItem, QTextEdit, QProgressBar, QGroupBox,
    QFileDialog, QMessageBox, QHeaderView, QFormLayout,
    QSpinBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
import pandas as pd
from pathlib import Path

from core.royalty.processor import RoyaltyProcessor
from services.logger import Logger


class RoyaltyWorker(QThread):
    """Worker thread cho xử lý nhuận bút"""
    
    progress_updated = Signal(float)
    log_updated = Signal(str)
    finished = Signal(bool, str)
    
    def __init__(self, processor, input_path, output_path):
        super().__init__()
        self.processor = processor
        self.input_path = input_path
        self.output_path = output_path
        
    def run(self):
        try:
            success, message = self.processor.process_file(
                self.input_path,
                self.output_path,
                progress_callback=self.progress_updated.emit,
                log_callback=self.log_updated.emit
            )
            self.finished.emit(success, message)
        except Exception as e:
            self.finished.emit(False, f"Lỗi không xác định: {str(e)}")


class RoyaltyTab(QWidget):
    """Tab tính nhuận bút với PySide6"""
    
    def __init__(self, logger: Logger):
        super().__init__()
        self.logger = logger
        self.input_file_path = None
        self.processor = None
        self.worker = None
        
        # Danh sách loại hình sử dụng
        self.usage_types = [
            "Video",
            "Audio", 
            "MV karaoke",
            "Midi karaoke",
            "Trailer",
            "Teaser"
        ]
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Thiết lập giao diện"""
        layout = QVBoxLayout(self)
        
        # File selection section
        file_group = self._create_file_section()
        layout.addWidget(file_group)
        
        # Royalty rates section
        royalty_group = self._create_royalty_section()
        layout.addWidget(royalty_group)
        
        # Process button
        self.process_btn = QPushButton("🚀 Xử lý file")
        self.process_btn.setEnabled(False)
        self.process_btn.clicked.connect(self.process_file)
        self.process_btn.setProperty("class", "success")
        self.process_btn.setMinimumHeight(50)
        layout.addWidget(self.process_btn)
        
        # Progress section
        progress_group = self._create_progress_section()
        layout.addWidget(progress_group)
        
        # Log section
        log_group = self._create_log_section()
        layout.addWidget(log_group)
        
    def _create_file_section(self) -> QGroupBox:
        """Tạo section chọn file"""
        group = QGroupBox("📁 Chọn file Excel")
        layout = QVBoxLayout(group)
        
        # File selection button and label
        file_layout = QHBoxLayout()
        
        self.select_file_btn = QPushButton("Chọn file Excel")
        self.select_file_btn.clicked.connect(self.select_file)
        file_layout.addWidget(self.select_file_btn)
        
        self.file_label = QLabel("Chưa chọn file")
        self.file_label.setStyleSheet("color: #666666; font-style: italic;")
        file_layout.addWidget(self.file_label)
        
        file_layout.addStretch()
        layout.addLayout(file_layout)
        
        return group
        
    def _create_royalty_section(self) -> QGroupBox:
        """Tạo section nhập mức nhuận bút"""
        group = QGroupBox("💰 Cấu hình mức nhuận bút")
        main_layout = QVBoxLayout(group)
        
        # Percentage controls
        percent_layout = QFormLayout()
        
        self.half_percent_spin = QSpinBox()
        self.half_percent_spin.setRange(1, 100)
        self.half_percent_spin.setValue(50)
        self.half_percent_spin.setSuffix("%")
        self.half_percent_spin.valueChanged.connect(self._recalculate_rates)
        percent_layout.addRow("Tỷ lệ mức nửa bài:", self.half_percent_spin)
        
        self.renew_percent_spin = QSpinBox()
        self.renew_percent_spin.setRange(1, 100)
        self.renew_percent_spin.setValue(40)
        self.renew_percent_spin.setSuffix("%")
        self.renew_percent_spin.valueChanged.connect(self._recalculate_rates)
        percent_layout.addRow("Tỷ lệ mức gia hạn:", self.renew_percent_spin)
        
        main_layout.addLayout(percent_layout)
        
        # Royalty rates - Vertical layout
        rates_layout = QVBoxLayout()
        
        # Create input fields for each usage type
        self.rate_inputs = {}
        
        for row, usage_type in enumerate(self.usage_types):
            # Create group for each usage type
            usage_group = QGroupBox(f"🎵 {usage_type}")
            usage_layout = QHBoxLayout(usage_group)
            
            # Full rate input
            full_label = QLabel("Mức đầy đủ:")
            full_input = QLineEdit("0")
            full_input.setPlaceholderText("Nhập mức nhuận bút đầy đủ")
            full_input.textChanged.connect(self._recalculate_rates)
            
            # Half rate display
            half_label = QLabel("Mức nửa bài:")
            half_display = QLabel("0")
            half_display.setStyleSheet("color: #10b981; font-weight: 600;")
            
            # Renewal rate display
            renew_label = QLabel("Mức gia hạn:")
            renew_display = QLabel("0")
            renew_display.setStyleSheet("color: #f59e0b; font-weight: 600;")
            
            # Add to layout
            usage_layout.addWidget(full_label)
            usage_layout.addWidget(full_input)
            usage_layout.addWidget(half_label)
            usage_layout.addWidget(half_display)
            usage_layout.addWidget(renew_label)
            usage_layout.addWidget(renew_display)
            
            # Store references
            self.rate_inputs[usage_type.lower()] = {
                'full': full_input,
                'half': half_display,
                'renew': renew_display
            }
            
            rates_layout.addWidget(usage_group)
        
        main_layout.addLayout(rates_layout)
        
        return group
        
    def _create_progress_section(self) -> QGroupBox:
        """Tạo section hiển thị tiến trình"""
        group = QGroupBox("📊 Tiến trình xử lý")
        layout = QVBoxLayout(group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Sẵn sàng")
        self.progress_label.setStyleSheet("color: #666666; font-style: italic;")
        layout.addWidget(self.progress_label)
        
        return group
        
    def _create_log_section(self) -> QGroupBox:
        """Tạo section log"""
        group = QGroupBox("📝 Nhật ký xử lý")
        layout = QVBoxLayout(group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_text)
        
        return group
        
    def select_file(self):
        """Chọn file Excel"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn file Excel",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        
        if file_path:
            self.input_file_path = file_path
            self.file_label.setText(f"Đã chọn: {Path(file_path).name}")
            self.file_label.setStyleSheet("color: #28a745; font-weight: bold;")
            self.process_btn.setEnabled(True)
            self.add_log(f"Đã chọn file: {Path(file_path).name}")
            
    def _recalculate_rates(self):
        """Tính lại mức nửa bài và gia hạn"""
        half_percent = self.half_percent_spin.value() / 100.0
        renew_percent = self.renew_percent_spin.value() / 100.0
        
        for usage_type, inputs in self.rate_inputs.items():
            try:
                full_rate = float(inputs['full'].text() or 0)
                
                # Calculate and set half rate
                half_rate = int(full_rate * half_percent)
                inputs['half'].setText(f"{half_rate:,}")
                
                # Calculate and set renewal rate
                renew_rate = int(full_rate * renew_percent)
                inputs['renew'].setText(f"{renew_rate:,}")
                
            except (ValueError, TypeError):
                pass
                    
    def _collect_royalty_data(self) -> dict:
        """Thu thập dữ liệu nhuận bút từ bảng"""
        royalty_dict = {}
        has_valid_data = False
        
        for usage_type, inputs in self.rate_inputs.items():
            try:
                full_rate = int(float(inputs['full'].text() or 0))
                half_rate = int(float(inputs['half'].text().replace(',', '') or 0))
                renew_rate = int(float(inputs['renew'].text().replace(',', '') or 0))
                
                royalty_dict[usage_type] = (full_rate, half_rate, renew_rate)
                
                if full_rate > 0:
                    has_valid_data = True
                    
            except (ValueError, TypeError) as e:
                self.add_log(f"Lỗi nhập liệu cho {usage_type}: {e}")
                return None
                
        if not has_valid_data:
            self.add_log("⚠️ Vui lòng nhập ít nhất một mức nhuận bút!")
            return None
            
        self.add_log(f"✓ Đã thu thập mức nhuận bút cho {len(royalty_dict)} loại hình")
        return royalty_dict
        
    def process_file(self):
        """Xử lý file Excel"""
        if not self.input_file_path:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn file trước!")
            return
            
        # Collect royalty data
        royalty_dict = self._collect_royalty_data()
        if not royalty_dict:
            return
            
        # Generate output path
        input_path = Path(self.input_file_path)
        output_path = input_path.parent / f"{input_path.stem}_NhuanBut.xlsx"
        
        # Disable UI during processing
        self.process_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Đang xử lý...")
        
        # Create processor and worker
        self.processor = RoyaltyProcessor(royalty_dict)
        self.worker = RoyaltyWorker(self.processor, self.input_file_path, str(output_path))
        
        # Connect signals
        self.worker.progress_updated.connect(self._update_progress)
        self.worker.log_updated.connect(self.add_log)
        self.worker.finished.connect(self._on_processing_finished)
        
        # Start processing
        self.worker.start()
        self.add_log("🚀 Bắt đầu xử lý file nhuận bút...")
        
    def _update_progress(self, value: float):
        """Cập nhật tiến trình"""
        self.progress_bar.setValue(int(value))
        self.progress_label.setText(f"Đang xử lý... {value:.1f}%")
        
    def _on_processing_finished(self, success: bool, message: str):
        """Xử lý khi hoàn tất"""
        self.process_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.progress_label.setText("Hoàn tất!")
            self.add_log(f"✅ {message}")
            QMessageBox.information(self, "Thành công", message)
        else:
            self.progress_label.setText("Lỗi!")
            self.add_log(f"❌ {message}")
            QMessageBox.critical(self, "Lỗi", message)
            
    def add_log(self, message: str):
        """Thêm log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        self.log_text.append(formatted_message)
        
        if self.logger:
            self.logger.info(f"[RoyaltyTab] {message}")
            
        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)