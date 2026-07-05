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
- [ ] Dòng bị `toolong` dai dẳng (hallucination) → log `🔪 … cứu 'toolong' bằng cách tách N câu — OK`, ra audio hoàn chỉnh thay vì FAIL (chỉ luồng provider không-RVC; câu quá ngắn/không tách được vẫn FAIL như cũ)
- [ ] Sửa text 1 dòng (Regenerate Line) → file cũ thành `line_NNNN.old.mp3`
- [ ] **Merge FFmpeg** → ra `final.mp3` + `final_synced.srt`; bật "Cân âm lượng các dòng" merge lại → log `🔉 Đã cân âm lượng N dòng`
- [ ] Bật "Chuẩn hóa âm lượng (-16 LUFS)" → merge → final nghe đều
- [ ] Thu nhỏ app lúc batch sắp xong → **toast Windows** hiện khi xong

## C2. Gắn cảm xúc AI (SRT)
- [ ] Trang SRT → **🎭 Tự gắn cảm xúc (AI)** (cần API key dịch) → confirm → ra `<tên>_emo.srt` + nạp lại; log "Phân bố: [vui]×N…"
- [ ] Các dòng có tag `[vui]/[giận]/…` ở đầu → TTS Edge đọc đổi tốc độ/cao độ; engine khác không đọc tag thành tiếng
- [ ] Chạy lại lần 2 → tag cũ được thay, không bị chồng `[vui] [buồn]`
- [ ] Provider = Offline → nút báo lỗi hướng dẫn chọn Claude/Gemini/…

## D. Wizard lồng tiếng (test với video ngắn 1-2 phút)
- [ ] **🎬 Lồng tiếng tự động** → dialog có dropdown Hồ sơ giọng + các checkbox (gồm 👄 Khớp khẩu hình)
- [ ] Chạy full chuỗi → 5 bước chạy lần lượt, ra `<video>_dubbed.mp4` + khối 📊 tổng kết
- [ ] Bật "Gắn phụ đề cứng" → video ra có sub burn-in, chữ khớp tiếng (dùng final_synced.srt)
- [ ] **👄 Khớp khẩu hình** (cần lipsync_env + Wav2Lip + GPU): tick → chạy → bước 6/6 → ra `<video>_dubbed_lipsync.mp4`, miệng khớp giọng, giữ nguyên phụ đề cứng + mix audio
- [ ] Tick 👄 nhưng THIẾU env Wav2Lip → preflight báo lỗi rõ (không chạy dở rồi mới lỗi)
- [ ] 👄 chạy nhưng Wav2Lip lỗi (vd video không có mặt) → log ⚠, vẫn giữ `<video>_dubbed.mp4` (fail-open)
- [ ] Trang Video → card **👄 Khớp khẩu hình (Lip-sync)** đứng riêng: chọn video + tiếng → ra `_lipsync.mp4`; thiếu env → log hướng dẫn
- [ ] **✨ Làm nét mặt (GFPGAN)**: tick checkbox trên card Lip-sync (hoặc trong wizard) → sau khớp khẩu hình chạy thêm GFPGAN → ra `_lipsync_hd.mp4`, mặt nét hơn hẳn vùng miệng
- [ ] Tick ✨ nhưng thiếu gfpgan/model → wizard preflight báo lỗi rõ; card standalone log ⚠ và giữ bản chưa nét (fail-open)
- [ ] **👥 Đa mặt**: video 2 người cạnh nhau → chọn "Vùng mặt = Nửa trái/phải" → chỉ mặt bên đó được khớp miệng, nửa còn lại nguyên vẹn (crop→sync→dán ngược); "Cả khung" = như cũ
- [ ] ETA hiện trên thanh tiến trình dạng `45% · còn ~2p30s`
- [ ] **📺 YouTube → Lồng tiếng**: dán 1 link vào ô YouTube → Bắt đầu → tải về (thanh % chạy) → chạy 5 bước → tự mở video `_dubbed.mp4` bằng trình phát mặc định
- [ ] Dán **nhiều link** (mỗi dòng 1 link) → tải + dub tuần tự từng video, mỗi cái xong tự mở
- [ ] Chưa cài yt-dlp → log báo `❌ Chưa cài yt-dlp ... pip install -U yt-dlp` (không treo)
- [ ] Tắt "Mở xem ngay khi xong" → xong không tự mở; đổi thư mục Tải về → đóng/mở app vẫn nhớ

## D2. Video Karaoke (chữ chạy theo giọng)
- [ ] Trang Video → card 🖼 Audio → Video: chọn audio + SRT + tick **🎤 Karaoke (chữ chạy)** → Tạo Video → ra `<audio>_video.mp4`
- [ ] Mở video: từng từ tô **vàng** dần theo giọng (chưa đọc = trắng), canh giữa đáy, viền đen dễ đọc, dấu tiếng Việt đúng
- [ ] Bật kèm 🌊 Sóng nhạc / đổi Khung 9:16 → vẫn ra karaoke đúng khung, chữ nằm trên sóng
- [ ] SRT lỗi/không đọc được → tự lùi về burn phụ đề thường (không chết cả video)

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

## M. Đợt 2026-07-02 (5): ASS/VTT + Script→Audio + Thu âm mic
- [ ] **Load .ass**: Load SRT chọn file .ass (anime fansub) → log "🔄 Đã chuyển ... _conv.srt" → danh sách dòng hiện đúng, không còn tag {\\...}, chạy TTS bình thường
- [ ] **Load .vtt** (YouTube xuất) → convert OK, timestamps đúng; file lỗi/rỗng → báo lỗi rõ, không crash
- [ ] Trang Dịch → "Dịch SRT" chọn file .ass → convert rồi dịch, ra `_conv_vi.srt`
- [ ] **🔊 Script → Audio**: sau khi Dịch truyện có `_script_dich.txt` → bấm nút trên card dịch truyện → chọn file → nhảy sang trang Tài liệu với các đoạn lời thoại → Đọc (TTS) + Merge ra file audio đọc truyện
- [ ] File txt thường (không có dòng "→") → báo lỗi hướng dẫn, không nạp
- [ ] **🎙 Thu âm**: panel VoxCPM/VieNeu/F5/Omni → nút 🎙 cạnh Browse → dialog liệt kê đúng micro của máy → Thu 15s (đếm ngược) → xong tự điền đường dẫn wav vào ô Audio mẫu → ▶ Nghe lại đúng giọng vừa thu
- [ ] Bấm ⏹ Dừng giữa lúc thu (vd giây thứ 5) → file vẫn được lưu (~5s) và điền vào ô
- [ ] Máy không có mic (rút hết) → báo "Không tìm thấy thiết bị thu âm", không crash

