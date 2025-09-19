# vcpmctool/ui/components.py
import flet as ft
import os
import pandas as pd


class FileRow(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.files = []  # List to store selected file objects
        self._list_view = ft.ListView(height=150, spacing=10, controls=[])
        self.content = ft.Column([self._list_view])

    def update_files(self, files):
        self.files = files
        self._list_view.controls.clear()
        for f in self.files:
            if f.path:
                self._list_view.controls.append(
                    ft.Text(os.path.basename(f.path)))
        self.update()


class LogPanel(ft.UserControl):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.list_view = ft.ListView(height=200, spacing=5, auto_scroll=True)
        self.content = self.list_view

    def add_text(self, text: str):
        self.list_view.controls.append(ft.Text(text))
        self.update()


class ProgressBar(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.progress_bar = ft.ProgressBar(width=400, value=0)
        self.content = self.progress_bar

    def update_progress(self, value: float):
        self.progress_bar.value = value
        self.update()


class PreviewTable(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.data_table = ft.DataTable(columns=[], rows=[])
        self.content = ft.Column(
            [ft.Text("Preview:", weight=ft.FontWeight.BOLD), self.data_table],
            scroll=ft.ScrollMode.ALWAYS, expand=True
        )

    def update_table(self, df: pd.DataFrame):
        self.data_table.columns.clear()
        self.data_table.rows.clear()
        if df.empty:
            self.update()
            return

        preview_cols = [
            col for col in [
                "STT",
                "ID Video",
                "Tên tác phẩm",
                "Ngày bắt đầu",
                "Thời hạn kết thúc",
                "Share%"] if col in df.columns]

        for col in preview_cols:
            self.data_table.columns.append(ft.DataColumn(ft.Text(col)))

        for _, row in df.head(20).iterrows():  # Chỉ hiển thị 20 dòng đầu
            cells = []
            for col in preview_cols:
                cells.append(ft.DataCell(ft.Text(str(row.get(col, "")))))
            self.data_table.rows.append(ft.DataRow(cells=cells))
        self.update()


class LabeledSwitch(ft.UserControl):
    def __init__(self, label: str, value: bool):
        super().__init__()
        self.switch = ft.Switch(value=value)
        self.content = ft.Row([ft.Text(label), self.switch])

    def get_value(self):
        return self.switch.value
