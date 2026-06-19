# CHECKLIST KIỂM THỬ — các tính năng thêm mới (11 đợt)

> Chạy `python apppp_integrated.py` (dev) hoặc exe sau khi build.
> Mỗi mục ~30 giây – 2 phút. Đánh ✅/❌ vào cuối dòng.

## A. Khởi động & thiết lập
- [ ] App mở bình thường, đăng nhập OK, không có dòng ❌ lạ trong logbox lúc khởi động
- [ ] Trang Hệ thống → nút **🔍 Kiểm tra môi trường** chạy lại diagnostics trong logbox
- [ ] Trang Hệ thống → nút **📄 Mở log hôm nay** mở được file log (thư mục `logs/` cạnh settings.json)
- [ ] Chỉnh **Tốc độ Edge** thành `+25%`, tick/untick vài checkbox → thoát app → mở lại → các thiết lập **được giữ nguyên** (file `ui_prefs.json` xuất hiện)

## B. Giọng & tiền xử lý text
- [ ] Tab Giọng nói: hàng "Edge — Tốc độ / Cao độ" hiển thị đủ, không tràn khung
- [ ] **📖 Từ điển phát âm**: thêm `ChatGPT = chát gi pi ti` → Lưu → Quick TTS gõ "Tôi dùng ChatGPT" → Nghe thử → đọc đúng "chát gi pi ti"
- [ ] Load một SRT → mở Từ điển → **🔍 Gợi ý từ** → thấy danh sách `từ =    # xuất hiện N lần`
- [ ] Quick TTS: "giá 1.500.000đ, hẹn 19h30 ngày 20/11/2024" → Nghe thử → đọc thành chữ tiếng Việt (checkbox "Đọc số..." đang bật)
- [ ] Chọn vài voice Edge khác nhau → mở lại dropdown → các voice vừa dùng **ghim đầu danh sách**
- [ ] Lưu 2 Hồ sơ giọng Edge khác nhau → **🔬 So giọng** → tick 2 hồ sơ → nghe lần lượt, xong giọng hiện tại được khôi phục
- [ ] Gõ telex `xin chaof` vào ô "Nội dung mẫu" của panel VieNeu/F5 → ra "xin chào"

## C. Luồng SRT chính
- [ ] Load SRT ~20-30 dòng → dòng `🩺 Khám SRT: N lỗi, M cảnh báo` hiện (nếu file có vấn đề) → bấm **🩺 Khám SRT** xem chi tiết
- [ ] **🔧 Sửa SRT (tự động)** với file có lỗi → ra `_fixed.srt` + tự nạp lại
- [ ] **🎧 Thử 3 dòng đầu** (chọn Output trước) → nghe 3 dòng đúng giọng đang cấu hình
- [ ] Chạy **TTS** với Edge: log có `⚡ Edge TTS song song ×4`, các dòng `OK` ra không theo thứ tự — bình thường
- [ ] SRT có dòng lặp (2 dòng giống hệt nhau) → dòng sau hiện `♻ OK n (dòng trùng — dùng lại audio)`
- [ ] Bấm **Stop** giữa chừng → dừng êm; bấm TTS lại → `SKIP` các dòng đã có
- [ ] Xong batch: nếu có FAIL → **📋 Báo cáo QC** liệt kê; **🎧 Nghe dòng lỗi** mở dialog ▶/🔁; **🧩 Tạo lại dòng thiếu** chạy được
- [ ] Sửa text 1 dòng (Regenerate Line) → file cũ thành `line_NNNN.old.mp3`
- [ ] **Merge FFmpeg** → ra `final.mp3` + `final_synced.srt`; bật "Cân âm lượng các dòng" merge lại → log `🔉 Đã cân âm lượng N dòng`
- [ ] Bật "Chuẩn hóa âm lượng (-16 LUFS)" → merge → final nghe đều
- [ ] Thu nhỏ app lúc batch sắp xong → **toast Windows** hiện khi xong

