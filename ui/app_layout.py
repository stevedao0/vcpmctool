# vcpmctool/ui/app_layout.py (Phiên bản cập nhật với tab Royalty)
import flet as ft
from .components import FileRow, ProgressBar, PreviewTable, LogPanel, LabeledSwitch
from .tabs.royalty_tab import RoyaltyTab  # Import tab mới
from core.pipeline import process_files
from services.logger import Logger
from services.settings import Settings


def create_app_layout(page: ft.Page, settings: Settings, logger: Logger):
    """Tạo layout chính của ứng dụng với các tab"""

    # Tab container
    tab_container = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[],
        expand=True
    )

    # ========== TAB 1: MAIN PROCESSING ==========
    log_panel = LogPanel(logger)
    progress_bar = ProgressBar()
    preview_table = PreviewTable()
    input_files_row = FileRow()

    def on_files_picked(e: ft.FilePickerResultEvent):
        if e.files:
            input_files_row.update_files(e.files)
            log_panel.add_text(f"Đã chọn {len(e.files)} file.")

    file_picker = ft.FilePicker(on_result=on_files_picked)

    # File picker cho tab Royalty
    royalty_tab_instance = RoyaltyTab(logger)
    page.overlay.extend([file_picker, royalty_tab_instance.file_picker])

    def process_handler(e):
        files = [f.path for f in input_files_row.files if f.path]
        if not files:
            log_panel.add_text("Chưa chọn file đầu vào.")
            return

        try:
            process_btn.disabled = True
            page.update()

            initial_term = int(initial_field.value.strip())
            ext_term = int(ext_field.value.strip())
            auto_proper = auto_proper_switch.get_value()

            progress_bar.update_progress(None)
            log_panel.add_text("Bắt đầu xử lý...")

            results, success = process_files(
                files, initial_term, ext_term, logger, auto_proper=auto_proper
            )

            if success:
                log_panel.add_text("Xử lý thành công!")
                preview_table.update_table(results)
            else:
                log_panel.add_text(
                    "Xử lý hoàn tất với một vài cảnh báo/lỗi. Vui lòng xem file log.")

            progress_bar.update_progress(1)

        except ValueError as ve:
            log_panel.add_text(f"Lỗi nhập liệu: {ve}")
        except Exception as ex:
            log_panel.add_text(f"Lỗi không xác định: {ex}")
        finally:
            process_btn.disabled = False
            page.update()

    # Source panel
    source_panel = ft.Container(
        content=ft.Column([
            ft.Text("Input Files", size=20, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                "Chọn File Excel",
                on_click=lambda _: file_picker.pick_files(
                    allow_multiple=True,
                    file_type=ft.FilePickerFileType.CUSTOM,
                    allowed_extensions=["xlsx"]
                )
            ),
            input_files_row,
        ]),
        padding=10
    )

    # Options panel
    auto_proper_switch = LabeledSwitch(
        "Định dạng tên riêng (Proper Case)",
        settings.auto_propercase)
    initial_field = ft.TextField(
        label="Thời hạn ban đầu (năm)",
        value="2",
        width=200)
    ext_field = ft.TextField(
        label="Thời hạn gia hạn (năm)",
        value="2",
        width=200)
    process_btn = ft.ElevatedButton(
        "Xử lý",
        on_click=process_handler,
        icon=ft.icons.PLAY_ARROW)

    options_panel = ft.Container(
        content=ft.Column([
            ft.Text("Options", size=20, weight=ft.FontWeight.BOLD),
            auto_proper_switch,
            initial_field,
            ext_field,
            process_btn
        ]),
        padding=10
    )

    # Main processing tab layout
    main_tab_content = ft.Row(
        [
            ft.Column([source_panel, options_panel], width=400),
            ft.VerticalDivider(),
            ft.Column([progress_bar, preview_table, log_panel], expand=True),
        ],
        expand=True
    )

    # ========== TAB 2: ROYALTY PROCESSING ==========
    royalty_content = ft.Container(
        content=royalty_tab_instance,
        padding=10
    )

    # ========== TAB 3: SETTINGS ==========
    def toggle_theme(e):
        page.theme_mode = (
            ft.ThemeMode.DARK
            if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        settings.theme_mode = page.theme_mode
        page.update()

    settings_content = ft.Container(
        content=ft.Column([
            ft.Text("Cài đặt", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row([
                ft.Text("Chế độ tối:"),
                ft.Switch(on_change=toggle_theme)
            ]),
            ft.Row([
                ft.Text("Tự động Proper Case:"),
                ft.Switch(
                    value=settings.auto_propercase,
                    on_change=lambda e: setattr(
                        settings, 'auto_propercase', e.control.value)
                )
            ]),
            ft.Text(""),
            ft.Text("Phiên bản: 1.0.0", size=12, italic=True),
            ft.Text("© 2024 VCPMC Tool", size=12, italic=True)
        ]),
        padding=20
    )

    # ========== HELP TAB ==========
    help_content = ft.Container(
        content=ft.Column([
            ft.Text("Hướng dẫn sử dụng", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text("Tab Xử lý chính:", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("• Chọn file Excel cần xử lý"),
            ft.Text("• Cấu hình các tùy chọn (thời hạn, proper case)"),
            ft.Text("• Nhấn 'Xử lý' để bắt đầu"),
            ft.Text(""),
            ft.Text("Tab Nhuận bút:", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("• Chọn file Excel có dữ liệu tác phẩm"),
            ft.Text("• Nhập mức nhuận bút cho từng loại hình"),
            ft.Text("• Hệ thống tự động tính mức nửa bài (50%) và gia hạn (40%)"),
            ft.Text("• Nhấn 'Xử lý File' để tính toán và xuất kết quả"),
            ft.Text(""),
            ft.Text(
                "Lưu ý:",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.RED),
            ft.Text(
                "• File Excel phải có các cột: Thời gian, Hình thức sử dụng, Share%"),
            ft.Text("• Mức nhuận bút tính theo giây (< 2 phút = mức nửa bài)"),
            ft.Text("• File kết quả sẽ lưu cùng thư mục với hậu tố '_NhuanBut'"),
        ], scroll=ft.ScrollMode.AUTO),
        padding=20
    )

    # Add all tabs
    tab_container.tabs = [
        ft.Tab(
            text="Xử lý chính",
            icon=ft.icons.HOME,
            content=main_tab_content
        ),
        ft.Tab(
            text="Nhuận bút",
            icon=ft.icons.CALCULATE,
            content=royalty_content
        ),
        ft.Tab(
            text="Cài đặt",
            icon=ft.icons.SETTINGS,
            content=settings_content
        ),
        ft.Tab(
            text="Hướng dẫn",
            icon=ft.icons.HELP,
            content=help_content
        )
    ]

    return tab_container
