# -*- coding: utf-8 -*-
import os, io, time, threading, multiprocessing, sys
from pathlib import Path

# ---- FFmpeg bootstrap (bundle-friendly)
def _inject_ffmpeg_into_path():
    try:
        base = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
        ffdir = os.path.join(base, "ffmpeg")
        if os.path.isdir(ffdir):
            os.environ["PATH"] = ffdir + os.pathsep + os.environ.get("PATH", "")
            os.environ.setdefault("FFMPEG_LOCATION", ffdir)
    except Exception:
        pass

_inject_ffmpeg_into_path()

import flet as ft
from flet import Colors, Icons, ThemeMode, FontWeight, padding, margin, ScrollMode
from ui.widgets import group_tile, sticky_actions, status_bar, two_pane
from core.ScraperChecker import run_scraper, run_checker, run_downloader

def main(page: ft.Page):
    page.title = "AIO • YouTube Scraper • Checker • Downloader"
    page.theme = ft.Theme(color_scheme_seed=Colors.ORANGE_200)
    page.theme_mode = ThemeMode.LIGHT
    page.bgcolor = Colors.GREY_50
    page.window_width = 1100
    page.window_height = 820

    # ===== AppBar
    def toggle_theme(_):
        page.theme_mode = ThemeMode.DARK if page.theme_mode == ThemeMode.LIGHT else ThemeMode.LIGHT
        theme_btn.icon = Icons.LIGHT_MODE if page.theme_mode == ThemeMode.LIGHT else Icons.DARK_MODE
        page.update()
    theme_btn = ft.IconButton(icon=Icons.LIGHT_MODE, tooltip="Chuyển giao diện", on_click=toggle_theme)

    # Chọn tỉ lệ chia 2-pane
    ratio_dd = ft.Dropdown(
        label="Bố cục",
        value="2/3 : 1/3",
        options=[ft.dropdown.Option("2/3 : 1/3"),
                 ft.dropdown.Option("1/2 : 1/2"),
                 ft.dropdown.Option("1/3 : 2/3")],
        width=140
    )
    page.appbar = ft.AppBar(
        title=ft.Text("AIO • YouTube Scraper • Checker • Downloader", weight=FontWeight.BOLD, size=20),
        center_title=True, bgcolor=Colors.SURFACE, actions=[ratio_dd, theme_btn], elevation=2
    )

    # ===== Global
    output_dir = os.path.expanduser("~/Downloads"); os.makedirs(output_dir, exist_ok=True)
    stop_event = threading.Event()
    log_buffer = io.StringIO()

    # ===== Helpers
    def map_ratio(v: str):
        return {"2/3 : 1/3": (2,1), "1/2 : 1/2": (1,1), "1/3 : 2/3": (1,2)}.get(v, (2,1))

    def trim_log_if_needed():
        # tránh phình bộ nhớ: giữ tối đa 2000 dòng
        if len(log_list.controls) > 2000:
            del log_list.controls[:500]

    def log(msg, prefix=''):
        line = f"{time.strftime('%H:%M:%S')} | {prefix} {msg}"
        log_buffer.write(line + "\n")
        log_list.controls.append(ft.Text(line, size=12, font_family="Consolas"))
        trim_log_if_needed()
        page.update()

    # Tổng tiến trình
    overall_text = ft.Text("0/0", size=12)
    overall_bar = ft.ProgressBar(value=0, color=Colors.PRIMARY, expand=True)
    def overall_progress(done, total=0, *_):
        try: d = int(done); t = int(total)
        except Exception: d, t = 0, 0
        overall_text.value = f"{d}/{t}"
        overall_bar.value = None if t == 0 else d / t
        page.update()

    # Chi tiết 1 file
    current_title = ft.Text("Chưa bắt đầu", size=12)
    current_meta = ft.Text("", size=11, color=Colors.GREY_700)
    current_bar = ft.ProgressBar(value=0, color=Colors.AMBER, expand=True)
    def detail_progress(data: dict):
        phase = data.get('phase')
        if phase == 'downloading':
            p = data.get('percent'); spd = data.get('speed'); eta = data.get('eta')
            current_title.value = f"Đang tải: {os.path.basename(data.get('filename') or '')}"
            current_bar.value = max(0.0, min(1.0, p if p is not None else 0.0))
            parts = []
            if p is not None: parts.append(f"{p*100:0.1f}%")
            if spd: parts.append(f"{spd/1024/1024:0.2f} MB/s")
            if eta: parts.append(f"ETA {int(eta)}s")
            current_meta.value = " · ".join(parts)
        elif phase == 'finished':
            current_title.value = "Đã tải xong, đang hợp nhất/hậu xử lý..."
            current_bar.value = None; current_meta.value = ""
        elif phase == 'postprocessing':
            current_title.value = "Hậu xử lý (merge/convert/thumbnail/metadata)..."
            current_bar.value = None; current_meta.value = ""
        else:
            current_title.value = "Chuẩn bị..."; current_bar.value = None; current_meta.value = ""
        page.update()

    # ===== Pickers
    file_picker = ft.FilePicker(); d_file_picker = ft.FilePicker()
    cookies_picker = ft.FilePicker(); folder_picker = ft.FilePicker()
    page.overlay.extend([file_picker, d_file_picker, cookies_picker, folder_picker])

    def on_folder_chosen(e: ft.FilePickerResultEvent):
        nonlocal output_dir
        if e.path:
            output_dir = e.path
            scraper_out.value = output_dir; downloader_out.value = output_dir
            page.update()
    folder_picker.on_result = on_folder_chosen

    # ===== Left Pane: Tabs + cấu hình (scroll riêng)
    # --- Scraper
    scraper_channel = ft.TextField(label="URL / ID Kênh", expand=True, filled=True)
    scraper_out = ft.TextField(label="Thư mục xuất", expand=True, value=output_dir, disabled=True, filled=True)
    scraper_browse = ft.OutlinedButton("Chọn thư mục...", icon=Icons.FOLDER,
                                       on_click=lambda _: folder_picker.get_directory_path(dialog_title="Chọn thư mục"))
    scraper_panel = ft.Column([
        group_tile(Icons.LINK, "Kênh", ft.Row([scraper_channel], spacing=8), expanded=True),
        group_tile(Icons.FOLDER, "Thư mục", ft.Row([scraper_out, scraper_browse], spacing=8), expanded=True),
    ], scroll=ScrollMode.AUTO)

    # --- Checker
    checker_file_path = ""
    checker_file = ft.TextField(label="File .xlsx/.csv có cột 'ID Video'", expand=True, disabled=True, filled=True)
    checker_browse_file = ft.OutlinedButton("Chọn file...", icon=Icons.FOLDER_OPEN,
        on_click=lambda _: file_picker.pick_files(allow_multiple=False, dialog_title="Chọn file .xlsx/.csv",
                                                  allowed_extensions=['xlsx','xls','csv']))
    def on_checker_file(e: ft.FilePickerResultEvent):
        nonlocal checker_file_path
        if e.files:
            checker_file_path = e.files[0].path; checker_file.value = checker_file_path; page.update()
    file_picker.on_result = on_checker_file
    checker_panel = ft.Column([
        group_tile(Icons.DESCRIPTION, "File đầu vào", ft.Row([checker_file, checker_browse_file], spacing=8), expanded=True),
        group_tile(Icons.FOLDER, "Thư mục", ft.Row([scraper_out, scraper_browse], spacing=8), expanded=False)
    ], scroll=ScrollMode.AUTO)

    # --- Downloader
    downloader_input = ft.TextField(
        label="ID/URL Video • hoặc • File (.xlsx/.csv) có cột 'ID Video' • hoặc URL playlist/kênh/shorts",
        expand=True, filled=True
    )
    downloader_pick_file = ft.OutlinedButton("Chọn file danh sách...", icon=Icons.ATTACH_FILE,
        on_click=lambda _: d_file_picker.pick_files(allow_multiple=False, dialog_title="Chọn file .xlsx/.csv",
                                                    allowed_extensions=['xlsx','xls','csv']))
    def on_dl_file(e: ft.FilePickerResultEvent):
        if e.files: downloader_input.value = e.files[0].path; page.update()
    d_file_picker.on_result = on_dl_file

    quality = ft.Dropdown(
        label="Chất lượng",
        options=[ft.dropdown.Option("bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"),
                 ft.dropdown.Option("best"),
                 ft.dropdown.Option("bestvideo+bestaudio/best"),
                 ft.dropdown.Option("worst")],
        value="bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
        expand=True
    )
    audio_only = ft.Checkbox(label="Chỉ âm thanh (MP3)", value=False)
    threads = ft.Slider(min=1, max=4, divisions=3, value=2, label="{value} luồng")
    con_frags = ft.Slider(min=1, max=16, divisions=15, value=8, label="{value} mảnh/luồng")

    downloader_out = ft.TextField(label="Thư mục tải về", expand=True, value=output_dir, disabled=True, filled=True)
    downloader_browse_out = ft.OutlinedButton("Chọn thư mục...", icon=Icons.FOLDER,
        on_click=lambda _: folder_picker.get_directory_path(dialog_title="Chọn thư mục tải về"))

    cookies_text = ft.TextField(label="cookies.txt (tùy chọn)", expand=True, read_only=True, value="")
    cookies_pick = ft.OutlinedButton("Chọn cookies.txt", icon=Icons.FILE_OPEN,
        on_click=lambda _: cookies_picker.pick_files(allow_multiple=False, dialog_title="Chọn cookies.txt", allowed_extensions=['txt']))
    def on_cookies(e: ft.FilePickerResultEvent):
        if e.files: cookies_text.value = e.files[0].path; page.update()
    cookies_picker.on_result = on_cookies

    proxy_text = ft.TextField(label="Proxy (vd: http://user:pass@host:port)", expand=True, value="")
    use_archive = ft.Checkbox(label="Không tải trùng (download_archive.txt)", value=True)
    use_aria2 = ft.Checkbox(label="Dùng aria2c nếu có", value=False)

    downloader_panel = ft.Column([
        group_tile(Icons.LINK, "Đầu vào", ft.Row([downloader_input, downloader_pick_file], spacing=8), expanded=True),
        group_tile(Icons.SETTINGS, "Tuỳ chọn tải", ft.Row([quality, audio_only], spacing=8), expanded=True),
        group_tile(Icons.SPEED, "Hiệu năng", ft.Row([threads, con_frags], spacing=8), expanded=False),
        group_tile(Icons.SECURITY, "Cookies & Proxy", ft.Row([cookies_text, cookies_pick, proxy_text], spacing=8), expanded=False),
        group_tile(Icons.TUNE, "Khác", ft.Row([use_archive, use_aria2], spacing=16), expanded=False),
        group_tile(Icons.FOLDER, "Thư mục tải về", ft.Row([downloader_out, downloader_browse_out], spacing=8), expanded=True),
    ], scroll=ScrollMode.AUTO)

    tab_scraper = ft.Tab(text="Scraper", icon=Icons.LIST)
    tab_checker = ft.Tab(text="Checker", icon=Icons.CHECK_CIRCLE)
    tab_downloader = ft.Tab(text="Downloader", icon=Icons.DOWNLOAD)
    tabs = ft.Tabs(tabs=[tab_scraper, tab_checker, tab_downloader], selected_index=2)

    left_panel = ft.Column([tabs], expand=True, spacing=10, scroll=ScrollMode.AUTO)

    def update_left_panel(_=None):
        # thay nội dung theo tab
        left_panel.controls = [tabs,
            scraper_panel if tabs.selected_index == 0 else
            checker_panel if tabs.selected_index == 1 else
            downloader_panel
        ]
        page.update()
    tabs.on_change = update_left_panel
    update_left_panel()

    # ===== Right Pane: tiến trình + log (scroll riêng)
    spinner = ft.ProgressRing(visible=False)
    start_btn = ft.FilledButton("Bắt đầu", icon=Icons.PLAY_ARROW, bgcolor=Colors.PRIMARY, color=Colors.ON_PRIMARY, height=40)
    cancel_btn = ft.OutlinedButton("Huỷ", icon=Icons.CLOSE, on_click=lambda _: stop_event.set())
    clear_log_btn = ft.OutlinedButton("Clear", icon=Icons.CLEAR, on_click=lambda _: (log_list.controls.clear(), page.update()))
    save_log_btn = ft.OutlinedButton("Lưu log", icon=Icons.SAVE, on_click=lambda _: save_log())

    def save_log():
        path = os.path.join(output_dir, "app_log.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(log_buffer.getvalue())
        log(f"Đã lưu log: {path}", "[System]")

    log_list = ft.ListView(expand=True, spacing=2, auto_scroll=True)

    right_panel = ft.Column([
        group_tile(Icons.TIMER, "Tiến trình hiện tại", ft.Column([
            current_title,
            ft.Container(current_bar, padding=padding.only(top=6, bottom=6)),
            current_meta
        ], spacing=4), expanded=True),
        group_tile(Icons.ANALYTICS, "Tiến trình tổng", status_bar(overall_text, overall_bar), expanded=True),
        sticky_actions([start_btn, cancel_btn], [clear_log_btn, save_log_btn]),
        ft.Card(content=ft.Container(content=log_list, height=420, padding=8),
                elevation=1, margin=margin.only(top=8),
                shape=ft.RoundedRectangleBorder(radius=12)),
    ], expand=True, spacing=12, scroll=ScrollMode.AUTO)

    # ===== Combine as 2-pane
    left_w, right_w = map_ratio(ratio_dd.value)
    root_row = two_pane(left=left_panel, right=right_panel, left_expand=left_w, right_expand=right_w)
    def on_ratio_change(e):
        lw, rw = map_ratio(ratio_dd.value)
        root_row.controls[0].expand = lw
        root_row.controls[1].expand = rw
        page.update()
    ratio_dd.on_change = on_ratio_change

    # ===== Page body
    page.add(ft.Container(content=root_row, padding=padding.all(12), expand=True))

    # ===== Actions
    def on_start(_=None):
        stop_event.clear()
        # reset UI
        current_title.value, current_meta.value = "Chuẩn bị...", ""
        current_bar.value = 0
        overall_progress(0, 0)
        spinner.visible = True; start_btn.disabled = True; page.update()

        def work():
            try:
                if tabs.selected_index == 0:
                    if not scraper_channel.value.strip(): log("Thiếu kênh.", "[Lỗi]"); return
                    res = run_scraper(scraper_channel.value.strip(), scraper_out.value,
                                      log_func=log, progress_callback=overall_progress, stop_event=stop_event)
                elif tabs.selected_index == 1:
                    if not checker_file.value.strip(): log("Thiếu file.", "[Lỗi]"); return
                    res = run_checker(checker_file.value, log_func=log,
                                      progress_callback=overall_progress, stop_event=stop_event)
                else:
                    if not downloader_input.value.strip(): log("Thiếu đầu vào.", "[Lỗi]"); return
                    res = run_downloader(
                        downloader_input.value.strip(), out_folder=downloader_out.value,
                        quality=quality.value, audio_only=audio_only.value,
                        max_workers=int(threads.value), concurrent_frags=int(con_frags.value),
                        cookies_file=cookies_text.value or None, proxy=proxy_text.value or None,
                        progress_callback=overall_progress, detail_callback=detail_progress,
                        log_func=log, enable_aria2=use_aria2.value, use_archive=use_archive.value,
                        stop_event=stop_event
                    )
                if res: log(f"File kết quả: {res}", "[System]")
                if stop_event.is_set(): log("Đã huỷ theo yêu cầu.", "[System]")
                else: log("Hoàn thành!", "[System]")
            except Exception as e:
                log(str(e), "[Error]")
            finally:
                spinner.visible = False; start_btn.disabled = False; page.update()

        threading.Thread(target=work, daemon=True).start()

    start_btn.on_click = on_start

if __name__ == "__main__":
    multiprocessing.freeze_support()
    ft.app(target=main)