## D. Wizard lồng tiếng (test với video ngắn 1-2 phút)
- [ ] **🎬 Lồng tiếng tự động** → dialog có dropdown Hồ sơ giọng + 4 checkbox
- [ ] Chạy full chuỗi → 5 bước chạy lần lượt, ra `<video>_dubbed.mp4` + khối 📊 tổng kết
- [ ] Bật "Gắn phụ đề cứng" → video ra có sub burn-in, chữ khớp tiếng (dùng final_synced.srt)
- [ ] ETA hiện trên thanh tiến trình dạng `45% · còn ~2p30s`
- [ ] **📺 YouTube → Lồng tiếng**: dán 1 link vào ô YouTube → Bắt đầu → tải về (thanh % chạy) → chạy 5 bước → tự mở video `_dubbed.mp4` bằng trình phát mặc định
- [ ] Dán **nhiều link** (mỗi dòng 1 link) → tải + dub tuần tự từng video, mỗi cái xong tự mở
- [ ] Chưa cài yt-dlp → log báo `❌ Chưa cài yt-dlp ... pip install -U yt-dlp` (không treo)
- [ ] Tắt "Mở xem ngay khi xong" → xong không tự mở; đổi thư mục Tải về → đóng/mở app vẫn nhớ

## E. Tiện ích & dịch
- [ ] Trang Tools → **⏱ Dời thời gian SRT** → +500ms → ra `_shifted.srt` đúng
- [ ] Dịch SRT có tên riêng nằm trong glossary → bản dịch **giữ nguyên tên** nhất quán
- [ ] Phiên làm việc: chạy dở → thoát → mở lại → hint phiên cũ có dòng `• Giọng:` → Khôi phục → giọng được áp lại đúng

## E2. Đợt bổ sung (minh bạch + Windows + karaoke)
- [ ] Chạy batch Edge → đầu batch có dòng 🧾 khối lượng; cuối batch có dòng 📊 thống kê; chạy lần 2 thấy dòng ⏳ ước tính
- [ ] Thu nhỏ app khi đang chạy → icon taskbar có thanh tiến độ xanh
- [ ] Trang Hệ thống → 🔄 Cập nhật giọng Edge (cần mạng) → báo tổng số giọng; 🔎 cạnh dropdown Voice lọc được
- [ ] 📦 Xuất gói cấu hình → 📥 Nhập lại → báo .bak; 📂 mở đúng thư mục
- [ ] Video→Text với "Tách: Cụm ngắn (karaoke)" trên video ngắn → SRT ra dòng 2-4 từ bám nhịp nói
- [ ] Dialog Từ điển: đặt con trỏ vào dòng có cách đọc → 🔊 Nghe dòng này
- [ ] Mở wizard, đổi model/checkbox → đóng app mở lại → wizard giữ nguyên lựa chọn
- [ ] Wizard → Browse chọn 2 video ngắn (Ctrl+click) → entry hiện "(2 video)..." → chạy → dub tuần tự cả 2, cuối có tổng kết ✅/❌ từng video
- [ ] Tools → Watch folder: chọn thư mục, Bật theo dõi → copy 1 file .srt vào → ~8s sau tự chạy TTS + merge; copy video vào → tự chạy wizard; file đã xử lý không chạy lại khi bật lại

