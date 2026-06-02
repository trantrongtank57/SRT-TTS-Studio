"""video_stt_helper.py — Video/Audio → SRT + TXT bằng Whisper (faster-whisper).

Chạy bằng voxcpm_env/Scripts/python.exe.

Stdout protocol:
  PROGRESS:N:M      — đã xử lý N / M segments
  DONE:srt_path     — hoàn tất, đường dẫn file SRT output
  ERROR:message     — lỗi
"""
import argparse
import io
import os
import subprocess
import sys
import tempfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def _seconds_to_srt_time(s: float) -> str:
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    ms = int(round((s - int(s)) * 1000))
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def _extract_audio(input_path: str, ffmpeg: str) -> str:
    """Trích audio từ video → file WAV tạm, trả về đường dẫn."""
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    cmd = [
        ffmpeg, "-y", "-i", input_path,
        "-ar", "16000", "-ac", "1",   # 16 kHz mono — chuẩn Whisper
        "-vn",                         # bỏ video stream
        tmp.name,
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        err = r.stderr.decode("utf-8", errors="replace")[-400:]
        raise RuntimeError(f"ffmpeg lỗi: {err}")
    return tmp.name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",      required=True, help="Video hoặc audio input")
    parser.add_argument("--output-dir", required=True, help="Thư mục lưu .srt và .txt")
    parser.add_argument("--model",      default="large-v3", help="Whisper model size")
    parser.add_argument("--lang",       default="vi",       help="Ngôn ngữ ISO (vi/en/auto)")
    parser.add_argument("--ffmpeg",     default="ffmpeg",   help="Đường dẫn ffmpeg.exe")
    args = parser.parse_args()

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("ERROR:faster-whisper chưa cài trong voxcpm_env.", flush=True)
        sys.exit(1)

    import torch
    device  = "cuda" if torch.cuda.is_available() else "cpu"
    compute = "float16" if device == "cuda" else "int8"

    print(f"[STT] device={device} model={args.model} lang={args.lang}", file=sys.stderr, flush=True)

    # Trích audio nếu input là video
    audio_path = args.input
    tmp_wav    = None
    ext = os.path.splitext(args.input)[1].lower()
    video_exts = {".mp4", ".mkv", ".ts", ".avi", ".mov", ".webm", ".flv", ".wmv"}
    if ext in video_exts:
        print("[STT] Đang trích audio từ video...", file=sys.stderr, flush=True)
        try:
            tmp_wav    = _extract_audio(args.input, args.ffmpeg)
            audio_path = tmp_wav
        except Exception as e:
            print(f"ERROR:Không trích được audio: {e}", flush=True)
            sys.exit(1)

    # Tạo tên output từ tên file input
    base_name  = os.path.splitext(os.path.basename(args.input))[0]
    os.makedirs(args.output_dir, exist_ok=True)
    srt_path   = os.path.join(args.output_dir, base_name + "_stt.srt")
    txt_path   = os.path.join(args.output_dir, base_name + "_stt.txt")

    # Load model và transcribe — phát PROGRESS theo thời lượng đã xử lý
    # (faster-whisper trả về generator: lặp tới đâu nhận dạng tới đó, nên
    #  ta báo tiến trình ngay trong vòng lặp thay vì chờ materialise xong).
    srt_lines  = []
    txt_parts  = []
    try:
        model = WhisperModel(args.model, device=device, compute_type=compute)
        lang  = None if args.lang == "auto" else args.lang
        segments_gen, info = model.transcribe(
            audio_path,
            language=lang,
            beam_size=5,
            vad_filter=True,
            word_timestamps=False,
        )

        # Tổng thời lượng audio (giây) — dùng làm mốc 100% cho thanh tiến trình.
        total_dur = float(getattr(info, "duration", 0) or 0)
        # Quy đổi giây → mili-giây nguyên để dùng làm M trong PROGRESS:N:M
        total_ms  = max(int(total_dur * 1000), 1)
        last_pct  = -1
        idx       = 0
        for seg in segments_gen:
            idx  += 1
            start = _seconds_to_srt_time(seg.start)
            end   = _seconds_to_srt_time(seg.end)
            text  = seg.text.strip()
            srt_lines.append(f"{idx}\n{start} --> {end}\n{text}\n")
            txt_parts.append(text)

            # Tiến trình dựa trên vị trí (giây) đã nhận dạng so với tổng thời lượng.
            done_ms = min(int(seg.end * 1000), total_ms)
            pct = done_ms * 100 // total_ms
            if pct != last_pct:
                print(f"PROGRESS:{done_ms}:{total_ms}", flush=True)
                last_pct = pct
    except Exception as e:
        print(f"ERROR:Whisper lỗi: {e}", flush=True)
        sys.exit(1)
    finally:
        if tmp_wav and os.path.exists(tmp_wav):
            try: os.remove(tmp_wav)
            except Exception: pass

    if not srt_lines:
        print("ERROR:Không nhận dạng được giọng nói nào trong video.", flush=True)
        sys.exit(1)

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(txt_parts))

    # Đảm bảo thanh tiến trình chạm 100% trước khi báo DONE.
    print(f"PROGRESS:{total_ms}:{total_ms}", flush=True)
    print(f"DONE:{srt_path}", flush=True)


if __name__ == "__main__":
    main()
