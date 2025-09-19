# vcpmctool/core/processing_steps/text_formatter.py
import pandas as pd


def proper_case(text: str, small_words: list = [
                "của", "và", "trong", "cho", "với"]) -> str:
    """
    Chuyển đổi chuỗi sang dạng Proper Case, giữ các từ nhỏ ở dạng chữ thường.
    """
    if not text or pd.isna(text):
        return ""
    words = str(text).split()
    capitalized = []
    for i, word in enumerate(words):
        if word.lower() in small_words and i > 0 and i < len(words) - 1:
            capitalized.append(word.lower())
        else:
            capitalized.append(word.capitalize())
    return " ".join(capitalized)


def combine_notes(row: pd.Series) -> str:
    """
    Kết hợp các cột ghi chú và làm sạch chuỗi 'nan'.
    """
    ghi_chu = str(row.get("Ghi Chú Độc Quyền", "")).strip()
    note = str(row.get("NOTE", "")).strip()

    ghi_chu_clean = ghi_chu.replace("nan", "").strip()
    note_clean = note.replace("nan", "").strip()

    if ghi_chu_clean and note_clean:
        return f"{ghi_chu_clean} {note_clean}"
    return ghi_chu_clean or note_clean
