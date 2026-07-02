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
- [ ] **Cache bền qua phiên**: chạy TTS 1 SRT xong → thoát app → mở lại → xóa Output → chạy lại CÙNG SRT/giọng → các dòng hiện `♻` (dùng lại từ `tts_cache/` cạnh settings.json) thay vì gọi API
- [ ] **🤖 Tự phân vai (AI)**: tạo ≥2 hồ sơ giọng (tên gợi ý vd `nam_tre`/`nu_gia`) + nhập API key dịch → Load SRT hội thoại → **🎭 Phân vai** → **🤖 Tự phân vai (AI)** → chờ phân tích → bảng phân vai mở lại với các luật tự gán → **🎬 Lưu & Chạy** đọc đúng nhiều giọng
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
- [ ] Trang Dịch → "Sang:" chọn English → dịch 1 SRT ngắn (Claude/Gemini) → bản dịch ra tiếng Anh + log nhắc chọn giọng cùng ngôn ngữ; chọn lại Tiếng Việt → hành vi như cũ; provider Offline + Sang≠Việt → log thông báo bỏ qua
- [ ] Trang Video → 🖼 Audio → Video: chọn final.mp3 + 1 ảnh + final_synced.srt → 🎬 Tạo Video → ra `<audio>_video.mp4` 720p có chữ khớp tiếng; thử không ảnh → nền màu tối
- [ ] Trang Đọc tài liệu → Load file .epub → chia đoạn đúng thứ tự chương → Đọc TTS như docx/txt

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
- [ ] **hentaivnx** (adapter riêng): URL 1 chương `https://www.hentaivnx.com/truyen-hentai/<slug>/chapter-N/<id>` → tải đủ ảnh, thư mục đặt tên `chapter-N` (không phải ID số); URL cả bộ `.../<slug>-<id>` → lấy đủ danh sách chương, lọc `1-2` đúng (ảnh từ `*.2tcdn.cfd`, bỏ logo/banner)
- [ ] **🌐 Truyện nước ngoài (gallery-dl)**: tick checkbox + URL 1 chương MangaDex/mangakakalot (đã `pip install gallery-dl`) → tải ảnh, gộp được PDF/CBZ; bấm ⏹ Dừng → tiến trình gallery-dl bị kill
- [ ] Tick gallery-dl nhưng CHƯA cài → log ❌ `pip install -U gallery-dl`, không treo, không ảnh hưởng nút khác
- [ ] Trang nước ngoài chặn Cloudflare: chọn **Cookie = trình duyệt đã mở trang đó** (đóng trình duyệt trước) → tải được; log hiện `(cookies: <browser>)`

