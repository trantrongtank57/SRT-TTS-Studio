# -*- coding: utf-8 -*-
"""
faceenhance_helper.py — Làm nét khuôn mặt trong video bằng GFPGAN.

Chạy như SUBPROCESS bởi SRT TTS Studio (không import vào app), trong lipsync_env
(cùng env Wav2Lip — dùng lại torch/GPU). Dùng để "chữa" đầu ra Wav2Lip: vùng
miệng Wav2Lip render ở 96px nên mờ; GFPGAN phục hồi từng khung → mặt nét như
thật. Cũng dùng độc lập cho video bất kỳ.

Giao thức stdout chuẩn của app:
    PROGRESS:N:M          — đã xử lý N/M khung
    PROGRESS_MSG:<text>   — trạng thái
    WARN:<text>           — cảnh báo, chạy tiếp
    ERROR:<text>          — lỗi
    DONE:<path>           — xong, video kết quả

Cách gọi:
    lipsync_env\\Scripts\\python.exe faceenhance_helper.py \
        --input <video> --output <video ra> \
        --model <GFPGANv1.4.pth> --ffmpeg <ffmpeg.exe> \
        [--device auto|cpu|cuda] [--upscale 1] [--only-center-face]

    --selftest : kiểm tra gfpgan + model + torch/cuda rồi thoát.
"""

import argparse
import os
import subprocess
import sys
import tempfile
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def _emit(kind, text=""):
    print(f"{kind}:{text}", flush=True)


def _device(pref):
    try:
        import torch
        if pref == "cpu":
            return "cpu"
        if pref == "cuda":
            return "cuda"
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


def _make_restorer(model_path, upscale, device):
    # chdir về thư mục model để facexlib cache weights (gfpgan/weights/) ổn định
    # thay vì tải lại theo CWD mỗi lần.
    try:
        os.chdir(os.path.dirname(os.path.abspath(model_path)) or ".")
    except Exception:
        pass
    from gfpgan import GFPGANer
    return GFPGANer(model_path=os.path.abspath(model_path), upscale=upscale,
                    arch="clean", channel_multiplier=2, bg_upsampler=None,
                    device=device)


def selftest(args):
    dev = _device(args.device)
    try:
        import torch
        _emit("PROGRESS_MSG",
              f"python={sys.version.split()[0]} torch={torch.__version__} "
              f"cuda={torch.cuda.is_available()} device={dev}")
    except Exception as e:
        _emit("ERROR", f"Chưa cài torch: {e}")
        sys.exit(2)
    if not args.model or not os.path.isfile(args.model):
        _emit("ERROR", f"Không thấy model GFPGAN (.pth): {args.model!r}")
        sys.exit(2)
    try:
        import gfpgan  # noqa
        _emit("PROGRESS_MSG", "gfpgan import OK")
    except Exception as e:
        _emit("ERROR", f"Không import được gfpgan: {e} "
                       "(cài: pip install gfpgan; patch basicsr functional_tensor)")
        sys.exit(2)
    try:
        _make_restorer(args.model, 1, dev)
        _emit("PROGRESS_MSG", "GFPGANer init OK (model + facexlib weights sẵn sàng)")
    except Exception as e:
        _emit("ERROR", f"Không khởi tạo được GFPGANer: {e}")
        sys.exit(2)
    _emit("DONE", "selftest-ok")


