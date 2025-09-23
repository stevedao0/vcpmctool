# vcpmctool/ui/tabs/royalty_tab.py - Fixed Version
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QProgressBar, 
    QGroupBox, QFileDialog, QMessageBox, QFormLayout,
    QSpinBox, QFrame, QScrollArea, QSizePolicy
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
    """Tab tính nhuận bút"""
    
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
        
        # Dictionary lưu input fields
        self.rate_inputs = {}
        
        self._setup_ui()
        
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
        title_label = QLabel("💎 Tính toán nhuận bút Premium")
        title_label.setStyleSheet("font-size: 24px; font-weight: 700; margin-bottom: 10px; text-align: center;")
        layout.addWidget(title_label)
        
        # File selection
        file_group = self._create_file_section()
        layout.addWidget(file_group)
        
        # Configuration
        config_layout = QHBoxLayout()
        config_layout.setSpacing(15)
        
        # Left: Percentage settings
        percent_group = self._create_percentage_section()
        percent_group.setMinimumWidth(200)
        percent_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        config_layout.addWidget(percent_group)
        
        # Right: Royalty rates
        royalty_group = self._create_royalty_section()
        royalty_group.setMinimumWidth(600)
        royalty_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        config_layout.addWidget(royalty_group)
        
        layout.addLayout(config_layout)
        
        # Process button
        self.process_btn = QPushButton("🚀 Xử lý file Premium")
        self.process_btn.setEnabled(False)
        self.process_btn.clicked.connect(self.process_file)
        self.process_btn.setProperty("class", "primary")
        self.process_btn.setMinimumHeight(50)
        self.process_btn.setStyleSheet("font-size: 16px; font-weight: 700;")
        layout.addWidget(self.process_btn)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Sẵn sàng xử lý")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_label)
        
        # Log
        log_group = QGroupBox("📝 Nhật ký xử lý")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
    def _create_file_section(self) -> QGroupBox:
        """Tạo section chọn file"""
        group = QGroupBox("📁 Chọn file Excel")
        layout = QVBoxLayout(group)
        
        self.select_file_btn = QPushButton("📂 Chọn file Excel")
        self.select_file_btn.clicked.connect(self.select_file)
        layout.addWidget(self.select_file_btn)
        
        self.file_label = QLabel("Chưa chọn file")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setStyleSheet("font-style: italic; font-weight: 500; padding: 8px;")
        layout.addWidget(self.file_label)
        
        return group
        
    def _create_percentage_section(self) -> QGroupBox:
        """Tạo section cấu hình tỷ lệ"""
        group = QGroupBox("⚙️ Cấu hình tỷ lệ")
        layout = QFormLayout(group)
        
        # Half percentage
        self.half_percent_spin = QSpinBox()
        self.half_percent_spin.setRange(1, 100)
        self.half_percent_spin.setValue(50)
        self.half_percent_spin.setSuffix("%")
        self.half_percent_spin.valueChanged.connect(self._recalculate_rates)
        layout.addRow("Tỷ lệ mức nửa bài:", self.half_percent_spin)
        
        # Renewal percentage
        self.renew_percent_spin = QSpinBox()
        self.renew_percent_spin.setRange(1, 100)
        self.renew_percent_spin.setValue(40)
        self.renew_percent_spin.setSuffix("%")
        self.renew_percent_spin.valueChanged.connect(self._recalculate_rates)
        layout.addRow("Tỷ lệ mức gia hạn:", self.renew_percent_spin)
        
        return group
        
    def _create_royalty_section(self) -> QGroupBox:
        """Tạo section nhập mức nhuận bút"""
        group = QGroupBox("🔥 Mức nhuận bút theo loại hình")
        layout = QVBoxLayout(group)
        
        # Create grid for inputs
        grid_layout = QGridLayout()
        
        # Headers
        grid_layout.addWidget(QLabel("Loại hình"), 0, 0)
        grid_layout.addWidget(QLabel("Mức đầy đủ"), 0, 1)
        grid_layout.addWidget(QLabel("Mức nửa bài"), 0, 2)
        grid_layout.addWidget(QLabel("Mức gia hạn"), 0, 3)
        
        # Create inputs for each usage type
        for i, usage_type in enumerate(self.usage_types):
            row = i + 1
            
            # Type label
            type_label = QLabel(usage_type)
            grid_layout.addWidget(type_label, row, 0)
            type_label.setMinimumWidth(80)
            
            # Full rate input
            full_input = QLineEdit("0")
            full_input.setPlaceholderText("Nhập mức đầy đủ")
            full_input.setMinimumWidth(100)
            full_input.setMaximumWidth(150)
            full_input.textChanged.connect(self._recalculate_rates)
            grid_layout.addWidget(full_input, row, 1)
            
            # Half rate display
            half_display = QLabel("0")
            half_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
            half_display.setMinimumWidth(80)
            half_display.setMaximumWidth(120)
            half_display.setStyleSheet("background: #e8f5e8; color: #2d5a2d; padding: 5px; border-radius: 4px;")
            grid_layout.addWidget(half_display, row, 2)
            
            # Renewal rate display
            renew_display = QLabel("0")
            renew_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
            renew_display.setMinimumWidth(80)
            renew_display.setMaximumWidth(120)
            renew_display.setStyleSheet("background: #fff3cd; color: #856404; padding: 5px; border-radius: 4px;")
            grid_layout.addWidget(renew_display, row, 3)
            
            # Store references
            self.rate_inputs[usage_type.lower()] = {
                'full': full_input,
                'half': half_display,
                'renew': renew_display
            }
            
        layout.addLayout(grid_layout)
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
            # Kiểm tra file có tồn tại và đọc được không
            try:
                import pandas as pd
                test_df = pd.read_excel(file_path, nrows=1)
                
                self.input_file_path = file_path
                self.file_label.setText(f"✅ Đã chọn: {Path(file_path).name}")
                self.file_label.setStyleSheet("font-weight: 700; padding: 8px; color: rgba(34, 197, 94, 0.9);")
                self.process_btn.setEnabled(True)
                self.add_log(f"📂 Đã chọn file: {Path(file_path).name}")
                
                # Hiển thị thông tin file
                full_df = pd.read_excel(file_path)
                self.add_log(f"📊 File chứa {len(full_df)} dòng dữ liệu")
                
                # Kiểm tra các cột cần thiết
                required_cols = ['Hình thức sử dụng', 'Thời lượng']
                missing_cols = [col for col in required_cols if col not in full_df.columns]
                
                if missing_cols:
                    self.add_log(f"⚠️ Cảnh báo: Thiếu cột {', '.join(missing_cols)}")
                else:
                    self.add_log("✅ File có đầy đủ các cột cần thiết")
                    
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "❌ Lỗi đọc file",
                    f"Không thể đọc file Excel!\n\nLỗi: {str(e)}\n\nVui lòng kiểm tra:\n• File có đúng định dạng Excel không?\n• File có bị hỏng không?\n• File có đang mở trong ứng dụng khác không?"
                )
                return
            
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
        errors = []
        
        for usage_type, inputs in self.rate_inputs.items():
            try:
                full_rate = int(float(inputs['full'].text() or 0))
                half_rate = int(float(inputs['half'].text().replace(',', '') or 0))
                renew_rate = int(float(inputs['renew'].text().replace(',', '') or 0))
                
                royalty_dict[usage_type] = (full_rate, half_rate, renew_rate)
                
                if full_rate > 0:
                    has_valid_data = True
                    
            except (ValueError, TypeError) as e:
                errors.append(f"• {usage_type.title()}: {e}")
                
        if errors:
            error_msg = "❌ Lỗi nhập liệu:\n\n" + "\n".join(errors) + "\n\nVui lòng kiểm tra và nhập lại các giá trị hợp lệ."
            QMessageBox.warning(self, "Lỗi dữ liệu", error_msg)
            return None
                
        if not has_valid_data:
            QMessageBox.warning(
                self, 
                "Thiếu dữ liệu", 
                "⚠️ Vui lòng nhập ít nhất một mức nhuận bút!\n\nHướng dẫn:\n• Nhập mức nhuận bút đầy đủ cho các loại hình cần tính\n• Hệ thống sẽ tự động tính mức nửa bài và gia hạn"
            )
            return None
            
        valid_types = [k for k, v in royalty_dict.items() if v[0] > 0]
        self.add_log(f"✅ Đã cấu hình mức nhuận bút cho {len(valid_types)} loại hình: {', '.join([t.title() for t in valid_types])}")
        return royalty_dict
        
    def process_file(self):
        """Xử lý file Excel"""
        if not self.input_file_path:
            QMessageBox.warning(
                self, 
                "⚠️ Thiếu file đầu vào", 
                "Vui lòng chọn file Excel trước khi xử lý!\n\n📋 Hướng dẫn:\n• Nhấn nút 'Chọn file Excel'\n• Chọn file đã được xử lý ở tab 'Xử lý chính'\n• File phải có các cột: Thời lượng, Hình thức sử dụng"
            )
            return
            
        # Collect royalty data
        royalty_dict = self._collect_royalty_data()
        if not royalty_dict:
            return
            
        self.add_log("🚀 Bắt đầu xử lý file nhuận bút...")
        
        # Generate output path
        input_path = Path(self.input_file_path)
        output_path = input_path.parent / f"{input_path.stem}_NhuanBut_Premium.xlsx"
        
        self.add_log(f"📁 File đầu vào: {input_path.name}")
        self.add_log(f"📁 File kết quả: {output_path.name}")
        
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
            
            # Tạo custom success dialog
            success_dialog = QMessageBox(self)
            success_dialog.setWindowTitle("🎉 Thành công")
            success_dialog.setText("Xử lý file nhuận bút thành công!")
            success_dialog.setDetailedText(message)
            success_dialog.setIcon(QMessageBox.Icon.Information)
            success_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
            success_dialog.exec()
        else:
            self.progress_label.setText("Lỗi!")
            self.add_log(f"❌ {message}")
            
            # Tạo custom error dialog
            error_dialog = QMessageBox(self)
            error_dialog.setWindowTitle("❌ Lỗi xử lý")
            error_dialog.setText("Có lỗi xảy ra khi xử lý file!")
            error_dialog.setDetailedText(message)
            error_dialog.setIcon(QMessageBox.Icon.Critical)
            error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
            error_dialog.exec()
            
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