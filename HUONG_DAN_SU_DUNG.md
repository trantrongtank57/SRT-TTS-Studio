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
- **Bật/tắt nhanh** — các công tắc hay dùng (cắt lặng, đọc số kiểu Việt, tự tạo lại dòng lỗi…).
- **Chất lượng audio (QC)** — số file lỗi/thiếu + nút báo cáo, tạo lại.
- **Chi phí ước tính** — với nhà cung cấp tính phí.
- **Nhật ký gần đây** — vài dòng log cuối.

Bấm **🔄 Làm mới** để cập nhật, **🔧 Chẩn đoán** để mở khu vực chẩn đoán nâng cao.

---

## 5. Chuyển phụ đề SRT thành giọng đọc

Đây là chức năng cốt lõi. Quy trình:

1. Mở trang **🎙 TTS (SRT)**.
2. Bấm **Chọn file SRT** → chọn file `.srt`. Phần mềm tự đọc và báo số dòng + tóm tắt
   "khám SRT" (cảnh báo dòng lỗi, dòng quá dài, thời gian chồng nhau).
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
  dòng trống, tách dòng quá dài.
- **⏱ Dời thời gian SRT** — dịch toàn bộ timestamp ±N mili-giây.

**Tùy chọn khi Merge:**
- **Căn giữa khe lặng** — đặt giọng vào giữa khoảng trống thay vì sát đầu.
- **Chuẩn hóa âm lượng** (loudnorm) — chuẩn -16 LUFS (chuẩn YouTube).
- **Cân âm lượng từng dòng** — đồng đều khi phối nhiều giọng.
- **Định dạng ra:** mp3 / wav / m4a / opus.
- Sau khi merge, phần mềm tạo thêm `final_synced.srt` — phụ đề khớp đúng giọng nói thực tế.

---

## 6. Đọc PDF / Word / TXT

1. Mở trang **📄 Đọc tài liệu**.
2. Bấm **Mở PDF** (hoặc **Mở Word/TXT**) → chọn file. Phần mềm tách nội dung thành các đoạn nhỏ.
3. Chọn Output + giọng (như mục SRT).
4. Bấm **Đọc PDF (TTS)** để tạo audio từng đoạn.
5. Bấm **Merge PDF Audio** để nối thành một file.
6. Cần sửa một đoạn? Bấm **Regenerate đoạn PDF** để đọc lại riêng đoạn đó.

> Word (.docx) và TXT dùng chung quy trình với PDF.

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
- **Từ điển phát âm (📖)** — quy định cách đọc từ riêng (tên riêng, thuật ngữ). Có nút **🔍 Gợi ý từ**
  quét file để đề xuất từ nước ngoài cần phiên âm.
- **Cắt lặng đầu/cuối** — bỏ khoảng lặng thừa.
- **🔬 So giọng (A/B)** — đọc thử một câu bằng nhiều hồ sơ giọng để so sánh.

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
4. Bấm chạy → xuất `<tên video>_dubbed.mp4`.

Ghép giữ nguyên hình ảnh (không nén lại → nhanh), audio AAC 192k.

---

## 11. Lồng tiếng tự động (Auto-dub) & YouTube

**🎬 Lồng tiếng tự động** — làm trọn gói trong một lần bấm: nhận diện lời (STT) → dịch sang
tiếng Việt → tạo giọng đọc → ghép timeline → ghép vào video.

