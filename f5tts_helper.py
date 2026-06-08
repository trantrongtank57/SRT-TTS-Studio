"""F5-TTS-Vietnamese batch voice clone helper — chạy bằng f5tts_env\\Scripts\\python.exe.

Mô hình: F5-TTS-Vietnamese (https://github.com/nguyenthienhy/F5-TTS-Vietnamese,
checkpoint hynt/F5-TTS-Vietnamese-ViVoice). Nhân bản giọng từ 1 audio mẫu + lời
thoại mẫu (ref_text); nếu bỏ trống ref_text, F5-TTS tự nhận dạng (ASR) audio mẫu.

Chạy trên **GPU NVIDIA (CUDA + PyTorch)** nếu có, không thì tự rơi về CPU.

Giao thức stdout (giống vieneu_helper.py / voxcpm_helper.py — app đọc từng dòng):
    DONE:{idx}            line_{idx:04d}.wav đã sẵn sàng
    ERROR:{idx}:{reason}  dòng lỗi (audio im lặng sau các lần thử)
    WARN:{idx}:{reason}   thử lại
    ALL_DONE              kết thúc batch
Dòng thông tin ghi ra stderr với tiền tố [F5TTS].
"""
import argparse
import glob
import json
import os
import sys

# Ép stdout/stderr sang UTF-8 — nếu không, in tiếng Việt ra console cp1252 (Windows)
# sẽ ném UnicodeEncodeError và làm helper crash (exit 1) ngay ở nhánh báo lỗi.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import numpy as np
import soundfile as sf


def _log(msg):
    print(f"[F5TTS] {msg}", file=sys.stderr, flush=True)


def _find_ckpt(model_dir):
    """Tìm file checkpoint (.pt/.safetensors) trong model_dir.
    Ưu tiên model_last.pt rồi tới file .pt/.safetensors đầu tiên."""
    pref = os.path.join(model_dir, "model_last.pt")
    if os.path.isfile(pref):
        return pref
    for pat in ("*.safetensors", "*.pt"):
        hits = sorted(glob.glob(os.path.join(model_dir, pat)))
        if hits:
            return hits[0]
    return ""


def _find_vocab(model_dir):
    """Tìm vocab.txt trong model_dir."""
    cand = os.path.join(model_dir, "vocab.txt")
    if os.path.isfile(cand):
        return cand
    hits = sorted(glob.glob(os.path.join(model_dir, "*vocab*.txt")))
    return hits[0] if hits else ""


def _patch_torchaudio():
    """torchaudio 2.9+ giải mã/ghi audio qua **torchcodec** (cần FFmpeg DLL; trên
    Windows thường lỗi 'TorchCodec is required for load_with_torchcodec'). F5-TTS
    gọi `torchaudio.load` để đọc audio mẫu → sẽ crash. Vá `torchaudio.load` và
    `torchaudio.save` dùng **soundfile** (giống voxcpm_helper/vieneu_helper) để
    không phụ thuộc torchcodec. Phải gọi TRƯỚC khi import f5_tts."""
    try:
        import torch
        import torchaudio

        def _load(path, *a, **k):
            data, sr = sf.read(str(path), dtype="float32", always_2d=True)
            # soundfile: (frames, channels) → torchaudio: (channels, frames)
            return torch.from_numpy(data.T).contiguous(), sr

        def _save(path, tensor, sample_rate, *a, **k):
            arr = tensor.detach().cpu().numpy() if hasattr(tensor, "detach") else np.asarray(tensor)
            arr = np.asarray(arr, dtype="float32")
            if arr.ndim == 2:        # (channels, frames) → (frames, channels)
                arr = arr.T
            sf.write(str(path), arr, int(sample_rate))

        torchaudio.load = _load
        torchaudio.save = _save
        _log("Đã vá torchaudio.load/save → soundfile (không cần torchcodec)")
    except Exception as e:
        _log(f"Không vá được torchaudio ({e})")


