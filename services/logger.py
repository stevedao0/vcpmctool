# vcpmctool/services/logger.py
import logging


class Logger:
    def __init__(self, log_file: str):
        self.logger = logging.getLogger("VCPMC")
        self.logger.setLevel(logging.INFO)
        # Ngăn logger thêm handler nhiều lần nếu được khởi tạo lại
        if not self.logger.handlers:
            handler = logging.FileHandler(log_file, encoding='utf-8')
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)

    def info(self, msg: str):
        self.logger.info(msg)
        try:
            print(msg)
        except UnicodeEncodeError:
            print(msg.encode('ascii', errors='replace').decode('ascii'))

    def warning(self, msg: str):
        self.logger.warning(msg)
        try:
            print(f"WARNING: {msg}")
        except UnicodeEncodeError:
            print(f"WARNING: {msg.encode('ascii', errors='replace').decode('ascii')}")

    def error(self, msg: str):
        self.logger.error(msg)
        try:
            print(f"ERROR: {msg}")
        except UnicodeEncodeError:
            print(f"ERROR: {msg.encode('ascii', errors='replace').decode('ascii')}")
