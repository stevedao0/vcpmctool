# vcpmctool/core/processing_steps/row_processor.py (Phiên bản cuối cùng)
import pandas as pd
from typing import Dict, Any, Tuple

from . import column_mapper, date_calculator, text_formatter
from ..duration import parse_duration


def process_single_row(
        row: pd.Series,
        prev_state: dict,
        options: dict
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    new_row: Dict[str, Any] = {col: "" for col in column_mapper.OUTPUT_COLUMNS}

    stt_str = str(row.get("STT", "")).strip()
    is_sub_row = "." in stt_str
    new_row["STT"] = stt_str

    if is_sub_row:
        # Kế thừa thông tin từ dòng chính
        new_row["ID Video"] = prev_state.get("id", "")
        pub_date_str = prev_state.get("pub_date", "")
        # Các trường khác để trống vì đây là dòng phụ
    else:
        # Lấy thông tin từ dòng hiện tại
        new_row["ID Video"] = column_mapper.get_value_from_row(row, "ID Video")
        pub_date_str = column_mapper.get_value_from_row(row, "Ngày xuất bản")

        # Cập nhật trạng thái cho dòng phụ tiếp theo
        prev_state["id"] = new_row["ID Video"]
        prev_state["pub_date"] = pub_date_str

    auto_proper = options.get("auto_proper", True)
    for col in ["Code", "Tên tác phẩm", "Tác giả",
                "Tên tác giả nhạc", "Tên tác giả lời", "Hình thức sử dụng"]:
        value = column_mapper.get_value_from_row(row, col)
        new_row[col] = text_formatter.proper_case(
            value) if auto_proper and value else value

    thoi_gian_input = column_mapper.get_value_from_row(row, "Thời gian")
    thoi_gian, thoi_luong, _ = parse_duration(thoi_gian_input)
    new_row["Thời gian"] = thoi_gian
    new_row["Thời lượng"] = thoi_luong

    date_results = date_calculator.calculate_extensions(
        pub_date_str,
        options.get("initial_term"),
        options.get("ext_term")
    )
    new_row.update(date_results)

    new_row["Ghi chú"] = text_formatter.combine_notes(row)
    new_row["Tình trạng"] = column_mapper.get_value_from_row(
        row, "Tình trạng") or "Available (Hoạt động)"

    # Các cột nhuận bút sẽ giữ nguyên giá trị rỗng đã khởi tạo

    return new_row, prev_state
