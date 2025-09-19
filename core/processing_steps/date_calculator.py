# vcpmctool/core/processing_steps/date_calculator.py (Phiên bản cuối cùng)
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from ..datefmt import parse_date, to_ddmmyyyy


def calculate_extensions(
        start_date_str: str, initial_term: int, ext_term: int) -> dict:
    """
    Tính toán ngày bắt đầu, kết thúc và các lần gia hạn một cách chính xác.
    """
    # Khởi tạo dictionary kết quả
    dates = {
        "Ngày bắt đầu": "",
        "Thời hạn kết thúc": "",
        "Ngày xuất bản": start_date_str,
        "Gia hạn (lần 1)": "",
        "Gia hạn (lần 2)": "",
        "Gia hạn (lần 3)": "",
        "Gia hạn (lần 4)": "",
        "Gia hạn (lần 5)": "",
        "Error": ""}

    start_dt = parse_date(start_date_str)
    if not start_dt:
        dates["Error"] = f"Invalid date: {start_date_str}" if start_date_str else "Missing date"
        return dates

    dates["Ngày bắt đầu"] = to_ddmmyyyy(start_dt)

    # Tính thời hạn kết thúc ban đầu: start_date + N năm - 1 ngày
    end_dt = start_dt + relativedelta(years=initial_term) - timedelta(days=1)
    dates["Thời hạn kết thúc"] = to_ddmmyyyy(end_dt)

    # Ngày hiện tại để so sánh
    current_date = datetime.now()

    # Bắt đầu tính gia hạn từ ngày kết thúc của kỳ trước đó
    last_end_date = end_dt

    for i in range(1, 6):
        # Nếu ngày kết thúc của kỳ trước đã qua so với ngày hiện tại
        if last_end_date < current_date:
            # Ngày bắt đầu của kỳ gia hạn là ngày ngay sau ngày kết thúc trước
            # đó
            extension_start_date = last_end_date + timedelta(days=1)
            # Ngày kết thúc của kỳ gia hạn
            extension_end_date = extension_start_date + \
                relativedelta(years=ext_term) - timedelta(days=1)

            dates[f"Gia hạn (lần {i})"] = to_ddmmyyyy(extension_end_date)

            # Cập nhật ngày kết thúc cuối cùng để cho vòng lặp tiếp theo
            last_end_date = extension_end_date
        else:
            # Nếu chưa hết hạn thì không cần gia hạn nữa
            break

    return dates
