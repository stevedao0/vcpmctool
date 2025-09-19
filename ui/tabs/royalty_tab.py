# vcpmctool/ui/tabs/royalty_tab.py
"""
Tab tính nhuận bút cho vcpmctool
Giao diện Flet với layout nhập 6 loại hình và tỷ lệ %
"""
from core.royalty.processor import RoyaltyProcessor
import flet as ft
import os
from pathlib import Path
# from typing import Dict, Tuple, Optional  # Not used

# Import modules xử lý (cần thêm vào sys.path nếu cần)
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))


class RoyaltyTab(ft.UserControl):
    """Tab xử lý nhuận bút trong vcpmctool"""

    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.usage_types = [
            "Video",
            "Audio",
            "MV karaoke",
            "Midi karaoke",
            "Trailer",
            "Teaser"]
        self.royalty_dict = {}
        self.input_file_path = None
        self.processor = None

        # Create file picker in constructor so it can be added to page overlay
        self.file_picker = ft.FilePicker(on_result=self.on_file_picked)

        # UI Controls
        self.file_label = None
        self.progress_bar = None
        self.progress_text = None
        self.log_text = None
        self.process_button = None

        # Entry fields cho nhuận bút
        self.full_entries = {}  # Mức đầy đủ
        self.half_entries = {}  # Mức nửa bài
        self.renew_entries = {}  # Mức gia hạn

        self.half_percent_field = None
        self.renew_percent_field = None

    def build(self):
        # File picker is already created in constructor

        # File selection section
        self.file_label = ft.Text("Chưa chọn file", size=14)
        file_section = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Chọn file Excel cần xử lý:",
                    size=16,
                    weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.ElevatedButton(
                        "Chọn File Excel",
                        icon=ft.icons.FOLDER_OPEN,
                        on_click=lambda _: self.file_picker.pick_files(
                            allowed_extensions=["xlsx", "xls"],
                            file_type=ft.FilePickerFileType.CUSTOM
                        )
                    ),
                    self.file_label
                ])
            ]),
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5
        )

        # Royalty rates input section
        royalty_section = self._build_royalty_section()

        # Progress section
        self.progress_bar = ft.ProgressBar(width=400, value=0)
        self.progress_text = ft.Text("Sẵn sàng", size=12)
        progress_section = ft.Container(
            content=ft.Column([
                ft.Text("Tiến trình:", size=14, weight=ft.FontWeight.BOLD),
                self.progress_bar,
                self.progress_text
            ]),
            padding=10
        )

        # Log section
        self.log_text = ft.TextField(
            multiline=True,
            min_lines=5,
            max_lines=10,
            read_only=True,
            value="",
            border_color=ft.colors.GREY_400
        )
        log_section = ft.Container(
            content=ft.Column([
                ft.Text("Nhật ký xử lý:", size=14, weight=ft.FontWeight.BOLD),
                self.log_text
            ]),
            padding=10
        )

        # Process button
        self.process_button = ft.ElevatedButton(
            "Xử Lý File",
            icon=ft.icons.PLAY_ARROW,
            on_click=self.process_file,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor={
                    ft.MaterialState.DEFAULT: ft.colors.GREEN,
                    ft.MaterialState.DISABLED: ft.colors.GREY_400
                },
                color=ft.colors.WHITE
            )
        )

        # Main layout
        return ft.Column([
            file_section,
            royalty_section,
            ft.Row([self.process_button],
                   alignment=ft.MainAxisAlignment.CENTER),
            progress_section,
            log_section
        ], scroll=ft.ScrollMode.AUTO, expand=True)

    def _build_royalty_section(self) -> ft.Container:
        """Xây dựng phần nhập mức nhuận bút"""

        # Header row
        header = ft.Row([
            ft.Container(
                ft.Text(
                    "Loại hình",
                    weight=ft.FontWeight.BOLD),
                width=120),
            ft.Container(
                ft.Text(
                    "Tỷ lệ %",
                    weight=ft.FontWeight.BOLD),
                width=80),
        ])

        # Add usage type headers
        for utype in self.usage_types:
            header.controls.append(
                ft.Container(
                    ft.Text(
                        utype,
                        weight=ft.FontWeight.BOLD,
                        size=12),
                    width=100)
            )

        # Row 1: Mức nhuận bút đầy đủ
        self.full_entries = {}
        full_row = ft.Row([
            ft.Container(ft.Text("Mức nhuận bút"), width=120),
            ft.Container(width=80),  # Empty cell for %
        ])

        for utype in self.usage_types:
            entry = ft.TextField(
                width=100,
                height=40,
                text_size=12,
                border_radius=3,
                on_change=self.recalculate
            )
            self.full_entries[utype] = entry
            full_row.controls.append(entry)

        # Row 2: Mức nửa bài (50%)
        self.half_percent_field = ft.TextField(
            value="50",
            width=80,
            height=40,
            text_size=12,
            suffix_text="%",
            on_change=self.recalculate
        )

        self.half_entries = {}
        half_row = ft.Row([
            ft.Container(ft.Text("Mức nửa bài"), width=120),
            self.half_percent_field,
        ])

        for utype in self.usage_types:
            entry = ft.TextField(
                width=100,
                height=40,
                text_size=12,
                border_radius=3,
                read_only=True,
                bgcolor=ft.colors.GREY_200
            )
            self.half_entries[utype] = entry
            half_row.controls.append(entry)

        # Row 3: Mức gia hạn (40%)
        self.renew_percent_field = ft.TextField(
            value="40",
            width=80,
            height=40,
            text_size=12,
            suffix_text="%",
            on_change=self.recalculate
        )

        self.renew_entries = {}
        renew_row = ft.Row([
            ft.Container(ft.Text("Mức gia hạn"), width=120),
            self.renew_percent_field,
        ])

        for utype in self.usage_types:
            entry = ft.TextField(
                width=100,
                height=40,
                text_size=12,
                border_radius=3,
                read_only=True,
                bgcolor=ft.colors.GREY_200
            )
            self.renew_entries[utype] = entry
            renew_row.controls.append(entry)

        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Nhập mức nhuận bút:",
                    size=16,
                    weight=ft.FontWeight.BOLD),
                header,
                ft.Divider(),
                full_row,
                half_row,
                renew_row
            ]),
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5
        )

    def on_file_picked(self, e: ft.FilePickerResultEvent):
        """Xử lý khi chọn file"""
        if e.files and len(e.files) > 0:
            self.input_file_path = e.files[0].path
            self.file_label.value = f"Đã chọn: {
                os.path.basename(
                    self.input_file_path)}"
            self.process_button.disabled = False
            self.add_log(f"Đã chọn file: {self.input_file_path}")
        else:
            self.input_file_path = None
            self.file_label.value = "Chưa chọn file"
            self.process_button.disabled = True
        self.update()

    def recalculate(self, e=None):
        """Tính lại mức nửa bài và gia hạn khi thay đổi input"""
        try:
            half_percent = float(self.half_percent_field.value or 0) / 100
            renew_percent = float(self.renew_percent_field.value or 0) / 100

            for utype in self.usage_types:
                try:
                    full_value = float(self.full_entries[utype].value or 0)

                    # Tính mức nửa bài
                    half_value = int(full_value * half_percent)
                    self.half_entries[utype].value = str(half_value)

                    # Tính mức gia hạn
                    renew_value = int(full_value * renew_percent)
                    self.renew_entries[utype].value = str(renew_value)
                except BaseException:
                    self.half_entries[utype].value = "0"
                    self.renew_entries[utype].value = "0"

            self.update()
        except Exception as e:
            self.add_log(f"Lỗi tính toán: {e}")

    def collect_royalty_data(self) -> bool:
        """Thu thập dữ liệu nhuận bút từ form"""
        self.royalty_dict = {}
        has_valid_data = False

        for utype in self.usage_types:
            try:
                full_val = int(float(self.full_entries[utype].value or 0))
                half_val = int(float(self.half_entries[utype].value or 0))
                renew_val = int(float(self.renew_entries[utype].value or 0))

                self.royalty_dict[utype.lower()] = (
                    full_val, half_val, renew_val)

                if full_val > 0:
                    has_valid_data = True

            except ValueError as e:
                self.add_log(f"Lỗi nhập liệu cho {utype}: {e}")
                return False

        if not has_valid_data:
            self.add_log("⚠️ Vui lòng nhập ít nhất một mức nhuận bút!")
            return False

        self.add_log(
            f"✓ Đã thu thập mức nhuận bút cho {len(self.royalty_dict)} loại hình")
        return True

    def process_file(self, e=None):
        """Xử lý file Excel với nhuận bút"""
        if not self.input_file_path:
            self.add_log("❌ Chưa chọn file để xử lý!")
            return

        if not self.collect_royalty_data():
            return

        # Disable button during processing
        self.process_button.disabled = True
        self.progress_bar.value = 0
        self.progress_text.value = "Đang xử lý..."
        self.update()

        # Generate output filename
        input_path = Path(self.input_file_path)
        output_path = input_path.parent / f"{input_path.stem}_NhuanBut.xlsx"

        try:
            # Create processor
            self.processor = RoyaltyProcessor(self.royalty_dict)

            # Process file
            success, message = self.processor.process_file(
                self.input_file_path,
                str(output_path),
                progress_callback=self.update_progress,
                log_callback=self.add_log
            )

            if success:
                self.add_log(f"✅ {message}")
                self.progress_text.value = "Hoàn tất!"
                self.progress_bar.value = 100
            else:
                self.add_log(f"❌ {message}")
                self.progress_text.value = "Lỗi!"

        except Exception as e:
            self.add_log(f"❌ Lỗi không xác định: {e}")
            self.progress_text.value = "Lỗi!"

        finally:
            self.process_button.disabled = False
            self.update()

    def update_progress(self, value: float):
        """Cập nhật thanh tiến trình"""
        self.progress_bar.value = value / 100  # Flet uses 0-1 range
        self.progress_text.value = f"Đang xử lý... {value:.1f}%"
        self.update()

    def add_log(self, message: str):
        """Thêm log vào text field"""
        current_log = self.log_text.value or ""
        self.log_text.value = f"{current_log}\n{message}".strip()
        self.update()

        # Also log to main logger if available
        if self.logger:
            self.logger.info(f"[RoyaltyTab] {message}")
