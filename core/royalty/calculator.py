# vcpmctool/core/royalty/calculator.py
"""
Module tính toán nhuận bút dựa trên logic từ excel_module.py
Đã tối ưu để tránh conflict và sử dụng openpyxl
"""
import pandas as pd
from datetime import datetime
from typing import Dict, Tuple


class RoyaltyCalculator:
    """Lớp tính toán nhuận bút cho các loại hình sử dụng"""

    def __init__(self, royalty_dict: Dict[str, Tuple[int, int, int]]):
        """
        Khởi tạo với dictionary mức nhuận bút
        royalty_dict: {usage_type: (full_fee, half_fee, renew_fee)}
        """
        self.royalty_dict = {k.lower(): v for k, v in royalty_dict.items()}

    def parse_duration_to_seconds(self, duration_str: str) -> int:
        """Chuyển đổi chuỗi thời lượng thành giây"""
        if not duration_str or pd.isna(duration_str):
            return 0

        duration_str = str(duration_str).strip()

        # Xử lý định dạng HH:MM:SS
        if duration_str.count(':') == 2:
            try:
                parts = duration_str.split(':')
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = int(parts[2])
                return hours * 3600 + minutes * 60 + seconds
            except BaseException:
                pass

        # Xử lý định dạng MM:SS
        if duration_str.count(':') == 1:
            try:
                parts = duration_str.split(':')
                minutes = int(parts[0])
                seconds = int(parts[1])
                return minutes * 60 + seconds
            except BaseException:
                pass

        return 0

    def calculate_base_fee(self, usage_type: str, duration: str,
                           share_percent: str) -> Tuple[int, str]:
        """
        Tính mức nhuận bút cơ bản
        Returns: (fee, error_message)
        """
        usage_key = str(usage_type).strip().lower()

        # Kiểm tra loại hình có trong dictionary không
        if usage_key not in self.royalty_dict:
            return 0, f"Loại hình '{usage_type}' không có trong bảng mức nhuận bút"

        init_fee, half_fee, renew_fee = self.royalty_dict[usage_key]

        # Tính toán dựa trên thời lượng
        total_seconds = self.parse_duration_to_seconds(duration)

        if total_seconds < 120:  # Dưới 2 phút
            base_fee = half_fee
        else:
            base_fee = init_fee

        # Xử lý tỷ lệ share nếu có
        if share_percent and pd.notna(share_percent):
            share_str = str(share_percent).strip()

            # Xử lý dạng có ký hiệu %
            if "%" in share_str:
                try:
                    pct = float(share_str.replace("%", "")) / 100.0
                    base_fee = int(round(base_fee * pct))
                except Exception as e:
                    return base_fee, f"Lỗi chuyển đổi share%: {e}"
            else:
                # Xử lý dạng số thập phân
                try:
                    pct_float = float(share_str)
                    if 0 < pct_float < 1:
                        base_fee = int(round(base_fee * pct_float))
                except BaseException:
                    pass  # Giữ nguyên base_fee nếu không parse được

        return base_fee, ""

    def calculate_renewal_fees(
            self, base_fee: int, renewal_rate: float = 0.4) -> Dict[str, int]:
        """
        Tính mức nhuận bút gia hạn cho 5 lần
        renewal_rate: tỷ lệ % của mức cơ bản (mặc định 40%)
        """
        renewal_fee = int(round(base_fee * renewal_rate))

        return {
            "Mức nhuận bút gia hạn (lần 1)": renewal_fee,
            "Mức nhuận bút gia hạn (lần 2)": renewal_fee,
            "Mức nhuận bút gia hạn (lần 3)": renewal_fee,
            "Mức nhuận bút gia hạn (lần 4)": renewal_fee,
            "Mức nhuận bút gia hạn (lần 5)": renewal_fee
        }

    def parse_time_range(self, time_str: str) -> Tuple[str, str]:
        """
        Parse và chuẩn hóa chuỗi thời gian
        Returns: (formatted_time, duration)
        """
        if not time_str or pd.isna(time_str):
            return "", ""

        time_str = str(time_str).strip()
        # Chuẩn hóa các ký tự dash
        time_str = time_str.replace("–", "-").replace("—", "-")

        if "-" not in time_str:
            # Thời gian đơn
            return self._format_single_time(time_str), ""

        # Thời gian khoảng
        parts = time_str.split("-")
        if len(parts) != 2:
            return time_str, ""

        start = self._format_single_time(parts[0].strip())
        end = self._format_single_time(parts[1].strip())

        if start and end and "error" not in start and "error" not in end:
            formatted = f"{start} - {end}"
            duration = self._calculate_duration(start, end)
            return formatted, duration

        return time_str, ""

    def _format_single_time(self, time_str: str) -> str:
        """Chuẩn hóa thời gian đơn về định dạng HH:MM:SS"""
        if not time_str:
            return ""

        time_str = time_str.strip()

        # Đã là HH:MM:SS
        if time_str.count(':') == 2:
            try:
                # Validate and reformat to ensure proper zero padding
                parts = time_str.split(':')
                if len(parts) == 3:
                    h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
                    if 0 <= h < 24 and 0 <= m < 60 and 0 <= s < 60:
                        return f"{h:02d}:{m:02d}:{s:02d}"
            except (ValueError, IndexError):
                return "error"

        # MM:SS -> 00:MM:SS
        elif time_str.count(':') == 1:
            try:
                parts = time_str.split(':')
                if len(parts) == 2:
                    m, s = int(parts[0]), int(parts[1])
                    if 0 <= m < 60 and 0 <= s < 60:
                        return f"00:{m:02d}:{s:02d}"
            except (ValueError, IndexError):
                return "error"

        # Số đơn (giây) -> 00:00:SS
        else:
            try:
                seconds = int(time_str)
                if 0 <= seconds < 86400:  # Trong 1 ngày
                    hours = seconds // 3600
                    minutes = (seconds % 3600) // 60
                    secs = seconds % 60
                    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
            except ValueError:
                pass

        return "error"

    def _calculate_duration(self, start_str: str, end_str: str) -> str:
        """Tính thời lượng từ khoảng thời gian"""
        try:
            start_dt = datetime.strptime(start_str, "%H:%M:%S")
            end_dt = datetime.strptime(end_str, "%H:%M:%S")

            delta = end_dt - start_dt
            seconds = int(delta.total_seconds())

            if seconds < 0:
                # Handle cross-midnight case (e.g., 23:30 - 01:15)
                seconds += 86400

            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60

            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        except BaseException:
            return ""
