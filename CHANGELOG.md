# Changelog — SRT TTS Studio

Tất cả thay đổi đáng chú ý của phần mềm được ghi lại trong tệp này.
Định dạng dựa trên [Keep a Changelog](https://keepachangelog.com/vi/1.0.0/).

## [Chưa phát hành]

### Thêm mới
- **🛠 Tự sửa audio mẫu** — nút 🛠 mới cạnh 🎯 trên 4 hàng Audio mẫu: 🎯 chỉ BÁO lỗi, nút này
  SỬA những gì sửa được bằng ffmpeg (khuếch đại mẫu thu quá nhỏ, cắt lặng 2 đầu, chuẩn âm
  lượng loudnorm, nâng sample rate <16k lên 24k, cắt lấy 15s đầu nếu quá dài) → `_fixed.wav`,
  chấm lại điểm — điểm tăng mới điền vào ô (file gốc không bị đụng).
- **⏰ Hẹn giờ thêm 2 hành động theo dõi** — dropdown ⏰ Hẹn giờ có thêm "📡 Kiểm tra kênh
  YouTube (dub video mới)" và "📡 Kiểm tra bộ truyện chữ (tải chương mới)" — đêm 2h tự quét
  kênh/bộ truyện đã lưu trong 2 dialog 📡 (phần kiểm tra được tách khỏi dialog thành hàm
  gọi thẳng được).
- **📋 Dán SRT từ clipboard** — nút mới trang SRT: copy nguyên nội dung SRT từ web/mail/chat
  rồi bấm 1 nút — tự ghi file `clip_<stamp>.srt` vào thư mục cấu hình và nạp luôn, khỏi tự
  tạo file. Nội dung không giống SRT (không có `-->`) thì từ chối có hướng dẫn.
- **🎧 Audio song ngữ (học tiếng)** — nút mới cạnh 🔗 Gộp/✂ Tách (trang Dịch): từ SRT song
  ngữ sinh chuỗi "câu gốc → câu dịch" (tùy chọn: giọng riêng cho câu gốc bằng hồ sơ Edge qua
  tag [giọng:], thứ tự dịch-trước, đọc lại câu gốc lần 2) nạp vào pipeline Đọc tài liệu —
  Merge với "Nghỉ giữa đoạn" ~800–1200ms là ra mp3 luyện nghe.
- **📁 Phiên âm cả thư mục audio** — nút mới dưới hàng Video STT (trang Tách phụ đề): chọn 1
  thư mục audio/video → chạy STT tuần tự từng file, SRT+TXT đặt cạnh từng file; resume theo
  file (đã có `_stt.srt` thì bỏ qua); có ⏹ riêng — dành cho kho ghi âm/podcast.
- **🧾 Ghi lệnh ffmpeg khi lỗi** — 4 job lớn (Merge SRT, Ghép Audio→Video, Nén video,
  Audio→Video) khi ffmpeg lỗi giờ ghi NGUYÊN lệnh vào file log (`[FFMPEG-CMD]`) — gửi 🐞 Gói
  hỗ trợ là debug được ngay, không phải dựng lại lệnh bằng tay.
- **📈 Sparkline tốc độ trên Dashboard** — thẻ "Lịch sử tốc độ" (khu Chẩn đoán) vẽ thêm biểu
  đồ mini: mỗi batch 1 điểm giây/dòng theo engine (thấp = nhanh) — nhìn phát biết máy đang
  chậm dần (throttle nhiệt/chạy nền). Dữ liệu lưu qua phiên trong ui_prefs.
- **💾 Tự sao lưu cấu hình hàng tuần** — mỗi lần thoát app, nếu bản backup gần nhất >7 ngày:
  tự zip hồ sơ giọng/từ điển/ui_prefs... vào `<config>\backup\cfg_<stamp>.zip` (giữ 5 bản
  mới nhất) — lỡ tay xóa hồ sơ giọng thì 📥 Nhập gói cấu hình chọn file này là xong.
- **🎯 Chấm điểm audio mẫu** — nút 🎯 mới cạnh 🎙/🎬 trên 4 hàng Audio mẫu (VoxCPM/VieNeu/
  F5-TTS/OmniVoice): đo file mẫu (thời lượng, âm lượng, clipping, khoảng lặng, sample rate)
  → điểm /100 + gợi ý sửa cụ thể ("quá dài — cắt 8–15s", "nhiều lặng — cắt đoạn im"...) —
  chặn ca "clone cả đêm bằng mẫu tệ" trước khi bấm chạy.
- **📊 So 2 bản final (A/B)** — nút mới trang SRT: liệt kê các bản final trong Output (bật
  "🗂 Giữ final cũ" là có nhiều bản), chọn A + B + mốc thời gian → nghe cùng 1 đoạn của 2
  bản + xem loudness — "bản mới có hay hơn không" trả lời bằng tai trong 30 giây.
- **📱 Theo dõi qua LAN** — checkbox mới trang Hệ thống: mở trang web mini (chỉ xem) hiện
  tiến độ % + trạng thái + thống kê batch + FAIL + log gần đây, tự làm mới 5s — nằm giường
  mở điện thoại (cùng wifi) xem batch đêm chạy tới đâu. Tắt app/bỏ tick là đóng cổng;
  không lưu qua phiên.
- **↩ Hoàn tác đọc lại** — nút mới trong 📝 Bảng phụ đề: TRÁO bản audio hiện tại ↔ bản
  `.old.mp3` (backup tự động mỗi lần đọc lại) — nghe cả 2 bản rồi giữ bản ưng, bấm lần
  nữa là đổi ngược.
- **🔗 Gộp / ✂ Tách SRT song ngữ** — 2 nút mới trang Dịch: gộp SRT gốc + SRT dịch (từ 2
  nguồn bất kỳ) thành 1 file `gốc\dịch` để học tiếng/soát/burn 2 dòng; và tách file song
  ngữ thành 2 file đơn ngữ (file đơn mới TTS sạch được).
- **🗣 Xuất tag [giọng:] từ luật phân vai** — nút mới trong dialog 🎭 Phân vai: bake luật
  thành tag `[giọng:hồ_sơ]` đầu mỗi dòng → `<tên>_cast.srt` — SRT tự chứa casting (gửi máy
  khác không mất), và chạy batch TTS thường (nhanh, có cache + 4 luồng) thay vì chạy lồng
  tiếng phân vai chậm. Chỉ hồ sơ Edge (giới hạn của tag); luật chỉ-rate/pitch được báo bỏ qua.
- **🔢 Đọc số La Mã + đơn vị đo** — "Chương IV" → "Chương 4" (hết đọc "i-vê"), "5km" →
  "5 ki-lô-mét", "60km/h", "20°C" → "độ xê", "50%" → "phần trăm", kg/cm/mm/mg/ml — nằm
  trong checkbox "Đọc số kiểu Việt" sẵn có; chỉ nhận La Mã VIẾT HOA sau chữ Chương/Phần/
  Tập/... nên không đụng chữ thường.
- **🧹 Dọn cache dịch** — 🧹 Dọn dẹp thêm nhóm "Cache bản dịch (translate_cache.json)".
- **⏰ Hẹn giờ chạy đêm** — nút mới trên toolbar Bảng điều khiển: đặt giờ (vd 01:00) + hành
  động (Đọc TTS / Đọc Doc / 🚀 chuỗi truyện) → đến giờ app tự chạy (đang bận thì dời 5 phút
  thử lại). Kết hợp ☕ chống sleep sẵn có + 🌙 tắt máy = pipeline đêm trọn gói. App phải để
  mở; tắt app = hủy hẹn (cố ý không lưu qua phiên).
- **🧨 Webhook báo LỖI (không chỉ báo xong)** — webhook giờ bắn cả khi: batch xong nhưng có
  dòng FAIL, chuỗi 🚀 truyện lỗi/chết giữa chừng, lồng tiếng tự động dừng/lỗi, dịch SRT lỗi
  — đang ngủ biết ngay job chết lúc 2h sáng thay vì sáng dậy mới thấy trắng tay.
- **🔖 Dịch tài liệu resume được** — nhờ 💾 cache dịch: dịch dở bị Dừng/crash thì chạy lại
  cùng file, các câu đã dịch lấy từ cache (log `♻ ... coi như RESUME`), chỉ tốn API phần
  còn thiếu.
- **🈶 Từ điển tự học tên riêng từ bản dịch** — dịch SRT xong, app quét các tên riêng lặp
  ≥3 lần được bản dịch giữ nguyên (chưa có trong từ điển) → hỏi 1 phát "thêm N tên vào 📖?"
  — series dài giữ tên nhân vật nhất quán giữa các tập mà không phải tự soạn glossary.
- **🗂 Gắn phụ đề mềm (nhiều ngôn ngữ)** — card mới trang Video: nhét 1+ file SRT vào video
  thành các TRACK phụ đề bật/tắt được trong player (gốc + Việt + Anh trong 1 file) — không
  re-encode (`-c copy`), ra gần như tức thì; nhãn ngôn ngữ tự đoán từ đuôi tên file
  (`_vi`/`_en`...).
- **🎬 Cắt highlight / teaser** — card mới trang Video: nhập các mốc `mm:ss-mm:ss` → cắt và
  nối thành 1 clip ngắn từ video thành phẩm (không re-encode, mốc bám keyframe) — làm
  teaser/Shorts trong chục giây.
- **🧮 Ước khối lượng trước khi dịch** — mọi lần dịch giờ log trước "N dòng, ≈X ký tự,
  ~M lượt gọi API" (đã trừ phần lấy từ cache) — bấm dịch bộ 500 chương biết trước tốn
  bao nhiêu call.
- **💾 Cache bản dịch (đĩa)** — câu đã dịch được nhớ lại theo (provider, model, ngôn ngữ
  đích, ngữ cảnh, glossary): phim bộ/truyện dài lặp thoại y hệt ("Vâng", "Cảm ơn"...) khỏi
  trả tiền API lần 2; dịch LẠI một file sau khi sửa vài dòng gần như miễn phí. Bền qua phiên
  (`translate_cache.json` cạnh settings.json, trần 50k câu); dòng dịch hỏng không bị cache.
- **⚡ Dịch song song 3 luồng (cloud)** — các batch 40 dòng giờ gọi API 3 luồng cùng lúc
  (Claude/Gemini/OpenAI/Groq/DeepSeek): SRT 2000 dòng dịch nhanh gần gấp 3. Tạm dừng/Dừng
  hẳn vẫn ăn; thứ tự dòng giữ nguyên; dùng chung xoay key 🔑. Offline giữ tuần tự như cũ.
- **🗣 Tag đổi giọng theo dòng `[giọng:tên_hồ_sơ]`** — dòng SRT/đoạn văn bắt đầu bằng
  `[giọng:nam_tre]` sẽ đọc bằng giọng (voice+rate+pitch) của HỒ SƠ GIỌNG tên đó — casting lẻ
  1-2 câu thoại mà không cần mở 🎭 Phân vai. Chỉ hỗ trợ hồ sơ Edge TTS khi đang dùng Edge
  (engine local/RVC vẫn là việc của 🎭); engine khác tự bỏ tag, không đọc thành tiếng.
  Alias không dấu `[giong:]`/`[voice:]`; đứng TRƯỚC tag cảm xúc nếu dùng cả hai.
- **📜 Xuất phụ đề khớp audiobook (+.srt)** — checkbox mới hàng Merge Audio (tài liệu/truyện):
  xuất kèm `pdf_output_*.srt` mỗi đoạn 1 cue, mốc khớp CHÍNH XÁC file final (tính cả nghỉ
  giữa đoạn, hiệu ứng [sfx:], nhạc hiệu intro, tốc độ 🎚) — đưa vào 🖼 Audio→Video (kể cả
  🎤 karaoke) là có video truyện chữ chạy phụ đề.
- **🪞 Soát dịch cạnh gốc (2 cột)** — nút mới trang Dịch: chọn SRT gốc (tự đoán `_vi.srt`
  cạnh nó) → bảng 2 cột gốc | dịch, sửa cột dịch tại chỗ (có Telex), ▶ nghe audio dòng đó,
  💾 lưu đè file dịch (tự backup `.bak`); file dịch đang nạp trong app thì nạp lại + mời
  xóa audio các dòng đã sửa.
- **☕ Chống Windows ngủ khi đang chạy job** — có job chạy (TTS/dub/truyện/queue/RVC...) thì
  app tự giữ máy KHÔNG sleep (màn hình vẫn được tắt), xong job trả lại bình thường — batch
  đêm không còn chết vì máy tự ngủ sau 30 phút, khỏi chỉnh Power Options.
- **🔇 Im lặng 23h–7h** — checkbox mới trang Hệ thống: trong khung giờ đêm không phát âm báo
  (pháo hoa, error.wav, tiếng báo xong) — máy chạy đêm phòng ngủ khỏi giật mình; webhook +
  toast vẫn báo đủ.
- **🔑 Xoay vòng nhiều API key dịch** — ô API key (Claude/Gemini/OpenAI/Groq/DeepSeek) cho
  phép dán NHIỀU key cách nhau `;`: dính lỗi hạn mức (429/quota) tự chuyển key kế và chạy
  tiếp (nhớ key đang chạy tốt), lỗi khác vẫn báo ngay. Mọi tính năng dùng AI (dịch, casting,
  sửa SRT/OCR, hỏi AI...) hưởng chung — bộ nghìn chương không còn chết lúc 2h sáng vì 1 key
  hết hạn mức.
- **🪶 Xuất thêm .opus nhẹ** — checkbox mới hàng Merge Audio: audiobook xuất kèm bản `.opus`
  32k (giọng nói nghe tương đương mp3 128k, nhẹ ~1/4) — áp cho Merge tài liệu + chuỗi 🚀
  truyện chữ + 📡 watch.
- **📚 Mẫu ngữ cảnh dịch** — dropdown + 💾/🗑 cạnh ô "Ngữ cảnh/xưng hô": lưu các mẫu có tên
  ("tu tiên ta-ngươi", "tình cảm anh-em"...) chọn lại 1 phát thay vì gõ mỗi lần — đòn bẩy
  chất lượng dịch lớn nhất giờ dùng được tử tế; `context_presets.json` nằm trong 📦 gói
  cấu hình.
- **⏱ Chống treo (watchdog)** — đang chạy job mà tiến độ đứng im quá 10 phút (ffmpeg/helper
  đơ, mạng nghẽn) → cảnh báo logbox + bắn webhook (1 lần mỗi đợt treo); checkbox mới trang
  Hệ thống "⏱ Tự Dừng khi treo 10'" → tự bấm Dừng để watch/queue chạy việc kế thay vì đứng
  hình tới sáng.
- **🔁 Tải lại chương lỗi** — nút mới trên card Truyện chữ: chọn thư mục bộ → xóa các chương
  ngắn bất thường rồi tải bù (URL nguồn đọc từ `nguon.txt` tự ghi khi tải — bộ cũ thì lấy từ
  ô URL). Khép vòng với 🕳 soát chương.
- **📖 Từ điển phát âm THEO BỘ truyện** — đặt `glossary_series.json` (term → cách đọc) trong
  thư mục bộ: chuỗi 🚀/📡 tự nạp khi đọc bộ đó (đè từ điển chung khi trùng term), tự gỡ khi
  xong — "Ryu" mỗi bộ đọc một kiểu không còn giẫm nhau.
- **🎧 Nghe theo chương** — nút mới card Truyện chữ: liệt kê mp3 chương trong `audio_chap\`
  với ▶ từng chương (tựa lấy từ dòng đầu file chương), khỏi mò Explorer.
- **🌐 Trang nghe cả bộ (HTML)** — nút mới card Truyện chữ: `player_book.html` trong
  audio_chap — danh sách chương, click phát, hết chương tự chuyển chương sau (offline).
- **Đọc TXT mã hóa lạ (GBK/Shift-JIS/Big5/CP949)** — raw truyện Trung/Nhật/Hàn không phải
  UTF-8 giờ tự nhận diện bảng mã đúng (chấm điểm ký tự CJK/kana/hangul thật) thay vì ra
  mojibake mà TTS đọc thành rác. UTF-8/UTF-16/cp1258 như cũ.
- **🌧 Hiệu ứng NỀN `[sfxbg:tên]`** — trong tài liệu (Merge Audio): dòng riêng `[sfxbg:mưa]`
  bật ambience loop DƯỚI giọng đọc từ vị trí đó tới `[sfxbg:off]` (hoặc hết audio), fade
  in/out, tối đa 8 đoạn — kết hợp `[sfx:]` chèn tiếng động là thành audio drama. File lấy
  từ thư mục `sfx\` như [sfx:].
- **🆕 "Có gì mới"** — sau khi cập nhật bản mới, lần mở đầu tiên app hiện phần đầu CHANGELOG
  (đọc 1 lần, bấm Đã đọc là thôi) — tính năng mới không còn nằm im không ai biết.
- **⬇🚀 Tải/chạy NHIỀU bộ truyện 1 lần** — ô URL truyện chữ nhận nhiều link (cách nhau `;`
  hoặc khoảng trắng): nút ⬇ tải tuần tự từng bộ; nút 🚀 chạy cả chuỗi (tải → dịch → đọc →
  audiobook) tuần tự từng bộ — "nạp 5 bộ rồi đi ngủ". Bộ bị dừng/hủy → ngưng cả hàng; bộ lỗi
  → chạy tiếp bộ sau; 🌙 tắt máy chỉ khi chạy hết.
- **🕳 Soát chương thiếu/lỗi** — sau mỗi lần tải truyện tự quét: lỗ hổng số thứ tự chương
  (…998 rồi nhảy 1000) + chương ngắn bất thường (<300 byte — tải lỗi/trang trắng) → báo danh
  sách để chạy lại tải bù. Chương lẻ (10.5) và bản dịch `_vi` được tính đúng.
- **🎵 Nhạc nền ĐỔI THEO CHƯƠNG** — ô Nhạc nền (chuỗi 🚀 truyện chữ) nhận THƯ MỤC nhạc: mỗi
  chương mix 1 bài xoay vòng (trộn lúc đóng chương — re-run rẻ, chương cũ giữ nguyên) —
  truyện 10 tiếng đỡ nghe 1 bài loop. Merge tài liệu thường gặp thư mục thì dùng bài đầu.
- **🩺 Hỏi AI vì sao lỗi** — nút mới trang Hệ thống: gửi ~40 dòng log gần nhất (đường dẫn cá
  nhân đã ẩn) cho AI dịch-provider → chẩn đoán tiếng Việt (nguyên nhân + cách sửa từng bước)
  hiện trong cửa sổ riêng — user tự cứu mình trước khi phải gửi 🐞 Gói hỗ trợ.
- **🗂 Giữ bản final cũ** — checkbox mới cạnh tùy chọn Merge: merge lại không ghi đè —
  bản cũ tự đổi tên `final_YYYYmmdd_HHMMSS.*` để so sánh trước/sau khi regen vài dòng.
- **🎴 Xuất thẻ Anki (học ngoại ngữ)** — nút mới trang SRT: từ SRT (bản dịch SONG NGỮ càng
  tốt) + audio từng dòng có sẵn → `anki_deck\deck.txt` + thư mục media (tên file duy nhất,
  không đụng collection.media) + hướng dẫn import — mỗi câu 1 thẻ có phát âm.
- **🎭 Nhịp đọc theo dấu câu** — checkbox mới tab Giọng nói (mặc định tắt, Edge): câu kết `!`
  đọc nhanh hơn chút, câu bỏ lửng `...` đọc chậm lại — bản heuristic miễn phí của 🎭 Tự gắn
  cảm xúc AI; tag tường minh `[vui]`… luôn thắng; cache dòng trùng tách chế độ bật/tắt.
- **📁 Dịch cả thư mục** — nút mới trang Dịch: chọn thư mục → dịch tuần tự mọi `.txt/.docx`
  bên trong sang tiếng Việt ("thả 50 chương docx vào là đi ngủ"). Resume theo file (đã có
  `_vi.*` thì skip, kể cả khi đã đổi định dạng ra); tự bỏ qua file phụ của app
  (`*_vi`, `*_full`, youtube_description, podcast_script); lỗi 1 file chạy tiếp file sau;
  Pause/Stop dùng chung với các nút Dịch; có xác nhận chi phí trước khi chạy.
- **🌐 Câu ngoại ngữ tự đổi giọng (Edge)** — checkbox mới tab Giọng nói (mặc định tắt):
  truyện Việt chêm nguyên câu thoại tiếng Anh/Trung/Nhật/Hàn/Nga/Thái → câu đó tự đọc bằng
  voice Edge tương ứng thay vì giọng Việt đọc "bồi". Chỉ đổi khi CẢ CÂU là ngoại ngữ (câu
  Việt chêm vài từ Anh giữ nguyên giọng), chỉ với Edge + giọng vi-*; cache dòng trùng tự
  phân biệt chế độ bật/tắt nên không dùng nhầm audio cũ.
- **🎭 Đổi giọng file audio (RVC)** — card mới trang Text → Audio: convert giọng file audio
  CÓ SẴN (final/audiobook, chọn nhiều file được) sang giọng model RVC đang cấu hình ở panel
  RVC — không TTS lại, không tốn API. File dài tự chia đoạn 10 phút để convert (chặn
  RAM/timeout) rồi nối lại → `<tên>_rvc.mp3`.
- **🧹 Luật lọc text (regex)** — nút mới cạnh 📖 Từ điển phát âm: soạn các luật
  `pattern => thay_thế` (regex, hỗ trợ ^$ theo dòng, (?i)) XÓA/THAY rác trước khi TTS đọc —
  ghi chú người dịch `[TN: ...]`, footer "Đọc tiếp tại...", watermark nhóm dịch. Có nút 🧪
  thử trên câu mẫu; luật hỏng bị bỏ qua có báo; lưu `text_rules.json` (có trong 📦 gói cấu
  hình). Chỉ ảnh hưởng text đưa vào TTS — file gốc/bản dịch giữ nguyên.
- **🎞 Nền video loop + 🖼 Slideshow theo chương (Audio → Video)** — ô Nền giờ nhận: ảnh
  (như cũ), file VIDEO (loop làm nền động — mưa rơi/lò sưởi), hoặc THƯ MỤC ảnh → slideshow
  tự đổi ảnh đúng MỐC CHƯƠNG của audio (đọc chapter nhúng trong .m4b hoặc
  `youtube_description.txt` cạnh file; không có mốc thì chia đều). Ảnh được scale sẵn khớp
  khung; kết hợp được với 🌊 sóng/🏷 logo/🎤 karaoke.
- **🖱 Kéo-thả mở rộng** — thả vào cửa sổ app: `.txt/.epub/.docx` → nạp Đọc (TTS);
  audio (nhiều file được) → điền Audio → Video; video (nhiều file được) → mở wizard 🎬 Lồng
  tiếng đã điền sẵn; `.lrc` → ô Phụ đề Audio → Video. Phụ đề như cũ.
- **🌐 Trang nghe (HTML)** — nút mới trang SRT: xuất `player.html` cạnh final.mp3 — trình
  phát + toàn bộ transcript, câu đang phát tự sáng và cuộn theo, click câu để tua (đọc
  `final_synced.srt`, JS thuần không cần mạng/server). Gửi cho người khác = gửi 2 file cùng
  thư mục.
- **💾 Tự lưu phiên mỗi 60 giây** — app/máy sập giữa batch đêm thì `session.json` vẫn mới;
  mở lại app bấm ↩ Khôi phục là về đúng file + output + giọng đang dùng.
- **🩹 Sửa lỗi OCR bằng AI** — nút mới trên card 📷 Ảnh scan sách: gửi text OCR (vd
  `sach_ocr.txt`) qua AI dịch-provider (Claude/Gemini/OpenAI/Groq/DeepSeek) với chỉ dẫn
  "chỉ sửa lỗi nhận dạng, giữ nguyên nội dung" — sai dấu, từ dính/tách, dấu câu vỡ, 0↔O
  được dọn sạch trước khi đốt giờ TTS. Có xác nhận chi phí trước khi gửi; cụm lỗi API hoặc
  bị AI trả về lệch độ dài quá 30% (dấu hiệu tóm tắt bậy) tự giữ nguyên gốc — không bao giờ
  mất nội dung; heading "Chương N" giữ nguyên nên mục lục .m4b không ảnh hưởng. Kết quả ra
  `<tên>_fixed.txt` + hỏi nạp thẳng vào Đọc (TTS). ⏹ của card dừng được giữa chừng (phần đã
  sửa vẫn lưu).
- **📊 RAM/VRAM live trên Bảng điều khiển** — thẻ Tiến trình job có dòng "RAM / VRAM" mới,
  cập nhật mỗi 2s: % RAM hệ thống (psutil, fallback ctypes) + VRAM/GPU util qua nvidia-smi
  (đo trên thread nền, không chặn UI; máy không có GPU NVIDIA chỉ hiện RAM) — bắt sớm các
  vụ tràn RAM/VRAM (lip-sync, local TTS) ngay khi job đang chạy.
- **🎚 Tốc độ đọc audiobook (hậu kỳ)** — ô "🎚 Tốc độ ×" mới trên hàng Merge Audio (trang Tài
  liệu, mặc định 1.0): áp `atempo` lên file final SAU khi merge (giữ nguyên cao độ giọng) —
  các engine local (VoxCPM/VieNeu/F5/OmniVoice) vốn không chỉnh được tốc độ giờ cũng ra
  audiobook 1.1–1.25× được. Áp cho cả Merge Audio tài liệu lẫn chuỗi 🚀 truyện chữ + 📡 watch;
  mốc chương `.m4b` và mục lục YouTube tự chia lại theo hệ số nên tua chương vẫn đúng.
- **📋 Dán & đọc** — nút mới trên trang Text → Audio: dán thẳng nội dung clipboard vào ô văn
  bản và đọc luôn — copy text ở bất kỳ đâu (web/Word/chat) là 1 nút nghe được.
- **🎵 Tách audio khỏi video** — card mới trang Tách Nội Dung: chọn 1 hoặc nhiều video → xuất
  file MP3/WAV/M4A cạnh video (tách loạt được, có nút ⏹ riêng).
- **📻 Thư viện SFX** — nút mới cạnh hàng Merge Audio (trang Tài liệu): liệt kê các file trong
  thư mục `sfx\` với ▶ nghe thử và 📋 copy sẵn tag `[sfx:tên]`; kèm nút mở thư mục (tự tạo
  lần đầu) — khỏi phải nhớ tên file khi soạn tài liệu.
- **📖 Xuất EPUB** — nút mới trên card Tải truyện chữ: đóng gói các `chuong_*.txt` đã tải
  (hoặc bản dịch `_vi` — có cả hai thì hỏi chọn) thành sách điện tử `.epub` có mục lục chương,
  đọc trên điện thoại/máy đọc sách. Thuần stdlib, không thêm thư viện.
- **🎬 Intro/Outro video** — 2 ô mới trên card Audio → Video: nối clip hiệu kênh vào đầu/cuối
  video thành phẩm (tự scale khớp khung, clip không có tiếng tự chèn track lặng); video từ
  wizard 🎬 Lồng tiếng cũng được nối chung 2 ô này. Video chính không phải h264+aac thì bỏ
  qua an toàn.
- **📂 Watch folder nhận .txt/.epub** — thả file truyện/tài liệu vào thư mục theo dõi → tự đọc
  TTS + Merge thành audiobook trong `<tên>_audiobook\` (theo tùy chọn m4b/nghỉ/nhạc nền hiện
  tại); marker hoàn tất = file output tồn tại, sống sót restart như SRT/video.
- **📄 PDF scan → OCR → Đọc** — card 📷 Ảnh scan sách nhận thêm FILE PDF scan (mỗi trang là
  ảnh): nút 📄 mới tách ảnh từng trang bằng pypdf rồi đi qua đúng đường OCR → `sach_ocr.txt`
  → Đọc (TTS). PDF chữ vẫn dùng Load PDF thường.
- **✂ SponsorBlock khi tải YouTube** — checkbox mới trong card 📺 của wizard 🎬: cắt luôn các
  đoạn quảng cáo/tự quảng bá/xin like-sub/intro-outro (dữ liệu cộng đồng SponsorBlock) ngay
  khi tải — không tốn tiền dịch + TTS cho đoạn rác. Khi bật, chuỗi tự bỏ lối tắt "phụ đề có
  sẵn" (timestamp lệch sau khi cắt) và STT trên video đã cắt.
- **⬆ Cập nhật yt-dlp** — nút mới (trang Hệ thống): tự chạy `yt-dlp -U` (bản exe) hoặc
  `pip install -U yt-dlp` vào đúng env (bản module) rồi báo phiên bản mới; khi tải YouTube
  lỗi kiểu "Unable to extract..." log tự gợi ý bấm nút này (YouTube đổi API thường xuyên).
- **🔊 Tag hiệu ứng âm thanh `[sfx:tên]`** — trong tài liệu/truyện (TXT/docx/EPUB/truyện chữ),
  một dòng riêng dạng `[sfx:mưa]` sẽ chèn file âm thanh `mưa.mp3/wav/...` từ thư mục `sfx\`
  (cạnh settings.json hoặc cạnh exe) vào đúng vị trí khi Merge Audio thay vì đọc — truyện
  audio thành audio drama (gõ cửa, sấm, bước chân...). Mọi engine TTS tự bỏ qua tag; thiếu
  file chỉ cảnh báo, mốc chương .m4b vẫn đúng.
- **🏷 Logo kênh** — ô Logo mới trên card 🖼 Audio → Video: PNG logo đè góc phải trên mọi
  video xuất từ card này (cả chế độ 🌊 sóng nhạc), và tự áp luôn cho bước gắn phụ đề cứng
  của Ghép Audio → Video / wizard lồng tiếng (chỉ khi re-encode — mux thường vẫn giữ tốc độ
  copy). Logo tự scale ~14% bề ngang khung.
- **🎼 Lời bài hát .lrc → video karaoke** — ô Phụ đề của Audio → Video nhận thêm file `.lrc`
  (lời nhạc có mốc thời gian tải trên mạng, hỗ trợ cả enhanced LRC): tự chuyển thành SRT
  theo mốc trong file, kết hợp checkbox 🎤 Karaoke sẵn có → video lyric chữ chạy theo nhạc
  từ 1 file nhạc + 1 file lời. Chế độ loạt cũng tự ghép `<tên audio>.lrc` cạnh file.
- **📖 Wikipedia → Audio** — card 📰 (trang Tài liệu) nhận thêm link bài Wikipedia (mọi ngôn ngữ,
  cả bản mobile): lấy nội dung qua API chính chủ (không scrape HTML), mỗi mục lớn thành
  "Phần i: <tên mục>" → Merge với `.m4b có chương` cho mục lục tua theo mục; tự bỏ các mục
  Tham khảo/Liên kết ngoài/Xem thêm. ☕ Bản tin (1 nút) cũng dùng được link Wikipedia.
- **📷 Ảnh chụp / scan sách → Đọc (OCR)** — card mới ở trang Tài liệu: chọn thư mục ảnh chụp
  trang sách → nhận dạng chữ bằng EasyOCR (tái dùng voxcpm_env + manga_ocr_helper, thêm
  tiếng Việt), block xếp theo thứ tự đọc, text lưu ra `sach_ocr.txt` để dò lỗi rồi nạp thẳng
  vào pipeline Đọc (TTS). Thư mục chứa nhiều thư mục con = mỗi thư mục 1 chương → audiobook
  `.m4b` có mục lục.
- **📝 Dùng phụ đề có sẵn của YouTube** — checkbox mới trong card 📺 của wizard 🎬 Lồng tiếng
  (mặc định bật): video YouTube có phụ đề (người làm hoặc auto-caption) thì tải phụ đề đó
  thay vì chạy STT Whisper — nhanh và thường chính xác hơn. Ưu tiên sub người làm đúng
  ngôn ngữ gốc video; auto-caption được tự khử lặp kiểu cuộn; video không có sub phù hợp
  thì tự quay về STT như cũ. 📡 Theo dõi kênh hưởng chung.
- **🧹 Dọn dẹp file tạm** — nút mới (trang Hệ thống): quét 6 nhóm file app sinh ra (nghe thử
  %TEMP%, log phiên cũ, backup regen `.old.mp3` + take thử, audio lỗi QC, cache TTS, bản ghi
  âm mẫu) kèm số file + dung lượng từng nhóm, xóa nhóm được tick. Bản ghi âm mà hồ sơ giọng
  đang dùng được tự động giữ lại; log luôn giữ 2 file mới nhất.
- **🖱 Kéo-thả & chuột phải mở file** — kéo file `.srt`/`.ass`/`.vtt` từ Explorer thả thẳng vào
  cửa sổ app là tự nạp + nhảy sang trang TTS; thêm tùy chọn "🖱 Chuột phải" (trang Hệ thống)
  đăng ký menu chuột phải Windows "Mở bằng SRT TTS Studio" cho file `.srt`. Kèm card 📖 Truyện
  chữ mới trên Bảng điều khiển (số bộ theo dõi + tùy chọn đang bật) và thẻ "📖 truyện chữ →
  audiobook" trong 🚀 Bắt đầu nhanh.
- **📈 Thống kê sản lượng** — nút "📈 Sản lượng" mới (trang Hệ thống): bảng theo tháng cộng dồn
  số giờ audio, số chương audiobook và số video đã tạo (`production_stats.json`) — tự cập nhật
  ở các mốc hoàn tất (đóng chương truyện, Merge tài liệu, Audio→Video).
- **🌊 Soát sóng + phụ đề** — nút mới ở trang SRT: vẽ dạng sóng của file audio (kể cả file dài
  10 tiếng) kèm vạch mốc bắt đầu từng dòng phụ đề — nhìn ra ngay chỗ mất tiếng, chồng giọng
  hay lệch mà không cần nghe hết; click lên sóng để ▶ nghe 10 giây tại đúng điểm đó.
- **🔍 Soát bản dịch (dịch ngược)** — nút mới ở trang Dịch: dịch ngược bản `_vi.srt` về ngôn ngữ
  gốc rồi so với câu gốc, xuất `<tên>_backcheck.txt` liệt kê các dòng nghi dịch sai/lệch nghĩa
  (kèm GỐC/DỊCH/NGƯỢC). Cần nhà cung cấp dịch cloud.
- **🐞 Gói hỗ trợ** — nút mới (trang Hệ thống): đóng gói 2 log mới nhất + cấu hình UI + thông tin
  máy thành 1 file zip trên Desktop để gửi khi báo lỗi — **không kèm** API key/mật khẩu.
- **🖼 Audio → Video (ảnh nền)** — thẻ mới ở trang Video: ghép 1 file audio (+ ảnh nền tuỳ chọn
  + phụ đề burn tuỳ chọn) thành video mp4 — cho kênh "truyện audio" cần khung video để đăng
  YouTube. Kèm các tuỳ chọn: **🌊 Sóng nhạc động** (dải sóng chạy theo nhạc), **📐 Khung hình**
  16:9 / **9:16 (TikTok/Shorts)** / 1:1, và **🎬 chế độ loạt** (chọn nhiều audio → xuất hàng loạt
  video, mỗi audio tự ghép SRT cùng tên — khớp thẳng với `_pNN` của ✂ Chia final).
- **📰 Đọc bài báo / RSS → Audio** — card mới ở trang Tài liệu: dán link 1 bài báo
  (VnExpress/Dân Trí/Tuổi Trẻ…) hoặc link RSS → tự trích thân bài (bỏ menu/quảng cáo) → nạp vào
  pipeline đọc TTS; RSS lấy N bài mới nhất, mỗi bài thành một "chương" cho .m4b. Thêm nút
  **☕ Bản tin (1 nút)** làm trọn gói tải → đọc → ghép .m4b mục lục trong một lần bấm.
- **📑 Mục lục chương cho YouTube** — khi Merge tài liệu xuất `.m4b` có chương, tự tạo thêm
  `youtube_description.txt` (mỗi chương một dòng `MM:SS Tên`) — dán vào mô tả video là YouTube
  hiện chapter.
- **🔇 Cắt tại chỗ lặng khi ✂ Chia final** — tùy chọn (mặc định bật) dời mỗi mốc chia N phút về
  chỗ lặng gần nhất (±45s) để không cắt giữa câu; nếu có `final_synced.srt` cạnh audio thì file
  SRT chia kèm cũng khớp mốc mới.
- **🎵 Nhạc nền audiobook (Tài liệu)** — hàng "🎵 Nhạc nền" mới ở khu Merge Audio tài liệu: nhạc
  tự lặp dưới giọng đọc, cắt khi hết lời + fade 2s; áp cho cả chuỗi 🚀 truyện chữ.
- **🎭 Tag cảm xúc theo dòng** — thêm `[vui]` / `[buồn]` / `[giận]` / `[sợ]` / `[nhanh]` /
  `[chậm]` / `[thì thầm]` / `[hét]` vào đầu một dòng SRT hoặc đoạn text: **Edge TTS** tự đổi
  tốc độ/cao độ theo cảm xúc (cộng dồn lên rate/pitch đang đặt, có kẹp biên), **tag không bị
  đọc thành tiếng**. Hỗ trợ alias không dấu (`[buon]`/`[gian]`/`[thi tham]`…). Engine local
  (VoxCPM/VieNeu/F5/Omni) chỉ bỏ tag khỏi text (không có rate/pitch nên giọng không đổi).
- **🖼 Gói xuất bản audiobook** — ô "🖼 Ảnh bìa" mới trong card truyện chữ: sau khi ghép
  audiobook, tự **nhúng ID3** (album = tên truyện, artist = SRT TTS Studio, ảnh bìa) vào mp3 +
  tạo sẵn `thumbnail.png` 1280×720 (bìa cover-fit + tên truyện trên dải mờ; để trống = nền tối)
  — cùng `youtube_description.txt` là bộ file sẵn sàng upload.
- **🌐 Dịch thử 1 chương trước khi dịch cả bộ** — khi bật dịch cho bộ ≥5 chương, chuỗi 🚀 dịch
  thử đúng 1 chương rồi hiện 400 ký tự đầu để duyệt: Đồng ý → dịch tiếp; Từ chối → xóa bản thử
  (đổi engine/model chạy lại sẽ dịch lại) — tránh dịch nhầm engine cả nghìn chương. Watch tự
  động không hỏi.
- **🌐 Dịch truyện chữ nước ngoài → Việt trước khi đọc** — ô "Dịch sang tiếng Việt trước
  khi đọc" mới trong card 📖 Tải truyện chữ: chuỗi 🚀 Tải → Đọc → Audiobook giờ chèn thêm
  pha dịch từng chương (`chuong_NNNNN_vi.txt`) bằng đúng engine dịch đang chọn
  (Claude/Gemini/OpenAI/Groq/DeepSeek hoặc Offline NLLB — chạy đêm miễn phí), rồi mới đọc
  bản dịch → xuất **bộ audio `_vi` riêng** (tách hẳn bản gốc). Resume theo chương: dừng
  giữa chừng chạy lại không tốn lại API. Trong 📡 Theo dõi bộ truyện, thêm ` | dich` sau URL
  để bộ đó tự dịch rồi đọc.
- **🎤 Giọng riêng từng bộ khi Theo dõi truyện** — mỗi dòng watch có thể ghi ` | tên hồ sơ giọng`
  sau URL: chương mới của bộ đó được đọc bằng đúng hồ sơ giọng chỉ định, xong tự khôi phục
  giọng ban đầu — theo dõi nhiều bộ với giọng khác nhau không bị lẫn.
- **🎺 Nhạc hiệu Intro/Outro cho audiobook** — 2 ô "🎺 Intro / Outro" mới ở khu Merge Audio:
  chọn file nhạc hiệu đầu/cuối, nó tự khớp sample-rate/kênh rồi nối vào đầu & cuối audiobook;
  mốc chương `.m4b` tự dời theo độ dài intro (đoạn intro thành mục "Mở đầu"). Áp cho cả
  Merge Audio tài liệu lẫn chuỗi 🚀 truyện chữ. Để trống = tắt; nhớ qua phiên.
- **🔊 Chuẩn âm lượng audiobook (loudnorm)** — ô "Chuẩn âm lượng" mới cạnh tùy chọn m4b:
  chuẩn hoá về -16 LUFS (chuẩn YouTube), hữu ích khi trộn nhiều engine giọng local mỗi mức
  to nhỏ khác nhau. Thứ tự xử lý: loudnorm giọng → nhạc nền → nhạc hiệu → m4b.
- **🌙 Tắt máy khi xong** — ô mới trong card truyện chữ: chuỗi 🚀 và 📡 Theo dõi tự tắt máy
  sau 60 giây khi chạy xong (chỉ khi KHÔNG bị người dùng bấm dừng) — tiện để chạy bộ dài qua
  đêm. Hủy bằng lệnh `shutdown /a`. Không nhớ qua phiên (tránh bất ngờ lần sau).
- **⚡ Kịch bản 1-click** — dropdown mới trong card "Bật/tắt nhanh" (Bảng điều khiển):
  chọn Lồng tiếng phim / Truyện audio / Podcast là cả cụm tùy chọn (cắt lặng, loudnorm,
  cân âm lượng, định dạng ra, nghỉ giữa đoạn, m4b...) được set đúng một lượt;
  "↺ Mặc định" trả về như ban đầu. Giọng đọc không bị đụng.
- **✂ Chia final theo giờ** — nút mới ở trang SRT: chia file audio dài thành các phần
  N phút (mặc định 59 — vừa giới hạn upload) bằng stream-copy (không re-encode, chia
  gần như tức thì); nếu có `final_synced.srt` cạnh audio thì chia kèm SRT từng phần
  (timestamp tự dời về 0).
- **🚀 Bắt đầu nhanh** — nút mới trên thanh công cụ Bảng điều khiển cho người mới:
  chọn tình huống ("có SRT", "có video", "có link YouTube", "có PDF/Word", "muốn dịch",
  "gõ text thử giọng") → app mở đúng trang và in các bước làm vào ô log.
- **📚 Thư viện nhân vật series** — 🤖 Tự phân vai giờ nhớ "nhân vật nào giọng nào" vào
  `series_cast.json` cạnh file SRT (theo thư mục): làm phim bộ, các tập sau nhân vật quen
  tự giữ ĐÚNG giọng như tập trước — casting tập 2 trở đi gần như tự động và nhất quán cả bộ.
- **📡 Theo dõi kênh YouTube** — nút mới trong card YouTube của Trợ lý lồng tiếng: lưu danh
  sách kênh/playlist theo dõi, bấm "Kiểm tra & dub video mới" là liệt kê N video mới nhất
  mỗi kênh, bỏ qua video đã dub (nhận biết qua file `_dubbed.mp4` trong thư mục tải —
  sống sót qua restart), video mới tự vào hàng đợi lồng tiếng với tùy chọn wizard hiện tại.
- **🎵 Nhạc nền khi Merge FFmpeg** — ô "Nhạc nền" mới dưới các tùy chọn merge: chọn 1 file
  nhạc/ambience, nó tự lặp dưới giọng đọc (âm lượng chỉnh được, mặc định 0.12), tự cắt khi
  hết lời + fade-out 2 giây — truyện audio không còn "khô". Để trống = tắt; nhớ qua phiên.
- **📺 Dub cả playlist / kênh YouTube** — ô link YouTube của Trợ lý lồng tiếng giờ nhận
  luôn link playlist hoặc kênh (`/playlist?list=`, `/@tenkenh`, `/channel/`): tự liệt kê
  danh sách video (yt-dlp --flat-playlist, trần 100 video) rồi tải → dub tuần tự từng cái.
  Link video lẻ (kể cả có &list= kèm) vẫn chỉ dub đúng video đó như cũ.
- **☑ Tự soát đọc sai (STT) khi xong** — checkbox mới cạnh "Tự tạo lại dòng FAIL":
  batch SRT xong tự chạy 🎙🔍 Soát đọc sai; nếu auto-retry FAIL đang chạy thì chờ rảnh
  rồi mới soát (soát được luôn các dòng vừa retry). Chạy qua đêm sáng dậy có sẵn báo cáo.
  Có cả trong card "Bật/tắt nhanh" của Bảng điều khiển; được nhớ qua phiên.
- **🎨 Màu phân vai trong Bảng phụ đề** — khi SRT có luật phân vai, 📝 Bảng phụ đề thêm
  cột "Vai" và tô màu nền mỗi vai một màu — nhìn phát thấy ngay luật "từ dòng X đến Y"
  có lệch dòng không, khỏi phải nhớ số dòng trong đầu.
- **🎙🔍 Soát đọc sai bằng STT (round-trip QC)** — nút mới ở trang SRT: Whisper nghe lại
  toàn bộ audio đã tạo rồi so nội dung với text SRT — bắt các dòng đọc thiếu chữ/nuốt vế/
  đọc sai mà QC âm lượng-thời lượng không thấy. Kết quả mở cửa sổ từng dòng nghi sai
  kèm ▶ nghe / 🔁 đọc lại. (Cần voxcpm_env; model Whisper small, load 1 lần cho cả batch.)
- **🕘 Lịch sử job** — 30 batch gần nhất tự được ghi lại (file, output, thống kê, giọng);
  nút mới ở trang SRT mở danh sách: ↻ nạp lại nguyên cấu hình (SRT + output + giọng)
  để chạy tập tiếp theo của series, 📂 mở thư mục output cũ.
- **🎚 Phân vai theo tốc độ/cao độ (Edge)** — mỗi luật phân vai giờ có thêm 2 ô
  Tốc độ/Cao độ (vd `+20%` / `-3Hz`): cùng 1 giọng Edge nhưng mỗi nhân vật một nhịp —
  rẻ và nhanh hơn nhiều so với đổi hồ sơ/engine; chọn "(Giọng UI)" để chỉ chỉnh
  tốc độ/cao độ mà không đổi giọng (không cần tạo hồ sơ nào). Lưu kèm sidecar như cũ.
- **🎼 Tách nhạc nền khi ghép video (demucs)** — checkbox mới ở Mux (hiện khi "Giữ audio gốc"):
  bỏ hẳn lời thoại gốc, mix **nhạc nền sạch + giọng lồng tiếng** thay cho ducking —
  chất lượng "phim chiếu rạp". Tự fallback về ducking nếu máy thiếu voxcpm_env/model.
  Trợ lý lồng tiếng tự động dùng chung lựa chọn này.
- **⏸ Nghỉ giữa đoạn khi Merge Audio (Doc/PDF TTS)** — ô "Nghỉ giữa đoạn (ms)" (mặc định 300):
  chèn khoảng lặng giữa các đoạn để truyện audio nghe có nhịp thở tự nhiên; 0 = tắt.

- **🔍 Dub thử 60 giây đầu** — nút mới trong Trợ lý lồng tiếng: cắt 60s đầu video, chạy đủ
  5 bước trên clip rồi tự mở xem — duyệt giọng đọc/bản dịch/mix trước khi chạy full hàng giờ.
- **🎲 Gen 3 take, chọn bản ưng** — nút mới ở trang SRT: sinh 3 bản đọc khác nhau cho 1 dòng
  (TTS mỗi lần đọc một kiểu), nghe A/B/C rồi chọn; đóng không chọn thì bản cũ được khôi phục.

- **📶 Tự hồi phục khi rớt mạng giữa batch** — mất mạng lúc đang đọc (Edge/provider online)
  không còn dừng hẳn: phần mềm tự chờ mạng quay lại (tối đa 30 phút) rồi đọc tiếp —
  batch qua đêm / hàng đợi / watch folder sống sót qua các cú rớt mạng ngắn.
- **Đọc teencode/viết tắt chat** — "ko, dc, vs, mn, tks…" được đọc thành từ đầy đủ
  (chỉ từ viết thường nguyên chữ — "BT", "VS Code", "100k" không bị đụng; tắt được).
- **⚠ Cảnh báo giọng lệch ngôn ngữ** — Load SRT tiếng Anh khi đang chọn giọng tiếng Việt
  (hoặc ngược lại) sẽ được nhắc ngay, khỏi chạy cả nghìn dòng mới phát hiện.

- **Hỗ trợ phụ đề .ass / .ssa / .vtt** — Load SRT và Dịch SRT giờ nhận cả phụ đề anime/fansub
  (.ass) và YouTube (.vtt): tự chuyển sang SRT (bỏ tag định dạng) rồi chạy như thường.
- **🔊 Truyện tranh → truyện audio** — nút mới trên card Dịch truyện: nạp file script dịch
  (`_script_dich.txt`) vào pipeline Tài liệu → Audio, ra file đọc truyện chỉ với vài click.
- **🎙 Thu âm giọng mẫu ngay trong app** — nút 🎙 cạnh ô Audio mẫu của cả 4 engine nhân bản
  giọng: chọn micro, thu 3–120 giây (dừng sớm vẫn giữ phần đã thu), tự điền vào ô và nghe lại.

- **🎙 Podcast 2 giọng từ tài liệu (AI)** — kiểu NotebookLM: PDF/Word/EPUB/TXT → AI viết
  kịch bản hội thoại MC + chuyên gia → đọc bằng 2 hồ sơ giọng → tự ghép thành 1 file podcast.
  Kịch bản lưu .txt để xem/sửa; chạy lại là resume.

- **🔁 Tìm & thay trong SRT** — sửa hàng loạt (thường/regex, phân biệt hoa-thường), xem trước
  số dòng khớp, lưu `_edit.srt` và mời xóa audio các dòng bị đổi để đọc lại — sửa tên nhân vật
  dịch sai cả tập phim trong một phút.
- **Nhà cung cấp dịch giá rẻ: Groq & DeepSeek** — thêm 2 provider mới cho mọi tính năng LLM
  (dịch, rút gọn, phân vai AI, podcast); chi phí thấp hơn ~10–20 lần, Groq có gói miễn phí.

- **📋 Việc cần làm** — một bảng gộp mọi vấn đề còn tồn sau batch (dòng audio lỗi, dòng thiếu,
  dòng tràn khe) kèm nút xử lý ngay từng mục — khỏi phải nhớ 4 nút rời.
- **📚 Audiobook .m4b có chương** — Merge Audio (Tài liệu) có tùy chọn xuất thêm file .m4b
  với mốc chương tự nhận từ heading "Chương N…" — tua theo chương trên mọi player.

- **📝 Bảng phụ đề (sửa nhanh)** — toàn bộ SRT trong một cửa sổ dạng bảng: trạng thái từng
  dòng (lỗi timing, audio lỗi, đã có audio), sửa text, nghe, đọc lại từng dòng — không phải
  nhớ số dòng và bấm qua lại nhiều nút nữa.
- **📨 Webhook báo xong** — dán URL Discord/Telegram vào Cài đặt, mỗi job hoàn tất app tự
  nhắn (kèm số dòng, số FAIL) — batch qua đêm khỏi ngồi canh máy.

- **🪄 Sửa SRT bằng AI theo yêu cầu tùy ý** — gõ bất kỳ yêu cầu nào ("viết trang trọng hơn",
  "đổi xưng hô", "bỏ từ tục", "sửa chính tả") — AI áp dụng cho toàn bộ phụ đề, dòng không
  cần đổi giữ nguyên văn, không bao giờ mất nội dung.

### Cải tiến
- **🎨 Tùy chỉnh chữ phụ đề gắn cứng** — chọn cỡ (Nhỏ/Vừa/To) và màu (Trắng/Vàng/Xanh lá)
  ngay trong Trợ lý lồng tiếng; video đăng YouTube nhìn chuyên nghiệp hơn.
- **📖 Đọc từ đoạn X đến Y** (Tài liệu → Audio) — đọc riêng một chương của tài liệu dài
  không cần cắt file, áp dụng cho mọi engine.
- **💬 Chú thích nút (tooltip)** — rê chuột lên các nút chính sẽ hiện giải thích ngắn,
  người mới không phải đoán nghĩa các nút emoji.
- **🩺 Khám SRT / 🔧 Sửa SRT bắt dòng lặp** — phát hiện và tự gộp các cụm ≥3 dòng giống hệt
  liên tiếp (lỗi ảo giác của nhận dạng giọng nói) — hết cảnh TTS đọc lặp một câu 5 lần.
- **🎭 Luật phân vai được lưu kèm SRT** (`<tên>.cast.json`) — đóng app mở lại, Load đúng SRT
  là luật tự nạp về, công gán vai không mất.
- **Phân vai lai 🚻+🤖** — chạy 🚻 (đo giọng nam/nữ từ âm thanh) trước rồi 🤖 Tự phân vai:
  AI tách nhân vật theo lời thoại nhưng bám giới tính đo được → nhân vật nam không còn bị
  gán nhầm giọng nữ.
- **✂ Rút gọn AI** giờ hỏi phạm vi: chỉ dòng ❌ tràn khe, hoặc gồm cả dòng ⚠ hơi hẹp —
  chọn "Có" thì mọi dòng đọc ở tốc độ tự nhiên 1.0×, không dòng nào bị tăng tốc khi merge.
- **Merge timeline**: fade 30ms đầu/cuối từng dòng — hết tiếng "click/tạch" ở điểm nối
  giữa các câu sát nhau.
- **✂ Rút gọn AI (dòng tràn khe)** — nút mới ở trang SRT: dùng LLM dịch (Claude/Gemini/OpenAI)
  viết lại NGẮN HƠN các dòng phụ đề tràn khe thời gian (dài hơn khe dù merge tăng tốc 2×
  — nhóm lỗi mà 🔧 Sửa SRT tự động không xử lý được), giữ nguyên nghĩa và ngôn ngữ,
  xuất `<tên>_ai.srt` và tự nạp lại.
- **🚻 Phân vai Nam/Nữ theo âm thanh gốc** — nút mới trong bảng 🎭 Phân vai: đo cao độ giọng
  (F0) từng dòng trên audio gốc của video theo timestamp SRT, phân cụm tương đối trong chính
  video (cụm thấp = nam, cao = nữ) rồi tự gán 2 hồ sơ giọng nam/nữ thành luật phân vai —
  không cần API key, không thêm thư viện. Dòng sát biên kế thừa vai dòng trước; video chỉ có
  một giọng sẽ được báo thay vì gán bừa.

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