## H2. Dịch truyện nước ngoài → Tiếng Việt (card "Dịch truyện → Tiếng Việt")
- [ ] Cài trước: `voxcpm_env\Scripts\python.exe -m pip install easyocr`; chọn engine dịch ở trang Dịch (Claude/Gemini/OpenAI có key, hoặc Offline có model)
- [ ] Chọn **Nguồn** = thư mục ảnh 1 chương (vài trang tiếng Anh) → tiếng gốc `Tiếng Anh` → 🌐 Dịch → ra ảnh đã ghi chữ Việt trong `<nguồn>\_vi\<chương>\`, có `_script_dich.txt`, pháo hoa + mở thư mục
- [ ] Nguồn = thư mục chứa NHIỀU thư mục chương → mỗi chương ra 1 thư mục `_vi\<tên chương>\`
- [ ] Đóng gói `PDF mỗi chương` / `CBZ mỗi chương` → tạo đúng file
- [ ] Bấm ⏹ Dừng giữa lúc OCR/dịch → dừng được (kill tiến trình OCR), không treo, không pháo hoa
- [ ] CHƯA cài easyocr → log ❌ `pip install easyocr`, không treo, các nút khác vẫn chạy
- [ ] Provider online thiếu API key → báo lỗi sớm trước khi chạy OCR

## I. Đợt 2026-07-02: Rút gọn AI + Phân vai Nam/Nữ theo âm thanh
- [ ] **✂ Rút gọn AI (dòng tràn khe)**: Load SRT có dòng ❌ "tràn khe" (🩺 Khám SRT thấy) + có API key dịch → bấm ✂ → ra `<tên>_ai.srt` tự nạp lại → 🩺 Khám lại: số dòng ❌ giảm; nội dung dòng được viết ngắn hơn giữ nghĩa
- [ ] SRT không có dòng tràn khe → bấm ✂ → log "✅ Không có dòng nào tràn khe", không tạo file
- [ ] Provider dịch = Offline → bấm ✂ → log ❌ hướng dẫn chọn Claude/Gemini/OpenAI, không chạy
- [ ] Thiếu API key → báo lỗi sớm, không tạo file
- [ ] **🚻 Phân vai Nam/Nữ theo âm thanh**: tạo 2 hồ sơ giọng (vd `nam_tre`, `nu_tre`) → Load SRT khớp video có cả giọng nam + nữ → 🎭 Phân vai → nút 🚻 → chọn video gốc + hồ sơ nam/nữ → Phân tích → log cụm `nam ~XHz / nữ ~YHz` + bảng phân vai mở lại với luật tự gán → nghe thử vài dòng đúng giới
- [ ] Video chỉ có 1 giọng → log ❌ "chỉ có MỘT giọng", không gán bừa
- [ ] Chọn cùng 1 hồ sơ cho cả nam và nữ → báo lỗi "phải khác nhau"

## J. Đợt 2026-07-02 (2): Tách nhạc demucs + Rút gọn ⚠ + Nghỉ giữa đoạn
- [ ] **✂ Rút gọn AI hỏi phạm vi**: SRT vừa có dòng ❌ vừa có ⚠ → bấm ✂ → dialog hỏi "Gồm cả N dòng ⚠?"; chọn Có → sau khi xong 🩺 Khám lại: cả cảnh báo "hơi hẹp" cũng giảm (mọi dòng đọc 1.0×)
- [ ] **🎼 Tách nhạc nền (mux)**: tick "Giữ audio gốc" → checkbox 🎼 hiện ra (bỏ tick thì ẩn cùng ducking) → mux video có nhạc + lời thoại → log "🎼 Tách nhạc nền..." + progress demucs → video ra nghe **nhạc nền rõ, KHÔNG còn lời thoại gốc**, giọng dub sạch
- [ ] Máy không có voxcpm_env (hoặc đổi tạm override sai) → log ⚠ fallback ducking, mux vẫn hoàn tất
- [ ] Bấm ⏹ Dừng giữa lúc demucs đang chạy → dừng được, không treo, thư mục temp `mux_demucs_*` bị dọn
- [ ] Wizard lồng tiếng với "Giữ audio gốc" + 🎼 đã tick từ trang video → bước mux của wizard cũng tách nhạc
- [ ] **⏸ Nghỉ giữa đoạn**: Load Word/TXT → TTS → đặt "Nghỉ giữa đoạn (ms)" = 500 → Merge Audio → log "⏸ Chèn 500ms..." → file ra có khoảng lặng rõ giữa các đoạn; đặt 0 → merge liền như cũ
- [ ] Giá trị rác trong ô (vd "abc") → merge không khoảng nghỉ, không crash

## K. Đợt 2026-07-02 (3): 3 take + Dub thử 60s + fade
- [ ] **🎲 Gen 3 take**: Load SRT + Output có sẵn audio → bấm 🎲 → nhập số dòng → 3 take gen lần lượt (✅ hiện dần) → ▶ nghe từng bản khác nhau → ✔ chọn 1 → `line_NNNN.mp3` là bản đã chọn, các file `.takeK.mp3` bị xóa, bản gốc còn ở `.old.mp3`
- [ ] Đóng dialog không chọn gì → bản cũ được khôi phục (line_NNNN.mp3 như trước khi gen)
- [ ] Bấm ✔ khi đang gen dở → báo "đợi gen xong"; các file .takeK không lọt vào Merge/QC/missing scan
- [ ] **🔍 Thử 60s đầu (wizard)**: chọn video dài + cấu hình như thật → bấm 🔍 → clip 60s được cắt vào `<video>_preview_dub\` → chạy đủ 5 bước trên clip → tự mở bản thử; chạy full sau đó không đụng thư mục preview
- [ ] Dán link YouTube rồi bấm 🔍 → báo lỗi hướng dẫn (chỉ nhận file)
- [ ] **Fade chống click**: merge SRT có các dòng sát nhau → final không còn tiếng "tạch" ở điểm nối (so với bản merge cũ nếu có)

## L. Đợt 2026-07-02 (4): teencode + cảnh báo ngôn ngữ + tự hồi phục mạng
- [ ] **Teencode**: Quick TTS gõ "anh ko bik dc đâu, tks nha" → Nghe thử → đọc "anh không biết được đâu, cảm ơn nha"; gõ "BT là Bến Tre, giá 100k" → đọc nguyên văn (hoa + số không đổi); tắt checkbox "Đọc teencode" → đọc nguyên văn cả câu đầu
- [ ] **Cảnh báo ngôn ngữ**: Load SRT tiếng Anh khi giọng đang là vi-VN → logbox có dòng ⚠ "SRT có vẻ không phải tiếng Việt..."; Load SRT tiếng Việt + giọng en-US → ⚠ ngược lại; SRT + giọng cùng tiếng Việt → không cảnh báo
- [ ] **Tự hồi phục mạng**: chạy batch Edge → rút mạng giữa chừng → log "📶 Mất mạng — tự chờ..." (không dừng) → cắm mạng lại → trong ~30s log "📶 ✅ Mạng đã trở lại" + batch tự chạy tiếp đến hết
- [ ] Rút mạng rồi bấm ⏹ Dừng trong lúc đang chờ → dừng trong ~1 giây
- [ ] Chế độ song song (Edge ×4) cũng tự hồi phục như tuần tự

## F. Sau build (exe)
- [ ] `output\Portable\SRT_TTS_Studio_Portable.exe` mở được, đăng nhập OK
- [ ] Lặp lại nhanh mục B+C trên exe (ít nhất: glossary + TTS song song + merge)
- [ ] Bảng điều khiển trên exe: mục G chạy đúng (đặc biệt **Sẵn sàng chạy?** + **Chẩn đoán nâng cao**)
