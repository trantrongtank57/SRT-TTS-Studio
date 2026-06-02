"""Whisper STT helper — chạy bằng voxcpm_env/Scripts/python.exe."""
import argparse
import io
import sys

# Force UTF-8 stdout để in được tiếng Việt trên Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio",  required=True, help="File audio cần transcribe")
    parser.add_argument("--model",  default="small", help="Model size: tiny/base/small/medium/large-v3")
    parser.add_argument("--lang",   default="vi",   help="Ngôn ngữ ISO (vi, en, ...)")
    args = parser.parse_args()

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("ERROR:faster-whisper chưa cài. Chạy: pip install faster-whisper", flush=True)
        sys.exit(1)

    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute = "float16" if device == "cuda" else "int8"

    print(f"[Whisper] device={device}, model={args.model}", file=sys.stderr, flush=True)
    model = WhisperModel(args.model, device=device, compute_type=compute)

    segments, info = model.transcribe(
        args.audio,
        language=args.lang,
        beam_size=5,
        vad_filter=True,
    )

    # Tổng thời lượng audio (giây) → mốc 100% cho thanh tiến trình.
    total_ms = max(int(float(getattr(info, "duration", 0) or 0) * 1000), 1)
    parts = []
    last_pct = -1
    # faster-whisper trả về generator: lặp tới đâu nhận dạng tới đó, nên
    # phát PROGRESS ra stderr theo vị trí (giây) đã xử lý.
    for seg in segments:
        parts.append(seg.text.strip())
        done_ms = min(int(seg.end * 1000), total_ms)
        pct = done_ms * 100 // total_ms
        if pct != last_pct:
            print(f"PROGRESS:{done_ms}:{total_ms}", file=sys.stderr, flush=True)
            last_pct = pct
    print(f"PROGRESS:{total_ms}:{total_ms}", file=sys.stderr, flush=True)
    transcript = " ".join(parts).strip()
    print(transcript, flush=True)


if __name__ == "__main__":
    main()
