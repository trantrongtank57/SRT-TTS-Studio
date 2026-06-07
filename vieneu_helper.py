"""VieNeu-TTS batch voice clone helper — chạy bằng vieneu_env\\Scripts\\python.exe.

Mô hình: VieNeu-TTS (https://github.com/pnnbao97/VieNeu-TTS), mặc định v3 Turbo
(48 kHz). Chạy trên **GPU NVIDIA (CUDA + PyTorch)** — cần cài `vieneu[gpu]`.

Giao thức stdout (giống voxcpm_helper.py — app đọc từng dòng):
    DONE:{idx}            line_{idx:04d}.wav đã sẵn sàng
    ERROR:{idx}:{reason}  dòng lỗi (audio im lặng sau các lần thử)
    WARN:{idx}:{reason}   thử lại
    ALL_DONE              kết thúc batch
Dòng thông tin ghi ra stderr với tiền tố [VieNeu].
"""
import argparse
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
    print(f"[VieNeu] {msg}", file=sys.stderr, flush=True)


def _patch_hf_anon_token():
    """VieNeu v3 Turbo loader gọi hf_hub_download(..., token=True). huggingface_hub
    1.18+ NÉM lỗi LocalTokenNotFoundError khi token=True mà máy chưa lưu token —
    kể cả với repo PUBLIC (model VieNeu là public). Vá get_token_to_send để khi
    không có token thì gửi ẩn danh (None) thay vì raise → tải repo public bình thường,
    không cần tài khoản/đăng nhập HuggingFace."""
    try:
        from huggingface_hub.utils import _headers as _hfh
        _orig = _hfh.get_token_to_send

        def _safe(token):
            try:
                return _orig(token)
            except Exception:
                return None
        _hfh.get_token_to_send = _safe
    except Exception:
        pass