1. Bấm **🎬 Lồng tiếng tự động** (trang SRT hoặc thẻ Mux của trang Video).
2. Trong hộp thoại:
   - Chọn **video** (chọn nhiều video để xử lý hàng loạt).
   - Hoặc dán **link YouTube** (mỗi dòng một link) — phần mềm tự tải về rồi lồng tiếng.
   - Chọn **model STT** và **ngôn ngữ nguồn**.
   - Chọn **hồ sơ giọng** đọc.
   - Chọn **nhà cung cấp dịch** (Claude/Gemini/OpenAI/**Offline** — Offline không cần mạng/API).
   - Tích **Giữ audio gốc** + **ducking** nếu muốn.
   - Tích **Gắn phụ đề cứng** nếu muốn chèn sub vào hình.
3. Bấm chạy. Kết thúc tạo `<tên>_dubbed.mp4` + bản tóm tắt số dòng đã làm.

> Cần: ffmpeg, môi trường STT (whisper). Tải YouTube cần `yt-dlp`. Xem [Mục 17](#17-cài-đặt--cấu-hình).

---

## 12. Dịch phụ đề / tài liệu sang tiếng Việt

Trang **🌐 Dịch thuật** — dịch **SRT / PDF / Word / TXT** sang tiếng Việt tự nhiên.

1. Chọn **nhà cung cấp dịch:** Claude / Gemini / OpenAI (cần API key) hoặc **Offline** (chạy trên
   máy, không cần mạng — cần cài model dịch).
2. Bấm nút tương ứng: **Dịch SRT / Dịch PDF / Dịch Word-TXT** → chọn file.
3. Tùy chọn:
   - **Song ngữ** — giữ cả câu gốc và câu dịch.
   - **Ngữ cảnh** — mô tả bối cảnh/xưng hô để dịch nhất quán (đòn bẩy chất lượng lớn nhất cho phụ đề).
   - **Dịch xong đọc luôn (SRT)** — tự chuyển sang TTS ngay sau khi dịch.
4. Kết quả lưu thành `<tên>_vi.srt` (hoặc `.txt`/`.pdf`/`.docx`), giữ nguyên thời gian phụ đề.

Có **Tạm dừng / Tiếp tục / Dừng** riêng cho dịch. Dừng giữa chừng vẫn lưu phần đã dịch.

---

## 13. Công cụ Video

- **Tách Sub Cứng (Video OCR)** — đọc chữ phụ đề "cháy" trên video thành file SRT
  (cần cài VideOCR CLI). Có Tạm dừng / Tiếp tục / Dừng.
- **Speech-to-Text (STT)** — nhận diện lời nói trong video thành phụ đề/văn bản
  (faster-whisper). Chọn **Tách: câu** hoặc **karaoke** (2–4 từ/dòng), xuất srt/txt/docx/pdf.
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

> Mẹo: nếu dừng giữa chừng và còn nhiều dòng, dùng **Tạo giọng/Tiếp tục** nhanh hơn (tự bỏ qua
> file đã có). Nút 🧩 dành cho vài dòng lẻ bị lỗi sau khi chạy hết.

---

## 16. Tính năng nâng cao về quy trình

- **🎭 Phân vai (Casting)** — gán **giọng khác nhau cho từng nhân vật** trong phụ đề. Có **🤖 Tự
  phân vai (AI)** tự nhận diện người nói và gán giọng (cần ≥2 hồ sơ giọng + API key dịch).
- **📚 Hàng đợi** — nạp nhiều file SRT, chạy lần lượt tự động.
- **Khôi phục phiên** — mở lại đúng file + thư mục + giọng của lần làm trước.
- **Cache dòng trùng** — các câu lặp ("Vâng", "Cảm ơn"…) chỉ tạo một lần, dùng lại cho các tập sau
  và sau khi khởi động lại — tiết kiệm thời gian/chi phí.
- **Thông báo Windows** khi xong (nếu phần mềm đang thu nhỏ) + hiệu ứng pháo hoa + âm thanh.
- **Edit Studio** — cửa sổ xem video kèm audio (theo dòng hoặc cả file) để kiểm tra trước khi xuất.

---

## 17. Cài đặt (⚙) & cấu hình

Mở **⚙ Cài đặt** (trang Hệ thống). Các mục quan trọng:

- **API key** dịch thuật: Anthropic (Claude), Gemini, OpenAI.
- **API key** các nhà cung cấp TTS tiếng Việt (FPT/Vbee/Zalo/EverAI/MiniMax).
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
