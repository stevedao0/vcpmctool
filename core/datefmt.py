# vcpmctool/core/datefmt.py (Đã sửa lỗi)
import pandas as pd
from datetime import datetime


def parse_date(date_str: str) -> datetime:
    """
    Phân tích chuỗi ngày tháng với nhiều định dạng.
    Trả về None nếu không thể phân tích cú pháp.
    """
    if not date_str or pd.isna(date_str) or str(date_str).strip() == '':
        return None

    # Các định dạng ngày phổ biến (bao gồm cả dấu chấm)
    formats = [
        "%d/%m/%Y",    # 01/01/2024
        "%Y-%m-%d",    # 2024-01-01
        "%d-%m-%Y",    # 01-01-2024
        "%d/%m/%y",    # 01/01/24
        "%d.%m.%Y",    # 01.01.2024
        "%d.%m.%y",    # 01.01.24
        "%Y/%m/%d",    # 2024/01/01
        "%m/%d/%Y",    # 01/01/2024 (US format)
        "%d %m %Y",    # 01 01 2024 (space separated)
        "%d-%m-%y",    # 01-01-24 (short year with dash)
    ]

    for fmt in formats:
        try:
            # For space-separated formats, use the full string
            if " " in fmt and " " in str(date_str):
                return datetime.strptime(str(date_str).strip(), fmt)
            else:
                # For other formats, remove time part if exists
                date_part = str(date_str).split(" ")[0]
                return datetime.strptime(date_part, fmt)
        except (ValueError, TypeError):
            continue  # Thử định dạng tiếp theo

    return None  # Trả về None nếu không có định dạng nào khớp


def to_ddmmyyyy(dt: datetime) -> str:
    """
    Chuyển đổi đối tượng datetime sang chuỗi "dd/mm/YYYY".
    """
    if dt and isinstance(dt, datetime):
        return dt.strftime("%d/%m/%Y")
    return ""
