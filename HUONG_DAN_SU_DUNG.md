# HƯỚNG DẪN SỬ DỤNG — SRT TTS Studio

Phần mềm chuyển phụ đề (SRT), PDF, Word, TXT thành giọng đọc (audio MP3), kèm bộ công cụ
lồng tiếng video, dịch thuật, nhân bản giọng nói và tải truyện. Tài liệu này dành cho người
dùng cuối — đọc theo thứ tự hoặc nhảy đến phần bạn cần ở Mục lục.

---

## Mục lục

1. [Cài đặt & Khởi động](#1-cài-đặt--khởi-động)
2. [Đăng nhập & Mật khẩu](#2-đăng-nhập--mật-khẩu)
3. [Tổng quan giao diện](#3-tổng-quan-giao-diện)
4. [Bảng điều khiển (Dashboard)](#4-bảng-điều-khiển-dashboard)
5. [Chuyển phụ đề SRT thành giọng đọc](#5-chuyển-phụ-đề-srt-thành-giọng-đọc)
6. [Đọc PDF / Word / TXT](#6-đọc-pdf--word--txt)
7. [Nghe thử nhanh (Quick TTS)](#7-nghe-thử-nhanh-quick-tts)
8. [Chọn & tùy chỉnh giọng đọc](#8-chọn--tùy-chỉnh-giọng-đọc)
9. [Nhân bản giọng nói (Voice Clone)](#9-nhân-bản-giọng-nói-voice-clone)
10. [Ghép giọng vào video — Lồng tiếng](#10-ghép-giọng-vào-video--lồng-tiếng)
11. [Lồng tiếng tự động (Auto-dub) & YouTube](#11-lồng-tiếng-tự-động-auto-dub--youtube)
12. [Dịch phụ đề / tài liệu sang tiếng Việt](#12-dịch-phụ-đề--tài-liệu-sang-tiếng-việt)
13. [Công cụ Video (OCR, STT, nén, ghép, sửa)](#13-công-cụ-video)
14. [Tải truyện (Webtoon / Manga)](#14-tải-truyện-webtoon--manga)
15. [Kiểm tra chất lượng (QC) & sửa lỗi audio](#15-kiểm-tra-chất-lượng-qc--sửa-lỗi-audio)
16. [Tính năng nâng cao về quy trình](#16-tính-năng-nâng-cao-về-quy-trình)
17. [Cài đặt (⚙) & cấu hình](#17-cài-đặt--cấu-hình)
18. [Xử lý sự cố thường gặp](#18-xử-lý-sự-cố-thường-gặp)

---

## 1. Cài đặt & Khởi động

Phần mềm có hai dạng:

- **Bản cài đặt (.msi)** — chạy `SRT_TTS_Studio_Setup.msi`, cài như phần mềm Windows thông
  thường, tạo lối tắt ở Start Menu / Desktop.
- **Bản di động (.exe)** — chạy trực tiếp không cần cài:
  - `SRT_TTS_Studio_Portable.exe` — bản thường.
  - `SRT_TTS_Studio_Secured.exe` — bản có kiểm tra toàn vẹn chặt hơn.
  - `SRT_TTS_Studio_Trial.exe` — bản dùng thử 24 giờ (không chạy trên máy ảo).

**Yêu cầu:** Windows 10/11 64-bit. Lần đầu mở phải **có mạng Internet** (phần mềm kiểm tra
kết nối khi khởi động). Một số tính năng nâng cao (VoxCPM, VieNeu, F5-TTS, OmniVoice, STT,
dịch offline) cần cài thêm bộ "môi trường" (env) và model — xem [Mục 17](#17-cài-đặt--cấu-hình).

**Khởi động:** mở phần mềm → màn hình chờ (splash, ~3 giây, có nhạc) → hộp đăng nhập.

> ⚠️ Chỉ chạy được **một bản** cùng lúc. Nếu báo "Phần mềm đang chạy!", hãy đóng cửa sổ cũ trước.

---

## 2. Đăng nhập & Mật khẩu

- **Lần đầu chạy:** phần mềm yêu cầu **đặt mật khẩu**. Nhập và ghi nhớ — mật khẩu này bảo vệ
  phần mềm trên máy của bạn.
- **Các lần sau:** nhập mật khẩu để vào.
- **Nhập sai 5 lần** → bị **khóa 15 phút** (chống dò mật khẩu).
- Mật khẩu gắn với **máy tính cụ thể** (theo CPU + ổ đĩa C). Chép phần mềm sang máy khác sẽ
  phải đặt lại mật khẩu.

**Đăng xuất:** nút **Đăng xuất** ở góc trên phải — phần mềm sẽ dừng mọi tác vụ và quay lại
màn hình đăng nhập (không thoát hẳn).

**Thoát hẳn:** bấm nút **X** đóng cửa sổ → xác nhận → thoát.

---

## 3. Tổng quan giao diện

Giao diện gồm:

- **Thanh bên trái (sidebar):** danh sách các trang chức năng. Bấm để chuyển trang.
- **Khu vực bảng điều khiển/nhật ký (console):** phía trên bên phải — hiển thị tiến trình và
  thông báo. Có thể ẩn/hiện để rộng chỗ làm việc.
- **Khu vực chức năng (workspace):** phía dưới bên phải — chứa các "thẻ" (card) thao tác của
  trang đang chọn.
- **Thanh tiêu đề (trên cùng):** các nút điều khiển dùng chung — **Tạm dừng / Tiếp tục / Dừng /
  Làm lại** và **Chọn / Mở thư mục Output**. Các nút này tự bật/tắt theo tác vụ đang chạy.

> 💡 *(mới)* Có thể **kéo-thả** file `.srt`/`.ass`/`.vtt` từ Explorer thả thẳng vào cửa sổ app để
> nạp nhanh (tự nhảy sang trang TTS).

Các trang chính trong sidebar:

| Trang | Dùng để |
|---|---|
| 📊 Bảng điều khiển | Xem tổng quan trạng thái, lối tắt nhanh |
| 🎙 TTS (SRT) | Chuyển phụ đề SRT thành giọng đọc |
| 🗣 Giọng đọc | Chọn nhà cung cấp, giọng, hồ sơ giọng, nhân bản giọng |
| 🔊 Text → Audio | Nghe thử nhanh / gõ text ra giọng đọc |
| 📄 Đọc tài liệu | Đọc PDF / Word / TXT |
| 🎬 Trích xuất | Video OCR, Speech-to-Text |
| 🌐 Dịch thuật | Dịch SRT / PDF / Word / TXT sang tiếng Việt |
| 🎞 Công cụ Video | Nén, ghép audio→video, sửa video, theo dõi thư mục |
| ✂ Edit Studio | Xem/kiểm tra video kèm audio |
| 📚 Tải truyện | Tải & dịch truyện tranh |
| ⚙ Hệ thống | Cài đặt, cập nhật giọng, kiểm tra môi trường, log |

---

## 4. Bảng điều khiển (Dashboard)

Là trang mặc định khi mở phần mềm. **Chỉ để xem** (không chạy tác vụ trực tiếp), gồm các thẻ:

- **Trạng thái phiên** — chế độ hiện tại, file SRT, số dòng, số file output, số dòng lỗi.
- **Sức khỏe môi trường** — ✅/❌ cho từng engine (RVC, VoxCPM, VieNeu…).
- **Sẵn sàng chạy?** — kiểm tra trước (preflight) engine + tóm tắt "khám SRT".
- **Tiến trình job** — phần trăm, thời gian còn lại, nút Tạm dừng/Tiếp tục/Dừng.
- **Lối tắt nhanh** — nhảy nhanh đến các trang khác.
- **Nghe thử nhanh** — gõ text nghe ngay.
- **Bật/tắt nhanh** — các công tắc hay dùng (cắt lặng, đọc số kiểu Việt, tự tạo lại dòng lỗi, tự soát đọc sai…).
  - **⚡ Kịch bản 1-click** *(mới)* — chọn **Lồng tiếng phim / Truyện audio / Podcast** là cả cụm tùy
    chọn (cắt lặng, loudnorm, cân âm lượng, định dạng ra, nghỉ giữa đoạn, m4b…) được set đúng một
    lượt; **↺ Mặc định** trả về ban đầu. Không đụng đến giọng đọc.
- **Chất lượng audio (QC)** — số file lỗi/thiếu + nút báo cáo, tạo lại.
- **Chi phí ước tính** — với nhà cung cấp tính phí.
- **Nhật ký gần đây** — vài dòng log cuối.

Trên thanh công cụ: **🔄 Làm mới** để cập nhật, **🔧 Chẩn đoán** để mở khu vực chẩn đoán nâng cao,
và **🚀 Bắt đầu nhanh** *(mới, cho người mới)* — chọn tình huống của bạn ("có SRT", "có video",
"có link YouTube", "có PDF/Word", "muốn dịch", "gõ text thử giọng") → phần mềm mở đúng trang và
in các bước cần làm vào ô nhật ký.

---

## 5. Chuyển phụ đề SRT thành giọng đọc

Đây là chức năng cốt lõi. Quy trình:

1. Mở trang **🎙 TTS (SRT)**.
2. Bấm **Chọn file SRT** → chọn file `.srt` (hoặc **`.ass` / `.ssa` / `.vtt`** *(mới)* — phụ đề
   anime/fansub và YouTube được tự chuyển sang SRT). Phần mềm tự đọc và báo số dòng + tóm tắt
   "khám SRT" (cảnh báo dòng lỗi, dòng quá dài, thời gian chồng nhau). Nếu ngôn ngữ phụ đề có vẻ
   **lệch với giọng đang chọn** (vd SRT tiếng Anh + giọng tiếng Việt), phần mềm nhắc ngay ⚠ *(mới)*.
3. Bấm **Chọn Output** (trên thanh tiêu đề hoặc trong trang) → chọn thư mục lưu audio.
4. Sang trang **🗣 Giọng đọc** chọn nhà cung cấp + giọng (xem [Mục 8](#8-chọn--tùy-chỉnh-giọng-đọc)).
5. (Khuyến nghị) Bấm **🎧 Thử 3 dòng đầu** để nghe trước — tránh chạy cả nghìn dòng sai giọng.
6. Bấm **Tạo giọng (TTS)** để bắt đầu. Theo dõi % và nhật ký.
7. Khi xong: bấm **Merge FFmpeg** để ghép tất cả thành **một file timeline** (`final.mp3`)
   khớp đúng thời điểm phụ đề.

**Trong khi chạy:** dùng **Tạm dừng / Tiếp tục / Dừng** trên thanh tiêu đề. Nếu Dừng giữa
chừng rồi chạy lại, phần mềm **tự bỏ qua các dòng đã làm xong** (resume).

**Công cụ SRT hữu ích** (trang TTS):
- **🩺 Khám SRT** — kiểm tra lỗi trước khi chạy.
- **🔧 Sửa SRT (tự động)** — tạo `<tên>_fixed.srt`: sắp lại thời gian, sửa dòng đảo giờ, bỏ
  dòng trống, tách dòng quá dài, và **tự gộp các cụm ≥3 dòng giống hệt liên tiếp** *(mới)*
  (lỗi ảo giác của nhận dạng giọng nói — hết cảnh TTS đọc lặp một câu 5 lần).
- **⏱ Dời thời gian SRT** — dịch toàn bộ timestamp ±N mili-giây.
- **🔁 Tìm & thay trong SRT** *(mới)* — sửa hàng loạt (thường/regex, phân biệt hoa-thường),
  xem trước số dòng khớp, lưu `_edit.srt`, và mời xóa audio các dòng bị đổi để đọc lại.
- **📝 Bảng phụ đề (sửa nhanh)** *(mới)* — toàn bộ SRT trong một cửa sổ dạng bảng: trạng thái
  từng dòng (lỗi timing, audio lỗi, đã có audio), sửa text, nghe, đọc lại từng dòng. Khi SRT có
  luật phân vai còn tô màu nền theo vai để nhìn ra ngay luật có lệch dòng không.
- **✂ Rút gọn AI (dòng tràn khe)** *(mới)* — dùng LLM viết lại NGẮN HƠN các dòng phụ đề dài hơn
  khe thời gian (dù merge đã tăng tốc 2×), giữ nguyên nghĩa. Có thể chọn gồm cả dòng "hơi hẹp"
  để mọi dòng đọc ở tốc độ tự nhiên 1.0×.
- **🪄 Sửa SRT bằng AI (yêu cầu)** *(mới)* — gõ bất kỳ yêu cầu nào ("viết trang trọng hơn",
  "đổi xưng hô", "bỏ từ tục", "sửa chính tả") → AI áp dụng cho toàn bộ phụ đề, dòng không cần
  đổi giữ nguyên văn.
- **🎙🔍 Soát đọc sai (STT)** *(mới)* — Whisper nghe lại toàn bộ audio đã tạo rồi so nội dung với
  text SRT, bắt các dòng đọc thiếu chữ/nuốt vế/đọc sai mà QC âm lượng-thời lượng không thấy. Kết
  quả mở cửa sổ từng dòng nghi sai kèm ▶ nghe / 🔁 đọc lại. (Cần `voxcpm_env`.) Có checkbox
  **"Tự soát đọc sai khi xong"** để batch tự chạy sau khi tạo xong.
- **🕘 Lịch sử job** *(mới)* — 30 batch gần nhất tự được ghi lại (file, output, thống kê, giọng);
  ↻ nạp lại nguyên cấu hình để chạy tập tiếp theo của series, 📂 mở thư mục output cũ.
- **📋 Việc cần làm** *(mới)* — một bảng gộp mọi vấn đề còn tồn sau batch (dòng audio lỗi, dòng
  thiếu, dòng tràn khe, lỗi SRT còn lại) kèm nút xử lý ngay từng mục.

**Tùy chọn khi Merge:**
- **Căn giữa khe lặng** — đặt giọng vào giữa khoảng trống thay vì sát đầu.
- **Chuẩn hóa âm lượng** (loudnorm) — chuẩn -16 LUFS (chuẩn YouTube).
- **Cân âm lượng từng dòng** — đồng đều khi phối nhiều giọng.
- **🎵 Nhạc nền** *(mới)* — chọn 1 file nhạc/ambience, nó tự lặp dưới giọng đọc (âm lượng chỉnh
  được, mặc định 0.12), tự cắt khi hết lời + fade-out 2 giây. Để trống = tắt.
- **Định dạng ra:** mp3 / wav / m4a / opus.
- Sau khi merge, phần mềm tạo thêm `final_synced.srt` — phụ đề khớp đúng giọng nói thực tế.

**✂ Chia final theo giờ** *(mới)* — chia file audio dài thành các phần N phút (mặc định 59 — vừa
giới hạn upload) bằng stream-copy (không re-encode, gần như tức thì); nếu có `final_synced.srt`
cạnh audio thì chia kèm SRT từng phần (timestamp tự dời về 0). Tùy chọn **🔇 Cắt tại chỗ lặng**
(mặc định bật) dời mốc chia về chỗ lặng gần nhất để không cắt giữa câu.

**🎭 Tag cảm xúc theo dòng** *(mới)* — thêm tag vào **đầu** một dòng SRT (hoặc đoạn text):
`[vui]` `[buồn]` `[giận]` `[sợ]` `[nhanh]` `[chậm]` `[thì thầm]` `[hét]` (hỗ trợ cả không dấu
`[buon]`/`[gian]`…). Với **Edge TTS**, giọng tự đổi tốc độ/cao độ theo cảm xúc; **tag không bị
đọc thành tiếng**. Ví dụ: `[giận] Sao cậu dám!`. Giọng nhân bản local chỉ bỏ tag (không đổi giọng).

---

## 6. Đọc PDF / Word / TXT

1. Mở trang **📄 Đọc tài liệu**.
2. Bấm **Mở PDF** (hoặc **Mở Word/TXT**) → chọn file. Phần mềm tách nội dung thành các đoạn nhỏ.
3. Chọn Output + giọng (như mục SRT).
4. Bấm **Đọc PDF (TTS)** để tạo audio từng đoạn.
   - **📖 Đọc từ đoạn X đến Y** *(mới)* — đọc riêng một chương của tài liệu dài mà không cần cắt
     file (áp dụng cho mọi engine).
5. Bấm **Merge PDF Audio** để nối thành một file. Tùy chọn kèm theo *(mới)*:
   - **⏸ Nghỉ giữa đoạn (ms)** (mặc định 300) — chèn khoảng lặng giữa các đoạn để truyện audio
     nghe có nhịp thở tự nhiên; 0 = tắt.
   - **🎵 Nhạc nền** — chọn 1 file nhạc chạy nền dưới giọng đọc (âm lượng chỉnh được).
   - **🎺 Intro / Outro** *(mới)* — chọn file nhạc hiệu đầu/cuối, tự nối vào đầu & cuối audiobook;
     mốc chương `.m4b` tự dời theo độ dài intro (đoạn intro thành mục "Mở đầu"). Để trống = tắt.
   - **🔊 Chuẩn âm lượng** *(mới)* — chuẩn hoá về -16 LUFS (chuẩn YouTube), hữu ích khi trộn
     nhiều giọng local to nhỏ khác nhau.
   - **📚 Xuất .m4b có chương** — xuất thêm file audiobook `.m4b` với mốc chương tự nhận từ heading
     "Chương N…", tua theo chương trên mọi player. Kèm luôn **📑 `youtube_description.txt`** *(mới)*
     — mỗi chương một dòng `MM:SS Tên`, dán vào mô tả video là YouTube tự hiện chapter.
   - **🎺 Intro / Outro** *(mới)* — nối nhạc hiệu đầu/cuối audiobook (mốc chương .m4b tự dời theo).
   - **🔊 Chuẩn âm lượng** *(mới)* — chuẩn hoá -16 LUFS (chuẩn YouTube), hữu ích khi trộn nhiều
     engine giọng to nhỏ khác nhau.
6. Cần sửa một đoạn? Bấm **Regenerate đoạn PDF** để đọc lại riêng đoạn đó.

> Word (.docx), **EPUB** và TXT dùng chung quy trình với PDF.

**🎙 Podcast 2 giọng từ tài liệu (AI)** *(mới)* — kiểu NotebookLM: PDF/Word/EPUB/TXT → AI viết
kịch bản hội thoại MC + chuyên gia → đọc bằng **2 hồ sơ giọng** → tự ghép thành 1 file podcast.
Cần ≥2 hồ sơ giọng + API key dịch; kịch bản lưu `.txt` để xem/sửa; chạy lại là resume.

**📰 Đọc bài báo / RSS → Audio** *(mới)* — card "📰 Đọc bài báo / RSS" trên trang này:
- Dán link **1 bài báo** (VnExpress, Dân Trí, Tuổi Trẻ…) → phần mềm tự trích **thân bài**
  (bỏ menu, quảng cáo) → nạp vào pipeline đọc TTS.
- Dán link **RSS** + số bài → lấy N bài mới nhất, mỗi bài thành một "chương" (hợp với .m4b mục lục).
- Nút **☕ Bản tin (1 nút)** làm trọn gói: tải → đọc → ghép .m4b trong một lần bấm.

---

## 7. Nghe thử nhanh (Quick TTS)

Trang **🔊 Text → Audio**: gõ/dán văn bản bất kỳ → tạo audio ngay.

- **🎧 Nghe thử** — nghe ngay không lưu cố định.
- **⏹ Dừng nghe** — dừng phát.
- **🔊 Gen Audio** — xuất file vào thư mục Output.
- **Gõ Telex (VN)** — bật để gõ tiếng Việt kiểu Telex (vd: `chaof` → `chào`) ngay trong ô nhập,
  kể cả khi bộ gõ Unikey/EVKey không hoạt động.

---

## 8. Chọn & tùy chỉnh giọng đọc

Tại trang **🗣 Giọng đọc**:

- **Nhà cung cấp:** Edge TTS (miễn phí, nhiều giọng), FPT.AI, Vbee, Zalo AI, EverAI, MiniMax
  (các nhà cung cấp tiếng Việt — cần API key, khai trong ⚙ Cài đặt).
- **Giọng:** chọn từ danh sách. Bấm **🔎** để tìm nhanh theo tên (Edge có hàng trăm giọng).
- **🔄 Cập nhật giọng Edge** (trang Hệ thống) — tải danh sách giọng mới nhất.
- **Tốc độ / Cao độ** (Edge) — vd `+20%`, `-2Hz`.

**Hồ sơ giọng (💾 / 🗑):** lưu lại toàn bộ thiết lập giọng hiện tại thành một "hồ sơ" để áp
nhanh lần sau. Rất tiện khi bạn có nhiều cấu hình cho từng dự án/nhân vật.

**Tùy chọn xử lý văn bản:**
- **Đọc số tiền/ngày/giờ kiểu Việt** — vd "15.000đ" → "mười lăm nghìn đồng".
- **Đọc teencode/viết tắt chat** *(mới)* — "ko, dc, vs, mn, tks…" được đọc thành từ đầy đủ (chỉ
  từ viết thường nguyên chữ — "BT", "VS Code", "100k" không bị đụng; tắt được).
- **Từ điển phát âm (📖)** — quy định cách đọc từ riêng (tên riêng, thuật ngữ). Có nút **🔍 Gợi ý từ**
  quét file để đề xuất từ nước ngoài cần phiên âm.
- **Cắt lặng đầu/cuối** — bỏ khoảng lặng thừa.
- **🔬 So giọng (A/B)** — đọc thử một câu bằng nhiều hồ sơ giọng để so sánh.
- **🎭 Tag cảm xúc theo dòng** *(mới)* — đặt `[vui]` / `[buồn]` / `[giận]` / `[sợ]` / `[nhanh]` /
  `[chậm]` / `[thì thầm]` / `[hét]` ở đầu một dòng SRT/đoạn text: Edge TTS tự đổi tốc độ/cao độ
  theo cảm xúc, **tag không bị đọc thành tiếng** (có alias không dấu: `[buon]`, `[gian]`…).

---

## 9. Nhân bản giọng nói (Voice Clone)

Phần mềm có **5 engine** nhân bản/chuyển giọng (chọn ở trang Giọng đọc, **chỉ bật một cái**):

| Engine | Đặc điểm | Cần |
|---|---|---|
| **RVC** | Chuyển giọng đã tạo sang giọng mẫu | model `.pth` + (tùy chọn) index |
| **VoxCPM** | TTS nhân bản giọng | model VoxCPM + audio mẫu |
| **VieNeu-TTS** | Chất lượng cao 48 kHz, có giọng preset + cảm xúc | (model tự tải) + audio mẫu (nếu clone) |
| **F5-TTS** | Nhân bản giọng thuần | model F5 (bắt buộc) + audio mẫu (bắt buộc) |
| **OmniVoice** | Nhân bản giọng | (model tự tải) + audio mẫu (bắt buộc) |

**Cách dùng chung:**
1. Bật engine mong muốn (các engine khác tự bị khóa).
2. Khai **đường dẫn model** (nếu cần) và **audio mẫu** (file giọng muốn nhân bản, vài giây–vài chục giây).
   Lấy audio mẫu nhanh ngay trong app *(mới)*:
   - **🎙 Thu âm** — chọn micro, thu 3–120 giây (dừng sớm vẫn giữ phần đã thu), tự điền + nghe lại.
   - **🎬 Cắt từ video/YouTube** — cắt một đoạn 3–60 giây từ file video/audio hoặc link YouTube làm
     giọng mẫu; có tùy chọn **🎼 Tách giọng khỏi nhạc** cho mẫu sạch.
3. Có thể bấm **STT** để tự nhận diện chữ trong audio mẫu, và **Xử lý Audio** để tách nhạc/khử nhiễu cho mẫu sạch hơn.
4. Chạy TTS như bình thường (SRT/PDF/Quick TTS).

> Các engine này cần cài "môi trường" (env) và model riêng — xem [Mục 17](#17-cài-đặt--cấu-hình).
> Nếu thiếu, phần mềm sẽ báo rõ ở nhật ký khi khởi động.

---

## 10. Ghép giọng vào video — Lồng tiếng

Trang **🎞 Công cụ Video → thẻ Ghép Audio vào Video (Mux):**

1. **Chọn video** + **Chọn audio** (vd `final.mp3` vừa merge).
2. Chỉnh **âm lượng** từng nguồn (vd `100%`, `50%`).
3. **Giữ audio gốc** — tích để trộn audio gốc với giọng lồng. Khi đó có thêm:
   - **Tự hạ nhạc nền khi có lời (ducking)** — tự giảm audio gốc lúc giọng đọc nói, phục hồi
     lúc chỉ có nhạc/tiếng động (mặc định bật, tránh nhạc nền át giọng).
   - **🎼 Tách nhạc nền (demucs)** *(mới)* — bỏ hẳn lời thoại gốc, mix **nhạc nền sạch + giọng
     lồng tiếng** thay cho ducking (chất lượng "phim chiếu rạp"). Tự quay về ducking nếu máy
     thiếu `voxcpm_env`/model.
4. Bấm chạy → xuất `<tên video>_dubbed.mp4`.

Ghép giữ nguyên hình ảnh (không nén lại → nhanh), audio AAC 192k.

---

## 11. Lồng tiếng tự động (Auto-dub) & YouTube

**🎬 Lồng tiếng tự động** — làm trọn gói trong một lần bấm: nhận diện lời (STT) → dịch sang
tiếng Việt → tạo giọng đọc → ghép timeline → ghép vào video.

1. Bấm **🎬 Lồng tiếng tự động** (trang SRT hoặc thẻ Mux của trang Video).
2. Trong hộp thoại:
   - Chọn **video** (chọn nhiều video để xử lý hàng loạt).
   - Hoặc dán **link YouTube** (mỗi dòng một link) — phần mềm tự tải về rồi lồng tiếng. Nhận luôn
     **link playlist hoặc kênh** *(mới)* (`/playlist?list=`, `/@tenkenh`, `/channel/`): tự liệt kê
     danh sách video (trần 100) rồi tải → dub tuần tự. Link video lẻ (kể cả có `&list=`) vẫn chỉ
     dub đúng video đó.
   - Chọn **model STT** và **ngôn ngữ nguồn**.
   - Chọn **hồ sơ giọng** đọc.
   - Chọn **nhà cung cấp dịch** (Claude/Gemini/OpenAI/Groq/DeepSeek/**Offline** — Offline không cần mạng/API).
   - Tích **Giữ audio gốc** + **ducking** (hoặc **🎼 tách nhạc nền**) nếu muốn.
   - Tích **Gắn phụ đề cứng** nếu muốn chèn sub vào hình — có thể chọn **cỡ (Nhỏ/Vừa/To)** và
     **màu (Trắng/Vàng/Xanh lá)** *(mới)*.
3. (Khuyến nghị) Bấm **🔍 Dub thử 60 giây đầu** *(mới)* — chạy đủ 5 bước trên clip 60s rồi tự mở
   xem, để duyệt giọng/bản dịch/mix trước khi chạy full hàng giờ.
4. Bấm chạy. Kết thúc tạo `<tên>_dubbed.mp4` + bản tóm tắt số dòng đã làm.

**📡 Theo dõi kênh YouTube** *(mới)* — nút trong card YouTube: lưu danh sách kênh/playlist theo
dõi, bấm "Kiểm tra & dub video mới" để liệt kê N video mới nhất mỗi kênh, bỏ qua video đã dub
(nhận biết qua file `_dubbed.mp4`), video mới tự vào hàng đợi lồng tiếng.

> Cần: ffmpeg, môi trường STT (whisper). Tải YouTube cần `yt-dlp`. Xem [Mục 17](#17-cài-đặt--cấu-hình).

---

## 12. Dịch phụ đề / tài liệu sang tiếng Việt

Trang **🌐 Dịch thuật** — dịch **SRT / PDF / Word / TXT** sang tiếng Việt tự nhiên.

1. Chọn **nhà cung cấp dịch:** Claude / Gemini / OpenAI / **Groq / DeepSeek** *(mới — giá rẻ hơn
   ~10–20 lần, Groq có gói miễn phí)* (cần API key) hoặc **Offline** (chạy trên máy, không cần
   mạng — cần cài model dịch).
2. Bấm nút tương ứng: **Dịch SRT / Dịch PDF / Dịch Word-TXT** → chọn file.
3. Tùy chọn:
   - **Song ngữ** — giữ cả câu gốc và câu dịch.
   - **Ngữ cảnh** — mô tả bối cảnh/xưng hô để dịch nhất quán (đòn bẩy chất lượng lớn nhất cho phụ đề).
   - **Dịch xong đọc luôn (SRT)** — tự chuyển sang TTS ngay sau khi dịch.
4. Kết quả lưu thành `<tên>_vi.srt` (hoặc `.txt`/`.pdf`/`.docx`), giữ nguyên thời gian phụ đề.

Có **Tạm dừng / Tiếp tục / Dừng** riêng cho dịch. Dừng giữa chừng vẫn lưu phần đã dịch.

**🔍 Soát bản dịch (dịch ngược)** *(mới)* — nút dưới "Dịch Word/TXT": dịch ngược bản `_vi.srt` về
ngôn ngữ gốc rồi so với câu gốc, xuất `<tên>_backcheck.txt` liệt kê các dòng nghi dịch sai/lệch
nghĩa (GỐC / DỊCH / NGƯỢC). Đây là công cụ **gợi ý** (bản dịch ngược cũng có thể sai) — cần nhà
cung cấp dịch cloud.

> **Tự chờ mạng khi rớt kết nối** *(mới)* — các batch tạo giọng qua nhà cung cấp online không còn
> dừng hẳn khi mất mạng giữa chừng: phần mềm tự chờ mạng quay lại (tối đa 30 phút) rồi đọc tiếp,
> nên batch qua đêm / hàng đợi / watch folder sống sót qua các cú rớt mạng ngắn.

---

## 13. Công cụ Video

- **Tách Sub Cứng (Video OCR)** — đọc chữ phụ đề "cháy" trên video thành file SRT
  (cần cài VideOCR CLI). Có Tạm dừng / Tiếp tục / Dừng.
- **Speech-to-Text (STT)** — nhận diện lời nói trong video thành phụ đề/văn bản
  (faster-whisper). Chọn **Tách: câu** hoặc **karaoke** (2–4 từ/dòng), xuất srt/txt/docx/pdf.
- **🖼 Audio → Video (ảnh nền)** *(mới)* — ghép 1 file audio (+ ảnh nền tuỳ chọn + phụ đề burn
  tuỳ chọn) thành video mp4 — cho kênh "truyện audio" cần khung video để đăng YouTube. Tuỳ chọn:
  - **🌊 Sóng nhạc động** — dải sóng chạy theo nhạc sát đáy màn hình.
  - **📐 Khung hình** — 16:9 / **9:16 (TikTok/Shorts)** / 1:1.
  - **🎬 Chế độ loạt** — chọn nhiều audio → xuất hàng loạt video; mỗi audio tự ghép SRT cùng tên
    (khớp thẳng với các phần `_pNN` của ✂ Chia final → "audiobook dài → loạt video có sub" 2 click).
- **Nén video** — giảm dung lượng.
- **Sửa video** — sửa file video lỗi.
- **Căn chỉnh thời gian SRT** — canh lại thời gian phụ đề theo giọng nói trong audio.
- **📂 Theo dõi thư mục (Watch folder)** — bật để phần mềm **tự xử lý file mới** thả vào thư mục
  (SRT → tạo giọng; video → lồng tiếng tự động). Tự bỏ qua file của chính nó.

---

## 14. Tải truyện (Webtoon / Manga)

Trang **📚 Tải truyện:**

1. **Dán link** truyện (trang bộ hoặc trang chương).
2. Chọn **định dạng**: Ảnh (thư mục) / PDF mỗi chương / CBZ mỗi chương / 1 PDF cả bộ / 1 CBZ cả bộ.
3. (Tùy chọn) Nhập **khoảng chương**: `1-10` hoặc `1,2,5` (để trống = tất cả).
4. Bấm **⬇ Tải**. Phần mềm tự thử lại chương lỗi; chạy lại sẽ tiếp tục (resume).

**Truyện nước ngoài:** tích **🌐 Truyện nước ngoài (gallery-dl)** cho các site như MangaDex,
webtoons… (cần cài `gallery-dl`). Site có Cloudflare: chọn **Cookie (vượt Cloudflare)** = trình
duyệt bạn đã mở site đó (đóng trình duyệt trước khi tải).

**Chuyển định dạng truyện:** thẻ "Chuyển định dạng" — đổi qua lại **Ảnh ↔ CBZ ↔ PDF**.

**Dịch truyện → Tiếng Việt:** thẻ "Dịch truyện" — đọc chữ trong ảnh (OCR) → dịch → **ghi chữ Việt
đè lên ảnh**, xuất ảnh dịch + PDF/CBZ + (tùy chọn) file đối chiếu gốc–Việt (cần cài EasyOCR).

**🔊 Truyện tranh → truyện audio** *(mới)* — nút trên card Dịch truyện: nạp file script dịch
(`_script_dich.txt`) vào pipeline Tài liệu → Audio, ra file đọc truyện chỉ với vài click.

**📖 Tải truyện chữ (web novel) → Audiobook** *(mới)* — card "📖 Tải truyện chữ":
1. Dán link bộ truyện chữ → tải TEXT từng chương (`chuong_NNNNN.txt`) + (tuỳ chọn) file gộp cả bộ.
2. Nút **🚀 Tải → Đọc → Audiobook (1 nút)** làm trọn gói: tải → đọc TTS từng chương → ghép thành
   `<tên>_audiobook.mp3` + (tuỳ chọn) `.m4b` có chương. Resume theo chương; chạy lại chỉ đọc chương mới.
3. Tuỳ chọn kèm theo: **🌐 Dịch sang tiếng Việt trước khi đọc** (truyện nước ngoài → bộ audio `_vi`
   riêng), **🖼 Ảnh bìa** (nhúng ID3 + tạo `thumbnail.png` 1280×720 sẵn để upload), **🌙 Tắt máy
   khi xong**, nhạc nền / nhạc hiệu / chuẩn âm lượng như audiobook tài liệu.
4. **📡 Theo dõi bộ truyện** — lưu danh sách bộ, kiểm tra & tải chương mới, tuỳ chọn tự đọc luôn.
   Mỗi dòng có thể ghi `URL | tên hồ sơ giọng | dich` để mỗi bộ một giọng và tự dịch nếu cần.

> Trang web dùng nhiều JS/Cloudflare có thể không tải được (phần mềm sẽ báo rõ).

### 📖 Tải truyện chữ → Audiobook

Card **📖 Tải truyện chữ** (trang Tải truyện) tải chữ từ các trang truyện chữ → mỗi chương
1 file `chuong_NNNNN.txt` + (tùy chọn) 1 file gộp cả bộ.

- **🔊 Đọc TTS** — nạp các file `.txt` đã tải vào pipeline Tài liệu → Audio để đọc.
- **🚀 Tải → Đọc → Audiobook (1 nút)** — làm trọn gói: tải → đọc **theo từng chương** → nối
  thành `<tên>_audiobook.mp3` (+ tùy chọn `.m4b` có chương). Đọc theo chương nên chạy lại là
  resume, chương mới không làm lệch chương cũ. Bộ dài (≥10 chương) sẽ hỏi xác nhận giọng/số giờ
  trước khi chạy để tránh đọc nhầm giọng cả đêm.
- **🌐 Dịch sang tiếng Việt trước khi đọc** *(mới)* — với truyện nước ngoài: tự dịch từng chương
  (`chuong_NNNNN_vi.txt`) bằng engine dịch đang chọn (Claude/Gemini/OpenAI/Groq/DeepSeek hoặc
  **Offline NLLB** miễn phí) rồi mới đọc → ra **bộ audio `_vi` riêng**. Resume theo chương: dừng
  giữa chừng chạy lại không tốn lại API. *(Nhớ chọn giọng tiếng Việt trước khi chạy.)*
  Với bộ ≥5 chương, phần mềm **dịch thử 1 chương** và hiện 400 ký tự đầu để bạn duyệt trước
  khi dịch cả bộ — sai engine thì Từ chối, đổi engine rồi chạy lại (không tốn dịch nhầm cả bộ).
- **🖼 Ảnh bìa** *(mới)* — chọn 1 ảnh bìa: audiobook được **nhúng ID3** (tên truyện, ảnh bìa) +
  tạo sẵn `thumbnail.png` 1280×720 (có tên truyện) trong thư mục truyện — cùng file mô tả chương,
  là bộ file sẵn sàng upload. Để trống = thumbnail nền tối.
- **🌙 Tắt máy khi xong** *(mới)* — tự tắt máy sau 60 giây khi chạy xong (chỉ khi không bấm dừng),
  tiện chạy bộ dài qua đêm. Hủy bằng lệnh `shutdown /a`.
- **📡 Theo dõi bộ truyện** — lưu danh sách bộ đang ra; bấm kiểm tra là chỉ tải chương **mới** +
  cập nhật audiobook. Tùy chọn 🔊 đọc luôn chương mới. Mỗi dòng có thể ghi thêm sau URL:
  - ` | tên hồ sơ giọng` *(mới)* — đọc bộ đó bằng **giọng riêng** rồi tự khôi phục giọng ban đầu.
  - ` | dich` *(mới)* — dịch sang tiếng Việt rồi mới đọc (truyện nước ngoài).

> Nhạc hiệu Intro/Outro, Nhạc nền, Chuẩn âm lượng (mục 6) áp dụng luôn cho audiobook truyện chữ.

---

## 15. Kiểm tra chất lượng (QC) & sửa lỗi audio

Giọng đọc đôi khi bị lỗi (im lặng, đọc quá dài/lặp, đọc thiếu). Phần mềm **tự kiểm tra** mỗi file
và **tự thử lại** nhiều lần. File vẫn lỗi sẽ được đổi tên rõ ràng:
`line_0002_novoice.mp3` (im lặng) / `_toolong` (quá dài) / `_tooshort` (quá ngắn).

Công cụ QC (trang TTS):
- **📋 Báo cáo QC** — liệt kê file lỗi + dòng thiếu.
- **🔁 Tạo lại dòng lỗi** — đọc lại các file bị đánh dấu lỗi.
- **🧩 Tạo lại dòng thiếu** — đọc lại các dòng bị bỏ sót (FAIL).
- **🎧 Nghe dòng lỗi** — nghe + tạo lại từng dòng để quyết định "đọc lại" hay "sửa chữ".
- **🌊 Soát sóng + phụ đề** *(mới)* — vẽ dạng sóng của file audio (kể cả file dài hàng giờ) kèm vạch
  mốc bắt đầu từng dòng phụ đề: nhìn ra ngay chỗ mất tiếng, chồng giọng hay lệch mà không cần nghe
  hết; click lên sóng để ▶ nghe 10 giây tại đúng điểm đó.

> Mẹo: nếu dừng giữa chừng và còn nhiều dòng, dùng **Tạo giọng/Tiếp tục** nhanh hơn (tự bỏ qua
> file đã có). Nút 🧩 dành cho vài dòng lẻ bị lỗi sau khi chạy hết.

---

## 16. Tính năng nâng cao về quy trình

- **🎭 Phân vai (Casting)** — gán **giọng khác nhau cho từng nhân vật** trong phụ đề. Nhiều cách gán:
  - **🤖 Tự phân vai (AI)** — tự nhận diện người nói và gán giọng (cần ≥2 hồ sơ giọng + API key dịch).
  - **🚻 Phân vai Nam/Nữ theo âm thanh gốc** *(mới)* — đo cao độ giọng (F0) từng dòng trên audio gốc
    của video rồi phân cụm nam/nữ và gán 2 hồ sơ giọng — **không cần API key**.
  - **Phân vai lai 🚻 + 🤖** *(mới)* — chạy 🚻 trước rồi 🤖: AI tách nhân vật theo lời thoại nhưng
    bám giới tính đã đo → nhân vật nam không còn bị gán nhầm giọng nữ.
  - **🎚 Tốc độ/cao độ theo vai (Edge)** *(mới)* — mỗi luật phân vai có thêm 2 ô Tốc độ/Cao độ
    (vd `+20%` / `-3Hz`): cùng 1 giọng Edge nhưng mỗi nhân vật một nhịp; chọn "(Giọng UI)" để chỉnh
    tốc độ/cao độ mà không cần tạo hồ sơ nào.
  - **Luật phân vai lưu kèm SRT** *(mới)* (`<tên>.cast.json`) — đóng app mở lại, Load đúng SRT là
    luật tự nạp về.
  - **📚 Thư viện nhân vật series** *(mới)* — 🤖 Tự phân vai nhớ "nhân vật nào giọng nào" (theo thư
    mục, `series_cast.json`): làm phim bộ, các tập sau nhân vật quen tự giữ đúng giọng.
- **📚 Hàng đợi** — nạp nhiều file SRT, chạy lần lượt tự động.
- **Khôi phục phiên** — mở lại đúng file + thư mục + giọng của lần làm trước.
- **Cache dòng trùng** — các câu lặp ("Vâng", "Cảm ơn"…) chỉ tạo một lần, dùng lại cho các tập sau
  và sau khi khởi động lại — tiết kiệm thời gian/chi phí.
- **📨 Webhook báo xong** *(mới)* — dán URL Discord/Telegram vào ⚙ Cài đặt, mỗi job hoàn tất app tự
  nhắn (kèm số dòng, số FAIL) — batch qua đêm khỏi ngồi canh máy.
- **💬 Chú thích nút (tooltip)** *(mới)* — rê chuột lên các nút chính hiện giải thích ngắn, người
  mới không phải đoán nghĩa các nút emoji.
- **Thông báo Windows** khi xong (nếu phần mềm đang thu nhỏ) + hiệu ứng pháo hoa + âm thanh.
- **Edit Studio** — cửa sổ xem video kèm audio (theo dòng hoặc cả file) để kiểm tra trước khi xuất.

---

## 17. Cài đặt (⚙) & cấu hình

Mở **⚙ Cài đặt** (trang Hệ thống). Các mục quan trọng:

- **API key** dịch thuật: Anthropic (Claude), Gemini, OpenAI, **Groq, DeepSeek** *(mới)*.
- **API key** các nhà cung cấp TTS tiếng Việt (FPT/Vbee/Zalo/EverAI/MiniMax).
- **Webhook báo xong** *(mới)* — URL Discord/Telegram để nhận thông báo khi job hoàn tất.
- **Đường dẫn ffmpeg**, **VideOCR CLI**.
- **Model & môi trường** cho VoxCPM / VieNeu / F5-TTS / OmniVoice / dịch Offline.

**Đặt model/env cạnh file .exe:** phần mềm **tự dò** các thư mục model/env nếu bạn đặt chúng
cạnh file chạy — đỡ phải khai đường dẫn. Nếu không tự dò được, khai tay trong ⚙ Cài đặt.

**Các thành phần lớn cần cài thêm** (quá nặng để đóng gói sẵn) — tham khảo `MOVE_CHECKLIST.txt`:
- `voxcpm_env` + model VoxCPM (cho VoxCPM, STT, xử lý audio, dịch offline).
- `vieneu_env`, `f5tts_env`, `omnivoice_env` + model tương ứng.
- VideOCR CLI (cho Video OCR).
- `yt-dlp` (tải YouTube), `gallery-dl` (truyện nước ngoài), `easyocr` (dịch truyện).
- Model dịch offline (NLLB/envit5) nếu dùng dịch Offline.

Một số model **tự tải về lần đầu chạy** (cần mạng): VieNeu, OmniVoice, whisper (STT), vocoder…

**Công cụ khác (trang Hệ thống):**
- **📂 Mở thư mục cấu hình**, **📦 Xuất / 📥 Nhập gói cấu hình** (sao lưu/chuyển máy thiết lập).
- **🔍 Kiểm tra môi trường** — xem engine/model nào đã sẵn sàng (không cần khởi động lại).
- **📄 Mở log hôm nay** — xem nhật ký chi tiết để gửi khi báo lỗi.
- **📈 Sản lượng** *(mới)* — bảng theo tháng: số giờ audio, số chương audiobook, số video đã tạo.
- **🐞 Gói hỗ trợ** *(mới)* — đóng gói log + cấu hình + thông tin máy thành 1 file zip trên Desktop
  để gửi khi báo lỗi (**không kèm** API key / mật khẩu).
- **🖱 Chuột phải** *(mới)* — đăng ký menu chuột phải Windows "Mở bằng SRT TTS Studio" cho file `.srt`.

---

## 18. Xử lý sự cố thường gặp

| Hiện tượng | Cách xử lý |
|---|---|
| "Phần mềm đang chạy!" | Đóng cửa sổ cũ; nếu vẫn báo, đăng xuất rồi mở lại. |
| Thoát ngay khi mở | Có thể đang **offline** (bắt buộc có mạng khi mở), hoặc bản Trial chạy trên **máy ảo**. |
| Quên mật khẩu | Mật khẩu gắn theo máy — liên hệ nhà cung cấp phần mềm để được hỗ trợ đặt lại. |
| Bị khóa 15 phút | Do nhập sai 5 lần — chờ hết khóa rồi nhập lại. |
| Giọng đọc bị lỗi/lặp/im lặng | Edge TTS đôi khi không ổn định — dùng **🔁 Tạo lại dòng lỗi**; phần mềm tự thử lại. |
| Engine clone báo thiếu | Xem nhật ký khi khởi động + ⚙ Cài đặt; cài đúng env/model ([Mục 17](#17-cài-đặt--cấu-hình)). |
| Dịch báo lỗi key | Kiểm tra API key trong ⚙ Cài đặt, hoặc chuyển sang **Offline**. |
| Tải truyện 403 / Cloudflare | Chọn đúng **Cookie** trình duyệt đã mở site (và đóng trình duyệt trước khi tải). |
| Giọng đọc bị nhạc nền át | Khi Mux, bật **Giữ audio gốc** + **ducking**. |
| Cần gửi log báo lỗi | Trang Hệ thống → **📄 Mở log hôm nay** → gửi file đó. |

---

*Mọi thắc mắc hoặc cần hỗ trợ kỹ thuật, vui lòng liên hệ nhà cung cấp phần mềm và đính kèm file
log trong ngày để được xử lý nhanh nhất.*