## G. Bảng điều khiển (dashboard — trang mặc định khi mở app)
- [ ] App mở thẳng vào **📊 Bảng điều khiển**; thẻ **Trạng thái phiên** hiện mode/giọng/GPU/thư mục cấu hình đúng
- [ ] Load 1 SRT → thẻ Trạng thái phiên cập nhật **Số dòng** + **Đã tạo (file audio) = N / M**; thẻ **Sẵn sàng chạy?** hiện tóm tắt Khám SRT
- [ ] Thẻ **Lối tắt nhanh**: bấm mỗi nút → nhảy đúng trang tương ứng; **📂 Mở Output** mở đúng thư mục
- [ ] Đang chạy TTS → thẻ **Tiến trình job** hiện %/ETA + nút ⏸/▶/⏹ bật; thẻ **Thời gian chạy** đếm elapsed; xong job → 2 thẻ này về trạng thái nghỉ
- [ ] Thẻ **Bật/tắt nhanh**: gạt 1 switch (vd "Cắt lặng") → sang trang Giọng thấy checkbox tương ứng **đổi theo** (dùng chung biến)
- [ ] Thẻ **Đổi giọng nhanh**: chọn 1 Hồ sơ giọng → áp dụng ngay (log `✅ Đã áp dụng hồ sơ`), dropdown trang Giọng đồng bộ
- [ ] Thẻ **Nghe thử nhanh**: gõ text → 🎧 Nghe thử phát đúng giọng; ⏹ Dừng dừng được
- [ ] **🔧 Chẩn đoán nâng cao** (cuối trang): bấm → bung 4 thẻ (môi trường/tốc độ/model runtime/log) + tự cuộn tới; bấm lại → thu gọn
- [ ] Khu chẩn đoán: **Sức khỏe môi trường** + **Model tải lúc chạy** hiện ✅/❌ khớp với dòng "KIỂM TRA HỆ THỐNG" lúc khởi động
- [ ] Thẻ **Chất lượng audio (QC)** hiện số file lỗi/dòng thiếu; **Chi phí ước tính** hiện số ký tự (Edge = miễn phí)
- [ ] Mở trang khác rồi quay lại Bảng điều khiển → không bị treo/đơ; thẻ vẫn tự cập nhật mỗi 2s (mở app lâu không phình RAM/CPU)

## H. Tải truyện Webtoon (sidebar 📚 Tải truyện)
- [ ] Sidebar có mục **📚 Tải truyện (Webtoon)** trong nhóm TIỆN ÍCH; bấm mở đúng trang
- [ ] Dán URL 1 chương `https://truyenqq.com.vn/cuoc-song-thuong-ngay/chapter-1` → ⬇ Tải truyện → tải đủ ảnh vào `Lưu vào`/<tên truyện>/<chương>/, log `✔ N/N trang` + pháo hoa, mở thư mục
- [ ] Dán URL cả bộ + ô **Chương** = `1-2`, định dạng **Ảnh (thư mục)** → tải đúng 2 chương (có dò bù chương đầu nếu thiếu)
- [ ] Định dạng **1 PDF cả bộ** với `1-2` → ra 1 file `<tên>.pdf` mở xem được; **1 CBZ cả bộ** → ra 1 file `<tên>.cbz`
- [ ] Đang tải bấm **⏹ Dừng** → dừng trong vài giây, nút Tải bật lại, thanh tiến trình reset
- [ ] URL sai/để trống → log ❌ hướng dẫn, không treo
- [ ] **🌐 Truyện nước ngoài (gallery-dl)**: tick checkbox + URL 1 chương MangaDex/mangakakalot (đã `pip install gallery-dl`) → tải ảnh, gộp được PDF/CBZ; bấm ⏹ Dừng → tiến trình gallery-dl bị kill
- [ ] Tick gallery-dl nhưng CHƯA cài → log ❌ `pip install -U gallery-dl`, không treo, không ảnh hưởng nút khác
- [ ] Trang nước ngoài chặn Cloudflare: chọn **Cookie = trình duyệt đã mở trang đó** (đóng trình duyệt trước) → tải được; log hiện `(cookies: <browser>)`

## F. Sau build (exe)
- [ ] `output\Portable\SRT_TTS_Studio_Portable.exe` mở được, đăng nhập OK
- [ ] Lặp lại nhanh mục B+C trên exe (ít nhất: glossary + TTS song song + merge)
- [ ] Bảng điều khiển trên exe: mục G chạy đúng (đặc biệt **Sẵn sàng chạy?** + **Chẩn đoán nâng cao**)
