# vcpmctool/ui/tabs/royalty_tab.py - Premium Glass Morphism Version
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QProgressBar, 
    QGroupBox, QFileDialog, QMessageBox, QFormLayout,
    QSpinBox, QFrame
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
    """Tab tính nhuận bút với Premium Glass Morphism UI"""
    
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
        """Thiết lập giao diện Premium"""
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header với title
        header_layout = QHBoxLayout()
        title_label = QLabel("💎 Tính toán nhuận bút Premium")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: 700;
                color: #ffffff;
                margin-bottom: 8px;
            }
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # File selection section
        file_group = self._create_file_section()
        layout.addWidget(file_group)
        
        # Configuration section
        config_layout = QHBoxLayout()
        config_layout.setSpacing(20)
        
        # Left: Percentage controls
        percent_group = self._create_percentage_section()
        config_layout.addWidget(percent_group, 1)
        
        # Right: Royalty rates
        royalty_group = self._create_royalty_section()
        config_layout.addWidget(royalty_group, 2)
        
        layout.addLayout(config_layout)
        
        # Process button
        self.process_btn = QPushButton("🚀 Xử lý file Premium")
        self.process_btn.setEnabled(False)
        self.process_btn.clicked.connect(self.process_file)
        self.process_btn.setProperty("class", "success")
        self.process_btn.setMinimumHeight(60)
        self.process_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: 700;
            }
        """)
        layout.addWidget(self.process_btn)
        
        # Progress section
        progress_group = self._create_progress_section()
        layout.addWidget(progress_group)
        
        # Log section
        log_group = self._create_log_section()
        layout.addWidget(log_group)
        
    def _create_file_section(self) -> QGroupBox:
        """Tạo section chọn file Premium"""
        group = QGroupBox("📁 Chọn file Excel")
        layout = QVBoxLayout(group)
        layout.setSpacing(16)
        
        # File selection area
        file_frame = QFrame()
        file_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border: 2px dashed rgba(255, 255, 255, 0.3);
                border-radius: 16px;
                padding: 20px;
            }
        """)
        file_layout = QVBoxLayout(file_frame)
        
        self.select_file_btn = QPushButton("📂 Chọn file Excel")
        self.select_file_btn.clicked.connect(self.select_file)
        self.select_file_btn.setMinimumHeight(50)
        file_layout.addWidget(self.select_file_btn)
        
        self.file_label = QLabel("🎯 Chưa chọn file - Kéo thả file vào đây hoặc click để chọn")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-style: italic;
                font-size: 14px;
                padding: 10px;
            }
        """)
        file_layout.addWidget(self.file_label)
        
        layout.addWidget(file_frame)
        return group
        
    def _create_percentage_section(self) -> QGroupBox:
        """Tạo section cấu hình tỷ lệ"""
        group = QGroupBox("⚙️ Cấu hình tỷ lệ")
        layout = QFormLayout(group)
        layout.setSpacing(20)
        
        # Half percentage
        self.half_percent_spin = QSpinBox()
        self.half_percent_spin.setRange(1, 100)
        self.half_percent_spin.setValue(50)
        self.half_percent_spin.setSuffix("%")
        self.half_percent_spin.setMinimumHeight(40)
        self.half_percent_spin.valueChanged.connect(self._recalculate_rates)
        layout.addRow("🎵 Tỷ lệ mức nửa bài:", self.half_percent_spin)
        
        # Renewal percentage
        self.renew_percent_spin = QSpinBox()
        self.renew_percent_spin.setRange(1, 100)
        self.renew_percent_spin.setValue(40)
        self.renew_percent_spin.setSuffix("%")
        self.renew_percent_spin.setMinimumHeight(40)
        self.renew_percent_spin.valueChanged.connect(self._recalculate_rates)
        layout.addRow("🔄 Tỷ lệ mức gia hạn:", self.renew_percent_spin)
        
        return group
        
    def _create_royalty_section(self) -> QGroupBox:
        """Tạo section nhập mức nhuận bút Premium"""
        group = QGroupBox("💰 Mức nhuận bút theo loại hình")
        layout = QVBoxLayout(group)
        layout.setSpacing(16)
        
        # Create input fields for each usage type
        self.rate_inputs = {}
        
        for usage_type in self.usage_types:
            # Create card for each usage type
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    padding: 16px;
                    margin: 4px;
                }
            """)
            card_layout = QHBoxLayout(card)
            card_layout.setSpacing(16)
            
            # Icon and type name
            type_label = QLabel(f"🎵 {usage_type}")
            type_label.setMinimumWidth(120)
            type_label.setStyleSheet("""
                QLabel {
                    font-weight: 600;
                    font-size: 14px;
                    color: #ffffff;
                }
            """)
            card_layout.addWidget(type_label)
            
            # Full rate input
            full_input = QLineEdit("0")
            full_input.setPlaceholderText("Nhập mức đầy đủ")
            full_input.setMinimumWidth(120)
            full_input.textChanged.connect(self._recalculate_rates)
            card_layout.addWidget(full_input)
            
            # Arrow
            arrow_label = QLabel("→")
            arrow_label.setStyleSheet("color: rgba(255, 255, 255, 0.5); font-size: 16px;")
            card_layout.addWidget(arrow_label)
            
            # Half rate display
            half_display = QLabel("0")
            half_display.setMinimumWidth(80)
            half_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
            half_display.setStyleSheet("""
                QLabel {
                    background: rgba(16, 185, 129, 0.2);
                    color: #10b981;
                    font-weight: 600;
                    padding: 8px;
                    border-radius: 8px;
                    border: 1px solid rgba(16, 185, 129, 0.3);
                }
            """)
            card_layout.addWidget(half_display)
            
            # Renewal rate display
            renew_display = QLabel("0")
            renew_display.setMinimumWidth(80)
            renew_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
            renew_display.setStyleSheet("""
                QLabel {
                    background: rgba(245, 158, 11, 0.2);
                    color: #f59e0b;
                    font-weight: 600;
                    padding: 8px;
                    border-radius: 8px;
                    border: 1px solid rgba(245, 158, 11, 0.3);
                }
            """)
            card_layout.addWidget(renew_display)
            
            # Store references
            self.rate_inputs[usage_type.lower()] = {
                'full': full_input,
                'half': half_display,
                'renew': renew_display
            }
            
            layout.addWidget(card)
        
        return group
        
    def _create_progress_section(self) -> QGroupBox:
        """Tạo section tiến trình Premium"""
        group = QGroupBox("📊 Tiến trình xử lý")
        layout = QVBoxLayout(group)
        layout.setSpacing(12)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(32)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("✨ Sẵn sàng xử lý")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-style: italic;
                font-size: 14px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.progress_label)
        
        return group
        
    def _create_log_section(self) -> QGroupBox:
        """Tạo section log Premium"""
        group = QGroupBox("📝 Nhật ký xử lý")
        layout = QVBoxLayout(group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(180)
        self.log_text.setFont(QFont("JetBrains Mono", 10))
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
            self.file_label.setText(f"✅ Đã chọn: {Path(file_path).name}")
            self.file_label.setStyleSheet("""
                QLabel {
                    color: #10b981;
                    font-weight: 600;
                    font-size: 14px;
                    padding: 10px;
                }
            """)
            self.process_btn.setEnabled(True)
            self.add_log(f"📁 Đã chọn file: {Path(file_path).name}")
            
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
        """Thu thập dữ liệu nhuận bút từ form"""
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
                self.add_log(f"❌ Lỗi nhập liệu cho {usage_type}: {e}")
                return None
                
        if not has_valid_data:
            self.add_log("⚠️ Vui lòng nhập ít nhất một mức nhuận bút!")
            return None
            
        self.add_log(f"✅ Đã thu thập mức nhuận bút cho {len(royalty_dict)} loại hình")
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
        output_path = input_path.parent / f"{input_path.stem}_NhuanBut_Premium.xlsx"
        
        # Disable UI during processing
        self.process_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("🚀 Đang xử lý...")
        
        # Create processor and worker
        self.processor = RoyaltyProcessor(royalty_dict)
        self.worker = RoyaltyWorker(self.processor, self.input_file_path, str(output_path))
        
        # Connect signals
        self.worker.progress_updated.connect(self._update_progress)
        self.worker.log_updated.connect(self.add_log)
        self.worker.finished.connect(self._on_processing_finished)
        
        # Start processing
        self.worker.start()
        self.add_log("🚀 Bắt đầu xử lý file nhuận bút Premium...")
        
    def _update_progress(self, value: float):
        """Cập nhật tiến trình"""
        self.progress_bar.setValue(int(value))
        self.progress_label.setText(f"⚡ Đang xử lý... {value:.1f}%")
        
    def _on_processing_finished(self, success: bool, message: str):
        """Xử lý khi hoàn tất"""
        self.process_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.progress_label.setText("🎉 Hoàn tất!")
            self.add_log(f"✅ {message}")
            QMessageBox.information(self, "Thành công", f"🎉 {message}")
        else:
            self.progress_label.setText("❌ Lỗi!")
            self.add_log(f"❌ {message}")
            QMessageBox.critical(self, "Lỗi", f"❌ {message}")
            
    def add_log(self, message: str):
        """Thêm log với timestamp"""
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