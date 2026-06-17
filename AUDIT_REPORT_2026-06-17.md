# BÁO CÁO KIỂM TRA — SRT TTS Studio

**Ngày:** 2026-06-17
**Phạm vi:** Toàn bộ source (`apppp_integrated.py` ~19.815 dòng + 12 script companion), output build mới (`output/`, `dist/`), bảo mật, phụ thuộc ngoài folder, và đối chiếu TEST_CHECKLIST.md.
**Phương pháp:** Phân tích tĩnh AST + kiểm tra binary + đối chiếu cấu hình. *(Không thể chạy GUI Windows tương tác trong môi trường này.)*

---

## 1. Kết luận nhanh

Phần mềm **sạch về cấu trúc, bảo mật nguyên vẹn, build đầy đủ**. Tìm thấy **1 lỗi thread-safety đã được vá** (dòng 8043). Rủi ro thực tế duy nhất còn lại khi triển khai là **phụ thuộc lớn nằm ngoài folder** — đã có cơ chế cảnh báo tự động lúc khởi động.

| Hạng mục | Kết quả |
|---|---|
| Biên dịch (CPython + rủi ro Cython) | ✅ Pass |
| Tên chưa định nghĩa / def trùng / global lỗi | ✅ Không có |
| Máy trạng thái `set_mode` | ✅ Nhất quán (26/26 mode) |
| Bảo mật code-protection (`.pyd`-only) | ✅ Nguyên vẹn cả 3 exe |
| Integrity manifest (Secured) | ✅ Khớp SHA-256 |
| Lỗ hổng (eval/exec/pickle/shell) | ✅ Không có rủi ro |
| Quá tải tài nguyên | ✅ Có giới hạn (Semaphore 4) |
| Lỗi thread-safety | ⚠️→✅ 1 lỗi, đã vá |
| Phụ thuộc ngoài folder | ⚠️ Nhiều (xem mục 4) — có cảnh báo tự động |

---

## 2. Xác minh build output

`build_all.bat` đã tạo đầy đủ (timestamp hôm nay, sau bản vá):

- `output/SRT_TTS_Studio_Setup.msi` — installer tự chứa
- `output/Portable/` — 3 exe onefile (Portable / Secured / Trial) + `.integrity`, 12 script companion, `rvc_env/`, `hubert_base.pt`, `rmvpe.pt`, model F5 (`F5-TTS-Vietnamese-ViVoice/`)
- `dist/SRT_TTS_Studio/` — bản onedir + `ffmpeg.exe`/`ffprobe.exe` + `.pyd` + `.integrity`
- `output/MOVE_CHECKLIST.txt` — giống bản repo (đã ship)

---

## 3. Bảo mật & lỗ hổng

**Code protection — nguyên vẹn:**
- Cả 3 exe onefile chỉ tham chiếu `apppp_integrated.cp314-win_amd64.pyd`, **không rò rỉ `.pyc`** của module chính → bộ lọc `a.pure` hoạt động đúng trên cả 4 spec.
- Onedir: `.pyd` hiện diện trong `_internal/`, không có `.pyc` rò rỉ.
- `.integrity` của bản Secured có `h` = SHA-256 thực của exe → manifest mới, đồng bộ.

**Quét lỗ hổng:**
- Không có `eval()` / `exec()` / `os.system()` / `pickle.loads` / `marshal.loads` trên dữ liệu ngoài.
- `shell=True` duy nhất (dòng ~18814) chỉ chạy lệnh cố định `vol C:` để lấy serial ổ đĩa (DRM) — không có input người dùng → an toàn.
- 3 endpoint LLM dịch đều **HTTPS** (anthropic / googleapis / openai). Không có `http://` truyền dữ liệu nhạy cảm.
- Secret (`_HMAC_SECRET`/`_PBKDF2_SALT`) được Cython intern trong `.pyd`, không lộ dạng byte phẳng.

**7 lớp bảo vệ runtime** (Cython → integrity → self-integrity → hardware DRM → PBKDF2 → brute-force lockout → trial/VM) đều còn nguyên trong source.

---

## 4. Phụ thuộc NẰM NGOÀI folder (rủi ro triển khai chính)

App kết nối tới các thành phần không được build kèm. **Khi sang máy khác sẽ thiếu** nếu không xử lý:

**A. Phải copy tay (env + model lớn):**

| Thành phần | Phục vụ |
|---|---|
| `voxcpm_env/` + model VoxCPM-1.5-VN | VoxCPM, STT, lọc audio, căn SRT, Video-STT, PDF, dịch offline (1 env → 7 tính năng) |
| `vieneu_env/` | VieNeu-TTS |
| `f5tts_env/` | F5-TTS |
| `omnivoice_env/` | OmniVoice |
| `translate_env/` (tùy chọn) | Dịch offline envit5 |
| VideOCR CLI | Tách sub cứng (OCR) |
| Model dịch offline (NLLB/envit5) | Dịch provider "Offline" |