## N. Đợt 2026-07-02 (6): Podcast + sidecar phân vai + phân vai lai
- [ ] **🎙 Podcast**: tạo 2 hồ sơ giọng khác nhau + có API key dịch → trang Tài liệu → card Podcast → chọn 1 file docx/txt vài trang → Tạo Podcast → kịch bản `podcast_script.txt` xuất hiện trong `<file>_podcast\` → các lượt A/B được đọc bằng đúng 2 giọng → tự merge ra 1 file mp3, nghe như hội thoại
- [ ] Bấm ⏹ giữa lúc đọc → dừng; chạy lại wizard cùng file → các lượt đã đọc được skip (resume)
- [ ] Xong podcast → giọng đang cấu hình ở tab Giọng nói được trả về như trước khi chạy
- [ ] Provider Offline / thiếu key / <2 hồ sơ → báo lỗi sớm, không chạy
- [ ] Chọn file PDF làm nguồn → extract qua pdf_helper OK (cần python có pypdf)
- [ ] **Sidecar phân vai**: gán vài luật trong 🎭 → 💾 Lưu → thấy `<srt>.cast.json` cạnh SRT → đóng app mở lại → Load đúng SRT đó → log "🎭 Đã nạp N luật..." → mở 🎭 thấy đủ luật
- [ ] Xóa hết luật rồi Lưu → file sidecar bị xóa; Load SRT khác (không có sidecar) → luật trong RAM giữ nguyên
- [ ] **Phân vai lai**: chạy 🚻 (video 2 giới) xong → chạy 🤖 Tự phân vai → log "🚻 Dùng N hint giới tính..." → nhân vật nam không bị gán hồ sơ giọng nữ; Load SRT khác → hint bị xóa (log 🤖 không nhắc hint)

## O. Đợt 2026-07-02 (7): Tìm & thay + dòng lặp + Groq/DeepSeek
- [ ] **🔁 Tìm & thay**: Load SRT → nút 🔁 (cột io) → nhập tìm/thay → Xem trước hiện đúng số dòng + ví dụ trước/sau → Thay & lưu → `_edit.srt` tự nạp lại
- [ ] Các dòng bị đổi đã có audio → hỏi "Xóa audio N dòng..." → Yes → file mp3 các dòng đó bị xóa → 🧩 đọc lại đúng text mới
- [ ] Tick Regex + pattern sai (vd `[`) → báo "❌ Regex lỗi", không crash; bỏ tick "Phân biệt HOA/thường" → khớp cả hoa lẫn thường
- [ ] **Dòng lặp**: SRT có 3+ dòng giống hệt liên tiếp → 🩺 Khám báo "lặp giống hệt N dòng liên tiếp"; 🔧 Sửa SRT → log "Gộp N dòng lặp...", file `_fixed.srt` chỉ còn 1 dòng với khe kéo dài; 2 dòng lặp (chủ ý kịch) → không đụng
- [ ] **Groq/DeepSeek**: ⚙ Cài đặt có 2 ô key mới (che *) → nhập key Groq → trang Dịch chọn provider Groq → dịch 1 SRT ngắn OK; DeepSeek tương tự; đổi model qua dropdown "Groq — llama-3.1-8b-instant" cũng chạy
- [ ] Chọn Groq nhưng chưa nhập key → báo "Chưa nhập API key cho Groq" sớm
- [ ] Các tính năng LLM khác (✂ Rút gọn AI, 🤖 Tự phân vai, 🎙 Podcast) chạy được với provider Groq/DeepSeek

## P. Đợt 2026-07-02 (8): Việc cần làm + m4b + tooltip
- [ ] **📋 Việc cần làm**: sau 1 batch có FAIL/dòng lỗi → log có dòng 💡 → bấm nút 📋 (đầu cột io) → dialog liệt kê đúng: dòng lỗi QC (kèm loại), dòng thiếu, dòng tràn khe — bấm nút từng mục chạy đúng chức năng
- [ ] Output sạch (không lỗi gì) → panel hiện "✅ Sạch sẽ!"
- [ ] **Tooltip**: rê chuột đứng yên ~0.5s trên 🩺/🔧/✂/🎲/📋... → hiện chú thích; rời chuột/bấm → biến mất; hover color của nút vẫn hoạt động
- [ ] **📚 m4b**: Load Word/EPUB có heading "Chương 1/2/3..." → TTS → tick "Xuất .m4b có chương" → Merge Audio → ngoài mp3 có thêm `.m4b`; mở bằng player (VLC/Apple Books) → tua theo đúng chương
- [ ] Tài liệu không có heading → m4b vẫn ra với 1 chương "Mở đầu"
- [ ] Bỏ tick m4b → chỉ ra mp3 như cũ; m4b lỗi (thiếu codec) → log ⚠ nhưng mp3 vẫn nguyên

## Q. Đợt 2026-07-02 (9): Bảng phụ đề + đọc theo đoạn + webhook
- [ ] **📝 Bảng phụ đề**: Load SRT (có vài dòng lỗi lint + vài dòng đã có audio) → nút 📝 → bảng hiện đủ dòng, cột TT có ❌/⚠/✅/🔴 đúng; SRT >1000 dòng cuộn mượt
- [ ] Chọn dòng → sửa text ở ô dưới → ✏ Cập nhật → cột TT thêm ✏; ▶ Nghe phát đúng audio dòng; 🔁 Đọc lại → audio mới theo text vừa sửa
- [ ] 💾 Lưu file → `_edit.srt` tự nạp lại; các dòng sửa-chưa-regen được hỏi xóa audio; Đóng không lưu → SRT gốc nguyên vẹn
- [ ] **📖 Từ đoạn/đến**: Load Word dài → "Từ đoạn 10 đến 20" → Đọc (TTS) → chỉ ra `pdf_line_0010..0020`; log có dòng 📖; rỗng → đọc tất cả; nhập ngược (20→10) tự đảo
- [ ] Range cũng áp cho engine local (VoxCPM/VieNeu/F5/Omni đọc PDF)
- [ ] **📨 Webhook**: dán URL webhook Discord vào ⚙ Cài đặt → chạy 1 batch xong → tin nhắn hiện trong kênh Discord (kèm số dòng/FAIL); xóa URL → không gửi nữa; URL sai → không crash, không chậm app

## R. Đợt 2026-07-03: Sửa SRT bằng AI + style burn-in
- [ ] **🪄 Sửa SRT bằng AI**: Load SRT → nút 🪄 → gõ "đổi hết 'tôi' thành 'tớ'" → chạy → `_ai.srt` nạp lại, đúng các dòng có 'tôi' bị đổi, dòng khác giữ nguyên văn
- [ ] Dòng đã có audio bị đổi → hỏi xóa như Tìm & thay; prompt quá ngắn (<5 ký tự) → cảnh báo; provider Offline → từ chối kèm hướng dẫn
- [ ] Đang chạy 🪄 thì bấm ✂ Rút gọn AI → báo "Đang chạy" (chung khóa)
- [ ] **🎨 Style burn-in**: wizard → tick "Gắn phụ đề cứng" + Cỡ "To" + Màu "Vàng" → video ra chữ vàng to viền đen; đổi "Nhỏ"+"Trắng" → đúng theo; lựa chọn được nhớ sau khi đóng/mở app

## S. Đợt 2026-07-03 (2): Soát đọc sai STT + Lịch sử job + Phân vai rate/pitch
- [ ] **🎙🔍 Soát đọc sai (STT)**: chạy 1 batch SRT ngắn xong → nút 🎙🔍 (cột io) → thanh tiến trình chạy → nếu sạch: log "✅ N dòng khớp nội dung"; sửa tay 1 file `line_NNNN.mp3` (thay bằng audio nói câu khác) → chạy lại → dialog mở đúng dòng đó kèm % khớp + "Kỳ vọng/Nghe được" → ▶ nghe đúng file, 🔁 đọc lại xong hiện ✅
- [ ] Chưa Load SRT / output rỗng / thiếu voxcpm_env → từ chối sớm kèm hướng dẫn, không crash
- [ ] Đang TTS chạy → bấm 🎙🔍 → báo "Đang có tiến trình khác"
- [ ] **🕘 Lịch sử job**: chạy xong 1 batch provider → nút 🕘 → dialog có entry mới nhất (thời gian, file, số dòng, giọng); ↻ → SRT + output + giọng được nạp lại đúng (đổi giọng khác trước khi ↻ để thấy giọng bị đổi về); 📂 mở đúng thư mục; entry PDF chỉ áp giọng + output kèm hướng dẫn
- [ ] `job_history.json` xuất hiện cạnh settings.json, tối đa 30 entry
- [ ] **🎚 Phân vai rate/pitch**: 🎭 Phân vai → luật chọn "(Giọng UI)" + Tốc độ `+40%` cho dòng 0-2 → 🎬 Lưu & Chạy → 3 dòng đầu đọc nhanh hơn hẳn, các dòng khác bình thường; xong batch ô Tốc độ Edge trên tab Giọng nói trở về giá trị cũ
- [ ] Luật hồ sơ + override pitch `-5Hz` → nhóm đó vừa đổi giọng vừa trầm hơn; sidecar `.cast.json` lưu cả rate/pitch, load lại SRT vẫn còn
- [ ] Không có hồ sơ giọng nào vẫn mở được dialog phân vai (chỉ dùng "(Giọng UI)" + rate/pitch)

## T. Đợt 2026-07-03 (3): Auto soát STT + màu phân vai + playlist YouTube
- [ ] **☑ Tự soát đọc sai (STT) khi xong**: tick checkbox (tab Giọng nói) → chạy 1 batch SRT ngắn → sau khi xong (và sau auto-retry nếu cùng bật) tự thấy log 🎙🔍 + thanh tiến trình soát chạy; có dòng nghi sai → dialog tự mở
- [ ] Checkbox được nhớ qua phiên (ui_prefs); toggle cũng có trong card "Bật/tắt nhanh" Dashboard và đồng bộ 2 chiều
- [ ] Bỏ tick → batch xong không tự soát; batch PDF → không tự soát (chỉ SRT)
- [ ] **🎨 Màu phân vai**: đặt ≥2 luật phân vai (khác hồ sơ hoặc khác rate/pitch) → mở 📝 Bảng phụ đề → có cột "Vai" + mỗi vai một màu nền đúng dải dòng; dòng ngoài luật không màu; SRT không có luật → bảng như cũ (không có cột Vai)
- [ ] Sửa text 1 dòng có màu → ✏ Cập nhật → dòng vẫn giữ màu vai
- [ ] **📺 Playlist YouTube**: wizard → ô link dán link playlist ngắn (3-5 video) → chạy → log "📚 Playlist/kênh... ✅ N video trong danh sách" → tải + dub tuần tự từng video, mỗi video một thư mục `_dub`
- [ ] Link kênh `/@tenkenh` → tự nối `/videos`, liệt kê OK; danh sách >100 → log trần 100
- [ ] Link watch?v= có `&list=` kèm → vẫn chỉ dub 1 video đó (không nổ ra cả playlist)
- [ ] Bấm ⏹ giữa chừng playlist → hủy phần còn lại như hàng đợi video thường

## U. Đợt 2026-07-03 (4): Thư viện nhân vật + theo dõi kênh + nhạc nền merge
- [ ] **📚 Thư viện nhân vật**: đặt 2 SRT cùng thư mục → tập 1 chạy 🤖 Tự phân vai → `series_cast.json` xuất hiện cạnh SRT + log "📚 Đã lưu N nhân vật"; Load tập 2 → 🤖 → log "📚 Nạp N nhân vật đã có giọng" và các nhân vật cũ giữ đúng hồ sơ như tập 1
- [ ] Xóa 1 hồ sơ giọng có trong thư viện → 🤖 tập sau không lỗi (nhân vật trỏ hồ sơ đã xóa bị bỏ, LLM gán lại)
- [ ] **📡 Theo dõi kênh**: wizard → card YouTube → nút 📡 → dán 1 link kênh/playlist → 💾 Lưu (ra `yt_watch.json`) → "🔍 Kiểm tra & dub video mới" → log liệt kê "X/N video chưa dub" → các video mới vào hàng đợi dub với đúng tùy chọn wizard
- [ ] Chạy kiểm tra lần 2 sau khi dub xong → log "✅ Không có video mới"; đang dub mà bấm kiểm tra → từ chối
- [ ] **🎵 Nhạc nền merge**: chọn file nhạc + Vol 0.12 → Merge FFmpeg → final có nhạc nền nhỏ dưới giọng, tự lặp nếu nhạc ngắn hơn, kết thúc đúng lúc hết lời (fade 2s); nghe rõ lời không bị nhạc đè
- [ ] Để trống ô nhạc nền → merge như cũ; đường dẫn sai → log ⚠ bỏ qua, merge vẫn chạy; Vol 0.3 → nhạc to hơn rõ rệt; kết hợp loudnorm vẫn OK
- [ ] Đường dẫn nhạc nền + Vol được nhớ qua phiên (ui_prefs)

## V. Đợt 2026-07-03 (5): Kịch bản 1-click + chia file + Bắt đầu nhanh
- [ ] **⚡ Kịch bản**: Dashboard → card Bật/tắt nhanh → chọn "📖 Truyện audio" → Áp dụng → các checkbox liên quan đổi đúng (căn giữa khe lặng ON, loudnorm ON, m4b ON, nghỉ đoạn 400); trang Giọng nói/SRT/Doc hiển thị đồng bộ; "↺ Mặc định" trả về ban đầu
- [ ] Áp kịch bản KHÔNG đổi giọng/provider/engine đang chọn
- [ ] **✂ Chia final theo giờ**: merge 1 file final dài >2 phút → nút ✂ → đặt "Phút mỗi phần" = 1 → ra `final_p01/p02/...` đúng số phần, mỗi phần đúng ~1 phút, chia xong mở thư mục; có `final_synced.srt` → ra kèm `_pNN.srt` timestamp bắt đầu từ 0
- [ ] File ngắn hơn 1 phần → log "không cần chia", không ra file; file sai đường dẫn → báo lỗi sớm
- [ ] **🚀 Bắt đầu nhanh**: Dashboard → nút 🚀 → dialog 6 tình huống; bấm "Có file SRT" → nhảy trang TTS + logbox in 4 bước; bấm "Có video" → mở thẳng wizard lồng tiếng

## W. Đợt 2026-07-03 (6): Viết truyện AI (ainovel-cli)
- [ ] Trang **Tài liệu** hiện card "📖 Viết truyện AI (ainovel-cli)" với ô prompt, thư mục truyện, dropdown Phong cách, ô Model, 4 nút
- [ ] **Chưa có ainovel-cli.exe**: nhập prompt → 📖 Viết truyện → log ❌ hướng dẫn tải/đặt exe cạnh app, KHÔNG treo, không ảnh hưởng nút khác
- [ ] Provider dịch = **Offline** (⚙ Cài đặt) → 📖 Viết truyện → log ❌ nhắc đổi sang Claude/Gemini/OpenAI/DeepSeek/Groq
- [ ] Provider cloud nhưng **API key rỗng** → log ❌ nhắc điền key ở ⚙ Cài đặt
- [ ] (Có exe + key) prompt ngắn → chạy → xem `<thư mục>\.ainovel_cfg\config.json` đúng provider/model/api_key; chương `.md` sinh ở `<thư mục>\output\novel\chapters\`; **⏹ Dừng** kill được tiến trình
- [ ] **🔊 Nạp truyện → Đọc (TTS)**: sau khi có chương → nạp → `subtitle_list` hiện các đoạn, sang trang Doc, "Đọc (TTS)" + "Merge Audio" chạy được
- [ ] **📂 Mở thư mục** mở đúng `output\novel`; nút 📁 chọn thư mục hoạt động

## X. Đợt 2026-07-03 (7): Tải truyện chữ (web novel) → Audio
- [ ] Trang **📚 Tải truyện** hiện card "📖 Tải truyện chữ (web novel) → Audio" (URL / Chương / checkbox Gộp / Lưu vào / 4 nút)
- [ ] Dán URL bộ truyện truyenfull (domain còn sống, vd `https://truyenfull.io/<slug>/`) + Chương `1-3` → ⬇ Tải truyện chữ → ra `chuong_00001.txt`..`chuong_00003.txt` trong `Lưu vào\<slug>\`, log `✔ Chương N (X ký tự)`, mỗi file mở ra có header "Chương N: ..." + nội dung sạch (không dính menu/quảng cáo script) — **lưu ý: AV trên máy build chặn nhóm site truyện (lỗi 499) → test trên máy/mạng không chặn**
- [ ] Checkbox **Gộp 1 file TXT cả bộ** bật → có thêm `<slug>_full.txt` ghép đúng thứ tự chương
- [ ] Chạy lại cùng URL/khoảng → log `— đã có, bỏ qua` (resume), không tải lại
- [ ] Dán URL **1 chương** (`.../chuong-5/`) → chỉ tải 1 chương đó
- [ ] Đang tải bấm **⏹ Dừng** → dừng trong vài giây, nút Tải bật lại
- [ ] URL trống/sai → log ❌ hướng dẫn; trang cần JS/Cloudflare → log ❌ "không tách được nội dung"/"không tìm thấy link chương", không treo
- [ ] Đang tải truyện chữ thì bấm ⬇ ở card Webtoon (và ngược lại) → log ⚠ "Đang có tác vụ truyện chạy"
- [ ] **🔊 Đọc TTS**: chọn file `_full.txt` (hoặc nhiều file chương) → `subtitle_list` hiện các đoạn `[i]`, tự sang trang Tài liệu, "Đọc (TTS)" + "Merge Audio" chạy được; bật **Xuất .m4b có chương** → file m4b có mục lục đúng tên "Chương N" (ffprobe show_chapters)
- [ ] **🚀 Tải → Đọc → Audiobook (1 nút, THEO CHƯƠNG)**: URL bộ truyện + Chương `1-3` + tick `.m4b có chương` → 🚀 → pha tải xong thì đọc TỪNG chương (`🚀 [k/N] Đọc chuong_...`), mỗi chương ra `audio_chap\chuong_NNNNN.mp3` (parts bị xóa sau khi đóng chương), cuối cùng `🚀 ③ Nối` ra `<truyện>_audiobook.mp3` + `.m4b` mục lục đúng tên chương + pháo hoa
- [ ] Chạy lại 🚀 cùng URL/khoảng → pha tải log `♻ N/M chương đã có`, pha TTS bỏ qua chương đã có mp3, log "Không có chương mới — audiobook giữ nguyên" (không nối lại)
- [ ] Tải thêm chương mới (tăng khoảng lên `1-5`) → chạy 🚀 → CHỈ đọc 2 chương mới, audiobook nối lại đủ 5 chương đúng thứ tự
- [ ] Đang chạy 🚀 bấm **⏹ Dừng** ở pha TTS → dừng được; chạy lại → resume mức đoạn (parts của chương dở giữ nguyên)
- [ ] Xóa 1 file `audio_chap\chuong_00002.mp3` rồi chạy 🚀 → chỉ chương 2 được đọc lại (regen theo chương)
- [ ] **📡 Theo dõi bộ truyện**: thêm 1-2 URL bộ đang ra → 💾 Lưu (ra `novel_watch.json` cạnh settings.json) → 🔍 Kiểm tra: bộ đã tải đủ log "không có chương mới"; bộ có chương mới log `+N chương mới` + cập nhật `_full.txt` + pháo hoa; đóng mở app danh sách + checkbox 🔊 còn nguyên
- [ ] **📡 + 🔊 Đọc luôn chương mới**: tick 🔊 → 🔍 → sau pha tải, các bộ có chương mới tự đọc TTS đúng phần mới + audiobook nối lại; bộ không có chương mới KHÔNG bị đọc lại
- [ ] Đang có tác vụ truyện khác chạy → 🚀/🔍 từ chối với log ⚠, không chen ngang

## Y. Đợt 2026-07-03 (8): 🎬 Lấy audio mẫu từ video / YouTube
- [ ] Cả 4 panel clone (VoxCPM/VieNeu/F5-TTS/OmniVoice) đều có nút **🎬** cạnh nút 🎙 ở hàng Audio mẫu
- [ ] Bấm 🎬 → dialog "Lấy audio mẫu từ video / YouTube" (Nguồn / Bắt đầu / Lấy N giây / checkbox 🎼 / 3 nút)
- [ ] **File local**: Browse chọn 1 video/mp3 trên máy + Bắt đầu `1:30` + Lấy `12` → ✂ Cắt → status ✅, ô Audio mẫu của ĐÚNG engine được điền `ref_vid_*.wav` (trong `recordings\` cạnh settings.json), ▶ Nghe lại đúng đoạn
- [ ] **Link YouTube**: dán link + Bắt đầu `0:05` → ✂ Cắt → chỉ tải đúng đoạn (nhanh, vài trăm KB), ra WAV đúng thời lượng — đã verify lệnh 2026-07-03 với yt-dlp 2026.06.09
- [ ] Tick **🎼 Tách giọng khỏi nhạc** với đoạn có nhạc nền → chạy demucs (lần đầu lâu) → WAV ra `_voice.wav` chỉ còn giọng; máy không có voxcpm_env → log ⚠ bỏ qua tách, vẫn ra bản chưa tách
- [ ] Thời điểm bắt đầu vượt quá độ dài nguồn → status ❌ "Cắt thất bại / đoạn quá ngắn", không điền ô
- [ ] Chưa cài yt-dlp (tạm đổi tên exe/env) + dán link → status ❌ hướng dẫn cài, không treo
- [ ] Đang tải/cắt bấm **⏹ Dừng** hoặc đóng dialog → tiến trình bị kill, không treo app

## Z. Đợt 2026-07-03 (9): ▶ Nghe thử trong Tìm giọng 🔎
- [ ] Tab Giọng nói → 🔎 → chọn 1 giọng `vi-*` trong list → **▶ Nghe thử** → nghe câu mẫu tiếng Việt bằng đúng giọng đó; giọng UI hiện tại KHÔNG bị đổi (dropdown giữ nguyên)
- [ ] Chọn giọng `ja-JP`/`en-US` → ▶ → câu mẫu đúng ngôn ngữ đó (không đọc tiếng Việt ngọng)
- [ ] Bấm ▶ liên tiếp 2 giọng → chỉ bản sau phát (không chồng tiếng)
- [ ] Đang chạy batch TTS → ▶ → log ⚠ từ chối (giọng dùng chung), không phá batch

## AA. Đợt 2026-07-03 (10): 📰 Đọc báo/RSS + 🌊 Sóng nhạc động
- [ ] Trang **Tài liệu → Audio** hiện card "📰 Đọc bài báo / RSS → Audio" (Link / Số bài / 2 nút)
- [ ] Dán link 1 **bài báo** VnExpress/Dân Trí/Tuổi Trẻ → 📰 → log `✔ <tiêu đề> (N ký tự)`, `subtitle_list` hiện các đoạn, mode pdf bật → "Đọc (TTS)" chạy được — nội dung là THÂN BÀI (không dính menu/hộp promo "Chọn VnExpress làm nguồn...")
- [ ] Dán link **RSS** (`https://vnexpress.net/rss/tin-moi-nhat.rss`) + Số bài `3` → lấy 3 bài mới nhất, mỗi bài header `Phần i: <tiêu đề>`; bài video/quiz (ít chữ) bị bỏ qua với ⚠ — đã verify live 2026-07-03
- [ ] Merge với **.m4b có chương** sau khi đọc RSS nhiều bài → m4b có mục lục theo bài (ffprobe show_chapters)
- [ ] Link rác / trang cần JS → log ❌ rõ ràng, không treo; ⏹ Dừng giữa lúc tải nhiều bài → dừng được
- [ ] **🌊 Sóng nhạc động** (card Audio→Video, trang Video): tick 🌊 + audio + ảnh nền → 🎬 Tạo Video → video ra có dải sóng chạy theo nhạc sát đáy màn hình (đã verify lệnh 2 nhánh ảnh nền/nền màu với ffmpeg 8.0)
- [ ] 🌊 + phụ đề burn → chữ phụ đề nằm TRÊN dải sóng, không bị che
- [ ] Bỏ tick 🌊 → hành vi cũ giữ nguyên (ảnh tĩnh, tune stillimage)

## AB. Đợt 2026-07-03 (11): ☕ Bản tin 1 nút
- [ ] Card 📰 có nút **☕ Bản tin (1 nút)** giữa 📰 và ⏹
- [ ] Dán RSS (`https://vnexpress.net/rss/tin-moi-nhat.rss`) + Số bài `3` → ☕ → 3 pha liền mạch (tải bài → `☕ ② Đọc TTS` → `☕ ③ Merge`) → ra `pdf_output_*.mp3` + `.m4b` mục lục theo bài trong `Downloads\BanTin\bantin_<stamp>\` + pháo hoa + mở thư mục
- [ ] Dán link 1 bài lẻ → ☕ → ra mp3 (không .m4b — chỉ 1 bài)
- [ ] Đang chạy ☕ bấm ⏹ ở pha TTS → dừng được, không treo
- [ ] Đang có job TTS khác chạy → ☕ từ chối với log ⚠
- [ ] Nút 📰 thường (nạp không đọc) vẫn hoạt động như cũ

## AC. Đợt 2026-07-03 (12): Khung dọc + Mục lục YouTube + Cắt tại chỗ lặng
- [ ] **Khung hình Audio→Video**: dropdown "Khung:" có 16:9 / 9:16 / 1:1; chọn **9:16** + ảnh nền + 🌊 → video ra 720×1280 (đã verify lệnh), ảnh được pad giữa, sóng vẫn sát đáy
- [ ] Chọn 1:1 → ra 720×720; để 16:9 → hành vi cũ (1280×720)
- [ ] **Mục lục YouTube**: Merge Audio với ".m4b có chương" (tài liệu có heading Chương N) → cạnh output có `youtube_description.txt`, dòng đầu `00:00`, mỗi chương 1 dòng `MM:SS Tên` — dán vào mô tả YouTube hiện chapter
- [ ] Chuỗi 🚀 truyện chữ với .m4b → `youtube_description.txt` cũng xuất hiện trong thư mục truyện
- [ ] **🔇 Cắt tại chỗ lặng** (✂ Chia final theo giờ): file dài >2 phần + tick 🔇 → log "Đang dò chỗ lặng..." rồi `🔇 Mốc cắt: ...`, nghe cuối mỗi phần KHÔNG đứt giữa câu; file SRT chia kèm khớp mốc mới
- [ ] Bỏ tick 🔇 → cắt đúng mốc cứng như cũ; file toàn tiếng không có chỗ lặng → log ⚠ fallback mốc cứng

## AD. Đợt 2026-07-03 (13): 🎵 Nhạc nền audiobook + Batch Audio→Video
- [ ] Trang Tài liệu → dưới hàng "Nghỉ giữa đoạn" có hàng **🎵 Nhạc nền** (ô path + 📁 + Vol, mặc định 0.12); giá trị được nhớ qua phiên (ui_prefs)
- [ ] Load TXT ngắn → Đọc TTS → chọn file nhạc + **Merge Audio** → log `[PDF] 🎵 Đã trộn nhạc nền...` → nghe final có nhạc nhẹ dưới giọng, ĐỘ DÀI KHÔNG ĐỔI, nhạc fade nhỏ dần 2s cuối; nhạc ngắn hơn giọng đọc vẫn phủ đủ (loop — đã verify)
- [ ] Bật ".m4b có chương" cùng nhạc nền → file .m4b cũng có nhạc
- [ ] Chuỗi 🚀 truyện chữ với ô nhạc nền đã set → `_audiobook.mp3` có nhạc nền
- [ ] Ô nhạc nền rỗng → hành vi cũ; file nhạc không tồn tại/lỗi → log ⚠, final sạch vẫn còn
- [ ] **Batch Audio→Video**: Browse audio chọn NHIỀU file (vd các `_pNN.mp3` từ ✂ Chia) → ô hiện `a.mp3; b.mp3;...` → 🎬 → mỗi file ra 1 video `[k/N]`, pháo hoa 1 lần cuối
- [ ] Batch với các phần có `_pNN.srt` cạnh file → log ℹ bỏ qua ô Phụ đề + mỗi video tự burn đúng SRT cùng tên
- [ ] Đang chạy loạt bấm **⏹** → hủy cả loạt (không chỉ file hiện tại); 1 file lỗi → log ❌ và chạy tiếp file sau
- [ ] Chọn 1 file như cũ → hành vi cũ giữ nguyên

## AE. Đợt 2026-07-04: 🎺 Nhạc hiệu + chốt xác nhận chuỗi dài
- [ ] Trang Tài liệu → dưới hàng 🎵 có hàng **🎺 Intro / Outro** (2 ô + 📁); giá trị nhớ qua phiên
- [ ] Chọn intro/outro (file nhạc bất kỳ, kể cả stereo 44.1k) + Merge Audio → log `🎺 Đã nối nhạc hiệu (intro+outro)...` → final có nhạc hiệu đầu/cuối, phần giọng nguyên vẹn — đã verify lệnh (intro 2s+outro 3s vào track 6s → 11s)
- [ ] Bật ".m4b có chương" + intro → mốc chương DỜI đúng theo intro, chương "Mở đầu" phủ đoạn nhạc hiệu (verified: marks 0/2.0/5.0)
- [ ] Có cả 🎵 nhạc nền + 🎺 → nhạc nền CHỈ phủ phần giọng đọc, không đè lên jingle
- [ ] Chuỗi 🚀 truyện chữ với intro/outro đã set → `_audiobook.mp3` + m4b có nhạc hiệu
- [ ] **Chốt xác nhận chuỗi dài**: 🚀 với bộ ≥10 chương chưa đọc → sau pha tải hiện dialog "Sắp đọc N chương (~X ký tự ≈ Y giờ audio) / Giọng: ..." → chọn No → log hủy, phần đã tải giữ nguyên; chọn Yes → chạy tiếp
- [ ] 🚀 với <10 chương mới (hoặc chạy lại đã gần đủ) → KHÔNG hỏi, chạy luôn
- [ ] 📡 watch + 🔊 tự đọc → KHÔNG hỏi (chạy không người trông)

## AF. Đợt 2026-07-04 (2): Giọng riêng per bộ + 🌙 Tắt máy + Chuẩn âm lượng
- [ ] Hàng "Nghỉ giữa đoạn" có thêm checkbox **Chuẩn âm lượng**; Merge Audio với file giọng nhỏ tiếng → log `🔊 Đã chuẩn hoá âm lượng (-16 LUFS)` → nghe to đều (verified: -29dB → -15.7dB, sample-rate giữ nguyên)
- [ ] Thứ tự xử lý đúng khi bật cả 4: chuẩn âm lượng GIỌNG trước → nhạc nền → nhạc hiệu → m4b (nhạc nền không bị kéo to, jingle không bị đổi mức)
- [ ] **📡 Giọng riêng từng bộ**: dialog watch hiện hướng dẫn `URL | tên hồ sơ` + danh sách hồ sơ; dòng có `| ho_so_A` → pha 🔊 log `🎤 Giọng cho <bộ>: ho_so_A` và audio ĐÚNG giọng đó; dòng không có `|` → giọng hiện tại; xong tất cả log `↩ Đã khôi phục giọng ban đầu` và UI giọng trở về như cũ
- [ ] Tên hồ sơ sai trong dòng watch → log ⚠ dùng giọng hiện tại, không chết
- [ ] **🌙 Tắt máy khi xong** (checkbox hàng 🚀): tick + chạy 🚀 bộ nhỏ → xong log `🌙 XONG VIỆC — máy sẽ TẮT sau 60 giây` + Windows đếm ngược (hủy: `shutdown /a`); bấm ⏹ giữa chừng → KHÔNG tắt máy
- [ ] Checkbox 🌙 mặc định TẮT mỗi lần mở app (cố ý không nhớ qua phiên)

## AG. Đợt 2026-07-04 (3): 🌐 Dịch truyện nước ngoài → Việt → audiobook
- [ ] Card truyện chữ có checkbox **🌐 Dịch sang tiếng Việt trước khi đọc**; trạng thái nhớ qua phiên
- [ ] Tick 🌐 + provider cloud chưa có key → 🚀 báo ❌ sớm (trước khi tải); provider Offline chưa đặt model → ❌ hướng dẫn ⚙ Cài đặt
- [ ] URL truyện tiếng Anh/Trung (trang dạng chapter-N) + Chương `1-3` + 🌐 → 🚀: pha `①b Dịch` chạy sau pha tải, ra `chuong_NNNNN_vi.txt` từng chương; pha TTS đọc bản DỊCH → mp3 là `chuong_NNNNN_vi.mp3`, audiobook là `<tên>_vi_audiobook.mp3` (verified logic bằng fixture: dịch 3 chương, resume 0 lần gọi engine, chương mới chỉ dịch 1)
- [ ] Chạy lại 🚀 cùng bộ → pha dịch log `♻ N/M chương đã dịch`, KHÔNG gọi lại API
- [ ] Bấm ⏹ giữa pha dịch → dừng (kể cả Offline subprocess); chương đang dịch dở KHÔNG ghi file → chạy lại dịch lại chương đó
- [ ] Dialog xác nhận chuỗi dài hiện thêm dòng "Kèm DỊCH bằng <provider>"
- [ ] BỎ tick 🌐 chạy cùng bộ → đọc bản GỐC, ra bộ mp3/audiobook riêng không lẫn bản `_vi`; file gộp `_full.txt` không chứa bản dịch
- [ ] **📡 watch per bộ**: dòng `URL | hồ_sơ | dich` → bộ đó tự dịch chương mới rồi đọc bản dịch; dòng không có `dich` giữ nguyên hành vi cũ; có dòng `dich` mà thiếu key/model → 🔍 từ chối sớm

## AH. Đợt 2026-07-04 (4): 🖼 Gói xuất bản + dịch thử 1 chương
- [ ] Card truyện chữ có hàng **🖼 Ảnh bìa** (nhớ qua phiên); chạy 🚀 xong → thư mục truyện có `thumbnail.png` 1280×720 (bìa cover-fit + tên truyện chữ Việt trên dải mờ; không chọn bìa = nền tối) — verified PIL
- [ ] File `_audiobook.mp3` sau 🚀 có **tag ID3**: album = tên truyện, artist = SRT TTS Studio, ảnh bìa nhúng (mở bằng player/Explorer thấy bìa) — verified ffprobe attached_pic=1, audio nguyên vẹn
- [ ] **Dịch thử 1 chương**: 🚀 + 🌐 với bộ ≥5 chương chưa dịch → dịch đúng 1 chương rồi hiện dialog 400 ký tự đầu bản dịch; chọn **Yes** → dịch tiếp phần còn lại; chọn **No** → dừng + file `_vi` thử bị XÓA (đổi engine chạy lại sẽ dịch lại bản thử bằng engine mới)
- [ ] Bộ <5 chương chưa dịch → không hỏi, dịch thẳng; 📡 watch với `| dich` → không bao giờ hỏi (chạy không người trông)

## AI. Đợt 2026-07-04 (5): 🎭 Tag cảm xúc + 🐞 Gói hỗ trợ
- [ ] SRT có dòng `[vui] Chào cậu!` + Edge TTS → nghe nhanh/cao hơn dòng thường; `[buồn]`/`[chậm]` → chậm/trầm hơn; **tag KHÔNG bị đọc thành tiếng**
- [ ] Alias không dấu `[buon]`/`[gian]`/`[thi tham]` hoạt động như có dấu
- [ ] Dòng `[nhạc] ♪...` hoặc `[tên nhân vật]` (ngoài whitelist) → giữ nguyên, đọc như cũ (verified fixture 9 case)
- [ ] Engine local (VoxCPM/VieNeu/F5/Omni) với dòng có tag → tag bị bỏ khỏi text đưa vào helper (nghe không có "vui"), giọng không đổi (local không có rate/pitch)
- [ ] Tag + casting per-rule rate/pitch → delta cảm xúc CỘNG DỒN lên rate/pitch của rule (verified combiner + kẹp biên ±200%)
- [ ] Quick TTS gõ `[hét] Tránh ra!` → Nghe thử → to/nhanh rõ rệt
- [ ] **🐞 Gói hỗ trợ** (trang Hệ thống, cạnh 📦): bấm → ra `srt_tts_support_<stamp>.zip` trên Desktop chứa 2 log mới nhất + ui_prefs + tts_prices + sysinfo.txt; **KHÔNG có settings.json/auth.dat** (mở zip kiểm tra); Explorer mở chọn sẵn file

## AJ. Đợt 2026-07-04 (6): 🔍 Soát bản dịch + 🌊 Soát sóng
- [ ] **🔍 Soát bản dịch (dịch ngược)** (trang Dịch, dưới Dịch Word/TXT): cần provider cloud (Offline → ❌ hướng dẫn); chọn SRT gốc → tự đoán `_vi.srt` cạnh nó → hỏi số dòng soát (mặc định ≤300) → dịch ngược về ngôn ngữ đoán từ SRT gốc (EN/中文/日本語/…) → ra `<tên>_backcheck.txt` liệt kê dòng khớp < 0.45 (mỗi dòng: GỐC/DỊCH/NGƯỢC) + Explorer mở chọn file
- [ ] Bản dịch tốt → log `✅ N dòng đều khớp tốt`; sửa 1 dòng `_vi.srt` thành sai nghĩa hẳn → chạy lại → dòng đó bị flag 🔴
- [ ] Ngôn ngữ đích ở trang Dịch được KHÔI PHỤC sau khi soát (kể cả khi lỗi giữa chừng)
- [ ] **🌊 Soát sóng + phụ đề** (trang SRT, cột io dưới 🎧): load SRT + có final → 🌊 → chọn audio (mặc định final) → dải sóng vẽ ra (file dài log "hơi lâu"), vạch XANH đúng mốc bắt đầu từng dòng, mốc phút dưới đáy, cuộn ngang được — verified decode: đoạn lặng 8-12s hiện phẳng rõ giữa 2 khối sóng
- [ ] Click lên sóng → vạch đỏ + status hiện `mm:ss | dòng gần nhất [n]: text`; **▶ Nghe 10s tại điểm click** phát đúng đoạn đó; ⏹ dừng phát
- [ ] Chưa load SRT → sóng vẫn vẽ (không vạch xanh), không crash; audio 10 tiếng → px/giây tự giảm để không vượt trần canvas

## AK. Đợt 2026-07-04 (7): 📈 Thống kê sản lượng
- [ ] Trang Hệ thống (hàng 📦/🐞) có nút **📈 Sản lượng**; chưa có dữ liệu → hiện hướng dẫn
- [ ] Chạy 🚀 truyện chữ (vài chương) → mở 📈 → tháng này cộng đúng số chương + giờ audio (file `production_stats.json` cạnh settings.json)
- [ ] Merge Audio tài liệu → giờ audio tăng thêm đúng độ dài output; Audio→Video (kể cả batch) → cột Video +1 mỗi file
- [ ] Bảng hiện từng tháng mới→cũ + dòng TỔNG; qua tháng mới tự tách dòng (verified fixture cộng dồn)
- [ ] Thống kê lỗi (file hỏng/khóa) → pipeline vẫn chạy bình thường, không crash

## AL. Đợt 2026-07-04 (8): 🖱 Kéo-thả + chuột phải + card truyện Dashboard
- [ ] **Kéo-thả**: kéo file `.srt` từ Explorer thả vào cửa sổ app → tự load + nhảy trang TTS + log `🖱 Đã load`; thả `.ass`/`.vtt` → convert + load như Load SRT; thả file khác (.mp4/.txt) → log hướng dẫn, không crash
- [ ] Kéo-thả hỏng vì lý do gì đó (máy lạ) → app vẫn chạy bình thường (tính năng tắt im lặng)
- [ ] **🖱 Chuột phải** (trang Hệ thống): bấm → Yes trên bản .exe → Explorer chuột phải file .srt có "Mở bằng SRT TTS Studio" → chọn → app mở và tự load file đó (sau splash/login ~2.6s); bấm → No → mục menu biến mất; bản dev python → log giải thích, không ghi registry
- [ ] **Card 📖 Truyện chữ trên Dashboard**: hiện số bộ đang theo dõi + trạng thái 🔊 + tùy chọn đang bật (🌐/🖼/.m4b); nút 🔄 cập nhật, 🔍 mở dialog theo dõi, 📖 nhảy trang truyện
- [ ] **🚀 Bắt đầu nhanh** có thẻ mới "📖 Có link truyện chữ → audiobook" → bấm nhảy trang truyện + in 4 bước

## F. Sau build (exe)
- [ ] `output\Portable\SRT_TTS_Studio_Portable.exe` mở được, đăng nhập OK
- [ ] Lặp lại nhanh mục B+C trên exe (ít nhất: glossary + TTS song song + merge)
- [ ] Bảng điều khiển trên exe: mục G chạy đúng (đặc biệt **Sẵn sàng chạy?** + **Chẩn đoán nâng cao**)
