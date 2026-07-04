# Changelog — SRT TTS Studio

Tất cả thay đổi đáng chú ý của phần mềm được ghi lại trong tệp này.
Định dạng dựa trên [Keep a Changelog](https://keepachangelog.com/vi/1.0.0/).

## [Chưa phát hành]

### Thêm mới
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
