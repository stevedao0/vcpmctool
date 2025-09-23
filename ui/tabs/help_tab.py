# vcpmctool/ui/tabs/help_tab.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLabel, QPushButton, QGroupBox, QTabWidget
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QDesktopServices


class HelpTab(QWidget):
    """Tab hướng dẫn sử dụng"""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        
    def _setup_ui(self):
        """Thiết lập giao diện"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("❓ Hướng dẫn sử dụng VCPMC Tool")
        title.setStyleSheet("font-size: 24px; font-weight: 700; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Help content tabs
        help_tabs = QTabWidget()
        
        # Main processing help
        main_help = self._create_main_help()
        help_tabs.addTab(main_help, "🏠 Xử lý chính")
        
        # Royalty help
        royalty_help = self._create_royalty_help()
        help_tabs.addTab(royalty_help, "💰 Nhuận bút")
        
        # FAQ
        faq_help = self._create_faq_help()
        help_tabs.addTab(faq_help, "❓ FAQ")
        
        # Troubleshooting
        trouble_help = self._create_troubleshooting_help()
        help_tabs.addTab(trouble_help, "🔧 Khắc phục sự cố")
        
        layout.addWidget(help_tabs)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        contact_btn = QPushButton("📧 Liên hệ hỗ trợ")
        contact_btn.clicked.connect(self._open_contact)
        contact_btn.setProperty("class", "primary")
        button_layout.addWidget(contact_btn)
        
        button_layout.addStretch()
        
        manual_btn = QPushButton("📖 Tài liệu chi tiết")
        manual_btn.clicked.connect(self._open_manual)
        button_layout.addWidget(manual_btn)
        
        layout.addLayout(button_layout)
        
    def _create_main_help(self) -> QWidget:
        """Tạo hướng dẫn tab xử lý chính"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h2>🏠 Hướng dẫn sử dụng Tab Xử lý chính</h2>
        
        <h3>📋 Các bước thực hiện:</h3>
        <ol>
            <li><b>Chọn file Excel:</b>
                <ul>
                    <li>Nhấn nút "Chọn file Excel" hoặc Ctrl+O</li>
                    <li>Chọn một hoặc nhiều file .xlsx/.xls</li>
                    <li>File sẽ hiển thị trong danh sách</li>
                </ul>
            </li>
            
            <li><b>Cấu hình tùy chọn:</b>
                <ul>
                    <li><b>Thời hạn ban đầu:</b> Số năm bảo hộ ban đầu (mặc định: 2 năm)</li>
                    <li><b>Thời hạn gia hạn:</b> Số năm cho mỗi lần gia hạn (mặc định: 2 năm)</li>
                    <li><b>Proper Case:</b> Tự động viết hoa chữ cái đầu từ</li>
                </ul>
            </li>
            
            <li><b>Xử lý file:</b>
                <ul>
                    <li>Nhấn "Bắt đầu xử lý" hoặc F5</li>
                    <li>Theo dõi tiến trình trong thanh progress</li>
                    <li>Xem kết quả trong bảng preview</li>
                </ul>
            </li>
        </ol>
        
        <h3>📊 Dữ liệu đầu vào yêu cầu:</h3>
        <table border="1" cellpadding="5">
            <tr><th>Cột</th><th>Mô tả</th><th>Bắt buộc</th></tr>
            <tr><td>STT</td><td>Số thứ tự</td><td>✅</td></tr>
            <tr><td>ID Video</td><td>YouTube Video ID (11 ký tự)</td><td>✅</td></tr>
            <tr><td>Tên tác phẩm</td><td>Tên bài hát/tác phẩm</td><td>✅</td></tr>
            <tr><td>Tác giả</td><td>Tên tác giả</td><td>✅</td></tr>
            <tr><td>Thời gian</td><td>Khoảng thời gian (mm:ss - mm:ss)</td><td>✅</td></tr>
            <tr><td>Ngày xuất bản</td><td>Ngày phát hành</td><td>✅</td></tr>
            <tr><td>Hình thức sử dụng</td><td>Video, Audio, MV karaoke...</td><td>❌</td></tr>
        </table>
        
        <h3>📤 Kết quả đầu ra:</h3>
        <ul>
            <li>File Excel với hậu tố "_Ket_qua.xlsx"</li>
            <li>Các cột được tính toán tự động:
                <ul>
                    <li>Ngày bắt đầu, Thời hạn kết thúc</li>
                    <li>5 lần gia hạn (nếu cần)</li>
                    <li>Thời lượng được format chuẩn</li>
                    <li>Link YouTube có thể click</li>
                </ul>
            </li>
        </ul>
        """)
        
        layout.addWidget(help_text)
        return widget
        
    def _create_royalty_help(self) -> QWidget:
        """Tạo hướng dẫn tab nhuận bút"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h2>💰 Hướng dẫn sử dụng Tab Nhuận bút</h2>
        
        <h3>📋 Các bước thực hiện:</h3>
        <ol>
            <li><b>Chọn file Excel:</b>
                <ul>
                    <li>File phải chứa dữ liệu tác phẩm đã xử lý</li>
                    <li>Có các cột: Thời lượng, Hình thức sử dụng, Share%</li>
                </ul>
            </li>
            
            <li><b>Cấu hình mức nhuận bút:</b>
                <ul>
                    <li><b>Tỷ lệ mức nửa bài:</b> % của mức đầy đủ (mặc định: 50%)</li>
                    <li><b>Tỷ lệ mức gia hạn:</b> % của mức đầy đủ (mặc định: 40%)</li>
                    <li>Nhập mức nhuận bút đầy đủ cho từng loại hình</li>
                </ul>
            </li>
            
            <li><b>Xử lý tính toán:</b>
                <ul>
                    <li>Hệ thống tự động tính mức nửa bài và gia hạn</li>
                    <li>Áp dụng tỷ lệ Share% nếu có</li>
                    <li>Tạo link YouTube với timestamp</li>
                </ul>
            </li>
        </ol>
        
        <h3>🧮 Logic tính toán:</h3>
        <ul>
            <li><b>Mức nhuận bút:</b>
                <ul>
                    <li>Thời lượng ≥ 2 phút: Mức đầy đủ</li>
                    <li>Thời lượng < 2 phút: Mức nửa bài</li>
                </ul>
            </li>
            <li><b>Áp dụng Share%:</b>
                <ul>
                    <li>Nếu có Share%: Mức nhuận bút × Share%</li>
                    <li>Hỗ trợ định dạng: 50%, 0.5, 50</li>
                </ul>
            </li>
            <li><b>Mức gia hạn:</b>
                <ul>
                    <li>Chỉ tính khi có ngày gia hạn tương ứng</li>
                    <li>Bằng % của mức nhuận bút cơ bản</li>
                </ul>
            </li>
        </ul>
        
        <h3>🔗 Link YouTube với Timestamp:</h3>
        <ul>
            <li>Tự động tạo từ ID Video + Thời gian bắt đầu</li>
            <li>Format: https://youtube.com/watch?v=ID&t=XXXs</li>
            <li>Click để mở trực tiếp tại thời điểm chính xác</li>
        </ul>
        """)
        
        layout.addWidget(help_text)
        return widget
        
    def _create_aio_help(self) -> QWidget:
        """Tạo hướng dẫn AIO Tool"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h2>🚀 Hướng dẫn sử dụng AIO YouTube Tool</h2>
        
        <h3>📋 Tổng quan:</h3>
        <p>AIO Tool tích hợp 4 chức năng chính để làm việc với YouTube:</p>
        <ul>
            <li><b>🔍 Scraper:</b> Lấy danh sách video từ kênh YouTube</li>
            <li><b>✅ Checker:</b> Kiểm tra trạng thái video từ danh sách</li>
            <li><b>⬇️ Downloader:</b> Tải video với nhiều tùy chọn chất lượng</li>
            <li><b>📊 Enricher:</b> Lấy metadata chi tiết (tags, chapters, transcript)</li>
        </ul>
        
        <h3>🔍 Scraper - Lấy danh sách video:</h3>
        <ol>
            <li><b>Nhập kênh:</b>
                <ul>
                    <li>URL đầy đủ: https://www.youtube.com/channel/UC...</li>
                    <li>Channel ID: UC... (11 ký tự)</li>
                    <li>Handle: @channelname</li>
                    <li>Custom URL: /c/channelname</li>
                </ul>
            </li>
            <li><b>Cấu hình:</b>
                <ul>
                    <li>Giới hạn video: 10-1000 (mặc định 200)</li>
                    <li>Bao gồm Shorts: Lấy cả video ngắn</li>
                </ul>
            </li>
            <li><b>Kết quả:</b> File Excel với thông tin video cơ bản</li>
        </ol>
        
        <h3>✅ Checker - Kiểm tra trạng thái video:</h3>
        <ol>
            <li><b>File đầu vào:</b> Excel/CSV có cột "ID Video"</li>
            <li><b>Chức năng:</b>
                <ul>
                    <li>Kiểm tra video còn tồn tại không</li>
                    <li>Cập nhật thông tin mới nhất</li>
                    <li>Phát hiện video bị xóa/private</li>
                </ul>
            </li>
            <li><b>Hiệu năng:</b> 1-8 luồng đồng thời</li>
        </ol>
        
        <h3>⬇️ Downloader - Tải video:</h3>
        <ol>
            <li><b>Đầu vào:</b>
                <ul>
                    <li>Video ID/URL đơn lẻ</li>
                    <li>File Excel/CSV có danh sách</li>
                    <li>Playlist/Channel URL</li>
                </ul>
            </li>
            <li><b>Chất lượng:</b>
                <ul>
                    <li>bestvideo+bestaudio: Chất lượng cao nhất</li>
                    <li>720p/480p: Chất lượng cố định</li>
                    <li>Audio only: Chỉ tải âm thanh (MP3)</li>
                </ul>
            </li>
            <li><b>Tùy chọn nâng cao:</b>
                <ul>
                    <li>Cookies: Bypass giới hạn địa lý</li>
                    <li>Proxy: Sử dụng proxy server</li>
                    <li>aria2c: Tăng tốc tải xuống</li>
                    <li>Archive: Tránh tải trùng</li>
                </ul>
            </li>
        </ol>
        
        <h3>🔧 Mở AIO Tool đầy đủ:</h3>
        <p>Nhấn nút "Mở AIO Tool đầy đủ" để:</p>
        <ul>
            <li>Truy cập giao diện Flet hiện đại</li>
            <li>Sử dụng tính năng Enricher</li>
            <li>Cấu hình chi tiết hơn</li>
            <li>Xem progress real-time</li>
        </ul>
        
        <h3>⚠️ Lưu ý quan trọng:</h3>
        <ul>
            <li><b>yt-dlp:</b> Thư viện cập nhật thường xuyên, có thể cần update</li>
            <li><b>YouTube API:</b> Có thể thay đổi, gây lỗi tạm thời</li>
            <li><b>Cookies:</b> Cần thiết cho video có giới hạn</li>
            <li><b>Rate limiting:</b> Tránh spam request quá nhanh</li>
        </ul>
        
        <h3>🛠️ Khắc phục sự cố:</h3>
        <table border="1" cellpadding="5">
            <tr><th>Lỗi</th><th>Nguyên nhân</th><th>Giải pháp</th></tr>
            <tr><td>HTTP 403</td><td>Bị chặn IP</td><td>Sử dụng proxy/VPN</td></tr>
            <tr><td>Video unavailable</td><td>Bị xóa/private</td><td>Kiểm tra URL</td></tr>
            <tr><td>Format not available</td><td>Chất lượng không hỗ trợ</td><td>Chọn "best"</td></tr>
            <tr><td>Download slow</td><td>Kết nối chậm</td><td>Giảm concurrent fragments</td></tr>
        </table>
        """)
        
        layout.addWidget(help_text)
        return widget
        
    def _create_faq_help(self) -> QWidget:
        """Tạo FAQ"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h2>❓ Câu hỏi thường gặp (FAQ)</h2>
        
        <h3>🔍 Câu hỏi về xử lý file:</h3>
        
        <p><b>Q: File Excel của tôi không được xử lý, tại sao?</b><br>
        A: Kiểm tra:
        <ul>
            <li>File có đang mở trong Excel không? Đóng file trước khi xử lý</li>
            <li>Các cột bắt buộc có đầy đủ không?</li>
            <li>Định dạng ngày tháng có đúng không? (dd/mm/yyyy)</li>
            <li>ID Video có đúng 11 ký tự không?</li>
        </ul>
        </p>
        
        <p><b>Q: Thời gian không được format đúng?</b><br>
        A: Thời gian phải có định dạng:
        <ul>
            <li>mm:ss - mm:ss (ví dụ: 01:30 - 04:25)</li>
            <li>hh:mm:ss - hh:mm:ss (ví dụ: 00:01:30 - 00:04:25)</li>
            <li>Sử dụng dấu gạch ngang (-) để phân cách</li>
        </ul>
        </p>
        
        <p><b>Q: Ngày gia hạn không hiển thị?</b><br>
        A: Gia hạn chỉ hiển thị khi:
        <ul>
            <li>Thời hạn hiện tại đã hết (so với ngày hiện tại)</li>
            <li>Ngày xuất bản hợp lệ</li>
            <li>Thời hạn ban đầu và gia hạn > 0</li>
        </ul>
        </p>
        
        <h3>💰 Câu hỏi về nhuận bút:</h3>
        
        <p><b>Q: Mức nhuận bút không được tính?</b><br>
        A: Kiểm tra:
        <ul>
            <li>Đã nhập mức nhuận bút cho loại hình tương ứng chưa?</li>
            <li>Cột "Hình thức sử dụng" có khớp với loại hình đã cấu hình?</li>
            <li>Thời lượng có được tính đúng không?</li>
        </ul>
        </p>
        
        <p><b>Q: Share% không được áp dụng?</b><br>
        A: Share% hỗ trợ các định dạng:
        <ul>
            <li>50% (có ký hiệu phần trăm)</li>
            <li>0.5 (số thập phân)</li>
            <li>50 (số nguyên, sẽ hiểu là 50%)</li>
        </ul>
        </p>
        
        <h3>🔧 Câu hỏi kỹ thuật:</h3>
        
        <p><b>Q: Ứng dụng chạy chậm hoặc bị treo?</b><br>
        A: 
        <ul>
            <li>File Excel quá lớn (>1000 dòng) có thể chậm</li>
            <li>Đóng các ứng dụng khác để giải phóng RAM</li>
            <li>Khởi động lại ứng dụng</li>
        </ul>
        </p>
        
        <p><b>Q: Làm sao để cập nhật ứng dụng?</b><br>
        A: Liên hệ bộ phận IT để nhận phiên bản mới nhất.</p>
        """)
        
        layout.addWidget(help_text)
        return widget
        
    def _create_troubleshooting_help(self) -> QWidget:
        """Tạo hướng dẫn khắc phục sự cố"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h2>🔧 Khắc phục sự cố</h2>
        
        <h3>🚨 Lỗi thường gặp:</h3>
        
        <h4>❌ "Failed to read file - may be open"</h4>
        <p><b>Nguyên nhân:</b> File Excel đang được mở trong ứng dụng khác<br>
        <b>Giải pháp:</b>
        <ul>
            <li>Đóng file Excel trong Microsoft Excel</li>
            <li>Kiểm tra file có bị khóa bởi user khác không</li>
            <li>Copy file sang vị trí khác và thử lại</li>
        </ul>
        </p>
        
        <h4>❌ "Write failed - check if output file is open"</h4>
        <p><b>Nguyên nhân:</b> File kết quả đang được mở<br>
        <b>Giải pháp:</b>
        <ul>
            <li>Đóng file kết quả nếu đang mở</li>
            <li>Xóa file kết quả cũ và thử lại</li>
            <li>Chạy ứng dụng với quyền Administrator</li>
        </ul>
        </p>
        
        <h4>❌ "Invalid date format"</h4>
        <p><b>Nguyên nhân:</b> Định dạng ngày không đúng<br>
        <b>Giải pháp:</b>
        <ul>
            <li>Sử dụng định dạng dd/mm/yyyy (ví dụ: 01/01/2024)</li>
            <li>Kiểm tra không có ký tự đặc biệt</li>
            <li>Đảm bảo ngày/tháng/năm hợp lệ</li>
        </ul>
        </p>
        
        <h3>🔍 Cách kiểm tra lỗi:</h3>
        <ol>
            <li><b>Xem log chi tiết:</b>
                <ul>
                    <li>Mở file "vcpmctool.log" trong thư mục ứng dụng</li>
                    <li>Tìm dòng có từ khóa "ERROR" hoặc "WARNING"</li>
                </ul>
            </li>
            
            <li><b>Kiểm tra dữ liệu đầu vào:</b>
                <ul>
                    <li>Mở file Excel và kiểm tra từng cột</li>
                    <li>Đảm bảo không có ô trống ở các cột bắt buộc</li>
                    <li>Kiểm tra định dạng dữ liệu</li>
                </ul>
            </li>
            
            <li><b>Test với file nhỏ:</b>
                <ul>
                    <li>Tạo file Excel với 5-10 dòng dữ liệu mẫu</li>
                    <li>Nếu chạy được, vấn đề có thể ở dữ liệu cụ thể</li>
                </ul>
            </li>
        </ol>
        
        <h3>🆘 Khi cần hỗ trợ:</h3>
        <p>Nếu vẫn gặp vấn đề, vui lòng cung cấp:
        <ul>
            <li>File Excel gốc (hoặc file mẫu tương tự)</li>
            <li>Ảnh chụp màn hình lỗi</li>
            <li>File log (vcpmctool.log)</li>
            <li>Mô tả chi tiết các bước đã thực hiện</li>
        </ul>
        </p>
        
        <h3>💡 Mẹo sử dụng hiệu quả:</h3>
        <ul>
            <li>Luôn backup dữ liệu trước khi xử lý</li>
            <li>Xử lý từng file nhỏ thay vì file lớn</li>
            <li>Kiểm tra kết quả trước khi sử dụng</li>
            <li>Cập nhật ứng dụng thường xuyên</li>
            <li>Đọc log để hiểu rõ quá trình xử lý</li>
        </ul>
        """)
        
        layout.addWidget(help_text)
        return widget
        
    def _open_contact(self):
        """Mở liên hệ hỗ trợ"""
        # Có thể mở email client hoặc website
        QDesktopServices.openUrl(QUrl("mailto:support@vcpmc.vn?subject=VCPMC Tool Support"))
        
    def _open_manual(self):
        """Mở tài liệu chi tiết"""
        # Có thể mở file PDF hoặc website
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Tài liệu",
            "Tài liệu chi tiết sẽ được cung cấp riêng.\nVui lòng liên hệ bộ phận IT để nhận tài liệu."
        )