def _patch_torchaudio_load():
    """torch 2.11 mặc định giải mã audio qua torchcodec (cần FFmpeg DLL, hay lỗi
    'Could not load libtorchcodec' trên Windows). Vá torchaudio.load dùng soundfile
    để đọc audio mẫu (wav/flac/ogg/mp3) — giống voxcpm_helper, tránh phụ thuộc torchcodec."""
    try:
        import torch
        import torchaudio

        def _load(path, *a, **k):
            data, sr = sf.read(str(path), dtype="float32", always_2d=True)
            return torch.from_numpy(data.T), sr
        torchaudio.load = _load
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--texts-json",     required=True,  help="JSON [{index, text}]")
    parser.add_argument("--output-dir",     required=True,  help="Thư mục lưu line_NNNN.wav")
    parser.add_argument("--model-dir",      default="",     help="Thư mục/HF repo model VieNeu (rỗng = tự tải từ HuggingFace)")
    parser.add_argument("--onnx-dir",       default="",     help="Thư mục chứa file .onnx (bỏ qua tải HF, dùng cho CPU offline)")
    parser.add_argument("--reference",      default="",     help="File audio giọng mẫu (nhân bản)")
    parser.add_argument("--reference-text", default="",     help="Lời thoại audio mẫu (v3 Turbo bỏ qua)")
    parser.add_argument("--voice",          default="",     help="Tên giọng có sẵn (preset) — dùng khi không có audio mẫu")
    parser.add_argument("--emotion",        default="natural", help="natural | storytelling")
    parser.add_argument("--temperature",    type=float, default=0.8)
    parser.add_argument("--device",         default="auto", help="auto (GPU nếu có, không thì CPU) | cuda | cpu")
    args = parser.parse_args()

    # Đọc danh sách text
    with open(args.texts_json, encoding="utf-8-sig") as f:
        items = json.load(f)

    if not items:
        print("ALL_DONE", flush=True)
        return

    # Auto chọn thiết bị: có GPU NVIDIA/CUDA → dùng GPU (PyTorch, nhanh);
    # không có → tự rơi về CPU (ONNX torch-free, v3 Turbo vẫn chạy tốt).
    req = args.device.strip().lower()
    use_cuda = False
    if req in ("auto", "cuda"):
        try:
            import torch
            use_cuda = bool(torch.cuda.is_available())
            if use_cuda:
                _log(f"GPU: {torch.cuda.get_device_name(0)} → dùng CUDA (PyTorch)")
            elif req == "cuda":
                _log("Yêu cầu CUDA nhưng không thấy GPU → tự chuyển sang CPU (ONNX)")
        except Exception as e:
            _log(f"Không nạp được PyTorch CUDA ({e}) → dùng CPU (ONNX)")
    if not use_cuda:
        _log("Thiết bị: CPU (ONNX torch-free)")

    # Tham số khởi tạo model — GPU dùng backend pytorch, CPU dùng ONNX (mặc định)
    kwargs = {"device": "cuda" if use_cuda else "cpu"}
    if use_cuda:
        kwargs["backend"] = "pytorch"
    else:
        kwargs["backend"] = "onnx"
    model_dir = args.model_dir.strip()
    if model_dir and (os.path.isdir(model_dir) or "/" in model_dir):
        kwargs["backbone_repo"] = model_dir
        _log(f"Model: {model_dir}")
    else:
        _log("Model: mặc định (tự tải từ HuggingFace, cache lại lần sau)")
    if args.onnx_dir.strip() and os.path.isdir(args.onnx_dir.strip()):
        kwargs["onnx_dir"] = args.onnx_dir.strip()

    _log("Đang load model VieNeu-TTS...")
    _patch_hf_anon_token()    # cho phép tải model public không cần token HF
    _patch_torchaudio_load()  # đọc audio mẫu bằng soundfile, không cần torchcodec
    from vieneu import Vieneu
    tts = Vieneu(**kwargs)
    sample_rate = getattr(tts, "sample_rate", 48_000)
    _log(f"Model loaded. Sample rate: {sample_rate}Hz | device: {'cuda' if use_cuda else 'cpu'}")

    ref_audio = args.reference if args.reference and os.path.exists(args.reference) else None
    voice     = args.voice.strip() or None

    if ref_audio:
        _log("Chế độ: Nhân bản giọng (voice cloning từ audio mẫu)")
    elif voice:
        _log(f"Chế độ: Giọng có sẵn '{voice}'")
    else:
        _log("Chế độ: Giọng mặc định")

    # Tham số chung cho infer
    infer_kw = {"emotion": args.emotion, "temperature": args.temperature}
    if ref_audio:
        infer_kw["ref_audio"] = ref_audio
        if args.reference_text.strip():
            infer_kw["ref_text"] = args.reference_text.strip()
    elif voice:
        infer_kw["voice"] = voice

    os.makedirs(args.output_dir, exist_ok=True)

    MAX_RETRIES = 3

    for item in items:
        idx  = item["index"]
        text = item["text"]

        out_wav = os.path.join(args.output_dir, f"line_{idx:04d}.wav")

        best_audio = None
        best_peak  = 0.0

        for attempt in range(MAX_RETRIES):
            try:
                # Mỗi lần thử tăng nhẹ temperature để thoát local minimum
                kw = dict(infer_kw)
                kw["temperature"] = args.temperature + attempt * 0.1
                audio_np = tts.infer(text=text, **kw)

                audio_np = np.asarray(audio_np, dtype="float32").reshape(-1)
                audio_np = np.nan_to_num(audio_np, nan=0.0, posinf=0.0, neginf=0.0)
                peak = float(np.abs(audio_np).max()) if audio_np.size else 0.0

                if peak > best_peak:
                    best_peak  = peak
                    best_audio = audio_np

                if peak > 1e-6:
                    break  # có âm thanh, không cần thử lại
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
        sf.write(out_wav, best_audio, sample_rate)
        print(f"DONE:{idx}", flush=True)

    try:
        tts.close()
    except Exception:
        pass

    print("ALL_DONE", flush=True)


if __name__ == "__main__":
    main()
