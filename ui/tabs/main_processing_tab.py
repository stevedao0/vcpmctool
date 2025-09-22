# vcpmctool/ui/tabs/main_processing_tab.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QLabel, QLineEdit, QCheckBox,
    QListWidget, QTableWidget, QTableWidgetItem,
    QTextEdit, QProgressBar, QGroupBox, QFormLayout,
    QFileDialog, QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont
import pandas as pd
from pathlib import Path

from core.pipeline import process_files
from services.settings import Settings
from services.logger import Logger


class ProcessingWorker(QThread):
    """Worker thread để xử lý file không block UI"""
    
    progress_updated = Signal(int)
    status_updated = Signal(str)
    finished = Signal(pd.DataFrame, bool)
    error_occurred = Signal(str)
    
    def __init__(self, files, initial_term, ext_term, logger, auto_proper):
        super().__init__()
        self.files = files
        self.initial_term = initial_term
        self.ext_term = ext_term
        self.logger = logger
        self.auto_proper = auto_proper
        
    def run(self):
        try:
            self.status_updated.emit("Đang xử lý file...")
            self.progress_updated.emit(10)
            
            results, success = process_files(
                self.files,
                self.initial_term,
                self.ext_term,
                self.logger,
                auto_backup=True,
                auto_proper=self.auto_proper
            )
            
            self.progress_updated.emit(100)
            self.status_updated.emit("Hoàn tất!" if success else "Hoàn tất với cảnh báo")
            self.finished.emit(results, success)
            
        except Exception as e:
            self.error_occurred.emit(str(e))