*(`rvc_env/` và model F5 ĐÃ được build kèm trong Portable.)*

**B. Tự tải HuggingFace/torch-hub lần đầu (cần internet hoặc copy cache):**
`OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano` (VoxCPM), `charactr/vocos-mel-24khz` (F5), `pnnbao-ump/VieNeu-TTS-v3-Turbo`, `splendor1811/omnivoice-vietnamese`, `Systran/faster-whisper-*` (STT), `demucs htdemucs` (tách nhạc — nằm ở `~/.cache/torch/hub`, KHÁC chỗ HF cache nên hay bị quên).

**C. Đường dẫn mặc định hardcode trỏ về máy dev** (chỉ là fallback cuối):
- `E:\VoxCPM-1.5-VN\...` (model + env VoxCPM)
- `C:\Users\os\Downloads\Compressed\VideOCR-1.5.1\...\CLI`

Vô hại vì thứ tự ưu tiên là **settings.json → auto-dò cạnh exe → hardcode**. Nhưng trên máy khác phải set ⚙ Cài đặt hoặc thả folder cạnh exe đúng tên.

**Cơ chế an toàn:** `_run_startup_diagnostics()` **cảnh báo đầy đủ tất cả** mục A/B trong logbox lúc khởi động (đã xác minh `_hf_checks` cover MOSS + vocos + VieNeu + OmniVoice + faster-whisper + htdemucs + model dịch + PaddleOCR). `MOVE_CHECKLIST.txt` (ship kèm) liệt kê chi tiết từng bước.

---

## 5. Lỗi / xung đột / quá tải

**Phân tích tĩnh — sạch:**
- 0 hàm/handler định nghĩa trùng tên.
- 0 tên load nhưng chưa bao giờ bound (không NameError tiềm ẩn) — cả app lẫn 12 helper.
- `set_mode`: 26/26 mode được gọi đều có nhánh xử lý.
- 0 `global` khai báo mà không bao giờ gán; 0 tham số mặc định khả biến; 0 key dict trùng; 0 mẫu rủi ro Cython.

**Lỗi đã vá (mức nhẹ — thread-safety):**
`_run_video_stt_thread()` dòng 8043 trước đây gọi `set_mode("video_stt_running")` **trực tiếp trên worker thread**, trong khi 3 thread video còn lại đều bọc `app.after(0, lambda: ...)`. Đã sửa thành:
```python
app.after(0, lambda: set_mode("video_stt_running"))
```

**Quá tải — không có vấn đề:**
- TTS song song giới hạn `asyncio.Semaphore(_TTS_PARALLEL_N=4)`.
- Local engine spawn subprocess per-line là **tuần tự có chủ đích** (đúng nhưng chậm — documented).
- 13 chỗ `except:` trần đều ở vị trí nuốt lỗi có chủ đích (COM/taskbar/audio fallback), không che giấu lỗi logic.

---

## 6. Đối chiếu TEST_CHECKLIST.md

**Không thể chạy GUI Windows tương tác** trong môi trường này (app .exe Windows, không có display). Đã xác minh **tĩnh**: toàn bộ 33 tính năng trong checklist đều có code path tồn tại và nối dây đúng — glossary, telex, đọc số VN, SRT lint/autofix, TTS song song ×4, cache dòng trùng, QC dashboard (report/listen/retry), merge + `final_synced.srt`, wizard lồng tiếng, YouTube dub, watch folder, voice profiles, A/B audition, taskbar progress, karaoke STT, config bundle export/import…

**Phần cần tự bấm tay trên Windows (mục F):** mở `output/Portable/SRT_TTS_Studio_Portable.exe`, đăng nhập, chạy nhanh glossary + TTS song song + merge để xác nhận runtime.

---

## 7. Khuyến nghị

1. **Trước khi copy sang máy khác:** chạy `python _audit_deps.py` trên máy gốc để biết folder nào chưa nằm trong `output/Portable`.
2. **Trên máy đích:** mở app, đọc dòng "KIỂM TRA HỆ THỐNG" trong logbox — app tự báo thiếu gì.
3. **Cách an toàn nhất:** thả các env/model (mục 4A) **cạnh exe đúng tên folder** → app tự dò, khỏi cần ⚙ Cài đặt.
4. **Máy không internet:** phải copy cả `~/.cache/huggingface/` VÀ `~/.cache/torch/` (mục 4B).
5. Chạy mục F của TEST_CHECKLIST trên exe để xác nhận lần cuối.