def _make_normalizer():
    """Trả về hàm chuẩn hoá text tiếng Việt (vinorm.TTSnorm) nếu có cài;
    không thì trả về hàm identity. F5-TTS-Vietnamese được train trên text đã
    chuẩn hoá nên dùng vinorm cho chất lượng tốt nhất khi có sẵn."""
    try:
        from vinorm import TTSnorm

        def _norm(t):
            try:
                return TTSnorm(t, unknown=False, lower=False, rule=True).strip()
            except Exception:
                return t
        _log("Chuẩn hoá text: vinorm.TTSnorm")
        return _norm
    except Exception:
        _log("Chuẩn hoá text: bỏ qua (không có vinorm)")
        return lambda t: t


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--texts-json",     required=True,  help="JSON [{index, text}]")
    parser.add_argument("--output-dir",     required=True,  help="Thư mục lưu line_NNNN.wav")
    parser.add_argument("--model-dir",      required=True,  help="Thư mục chứa checkpoint (.pt) + vocab.txt")
    parser.add_argument("--ckpt-file",      default="",     help="Đường dẫn checkpoint cụ thể (ghi đè auto-find)")
    parser.add_argument("--vocab-file",     default="",     help="Đường dẫn vocab.txt cụ thể (ghi đè auto-find)")
    parser.add_argument("--model",          default="F5TTS_Base", help="Tên kiến trúc model (config) — fork dùng F5TTS_Base")
    parser.add_argument("--reference",      required=True,  help="File audio giọng mẫu (nhân bản)")
    parser.add_argument("--reference-text", default="",     help="Lời thoại audio mẫu (rỗng = F5-TTS tự ASR)")
    parser.add_argument("--speed",          type=float, default=1.0, help="Tốc độ đọc (1.0 = bình thường)")
    parser.add_argument("--nfe-step",       type=int,   default=32)
    parser.add_argument("--device",         default="auto", help="auto | cuda | cpu")
    args = parser.parse_args()

    # Đọc danh sách text
    with open(args.texts_json, encoding="utf-8-sig") as f:
        items = json.load(f)

    if not items:
        print("ALL_DONE", flush=True)
        return

    model_dir = args.model_dir.strip()
    if not model_dir or not os.path.isdir(model_dir):
        print(f"ERROR:-1:model dir không tồn tại: {model_dir}", flush=True)
        sys.exit(2)

    ckpt_file  = args.ckpt_file.strip()  or _find_ckpt(model_dir)
    vocab_file = args.vocab_file.strip() or _find_vocab(model_dir)
    if not ckpt_file or not os.path.isfile(ckpt_file):
        print(f"ERROR:-1:không tìm thấy checkpoint (.pt/.safetensors) trong {model_dir}", flush=True)
        sys.exit(2)
    if not vocab_file or not os.path.isfile(vocab_file):
        print(f"ERROR:-1:không tìm thấy vocab.txt trong {model_dir}", flush=True)
        sys.exit(2)

    ref_audio = args.reference.strip()
    if not ref_audio or not os.path.isfile(ref_audio):
        print(f"ERROR:-1:không tìm thấy audio mẫu: {ref_audio}", flush=True)
        sys.exit(2)

    # Auto chọn thiết bị: có GPU NVIDIA/CUDA → dùng GPU; không → CPU.
    req = args.device.strip().lower()
    device = "cpu"
    if req in ("auto", "cuda"):
        try:
            import torch
            if torch.cuda.is_available():
                device = "cuda"
                _log(f"GPU: {torch.cuda.get_device_name(0)} → dùng CUDA")
            elif req == "cuda":
                _log("Yêu cầu CUDA nhưng không thấy GPU → dùng CPU")
        except Exception as e:
            _log(f"Không nạp được PyTorch CUDA ({e}) → dùng CPU")
    if device == "cpu":
        _log("Thiết bị: CPU")

    _log(f"Checkpoint: {os.path.basename(ckpt_file)} | vocab: {os.path.basename(vocab_file)}")
    _log("Đang load model F5-TTS-Vietnamese...")
    _patch_torchaudio()   # đọc/ghi audio bằng soundfile, không cần torchcodec
    from f5_tts.api import F5TTS
    f5 = F5TTS(
        model=args.model,
        ckpt_file=ckpt_file,
        vocab_file=vocab_file,
        device=device,
    )
    _log(f"Model loaded | device: {device}")

    normalize = _make_normalizer()
    ref_text  = args.reference_text.strip()
    if ref_text:
        ref_text = normalize(ref_text)
        _log("Chế độ: Nhân bản giọng (có lời thoại mẫu)")
    else:
        _log("Chế độ: Nhân bản giọng (tự ASR audio mẫu)")

    os.makedirs(args.output_dir, exist_ok=True)

    MAX_RETRIES = 3

    for item in items:
        idx  = item["index"]
        text = normalize(item["text"])

        out_wav = os.path.join(args.output_dir, f"line_{idx:04d}.wav")

        best_audio = None
        best_sr    = 24_000
        best_peak  = 0.0

        for attempt in range(MAX_RETRIES):
            try:
                wav, sr, _ = f5.infer(
                    ref_file=ref_audio,
                    ref_text=ref_text,   # rỗng → F5-TTS tự ASR audio mẫu
                    gen_text=text,
                    speed=args.speed,
                    nfe_step=args.nfe_step,
                    remove_silence=True,
                    seed=None if attempt == 0 else (attempt * 1234 + idx),
                )
                audio_np = np.asarray(wav, dtype="float32").reshape(-1)
                audio_np = np.nan_to_num(audio_np, nan=0.0, posinf=0.0, neginf=0.0)
                peak = float(np.abs(audio_np).max()) if audio_np.size else 0.0

                if peak > best_peak:
                    best_peak  = peak
                    best_audio = audio_np
                    best_sr    = int(sr)

                if peak > 1e-6:
                    break  # có âm thanh
                else:
                    print(f"WARN:{idx}:silent attempt {attempt + 1}/{MAX_RETRIES} "
                          f"(peak={peak:.2e})", flush=True)

            except Exception as e:
                print(f"WARN:{idx}:attempt {attempt + 1} error: {e}", flush=True)

        if best_audio is None or best_peak < 1e-6:
            print(f"ERROR:{idx}:audio silent sau {MAX_RETRIES} lần thử", flush=True)
            continue

        # Chuẩn hoá biên độ
        best_audio = (best_audio / best_peak * 0.95).astype("float32")
        sf.write(out_wav, best_audio, best_sr)
        print(f"DONE:{idx}", flush=True)

    print("ALL_DONE", flush=True)


if __name__ == "__main__":
    main()
