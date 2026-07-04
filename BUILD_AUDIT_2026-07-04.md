# Báo cáo kiểm tra build — SRT TTS Studio

**Ngày:** 2026-07-04 · **Kiểm tra trên build vừa chạy** (verify trực tiếp bằng script, không đoán)
**Phạm vi:** biên dịch/Cython · bảo mật/lỗ hổng · phụ thuộc ngoài folder · lỗi/xung đột/quá tải · tài liệu đi kèm
**VERSION.txt:** `1.2.0` (bump từ 1.1.0 cho đợt tính năng này)

---

## 0. Kết luận nhanh

Build **SẠCH** và **BẢO MẬT ĐẠT**. Cython compile được, cả 3 onefile exe chỉ chứa `.pyd` (không rò bytecode), hash integrity khớp exe, mọi phụ thuộc resolve được trên máy build. Không thấy lỗi cấu trúc, trùng hàm, xung đột hay vòng lặp quá tải. Các `env`/model nặng không đi theo exe là **thiết kế** (quá lớn để nhúng), không phải lỗi — xem `MOVE_CHECKLIST.txt`.

---

## 1. Biên dịch & cú pháp ✅

- `python -m py_compile apppp_integrated.py` → **OK**
- `cythonize(...)` (chặt hơn CPython — đúng thứ build dùng ở bước 5) → **CYTHON OK**, không có lỗi "undeclared name"/global chưa gán.
- 1 sửa nhỏ trong đợt này: `_confirm_on_main(title, text, timeout=600)` — thêm lưới an toàn timeout + guard `app.after` để worker không treo khi app đang đóng (đã re-verify Cython sau sửa).

---

## 2. Bảo mật / lỗ hổng — ĐẠT ✅ (`_verify_security.py` → ALL CHECKS PASSED)

- **Strip filter `.pyc`** còn ở cả 4 spec (onedir + 3 onefile).
- **3 onefile exe** (Portable/Secured/Trial): trong CArchive (1175 entry) **chỉ có `apppp_integrated.cp314-win_amd64.pyd`, 0 `.pyc`** → không rò source bytecode; mỗi exe nhúng đủ **13 companion `.py`**.
- **Onedir (MSI):** `.pyd` có trong `_internal\`, **không** rò `apppp_integrated*.pyc`.
- **Self-integrity Secured.exe:** `.integrity.h` = `c701a7370a44a69aef1dc71d0017271323daa9cf576b2aeeffd79d1a5a75736f` **KHỚP** sha256 của `SRT_TTS_Studio_Secured.exe` vừa build.

---

## 3. Phụ thuộc ngoài folder — resolve được hết ✅ (`_audit_deps.py`)

- **5 env** (rvc/voxcpm/vieneu/f5tts/omnivoice), **model VoxCPM + F5-TTS**, `hubert_base.pt`/`rmvpe.pt`, và **6 model auto-download** (MOSS tokenizer, vocos, VieNeu, OmniVoice, faster-whisper, demucs htdemucs) đều ✅ trên máy build.
- `output\Portable\`: exe + `rvc_env` + 2 model RVC + F5 model đã có; các env/model nặng còn lại ⬜ (đúng thiết kế — copy tay theo `MOVE_CHECKLIST.txt`).
- Tính năng mới đợt này **không thêm dependency nào** (dùng lại engine dịch + ffmpeg sẵn có).

---

## 4. Lỗi / xung đột / quá tải ✅

Rà soát toàn bộ delta code chưa commit (8 tính năng mới, xem mục 5):
- Mọi hàm được gọi đều **tồn tại** (không NameError runtime); chữ ký khớp (`_translate_segments`, `_novel_tts_chapters_sync`, `_confirm_on_main`…).
- Logic tách 2 bộ audio gốc/`_vi` nhất quán; **không double nhạc hiệu** (nhánh `new_done==0` return sớm trước `_add_jingles`).
- Mọi Tk var đọc trên **main thread** trước khi vào worker (đúng luật thread-safety); mọi re-encode (loudnorm/jingle/tag) **fail-open** — lỗi thì giữ file gốc.
- Không thấy vòng lặp quá tải: pha dịch + TTS chạy **tuần tự theo chương, resume-safe**; watch chỉ chạy thủ công.

**Điểm cần lưu ý (không phải lỗi):**
- `_novel_watch_parse` coi field sau URL `= dich/dịch/vi` là cờ dịch → đừng đặt tên hồ sơ giọng đúng bằng `vi`/`dich`.
- Chế độ đọc bản dịch `_vi` dùng **giọng đang cấu hình** — nhớ chọn giọng vi-VN.
- 🌙 "Tắt máy khi xong" chạy `shutdown /s /t 60` thật — hủy bằng `shutdown /a`.

---

## 5. Tài liệu đi kèm — đã cập nhật cho 8 tính năng mới của build

| # | Tính năng | CHANGELOG | HƯỚNG DẪN | TEST_CHECKLIST | CLAUDE.md |
|---|---|---|---|---|---|
| 1 | 🌐 Dịch truyện chữ → Việt | ✅ | ✅ | ✅ AG | ✅ |
| 2 | 🎤 Giọng riêng từng bộ (watch) | ✅ | ✅ | ✅ AF | ✅ |
| 3 | 🎺 Nhạc hiệu Intro/Outro | ✅ | ✅ | ✅ AE | ✅ |
| 4 | 🔊 Chuẩn âm lượng audiobook | ✅ | ✅ | ✅ AF | ✅ |
| 5 | 🌙 Tắt máy khi xong | ✅ | ✅ | ✅ AF | ✅ |
| 6 | 🖼 Gói xuất bản (bìa + thumbnail + ID3) | ✅ | ✅ | ✅ AH | ✅ |
| 7 | 🌐 Dịch thử 1 chương (preview) | ✅ | ✅ | ✅ AH | ✅ |
| 8 | 🎭 Tag cảm xúc `[vui]/[buồn]/…` | ✅ | ✅ | ✅ AI | ✅ |

- `VERSION.txt` → `1.2.0`
- `MOVE_CHECKLIST.txt` → sửa "12 → 13 companion script" (thêm `manga_ocr_helper.py`), cập nhật ngày.
- 3 audit report cũ (2026-06-17/18) giữ nguyên (ảnh chụp lịch sử).

---

## Việc cần làm trước khi mang sang máy khác (rút gọn)
1. Copy theo `MOVE_CHECKLIST.txt`: `voxcpm_env`, `VoxCPM-1.5-VN`, `vieneu_env`, `f5tts_env`, `omnivoice_env`, VideOCR CLI (đặt **cạnh exe**).
2. Máy đích **có internet** lần đầu để tự tải nhóm HF/torch cache; nếu không, copy cả `%USERPROFILE%\.cache\huggingface` + `…\.cache\torch`.
3. Mở app → **🔍 Kiểm tra môi trường** → sửa hết dòng ❌ trong logbox.
