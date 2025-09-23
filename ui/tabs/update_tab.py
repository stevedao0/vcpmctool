# vcpmctool/ui/tabs/update_tab.py - AIO YouTube Tool Integration
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QProgressBar, 
    QGroupBox, QFileDialog, QMessageBox, QFormLayout,
    QSpinBox, QFrame, QScrollArea, QSizePolicy, QComboBox,
    QCheckBox, QSlider, QTabWidget, QListWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QSplitter
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QProcess
from PySide6.QtGui import QFont
import pandas as pd
import os
import sys
import json
import threading
import subprocess
from pathlib import Path
from typing import Optional, List, Union, Dict

from services.logger import Logger


class AIOWorker(QThread):
    """Worker thread cho AIO operations qua subprocess"""
    
    progress_updated = Signal(int, int)  # done, total
    detail_progress = Signal(dict)  # detail info for downloads
    log_updated = Signal(str)
    finished = Signal(bool, str, str)  # success, message, result_path
    
    def __init__(self, operation: str, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
        self.process = None
        
    def run(self):
        try:
            # Tìm AIO executable
            aio_path = self._find_aio_executable()
            if not aio_path:
                self.finished.emit(False, "Không tìm thấy AIO Tool executable", "")
                return
                
            # Chuẩn bị command
            cmd = self._build_command(aio_path)
            
            # Chạy subprocess
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            # Đọc output
            while True:
                output = self.process.stdout.readline()
                if output == '' and self.process.poll() is not None:
                    break
                if output:
                    self._parse_output(output.strip())
                    
            # Kiểm tra kết quả
            return_code = self.process.poll()
            if return_code == 0:
                self.finished.emit(True, "Hoàn thành thành công!", self.kwargs.get('output_dir', ''))
            else:
                error = self.process.stderr.read()
                self.finished.emit(False, f"Lỗi: {error}", "")
                
        except Exception as e:
            self.finished.emit(False, f"Lỗi subprocess: {str(e)}", "")
            
    def _find_aio_executable(self) -> Optional[str]:
        """Tìm AIO executable"""
        base_dir = Path(__file__).parent.parent.parent
        possible_paths = [
            base_dir / "Update" / "main.py",
            base_dir / "Update" / "aio_tool.exe",
            base_dir / "aio_tool.exe"
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        return None
        
    def _build_command(self, aio_path: str) -> List[str]:
        """Xây dựng command line"""
        # Sử dụng CLI wrapper thay vì main.py
        base_dir = Path(aio_path).parent
        cli_wrapper = base_dir / "cli_wrapper.py"
        
        if cli_wrapper.exists():
            cmd = [sys.executable, str(cli_wrapper)]
        elif aio_path.endswith('.py'):
            cmd = [sys.executable, aio_path]
        else:
            cmd = [aio_path]
            
        # Thêm arguments dựa trên operation
        cmd.extend(['--operation', self.operation])
        
        for key, value in self.kwargs.items():
            if value is not None and value != '':
                cmd.extend([f'--{key}', str(value)])
                
        return cmd
        
    def _parse_output(self, line: str):
        """Parse output từ subprocess"""
        try:
            if line.startswith('PROGRESS:'):
                # Format: PROGRESS:done,total
                parts = line.replace('PROGRESS:', '').split(',')
                done, total = int(parts[0]), int(parts[1])
                self.progress_updated.emit(done, total)
            elif line.startswith('LOG:'):
                # Format: LOG:message
                message = line.replace('LOG:', '')
                self.log_updated.emit(message)
            elif line.startswith('DETAIL:'):
                # Format: DETAIL:json_data
                data_str = line.replace('DETAIL:', '')
                data = json.loads(data_str)
                self.detail_progress.emit(data)
            else:
                # Regular log message
                self.log_updated.emit(line)
        except Exception:
            self.log_updated.emit(line)
            
    def stop(self):
        if self.process:
            self.process.terminate()


class UpdateTab(QWidget):
    """Tab AIO YouTube Tool - Scraper, Checker, Downloader"""
    
    def __init__(self, logger: Logger):
        super().__init__()
        self.logger = logger
        self.worker = None
        self.output_dir = os.path.expanduser("~/Downloads/AIO_Output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Thiết lập giao diện Glass Morphism"""
        # Main scroll area
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
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("🚀 AIO YouTube Tool - Premium Edition")
        title_label.setStyleSheet("font-size: 24px; font-weight: 700; margin-bottom: 20px; text-align: center;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - Controls
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Progress & Log
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter sizes
        splitter.setSizes([500, 700])
        
    def _create_left_panel(self) -> QWidget:
        """Tạo panel trái với tabs"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Scraper Tab
        scraper_tab = self._create_scraper_tab()
        self.tab_widget.addTab(scraper_tab, "🔍 Scraper")
        
        # Checker Tab  
        checker_tab = self._create_checker_tab()
        self.tab_widget.addTab(checker_tab, "✅ Checker")
        
        # Downloader Tab
        downloader_tab = self._create_downloader_tab()
        self.tab_widget.addTab(downloader_tab, "⬇️ Downloader")
        
        layout.addWidget(self.tab_widget)
        
        # Global settings
        settings_group = self._create_global_settings()
        layout.addWidget(settings_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("🚀 Bắt đầu")
        self.start_btn.clicked.connect(self.start_operation)
        self.start_btn.setProperty("class", "primary")
        self.start_btn.setMinimumHeight(50)
        self.start_btn.setStyleSheet("font-size: 16px; font-weight: 700;")
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹️ Dừng")
        self.stop_btn.clicked.connect(self.stop_operation)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        self.launch_full_btn = QPushButton("🔧 Mở AIO Tool đầy đủ")
        self.launch_full_btn.clicked.connect(self.launch_full_tool)
        button_layout.addWidget(self.launch_full_btn)
        
        layout.addLayout(button_layout)
        
        return widget
        
    def _create_scraper_tab(self) -> QWidget:
        """Tạo tab Scraper"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Channel input
        channel_group = QGroupBox("📺 Kênh YouTube")
        channel_layout = QFormLayout(channel_group)
        
        self.channel_input = QLineEdit()
        self.channel_input.setPlaceholderText("URL kênh, @handle, hoặc Channel ID (UC...)")
        channel_layout.addRow("Kênh:", self.channel_input)
        
        layout.addWidget(channel_group)
        
        # Options
        options_group = QGroupBox("⚙️ Tùy chọn")
        options_layout = QFormLayout(options_group)
        
        self.scraper_limit = QSpinBox()
        self.scraper_limit.setRange(10, 1000)
        self.scraper_limit.setValue(200)
        options_layout.addRow("Giới hạn video:", self.scraper_limit)
        
        self.include_shorts = QCheckBox("Bao gồm YouTube Shorts")
        self.include_shorts.setChecked(True)
        options_layout.addRow(self.include_shorts)
        
        layout.addWidget(options_group)
        layout.addStretch()
        
        return widget
        
    def _create_checker_tab(self) -> QWidget:
        """Tạo tab Checker"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # File input
        file_group = QGroupBox("📁 File đầu vào")
        file_layout = QVBoxLayout(file_group)
        
        file_input_layout = QHBoxLayout()
        self.checker_file_input = QLineEdit()
        self.checker_file_input.setPlaceholderText("Chọn file Excel/CSV có cột 'ID Video'")
        self.checker_file_input.setReadOnly(True)
        file_input_layout.addWidget(self.checker_file_input)
        
        self.checker_browse_btn = QPushButton("📂 Chọn file")
        self.checker_browse_btn.clicked.connect(self.browse_checker_file)
        file_input_layout.addWidget(self.checker_browse_btn)
        
        file_layout.addLayout(file_input_layout)
        layout.addWidget(file_group)
        
        # Options
        options_group = QGroupBox("⚙️ Tùy chọn")
        options_layout = QFormLayout(options_group)
        
        self.checker_workers = QSpinBox()
        self.checker_workers.setRange(1, 8)
        self.checker_workers.setValue(4)
        options_layout.addRow("Số luồng:", self.checker_workers)
        
        layout.addWidget(options_group)
        layout.addStretch()
        
        return widget
        
    def _create_downloader_tab(self) -> QWidget:
        """Tạo tab Downloader"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Input
        input_group = QGroupBox("📥 Đầu vào")
        input_layout = QVBoxLayout(input_group)
        
        input_row = QHBoxLayout()
        self.downloader_input = QLineEdit()
        self.downloader_input.setPlaceholderText("Video ID/URL, file Excel/CSV, hoặc playlist URL")
        input_row.addWidget(self.downloader_input)
        
        self.downloader_browse_btn = QPushButton("📂 Chọn file")
        self.downloader_browse_btn.clicked.connect(self.browse_downloader_file)
        input_row.addWidget(self.downloader_browse_btn)
        
        input_layout.addLayout(input_row)
        layout.addWidget(input_group)
        
        # Quality settings
        quality_group = QGroupBox("🎥 Chất lượng")
        quality_layout = QFormLayout(quality_group)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems([
            "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
            "best",
            "bestvideo+bestaudio/best", 
            "worst",
            "720p",
            "480p"
        ])
        quality_layout.addRow("Chất lượng:", self.quality_combo)
        
        self.audio_only = QCheckBox("Chỉ tải âm thanh (MP3)")
        quality_layout.addRow(self.audio_only)
        
        layout.addWidget(quality_group)
        
        # Performance settings
        perf_group = QGroupBox("⚡ Hiệu năng")
        perf_layout = QFormLayout(perf_group)
        
        self.download_workers = QSpinBox()
        self.download_workers.setRange(1, 4)
        self.download_workers.setValue(2)
        perf_layout.addRow("Số luồng tải:", self.download_workers)
        
        self.concurrent_frags = QSpinBox()
        self.concurrent_frags.setRange(1, 16)
        self.concurrent_frags.setValue(8)
        perf_layout.addRow("Mảnh đồng thời:", self.concurrent_frags)
        
        layout.addWidget(perf_group)
        
        # Advanced settings
        advanced_group = QGroupBox("🔧 Nâng cao")
        advanced_layout = QFormLayout(advanced_group)
        
        cookies_row = QHBoxLayout()
        self.cookies_input = QLineEdit()
        self.cookies_input.setPlaceholderText("Đường dẫn file cookies.txt (tùy chọn)")
        cookies_row.addWidget(self.cookies_input)
        
        self.cookies_browse_btn = QPushButton("📂")
        self.cookies_browse_btn.clicked.connect(self.browse_cookies_file)
        cookies_row.addWidget(self.cookies_browse_btn)
        
        advanced_layout.addRow("Cookies:", cookies_row)
        
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("http://user:pass@host:port")
        advanced_layout.addRow("Proxy:", self.proxy_input)
        
        self.use_aria2 = QCheckBox("Sử dụng aria2c")
        advanced_layout.addRow(self.use_aria2)
        
        self.use_archive = QCheckBox("Tránh tải trùng")
        self.use_archive.setChecked(True)
        advanced_layout.addRow(self.use_archive)
        
        layout.addWidget(advanced_group)
        layout.addStretch()
        
        return widget
        
    def _create_global_settings(self) -> QGroupBox:
        """Tạo cài đặt chung"""
        group = QGroupBox("🌐 Cài đặt chung")
        layout = QFormLayout(group)
        
        # Output directory
        output_row = QHBoxLayout()
        self.output_dir_input = QLineEdit(self.output_dir)
        self.output_dir_input.setReadOnly(True)
        output_row.addWidget(self.output_dir_input)
        
        self.output_browse_btn = QPushButton("📂 Chọn")
        self.output_browse_btn.clicked.connect(self.browse_output_dir)
        output_row.addWidget(self.output_browse_btn)
        
        layout.addRow("Thư mục xuất:", output_row)
        
        return group
        
    def _create_right_panel(self) -> QWidget:
        """Tạo panel phải với progress và log"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Progress section
        progress_group = QGroupBox("📊 Tiến trình")
        progress_layout = QVBoxLayout(progress_group)
        
        # Overall progress
        self.overall_label = QLabel("Sẵn sàng")
        self.overall_label.setStyleSheet("font-weight: 600; font-size: 14px;")
        progress_layout.addWidget(self.overall_label)
        
        self.overall_progress = QProgressBar()
        self.overall_progress.setVisible(False)
        progress_layout.addWidget(self.overall_progress)
        
        # Current item progress
        self.current_label = QLabel("")
        self.current_label.setStyleSheet("font-size: 12px; color: #666;")
        progress_layout.addWidget(self.current_label)
        
        self.current_progress = QProgressBar()
        self.current_progress.setVisible(False)
        progress_layout.addWidget(self.current_progress)
        
        layout.addWidget(progress_group)
        
        # Log section
        log_group = QGroupBox("📝 Nhật ký")
        log_layout = QVBoxLayout(log_group)
        
        # Log controls
        log_controls = QHBoxLayout()
        
        self.clear_log_btn = QPushButton("🗑️ Xóa log")
        self.clear_log_btn.clicked.connect(self.clear_log)
        log_controls.addWidget(self.clear_log_btn)
        
        self.save_log_btn = QPushButton("💾 Lưu log")
        self.save_log_btn.clicked.connect(self.save_log)
        log_controls.addWidget(self.save_log_btn)
        
        log_controls.addStretch()
        log_layout.addLayout(log_controls)
        
        # Log text
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setMaximumHeight(300)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        # Results section
        results_group = QGroupBox("📋 Kết quả")
        results_layout = QVBoxLayout(results_group)
        
        self.results_table = QTableWidget()
        self.results_table.setMaximumHeight(200)
        results_layout.addWidget(self.results_table)
        
        layout.addWidget(results_group)
        
        return widget
        
    def browse_checker_file(self):
        """Chọn file cho checker"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn file Excel/CSV",
            "",
            "Excel/CSV Files (*.xlsx *.xls *.csv)"
        )
        if file_path:
            self.checker_file_input.setText(file_path)
            
    def browse_downloader_file(self):
        """Chọn file cho downloader"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn file danh sách",
            "",
            "Excel/CSV Files (*.xlsx *.xls *.csv)"
        )
        if file_path:
            self.downloader_input.setText(file_path)
            
    def browse_cookies_file(self):
        """Chọn file cookies"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn file cookies.txt",
            "",
            "Text Files (*.txt)"
        )
        if file_path:
            self.cookies_input.setText(file_path)
            
    def browse_output_dir(self):
        """Chọn thư mục xuất"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Chọn thư mục xuất",
            self.output_dir
        )
        if dir_path:
            self.output_dir = dir_path
            self.output_dir_input.setText(dir_path)
            
    def start_operation(self):
        """Bắt đầu operation"""
        current_tab = self.tab_widget.currentIndex()
        
        if current_tab == 0:  # Scraper
            self._start_scraper()
        elif current_tab == 1:  # Checker
            self._start_checker()
        elif current_tab == 2:  # Downloader
            self._start_downloader()
            
    def _start_scraper(self):
        """Bắt đầu scraper"""
        if not self.channel_input.text().strip():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập kênh YouTube!")
            return
            
        self._prepare_ui_for_operation()
        
        self.worker = AIOWorker(
            operation="scraper",
            channel=self.channel_input.text().strip(),
            output_dir=self.output_dir,
            limit=self.scraper_limit.value(),
            include_shorts=self.include_shorts.isChecked()
        )
        
        self._connect_worker_signals()
        self.worker.start()
        
    def _start_checker(self):
        """Bắt đầu checker"""
        if not self.checker_file_input.text().strip():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn file đầu vào!")
            return
            
        self._prepare_ui_for_operation()
        
        self.worker = AIOWorker(
            operation="checker",
            file_path=self.checker_file_input.text(),
            output_dir=self.output_dir,
            max_workers=self.checker_workers.value()
        )
        
        self._connect_worker_signals()
        self.worker.start()
        
    def _start_downloader(self):
        """Bắt đầu downloader"""
        if not self.downloader_input.text().strip():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập đầu vào!")
            return
            
        self._prepare_ui_for_operation()
        
        self.worker = AIOWorker(
            operation="downloader",
            input_value=self.downloader_input.text().strip(),
            output_dir=self.output_dir,
            quality=self.quality_combo.currentText(),
            audio_only=self.audio_only.isChecked(),
            max_workers=self.download_workers.value(),
            concurrent_frags=self.concurrent_frags.value(),
            cookies_file=self.cookies_input.text() or None,
            proxy=self.proxy_input.text() or None,
            enable_aria2=self.use_aria2.isChecked(),
            use_archive=self.use_archive.isChecked()
        )
        
        self._connect_worker_signals()
        self.worker.start()
        
    def _prepare_ui_for_operation(self):
        """Chuẩn bị UI cho operation"""
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.overall_progress.setVisible(True)
        self.overall_progress.setValue(0)
        self.overall_label.setText("Đang khởi động...")
        self.add_log("🚀 Bắt đầu operation...")
        
    def _connect_worker_signals(self):
        """Kết nối signals của worker"""
        self.worker.progress_updated.connect(self._update_progress)
        self.worker.detail_progress.connect(self._update_detail_progress)
        self.worker.log_updated.connect(self.add_log)
        self.worker.finished.connect(self._on_operation_finished)
        
    def _update_progress(self, done: int, total: int):
        """Cập nhật tiến trình tổng"""
        if total > 0:
            self.overall_progress.setValue(int((done / total) * 100))
            self.overall_label.setText(f"Đang xử lý: {done}/{total}")
        else:
            self.overall_progress.setValue(0)
            
    def _update_detail_progress(self, data: dict):
        """Cập nhật tiến trình chi tiết"""
        phase = data.get('phase', '')
        if phase == 'downloading':
            percent = data.get('percent', 0)
            if percent:
                self.current_progress.setVisible(True)
                self.current_progress.setValue(int(percent * 100))
                
                filename = data.get('filename', '')
                speed = data.get('speed', 0)
                eta = data.get('eta', 0)
                
                status_parts = []
                if filename:
                    status_parts.append(f"📁 {os.path.basename(filename)}")
                if speed:
                    status_parts.append(f"⚡ {speed/1024/1024:.1f} MB/s")
                if eta:
                    status_parts.append(f"⏱️ {eta}s")
                    
                self.current_label.setText(" • ".join(status_parts))
        elif phase in ('finished', 'postprocessing'):
            self.current_progress.setVisible(False)
            self.current_label.setText("✅ Hoàn tất tải xuống")
            
    def _on_operation_finished(self, success: bool, message: str, result_path: str):
        """Xử lý khi operation hoàn tất"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.overall_progress.setVisible(False)
        self.current_progress.setVisible(False)
        
        if success:
            self.overall_label.setText("✅ Hoàn thành!")
            self.add_log(f"✅ {message}")
            if result_path:
                self.add_log(f"📁 Kết quả: {result_path}")
                
            # Hiển thị dialog thành công
            QMessageBox.information(
                self,
                "🎉 Thành công",
                f"{message}\n\n📁 Kết quả đã lưu tại:\n{result_path}"
            )
        else:
            self.overall_label.setText("❌ Lỗi!")
            self.add_log(f"❌ {message}")
            
            # Hiển thị dialog lỗi
            QMessageBox.critical(
                self,
                "❌ Lỗi",
                f"Có lỗi xảy ra:\n\n{message}"
            )
            
    def stop_operation(self):
        """Dừng operation"""
        if self.worker:
            self.worker.stop()
            self.add_log("⏹️ Đang dừng operation...")
            
    def launch_full_tool(self):
        """Mở AIO Tool đầy đủ"""
        try:
            base_dir = Path(__file__).parent.parent.parent
            aio_path = base_dir / "Update" / "main.py"
            
            if aio_path.exists():
                # Chạy AIO tool như process riêng
                subprocess.Popen([sys.executable, str(aio_path)], 
                               cwd=str(aio_path.parent))
                self.add_log("🔧 Đã mở AIO Tool đầy đủ")
            else:
                QMessageBox.warning(
                    self,
                    "Cảnh báo", 
                    "Không tìm thấy AIO Tool!\n\nVui lòng kiểm tra folder Update."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Không thể mở AIO Tool:\n{str(e)}"
            )
            
    def add_log(self, message: str):
        """Thêm log với timestamp"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        self.log_text.append(formatted_message)
        
        if self.logger:
            self.logger.info(f"[AIO] {message}")
            
        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
        
    def clear_log(self):
        """Xóa log"""
        self.log_text.clear()
        
    def save_log(self):
        """Lưu log"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu log",
            f"aio_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                self.add_log(f"💾 Đã lưu log: {file_path}")
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Lỗi",
                    f"Không thể lưu log:\n{str(e)}"
                )