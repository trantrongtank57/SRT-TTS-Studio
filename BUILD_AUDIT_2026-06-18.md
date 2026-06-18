# Báo cáo kiểm tra build — SRT TTS Studio

**Ngày:** 2026-06-18 · **Kiểm tra lại trên build vừa chạy** (verify trực tiếp trên file, không đoán)
**Phạm vi:** phụ thuộc ngoài folder · đầy đủ output · bảo mật/lỗ hổng · lỗi/xung đột/quá tải · TEST_CHECKLIST

---

## 0. Kết luận nhanh

Build **SẠCH** và **BẢO MẬT ĐẠT**. Không thấy lỗi cấu trúc, không trùng hàm, không rò bytecode, không lộ secret.
Vấn đề duy nhất — và là **nguyên nhân "chạy máy khác thiếu nhiều thứ"** — nằm ở **mục 1 (nhóm B & C)**: các `env` + model nặng + HuggingFace/torch cache **không tự đi theo exe/MSI**. Đây là thiết kế (quá lớn để nhúng), không phải lỗi build.

---

## 1. Phụ thuộc NGOÀI folder — gốc của "máy khác thiếu đồ"

### A. Build ĐÃ tự đóng gói — có sẵn trong `output\Portable\` ✅ (đã verify từng file)
12 companion `.py` · `hubert_base.pt` · `rmvpe.pt` · `rvc_env\` · `F5-TTS-Vietnamese-ViVoice\` (đã xác nhận `model_last.pt` 5.4 GB + `vocab.txt`).

### B. Build KHÔNG copy — PHẢI copy tay sang máy đích (hay thiếu nhất)
| Thành phần | Dung lượng | Dùng cho |
|---|---|---|
| `voxcpm_env\` | ~6–8 GB | VoxCPM, STT, căn giọng, lọc audio, dịch offline |
| Model `VoxCPM-1.5-VN\` | ~3.5 GB | VoxCPM TTS |
| `vieneu_env\` | ~2–6 GB | VieNeu-TTS |
| `f5tts_env\` | ~6–8 GB | F5-TTS-Vietnamese |
| `omnivoice_env\` | ~6–8 GB | OmniVoice Vietnamese |
| VideOCR CLI + PaddleOCR PP-OCRv5 | nhỏ | Tách sub cứng (OCR) |
| `yt-dlp` | nhỏ | YouTube → Lồng tiếng |

### C. Model tự tải runtime — KHÔNG nằm trong folder copy nào (ẩn, dễ quên nhất)
Ở `%USERPROFILE%\.cache\huggingface` và `…\.cache\torch`. Máy **có internet** tự tải lần đầu; máy **không net** phải copy cache tay.
- `OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano` — **bắt buộc** VoxCPM
- `charactr/vocos-mel-24khz` — **bắt buộc** F5-TTS (vocoder)
- `Systran/faster-whisper-*` — STT + Video→SRT
- `demucs htdemucs` (`955717e8-*.th`, torch hub) — tách nhạc
- `pnnbao-ump/VieNeu-TTS-v3-Turbo`, `splendor1811/omnivoice-vietnamese` — nếu không trỏ model local

### Path cứng trỏ máy build (chỉ là fallback cuối, đã xác minh trong source)
- VoxCPM: `E:\VoxCPM-1.5-VN\VoxCPM\pretrained\VoxCPM-1.5-VN` (+ `voxcpm_env` cạnh đó)
- VideOCR: `C:\Users\os\Downloads\Compressed\VideOCR-1.5.1\VideOCR-1.5.1\CLI`

→ Trên máy đích: đặt folder **cạnh exe** (auto-detect lo phần còn lại) hoặc trỏ trong **⚙ Cài đặt**.

### Cách kiểm tra
- **Máy đích:** bấm **🔍 Kiểm tra môi trường** (trang Hệ thống) → logbox liệt kê đúng cái thiếu.
- **Máy build:** chạy `python _audit_deps.py` trước khi mang đi (lưu ý: chạy trên **Windows máy build**, không chạy trong sandbox vì nó dò `~/.cache` của Windows).

---

## 2. Đầy đủ output ✅
- `output\SRT_TTS_Studio_Setup.msi` (~1.01 GB) — VERSION.txt = `1.0.0`
- `output\Portable\`: 3 exe (Portable/Secured/Trial, mỗi cái ~159 MB) + `.integrity` + 12 `.py` + 2 model RVC + `rvc_env\` + F5 model
- `dist\SRT_TTS_Studio\` (onedir cho MSI): `.pyd` + 12 `.py` + `ffmpeg.exe`/`ffprobe.exe` + 2 model RVC + `rvc_env\` — đầy đủ

---

## 3. Bảo mật / lỗ hổng — ĐẠT ✅ (verify trên đúng file build hôm nay)
- **Strip filter `.pyc`** có ở cả 4 spec đang dùng (onedir + 3 onefile).
- **3 onefile exe**: trong binary **chỉ tham chiếu `apppp_integrated.cp314-win_amd64.pyd`, 0 tham chiếu `.pyc`** → không rò source bytecode.
- **Onedir**: `.pyd` có trong `_internal\`, **không** có `apppp_integrated*.pyc` rò rỉ.
- **`.pyd` không lộ chuỗi nhạy cảm**: `_HMAC_SECRET`/`_PBKDF2_SALT`/`*_api_key`/`sk-ant` → **0 lần** xuất hiện. Chỉ còn 1 `apppp_integrated.py` (co_filename Cython — vô hại).
- **Self-integrity Secured.exe**: `h` trong `.integrity` = `6f7752ac…ba110` **KHỚP TUYỆT ĐỐI** sha256 toàn file exe.
- **Không rò credential**: không có `auth.dat`/`.lockout` lọt vào `dist\` hay `output\` (đã quét).
- **Không** có `eval`/`exec`/`os.system`/`pickle.load`/`yaml.load` còn hoạt động (`os.system` duy nhất đã bị comment). Chỉ **1** `shell=True` — lệnh cố định lấy serial ổ đĩa cho DRM, không nhận input người dùng → không injection.

---

## 4. Lỗi / xung đột / quá tải
- **Không trùng tên hàm** ở cấp module (408 hàm) → không có định nghĩa sau ghi đè âm thầm.
- `py_compile` **pass sạch**. Bản build đã ra `.pyd` thành công nghĩa là **Cython cũng đã compile được** (Cython chặt hơn py_compile, và build sẽ abort ở bước 5 nếu lỗi). Lần build sau vẫn nên chạy one-liner `cythonize(...)` trên Windows trước khi build 10 phút.
- **Quá tải đã có chặn**: TTS song song giới hạn `Semaphore(4)`; watch-folder poll mỗi 4s + chờ file ổn định 2 tick; subprocess đọc stream theo dòng (không `communicate()` treo). Casting/QC-regen engine local spawn 1 subprocess/dòng — chậm nhưng đúng thiết kế.
- **Điểm nhỏ (không nghiêm trọng):** 13 chỗ `except:` trần (nuốt cả `KeyboardInterrupt`/`SystemExit`). Hợp triết lý "không chặn TTS"; muốn sạch hơn thì đổi thành `except Exception:`.

---

## 5. TEST_CHECKLIST.md
Checklist là **kiểm thử GUI thủ công trên Windows** (bấm nút trên app) — không tự động hoá thay người trong môi trường này được (app GUI, cần Windows + model + âm thanh).

**Smoke test tĩnh đã chạy:** mọi handler mà checklist dựa vào đều **tồn tại** trong source (startup diagnostics, glossary, telex, SRT lint/fix/shift, TTS song song, QC, merge + synced SRT, wizard lồng tiếng, YouTube dub, watch folder, ui_prefs, logout/exit, các lớp security) → app **không crash kiểu "nút gọi hàm không tồn tại"**.

**Bạn cần tự chạy trên Windows** (ưu tiên):
1. Mục **A** (khởi động/đăng nhập/ui_prefs giữ thiết lập) + mục **F** (chạy đúng trên `SRT_TTS_Studio_Portable.exe`).
2. Mục **C** (SRT → Edge song song → Merge) — luồng chính.
3. Một vòng nhanh **B** (glossary + đọc số tiếng Việt) và **D** (wizard lồng tiếng) nếu dùng.

---

## Việc cần làm trước khi mang sang máy khác (rút gọn)
1. Copy theo `MOVE_CHECKLIST.txt`: `voxcpm_env`, `VoxCPM-1.5-VN`, `vieneu_env`, `f5tts_env`, `omnivoice_env`, VideOCR CLI (đặt **cạnh exe**).
2. Máy đích **có internet** lần đầu để tự tải nhóm C (HF/torch cache); nếu không, copy cả `%USERPROFILE%\.cache\huggingface` + `…\.cache\torch`.
3. Mở app → **🔍 Kiểm tra môi trường** → sửa hết dòng ❌ trong logbox.
