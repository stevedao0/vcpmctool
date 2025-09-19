# vcpmctool/core/processing_steps/column_mapper.py (Phiên bản cuối cùng)
import pandas as pd
from typing import Dict, List

# Danh sách các cột đầu ra theo đúng thứ tự mong muốn
OUTPUT_COLUMNS = [
    "STT",
    "ID Video",
    "Code",
    "Tên tác phẩm",
    "Tác giả",
    "Tên tác giả nhạc",
    "Tên tác giả lời",
    "Thời gian",
    "Thời lượng",
    "Ngày bắt đầu",
    "Thời hạn kết thúc",
    "Gia hạn (lần 1)",
    "Gia hạn (lần 2)",
    "Gia hạn (lần 3)",
    "Gia hạn (lần 4)",
    "Gia hạn (lần 5)",
    "Hình thức sử dụng",
    "Mức nhuận bút",
    "Mức nhuận bút gia hạn (lần 1)",
    "Mức nhuận bút gia hạn (lần 2)",
    "Mức nhuận bút gia hạn (lần 3)",
    "Mức nhuận bút gia hạn (lần 4)",
    "Mức nhuận bút gia hạn (lần 5)",
    "Error",
    "Share%",
    "TGShare",
    "Ghi chú",
    "Tình trạng",
    "Ngày xuất bản"]

# Ánh xạ từ cột đầu ra (key) sang các tên cột có thể có trong file đầu vào
# (value)
HEADER_MAPPING: Dict[str, List[str]] = {
    "STT": ["STT"],
    "ID Video": ["ID (Video)", "ID Video"],
    "Code": ["Code"],
    "Tên tác phẩm": ["Tên Tác Phẩm", "Tên tác phẩm"],
    "Tác giả": ["Tác Giả", "Tên Tác giả"],
    "Tên tác giả nhạc": ["Tác giả nhạc"],
    "Tên tác giả lời": ["Tác giả lời"],
    "Thời gian": ["Thời gian", "Vị trí bài hát trong link\n(Từ giờ:phút:giây đến giờ:phút:giây)"],
    "Hình thức sử dụng": ["Hình thức sử dụng", "Hình thức"],
    "Share%": ["Tỉ lệ % Share", "Share%"],
    "Ghi chú": ["Ghi Chú Độc Quyền", "NOTE", "Ghi chú"],
    "Tình trạng": ["Status", "Tình trạng"],
    "Ngày xuất bản": ["Ngày xuất bản", "Thời điểm xuất bản"]
}


def get_value_from_row(row: pd.Series, output_col_name: str) -> str:
    """
    Lấy giá trị từ một dòng (row) dựa trên các tên cột đầu vào có thể có.
    """
    possible_input_cols = HEADER_MAPPING.get(
        output_col_name, [output_col_name])
    for input_col in possible_input_cols:
        if input_col in row and pd.notna(row[input_col]):
            return str(row[input_col])
    return ""
