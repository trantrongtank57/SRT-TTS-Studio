# Changelog — SRT TTS Studio

Tất cả thay đổi đáng chú ý của phần mềm được ghi lại trong tệp này.
Định dạng dựa trên [Keep a Changelog](https://keepachangelog.com/vi/1.0.0/).

## [1.0.0] — 2026-06-23

Bản phát hành đầu tiên. Phần mềm chuyển phụ đề SRT / PDF / Word / TXT thành giọng đọc (TTS),
kèm bộ công cụ xử lý video, dịch thuật và nhân bản giọng nói cho tiếng Việt.

### TTS & Nhà cung cấp giọng đọc
- Edge TTS (Microsoft) — có **đọc song song 4 luồng** cho tốc độ cao.
- Các nhà cung cấp tiếng Việt: FPT.AI, Vbee, Zalo AI, EverAI, MiniMax.
- Danh sách giọng Edge **cập nhật động** (`edge_tts.list_voices`), pin giọng `vi-*` lên đầu, ô tìm kiếm giọng (🔎).
- Tùy chỉnh **tốc độ / cao độ** giọng Edge (rate/pitch).
- **Hồ sơ giọng** (lưu/áp nhanh toàn bộ cấu hình giọng), giọng dùng gần đây (MRU).

### Nhân bản giọng nói (Voice Clone)
- **RVC** — chuyển đổi giọng (rvc_env, Python 3.10).
- **VoxCPM** — TTS nhân bản giọng.
- **VieNeu-TTS** (v3 Turbo, 48 kHz) — tự tải model từ HF, hỗ trợ giọng preset + cảm xúc, chạy GPU/CPU (ONNX).
- **F5-TTS-Vietnamese** — nhân bản giọng thuần (ViVoice checkpoint).
- **OmniVoice Vietnamese** — nhân bản giọng, tự tải model từ HF.
- Sáu đường giọng **loại trừ lẫn nhau**, có tiền kiểm (pre-flight) trước khi chạy.
- Lọc/xử lý audio mẫu (tách nhạc, khử nhiễu) và STT điền sẵn câu tham chiếu.

### Lồng tiếng & Timeline
- **Merge timeline chống chồng giọng** — co giãn (atempo) từng dòng cho vừa khe phụ đề, tùy chọn căn giữa khe lặng.
- **Chuẩn hóa âm lượng** (loudnorm -16 LUFS) và **cân âm lượng từng dòng**.
- Xuất nhiều định dạng: mp3 / wav / m4a / opus; sinh **SRT đồng bộ** theo audio thật.
- **Ghép Audio → Video (Mux)** — giữ audio gốc + ducking tự động, gắn phụ đề cứng (mã hóa GPU NVENC).
- **Trợ lý lồng tiếng tự động** — STT → dịch → TTS → merge → mux trong một luồng; hỗ trợ hàng đợi nhiều video và **dán link YouTube**.

### Dịch thuật sang tiếng Việt
- Dịch SRT / PDF / Word (.docx) / TXT qua **Claude / Gemini / OpenAI / Offline (NLLB / envit5)**.
- Chế độ **song ngữ**, ô **ngữ cảnh** giữ xưng hô nhất quán, **dịch xong đọc luôn**.
- Tạm dừng / Tiếp tục / Dừng (cả online lẫn subprocess offline), lưu kết quả một phần khi dừng.
- Tự động phát hiện ngôn ngữ nguồn (langdetect + heuristic).

### Công cụ Video
- **Tách Sub Cứng (Video OCR)** — chạy VideOCR CLI, có tạm dừng/tiếp tục/dừng theo cây tiến trình.
- **Speech-to-Text** (faster-whisper) — chế độ tách câu / karaoke, xuất srt/txt/docx/pdf.
- **Nén video**, **ghép audio→video**, **sửa video**, **căn chỉnh thời gian SRT** (VAD).

### Tải truyện (Webtoon)
- Tải comic theo **bộ adapter site** (truyenqq, hentaivnx) + fallback generic.
- Backend **gallery-dl** cho truyện nước ngoài (MangaDex, mangakakalot, webtoons…), vượt Cloudflare qua cookie trình duyệt.
- Đường riêng cho **webtoonscan.com** (đọc cookie Firefox + UA giả lập).
- Xuất Ảnh / PDF / CBZ (mỗi chương hoặc cả bộ), tự thử lại chương lỗi, chống ảnh hỏng.
- **Chuyển định dạng** Ảnh ↔ CBZ ↔ PDF.
- **Dịch truyện → Tiếng Việt** — OCR (EasyOCR) → dịch → ghi chữ Việt đè lên ảnh.

### Kiểm soát chất lượng (QC)
- Tự QC mỗi file MP3 (phát hiện **novoice / toolong / tooshort**) + vòng thử lại.
- **Bảng QC**: quét file lỗi, tạo lại dòng lỗi, tạo lại dòng thiếu, nghe thử dòng lỗi.
- Làm sạch ký tự OCR/bẩn, bỏ qua dòng không đọc được, cắt lặng đầu/cuối.
- **Từ điển phát âm** (glossary) + **đọc số/tiền/ngày/giờ kiểu Việt**.
- **Cache dòng trùng** (RAM + đĩa, dùng lại giữa các tập/lần chạy).

### Quy trình & Giao diện
- Bố cục **sidebar + trang công việc**, **Bảng điều khiển (Dashboard)** tổng quan, làm mới/chẩn đoán.
- **Phân vai đa giọng** (casting) + **tự phân vai bằng AI**.
- **Hàng đợi**, **theo dõi thư mục** (watch folder) tự xử lý file mới.
- **Khôi phục phiên** làm việc, **A/B so giọng**, **nghe thử 3 dòng đầu**, **Quick TTS** + gõ Telex.
- **Khám SRT** (lint) + **sửa SRT tự động** + **dời thời gian SRT**.
- **Edit Studio** xem/kiểm video kèm audio.
- Thông báo Windows toast khi xong, hiệu ứng pháo hoa + âm thanh.

### Bảo vệ mã & Bảo mật
- Biên dịch **Cython** thành `.pyd` (mã máy native, không decompile được).
- Kiểm tra **toàn vẹn** (SHA-256) khi khởi động, fail-closed.
- **DRM phần cứng** (ràng theo CPU + serial ổ C), mật khẩu PBKDF2 200k vòng, khóa brute-force.
- Bản **Trial 24h** chặn máy ảo (6 lớp phát hiện VM).
- Đóng gói **.msi** (WiX) + 3 bản **.exe portable** (Portable / Secured / Trial).

### Cấu hình & Triển khai
- Tự dò thư mục cấu hình ghi được (exe dir → %LOCALAPPDATA% khi cài MSI).
- **Tự dò model/env đặt cạnh exe**, ghi đè qua ⚙ Cài đặt.
- **Xuất/Nhập gói cấu hình**, **lưu UI prefs** giữa các phiên.
- Ghi **log theo ngày**, chẩn đoán môi trường khi khởi động.