def run(args):
    import cv2  # opencv-python (đã có trong lipsync_env)
    if not os.path.isfile(args.input):
        _emit("ERROR", f"Không thấy video vào: {args.input}")
        sys.exit(2)
    if not args.model or not os.path.isfile(args.model):
        _emit("ERROR", f"Không thấy model GFPGAN: {args.model!r}")
        sys.exit(2)
    ffmpeg = args.ffmpeg if (args.ffmpeg and os.path.isfile(args.ffmpeg)) else "ffmpeg"
    dev = _device(args.device)
    out = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    _emit("PROGRESS_MSG", f"Khởi tạo GFPGAN (device={dev}, upscale={args.upscale})…")
    try:
        restorer = _make_restorer(args.model, args.upscale, dev)
    except Exception as e:
        _emit("ERROR", f"Không khởi tạo GFPGAN: {e}")
        sys.exit(2)

    cap = cv2.VideoCapture(os.path.abspath(args.input))
    if not cap.isOpened():
        _emit("ERROR", "OpenCV không mở được video vào.")
        sys.exit(2)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    ow, oh = W * args.upscale, H * args.upscale

    tmp_dir = tempfile.mkdtemp(prefix="faceenh_")
    tmp_vid = os.path.join(tmp_dir, "restored_silent.mp4")
    writer = cv2.VideoWriter(tmp_vid, cv2.VideoWriter_fourcc(*"mp4v"),
                             fps, (ow, oh))
    if not writer.isOpened():
        _emit("ERROR", "Không mở được VideoWriter (thiếu codec mp4v?).")
        cap.release()
        sys.exit(2)

    _emit("PROGRESS_MSG", f"Làm nét {total or '?'} khung ({W}x{H} @ {fps:.0f}fps)…")
    i = 0
    n_face = 0
    last = 0.0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            try:
                _cf, _rf, restored = restorer.enhance(
                    frame, has_aligned=False,
                    only_center_face=bool(args.only_center_face),
                    paste_back=True)
                if restored is None:
                    restored = frame
                else:
                    n_face += 1
            except Exception as e:
                if i == 0:
                    _emit("WARN", f"enhance lỗi khung đầu: {e} — giữ khung gốc")
                restored = frame
            if restored.shape[1] != ow or restored.shape[0] != oh:
                restored = cv2.resize(restored, (ow, oh))
            writer.write(restored)
            i += 1
            now = time.time()
            if now - last > 0.4:
                _emit("PROGRESS", f"{i}:{max(1, total or i)}")
                last = now
    finally:
        cap.release()
        writer.release()

    if i == 0:
        _emit("ERROR", "Không đọc được khung nào từ video.")
        sys.exit(2)
    _emit("PROGRESS_MSG", f"Đã làm nét {i} khung ({n_face} khung có mặt) — ghép audio…")

    # Ghép: video đã nét (im lặng) + audio GỐC của input (map optional '?' nên
    # video không tiếng vẫn chạy). stdin=DEVNULL để ffmpeg không treo chờ lệnh.
    cmd = [ffmpeg, "-y", "-v", "error",
           "-i", tmp_vid, "-i", os.path.abspath(args.input),
           "-map", "0:v:0", "-map", "1:a:0?",
           "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
           "-c:a", "aac", "-b:a", "192k",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    try:
        r = subprocess.run(cmd, stdin=subprocess.DEVNULL,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=36000,
                           creationflags=CREATE_NO_WINDOW)
    except Exception as e:
        _emit("ERROR", f"ffmpeg mux lỗi: {e}")
        sys.exit(2)
    finally:
        try:
            os.remove(tmp_vid)
            os.rmdir(tmp_dir)
        except Exception:
            pass
    if r.returncode != 0 or not (os.path.isfile(out) and os.path.getsize(out) > 1024):
        _emit("ERROR", f"ffmpeg ghép thất bại (exit {r.returncode}): "
                       f"{(r.stderr or '')[-300:]}")
        sys.exit(2)
    _emit("PROGRESS", f"{total or i}:{total or i}")
    _emit("DONE", out)


def main():
    ap = argparse.ArgumentParser(description="GFPGAN video face enhance")
    ap.add_argument("--input", default="")
    ap.add_argument("--output", default="")
    ap.add_argument("--model", default="")
    ap.add_argument("--ffmpeg", default="")
    ap.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    ap.add_argument("--upscale", type=int, default=1)
    ap.add_argument("--only-center-face", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest(args)
        return
    for req, name in ((args.input, "--input"), (args.output, "--output"),
                      (args.model, "--model")):
        if not req:
            _emit("ERROR", f"Thiếu tham số {name}")
            sys.exit(2)
    run(args)


if __name__ == "__main__":
    main()