class MainProcessingTab(QWidget):
    """Tab xử lý chính"""
    
    def __init__(self, settings: Settings, logger: Logger):
        super().__init__()
        self.settings = settings
        self.logger = logger
        self.selected_files = []
        self.worker = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Thiết lập giao diện"""
        layout = QHBoxLayout(self)
        
        # Splitter chính
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Panel trái - Input và Options
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # Panel phải - Preview và Log
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        # Thiết lập tỷ lệ splitter
        splitter.setSizes([400, 800])
        
    def _create_left_panel(self) -> QWidget:
        """Tạo panel trái"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # File selection group
        file_group = QGroupBox("📁 Chọn file đầu vào")
        file_layout = QVBoxLayout(file_group)
        
        self.select_btn = QPushButton("Chọn file Excel")
        self.select_btn.clicked.connect(self.select_files)
        file_layout.addWidget(self.select_btn)
        
        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(150)
        file_layout.addWidget(self.file_list)
        
        layout.addWidget(file_group)
        
        # Options group
        options_group = QGroupBox("⚙️ Tùy chọn")
        options_layout = QFormLayout(options_group)
        
        self.initial_term_edit = QLineEdit("2")
        self.initial_term_edit.setToolTip("Thời hạn ban đầu tính bằng năm")
        options_layout.addRow("Thời hạn ban đầu (năm):", self.initial_term_edit)
        
        self.ext_term_edit = QLineEdit("2")
        self.ext_term_edit.setToolTip("Thời hạn gia hạn tính bằng năm")
        options_layout.addRow("Thời hạn gia hạn (năm):", self.ext_term_edit)
        
        self.auto_proper_cb = QCheckBox("Tự động định dạng tên riêng (Proper Case)")
        self.auto_proper_cb.setChecked(self.settings.auto_propercase)
        self.auto_proper_cb.setToolTip("Tự động viết hoa chữ cái đầu của từng từ")
        options_layout.addRow(self.auto_proper_cb)
        
        layout.addWidget(options_group)
        
        # Process button
        self.process_btn = QPushButton("▶️ Bắt đầu xử lý")
        self.process_btn.setEnabled(False)
        self.process_btn.clicked.connect(self.process_files)
        self.process_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px;
                font-weight: bold;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #ffffff;
            }
        """)
        layout.addWidget(self.process_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Sẵn sàng")
        self.status_label.setStyleSheet("color: #666666; font-style: italic;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        return widget
        
    def _create_right_panel(self) -> QWidget:
        """Tạo panel phải"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Splitter dọc cho preview và log
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        # Preview table
        preview_group = QGroupBox("👁️ Xem trước kết quả")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_table = QTableWidget()
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.preview_table.horizontalHeader().setStretchLastSection(True)
        preview_layout.addWidget(self.preview_table)
        
        splitter.addWidget(preview_group)
        
        # Log panel
        log_group = QGroupBox("📝 Nhật ký xử lý")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log_text)
        
        splitter.addWidget(log_group)
        
        # Thiết lập tỷ lệ splitter
        splitter.setSizes([500, 200])
        
        return widget
        
    def select_files(self):
        """Chọn file đầu vào"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Chọn file Excel",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        
        if files:
            self.selected_files = files
            self.file_list.clear()
            
            for file_path in files:
                self.file_list.addItem(Path(file_path).name)
                
            self.process_btn.setEnabled(True)
            self.add_log(f"Đã chọn {len(files)} file")
            
    def process_files(self):
        """Xử lý file"""
        if not self.selected_files:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn file trước khi xử lý!")
            return
            
        try:
            initial_term = int(self.initial_term_edit.text().strip())
            ext_term = int(self.ext_term_edit.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập số hợp lệ cho thời hạn!")
            return
            
        # Disable UI during processing
        self.process_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Create and start worker thread
        self.worker = ProcessingWorker(
            self.selected_files,
            initial_term,
            ext_term,
            self.logger,
            self.auto_proper_cb.isChecked()
        )
        
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.status_updated.connect(self.status_label.setText)
        self.worker.finished.connect(self._on_processing_finished)
        self.worker.error_occurred.connect(self._on_processing_error)
        
        self.worker.start()
        self.add_log("Bắt đầu xử lý file...")
        
    def _on_processing_finished(self, results: pd.DataFrame, success: bool):
        """Xử lý khi hoàn tất"""
        self.process_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.add_log("✅ Xử lý thành công!")
            self._update_preview_table(results)
        else:
            self.add_log("⚠️ Xử lý hoàn tất với cảnh báo. Vui lòng kiểm tra log.")
            
        # Auto-hide progress after 3 seconds
        QTimer.singleShot(3000, lambda: self.status_label.setText("Sẵn sàng"))
        
    def _on_processing_error(self, error_msg: str):
        """Xử lý khi có lỗi"""
        self.process_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Lỗi!")
        
        self.add_log(f"❌ Lỗi: {error_msg}")
        QMessageBox.critical(self, "Lỗi", f"Có lỗi xảy ra:\n{error_msg}")
        
    def _update_preview_table(self, df: pd.DataFrame):
        """Cập nhật bảng xem trước"""
        if df.empty:
            return
            
        # Chọn các cột quan trọng để hiển thị
        preview_cols = [
            col for col in [
                "STT", "ID Video", "Tên tác phẩm", "Tác giả",
                "Ngày bắt đầu", "Thời hạn kết thúc", "Hình thức sử dụng"
            ] if col in df.columns
        ]
        
        preview_df = df[preview_cols].head(50)  # Chỉ hiển thị 50 dòng đầu
        
        # Thiết lập table
        self.preview_table.setRowCount(len(preview_df))
        self.preview_table.setColumnCount(len(preview_cols))
        self.preview_table.setHorizontalHeaderLabels(preview_cols)
        
        # Điền dữ liệu
        for row_idx, (_, row) in enumerate(preview_df.iterrows()):
            for col_idx, col_name in enumerate(preview_cols):
                item = QTableWidgetItem(str(row[col_name]))
                self.preview_table.setItem(row_idx, col_idx, item)
                
        # Auto-resize columns
        self.preview_table.resizeColumnsToContents()
        header = self.preview_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        self.add_log(f"Hiển thị {len(preview_df)} dòng đầu tiên trong bảng xem trước")
        
    def add_log(self, message: str):
        """Thêm log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        self.log_text.append(formatted_message)
        self.logger.info(message)
        
        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)