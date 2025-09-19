# vcpmctool/core/duration.py (Phiên bản cuối cùng, đã sửa lỗi định dạng)
from datetime import datetime


def _parse_and_format_time(time_str: str) -> str | None:
    """
    Hàm phụ để phân tích một chuỗi thời gian (ví dụ: "ss", "mm:ss" hoặc "hh:mm:ss")
    và luôn trả về định dạng "hh:mm:ss".
    """
    if not time_str:
        return None

    time_str = time_str.strip()

    # Thử các định dạng khác nhau
    time_formats = ['%H:%M:%S', '%M:%S']
    dt_object = None

    for fmt in time_formats:
        try:
            dt_object = datetime.strptime(time_str, fmt)
            break
        except ValueError:
            continue

    # Nếu không thành công, thử xử lý số đơn (giây)
    if not dt_object:
        try:
            # Kiểm tra nếu là số đơn (giây)
            seconds = int(time_str)
            if 0 <= seconds < 86400:  # Trong 1 ngày
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                secs = seconds % 60
                return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        except ValueError:
            pass

    if dt_object:
        return dt_object.strftime('%H:%M:%S')

    return None


def parse_duration(range_str: str) -> tuple[str, str, int]:
    """
    Phân tích cú pháp một chuỗi khoảng thời gian, định dạng lại nó,
    và tính toán thời lượng.
    - range_str: Chuỗi đầu vào như "00:00 - 04:56".
    - Trả về: (thoi_gian_formatted, thoi_luong, duration_seconds)
    """
    if not range_str or '-' not in range_str:
        return range_str, "", 0

    try:
        start_str, end_str = [s.strip() for s in range_str.split('-')]

        # Phân tích cú pháp và định dạng lại cả hai phần
        start_formatted = _parse_and_format_time(start_str)
        end_formatted = _parse_and_format_time(end_str)

        if start_formatted is None or end_formatted is None:
            return range_str, "", 0  # Trả về gốc nếu định dạng sai

        # Ghép lại chuỗi thời gian đã được định dạng chuẩn
        thoi_gian_formatted = f"{start_formatted} - {end_formatted}"

        # Chuyển đổi sang đối tượng datetime để tính toán
        start_dt = datetime.strptime(start_formatted, '%H:%M:%S')
        end_dt = datetime.strptime(end_formatted, '%H:%M:%S')

        duration_delta = end_dt - start_dt
        duration_seconds = int(duration_delta.total_seconds())

        if duration_seconds < 0:
            # Xử lý trường hợp qua ngày (ví dụ: 23:00 - 01:00)
            duration_seconds += 86400

        # Định dạng chuỗi thời lượng
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        thoi_luong = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

        return thoi_gian_formatted, thoi_luong, duration_seconds

    except Exception:
        return range_str, "", 0
