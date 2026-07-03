"""Whisper STT helper — chạy bằng voxcpm_env/Scripts/python.exe."""
import argparse
import io
import sys

# Force UTF-8 stdout để in được tiếng Việt trên Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio",  default="", help="File audio cần transcribe")
    parser.add_argument("--model",  default="small", help="Model size: tiny/base/small/medium/large-v3")
    parser.add_argument("--lang",   default="vi",   help="Ngôn ngữ ISO (vi, en, ...)")
    parser.add_argument("--verify-json", default="", dest="verify_json",
                        help='File JSON {"items":[{"idx":n,"file":path}]} — '
                             "transcribe hàng loạt (load model 1 lần), in "
                             "VERIFY:idx:text mỗi dòng + ALL_DONE (soát đọc sai)")
    args = parser.parse_args()
    if not args.audio and not args.verify_json:
        print("ERROR:cần --audio hoặc --verify-json", flush=True)
        sys.exit(1)

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

    if args.verify_json:
        # Chế độ soát đọc sai: nghe lại từng file line_NNNN.mp3 (clip ngắn) —
        # vad_filter TẮT (VAD hay nuốt clip 1-2s), beam 1 cho nhanh.
        import json
        with open(args.verify_json, "r", encoding="utf-8-sig") as f:
            items = json.load(f).get("items", [])
        n = max(len(items), 1)
        for i, it in enumerate(items):
            idx = it.get("idx", i)
            text = ""
            try:
                segs, _info = model.transcribe(
                    it.get("file", ""), language=args.lang,
                    beam_size=1, vad_filter=False)
                text = " ".join(s.text.strip() for s in segs).strip()
            except Exception as e:
                print(f"WARN:{idx}:{e}", file=sys.stderr, flush=True)
            print(f"VERIFY:{idx}:{text.replace(chr(10), ' ')}", flush=True)
            print(f"PROGRESS:{i + 1}:{n}", file=sys.stderr, flush=True)
        print("ALL_DONE", flush=True)
        return

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
