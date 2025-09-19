# vcpmctool/services/file_utils.py
from pathlib import Path


def generate_output_name(input_path: str, suffix: str) -> str:
    base = Path(input_path).stem
    return f"{base}{suffix}"
