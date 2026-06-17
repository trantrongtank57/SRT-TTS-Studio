# Báo cáo kiểm tra build — SRT TTS Studio

**Ngày:** 2026-06-17
**Phạm vi:** phụ thuộc ngoài folder · đầy đủ build output · bảo mật/lỗ hổng · lỗi/xung đột/quá tải · TEST_CHECKLIST

---

## 0. Tóm tắt

Build **sạch**, **bảo mật đạt**, **không có lỗi cấu trúc**. Vấn đề "chạy trên máy khác thiếu rất nhiều thứ" nằm hoàn toàn ở **mục 1 — nhóm B & C**: các môi trường (env) + model nặng và HuggingFace/torch cache **không tự đi theo exe/MSI**, phải copy riêng hoặc để máy đích tự tải khi có internet.

---

## 1. Phụ thuộc ngoài folder (gốc của "máy khác thiếu đồ")

### A. Build ĐÃ tự đóng gói — có sẵn trong `output\Portable\` ✅
- 12 companion `.py` (rvc/voxcpm/vieneu/f5tts/omnivoice helper, whisper_stt, audio_enhancer, pdf_helper, srt_align_helper, videocr_helper, video_stt_helper, translate_helper)
- `hubert_base.pt`, `rmvpe.pt`
- `rvc_env\`
- `F5-TTS-Vietnamese-ViVoice\` (model_last.pt + vocab.txt)

### B. Build KHÔNG copy — PHẢI copy tay sang máy khác (hay thiếu nhất)
| Thành phần | Dung lượng | Dùng cho |
|---|---|---|
| `voxcpm_env\` | ~6–8 GB | VoxCPM, STT, căn giọng, lọc audio, dịch offline |
| Model `VoxCPM-1.5-VN\` | ~3.5 GB | VoxCPM TTS |
| `vieneu_env\` | ~2–6 GB | VieNeu-TTS |
| `f5tts_env\` | ~6–8 GB | F5-TTS-Vietnamese |
| `omnivoice_env\` | ~6–8 GB | OmniVoice Vietnamese |
| VideOCR CLI + PaddleOCR PP-OCRv5 | nhỏ | Tách sub cứng (OCR) |

### C. Model tự tải runtime — KHÔNG nằm trong bất kỳ folder copy nào (ẩn, dễ quên nhất)
Nằm ở `%USERPROFILE%\.cache\huggingface` và `%USERPROFILE%\.cache\torch`. Máy **có internet** tự tải lần đầu; máy **không net** phải copy cache thủ công.
- `OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano` — **bắt buộc** cho VoxCPM
- `charactr/vocos-mel-24khz` — **bắt buộc** cho F5-TTS (vocoder)
- `Systran/faster-whisper-*` — STT + Video→SRT
- `demucs htdemucs` (`955717e8-*.th`, ở torch hub) — tách nhạc
- `pnnbao-ump/VieNeu-TTS-v3-Turbo`, `splendor1811/omnivoice-vietnamese` — model VieNeu/OmniVoice (nếu không trỏ model local)

### Path cứng trỏ về máy build (chỉ là fallback cuối)
- VoxCPM: `E:\VoxCPM-1.5-VN\VoxCPM\pretrained\VoxCPM-1.5-VN`
- VideOCR: `C:\Users\os\Downloads\Compressed\VideOCR-1.5.1\VideOCR-1.5.1\CLI`

→ Trên máy khác, đặt folder cạnh exe (auto-detect) **hoặc** trỏ trong ⚙ Cài đặt.

### Cách kiểm tra
- Trên **máy đích**: bấm **🔍 Kiểm tra môi trường** (trang Hệ thống) → logbox liệt kê chính xác cái nào thiếu.
- Trên **máy build**: chạy `python _audit_deps.py` trước khi mang đi.

---

## 2. Đầy đủ build output ✅

- `output\SRT_TTS_Studio_Setup.msi` (~1.01 GB)
- `output\Portable\`: 3 exe (Portable / Secured / Trial) + `SRT_TTS_Studio_Secured.exe.integrity` + 12 companion `.py` + `hubert_base.pt` + `rmvpe.pt` + `rvc_env\` + `F5-TTS-Vietnamese-ViVoice\`
- `dist\SRT_TTS_Studio\` (onedir cho MSI) hoàn chỉnh

---

## 3. Bảo mật / lỗ hổng — ĐẠT ✅ (verify trực tiếp trên file build)

- **Strip filter `.pyc`**: có đủ ở cả 4 spec (onedir + 3 onefile).
- **3 onefile exe**: archive **chỉ chứa `apppp_integrated.cp314-win_amd64.pyd`, KHÔNG rò bytecode `.pyc`** (parse trực tiếp TOC của PyInstaller CArchive để xác nhận). Mỗi exe nhúng đủ 12 companion `.py`.
- **Onedir**: `.pyd` có trong `_internal\`, không có `apppp_integrated*.pyc` rò rỉ.
- **`.pyd` không lộ chuỗi nhạy cảm**: không có `_HMAC_SECRET` / `_PBKDF2_SALT` / `anthropic_api_key` dạng plaintext. Chỉ còn 1 lần `apppp_integrated.py` (co_filename của Cython — vô hại).
- **Self-integrity Secured.exe**: hash `h` trong `.integrity` **khớp tuyệt đối** với sha256 toàn file exe.
- **Không** có `eval` / `exec` / `os.system` / `pickle.load` / `yaml.load`.
- Chỉ **1** `shell=True` — lệnh cố định `vol C:` (lấy serial ổ đĩa cho DRM), không có input người dùng → không có nguy cơ injection.

---

## 4. Lỗi / xung đột / quá tải

- **Không có hàm trùng tên** ở cấp module (408 hàm) → không có định nghĩa sau ghi đè âm thầm.
- `py_compile` pass sạch. **Lưu ý:** chạy lệnh `cythonize(...)` một dòng (trong CLAUDE.md) trên Windows trước mỗi build lớn — Cython chặt hơn `py_compile`.
- **Quá tải**: các đường nặng đều có chặn — TTS song song giới hạn `Semaphore(4)`, watch-folder poll mỗi 4s, subprocess có `timeout`. Casting/QC-regen với engine local spawn 1 subprocess/dòng (chậm nhưng đúng thiết kế, không phải lỗi).
- **Điểm nhỏ (không nghiêm trọng):** 13 chỗ `except:` trần — nuốt cả `KeyboardInterrupt`/`SystemExit`. Đúng triết lý "không chặn TTS" của app; nếu muốn sạch hơn thì đổi thành `except Exception:`.

---

## 5. TEST_CHECKLIST.md

Checklist là **kiểm thử GUI thủ công** (bấm nút trên app Windows) — không tự động hoá thay người được. Phải tự chạy trên Windows.

**Smoke test tĩnh đã chạy:** xác nhận **mọi handler** mà checklist dựa vào đều tồn tại trong source — startup diagnostics, glossary, telex, SRT lint/fix, TTS song song (`_generate_tts_parallel` là `async def`), QC, merge + synced SRT, wizard lồng tiếng, YouTube dub, watch folder, ui_prefs, logout/exit, các lớp security. **Tất cả đều có** → app không crash kiểu "nút gọi hàm không tồn tại".

---

## Phụ lục — thay đổi liên quan đã thực hiện trước đó (cập nhật không cần gỡ cài + giữ login)

- `product.wxs`: Version dùng biến `$(var.ProductVersion)`; `MajorUpgrade` thêm `AllowSameVersionUpgrades`.
- `build_all.bat` / `build_msi_protected.bat`: đọc `VERSION.txt` → truyền `-dProductVersion`; xoá `auth.dat`/`.lockout` khỏi `dist` trước khi Heat harvest.
- `apppp_integrated.py`: `PASSWORD_FILE`/`LOCKOUT_FILE` neo vào `_CONFIG_DIR` + tự migrate file cũ → login sống sót qua major-upgrade.
- Quy tắc phát hành: tăng `VERSION.txt` (3 số `x.y.z`) mỗi bản; **không bao giờ đổi `UpgradeCode`**.
