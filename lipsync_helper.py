# -*- coding: utf-8 -*-
"""
lipsync_helper.py — Khớp khẩu hình (lip-sync) cho video đã lồng tiếng.

Chạy như SUBPROCESS bởi SRT TTS Studio (không import vào app). Bọc quanh
Wav2Lip (https://github.com/Rudrabha/Wav2Lip): nhận 1 video có KHUÔN MẶT + 1
đường TIẾNG MỚI (wav/mp3/mp4) rồi sinh video mới với miệng khớp tiếng mới.

Vì Wav2Lip là 1 REPO (không phải package pip), helper này ủy quyền cho chính
`inference.py` của repo (chạy bằng cùng interpreter = lipsync_env python) để bảo
đảm đúng như thượng nguồn, rồi DỊCH output của nó sang giao thức tiến trình chuẩn
mà app đang dùng:

    PROGRESS:N:M          — đã xong N/M (thanh tiến trình)
    PROGRESS_MSG:<text>   — dòng trạng thái (đọc frame, load model…)
    WARN:<text>           — cảnh báo, vẫn chạy tiếp
    ERROR:<text>          — lỗi (khuôn mặt không thấy, thiếu model…)
    DONE:<path>           — xong, path video kết quả

Cách gọi (app dựng sẵn):
    lipsync_env\\Scripts\\python.exe lipsync_helper.py \
        --repo-dir  <Wav2Lip repo> \
        --checkpoint <wav2lip_gan.pth> \
        --face      <video khuôn mặt> \
        --audio     <wav/mp3/mp4 tiếng mới> \
        --out       <video kết quả .mp4> \
        [--pads 0 10 0 0] [--resize-factor 1] [--wav2lip-batch-size 128] \
        [--nosmooth] [--device auto|cpu|cuda] [--ffmpeg <ffmpeg.exe>]

    --selftest : kiểm tra môi trường (python/torch/cuda + repo + checkpoint +
                 model dò mặt s3fd) rồi thoát — KHÔNG sinh video.
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
import time

# stdout UTF-8 để log tiếng Việt không vỡ trên Windows cp1252 (giống các helper khác)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def _emit(kind, text=""):
    print(f"{kind}:{text}", flush=True)


def _find_s3fd(repo_dir):
    """Model dò khuôn mặt s3fd của Wav2Lip (thường thiếu nhất). Trả path hoặc ''."""
    cands = [
        os.path.join(repo_dir, "face_detection", "detection", "sfd", "s3fd.pth"),
        os.path.join(repo_dir, "checkpoints", "s3fd.pth"),
    ]
    for c in cands:
        if os.path.isfile(c):
            return c
    return ""


def _find_inference(repo_dir):
    for name in ("inference.py",):
        p = os.path.join(repo_dir, name)
        if os.path.isfile(p):
            return p
    return ""


def _torch_report():
    """(python, torch_ver, cuda_bool_or_None). torch chưa cài → torch_ver=None."""
    try:
        import torch
        return sys.version.split()[0], torch.__version__, bool(torch.cuda.is_available())
    except Exception as e:
        return sys.version.split()[0], None, None


def selftest(args):
    py, tv, cuda = _torch_report()
    _emit("PROGRESS_MSG", f"python={py}  torch={tv}  cuda={cuda}")
    ok = True
    repo = args.repo_dir or ""
    if not repo or not os.path.isdir(repo):
        _emit("ERROR", f"Không thấy thư mục Wav2Lip repo: {repo!r}")
        ok = False
    else:
        inf = _find_inference(repo)
        if not inf:
            _emit("ERROR", f"Không thấy inference.py trong repo: {repo}")
            ok = False
        else:
            _emit("PROGRESS_MSG", f"inference.py OK: {inf}")
        s3 = _find_s3fd(repo)
        if s3:
            _emit("PROGRESS_MSG", f"s3fd (dò mặt) OK: {s3}")
        else:
            _emit("ERROR",
                  "Thiếu model dò khuôn mặt s3fd.pth — tải về đặt vào "
                  "face_detection/detection/sfd/s3fd.pth "
                  "(xem README Wav2Lip).")
            ok = False
    ck = args.checkpoint or ""
    if not ck or not os.path.isfile(ck):
        _emit("ERROR", f"Không thấy checkpoint Wav2Lip (.pth): {ck!r}")
        ok = False
    else:
        _emit("PROGRESS_MSG", f"checkpoint OK: {ck}")
    if tv is None:
        _emit("ERROR", "Chưa cài torch trong lipsync_env.")
        ok = False
    if ok:
        _emit("DONE", "selftest-ok")
    else:
        sys.exit(2)


# tqdm/print của Wav2Lip: 'i/total' rải rác + các câu trạng thái đã biết.
_FRAC_RE = re.compile(r"(\d+)\s*/\s*(\d+)")
_NFRAMES_RE = re.compile(r"Number of frames available for inference:\s*(\d+)")
_PHASE_MARKERS = (
    "Reading video frames", "Number of frames", "Length of mel chunks",
    "Load audio", "Model loaded", "Loading model", "Face detection",
    "Recovering from OOM",
)


def run(args):
    repo = os.path.abspath(args.repo_dir)
    inf = _find_inference(repo)
    if not inf:
        _emit("ERROR", f"Không thấy inference.py trong repo Wav2Lip: {repo}")
        sys.exit(2)
    if not os.path.isfile(args.checkpoint):
        _emit("ERROR", f"Không thấy checkpoint: {args.checkpoint}")
        sys.exit(2)
    if not os.path.isfile(args.face):
        _emit("ERROR", f"Không thấy video khuôn mặt: {args.face}")
        sys.exit(2)
    if not os.path.isfile(args.audio):
        _emit("ERROR", f"Không thấy file tiếng: {args.audio}")
        sys.exit(2)
    if not _find_s3fd(repo):
        _emit("ERROR",
              "Thiếu model dò mặt s3fd.pth trong "
              "face_detection/detection/sfd/ — không dò được khuôn mặt.")
        sys.exit(2)

    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    # Wav2Lip ghi tạm vào ./temp và ./results (tương đối theo cwd=repo)
    for d in ("temp", "results"):
        try:
            os.makedirs(os.path.join(repo, d), exist_ok=True)
        except Exception:
            pass

    cmd = [sys.executable, inf,
           "--checkpoint_path", os.path.abspath(args.checkpoint),
           "--face", os.path.abspath(args.face),
           "--audio", os.path.abspath(args.audio),
           "--outfile", out,
           "--wav2lip_batch_size", str(args.wav2lip_batch_size)]
    if args.resize_factor and args.resize_factor > 1:
        cmd += ["--resize_factor", str(args.resize_factor)]
    if args.pads:
        cmd += ["--pads"] + [str(x) for x in args.pads]
    if args.nosmooth:
        cmd += ["--nosmooth"]

    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"
    # ffmpeg: Wav2Lip gọi `ffmpeg` từ PATH — nối thư mục ffmpeg do app truyền vào
    if args.ffmpeg and os.path.isfile(args.ffmpeg):
        env["PATH"] = os.path.dirname(os.path.abspath(args.ffmpeg)) + os.pathsep + env.get("PATH", "")
    # device
    if args.device == "cpu":
        env["CUDA_VISIBLE_DEVICES"] = ""

    _emit("PROGRESS_MSG", "Bắt đầu Wav2Lip (dò mặt + khớp miệng)…")
    # QUAN TRỌNG — KHÔNG dùng stdout=PIPE: inference.py gọi ffmpeg mux cuối qua
    # subprocess.call(shell=True); ffmpeg con thừa kế cùng pipe stdout/stderr và
    # BỊ DEADLOCK (0% CPU, treo vô hạn — đã bắt được khi test, standalone thì
    # chạy ngay). Cho con ghi thẳng ra FILE LOG rồi tail file → hết pipe, hết
    # deadlock. stdin=DEVNULL để ffmpeg không chờ lệnh tương tác.
    tail = []                      # giữ vài dòng cuối để báo lỗi có ngữ cảnh
    state = {"total": 0, "last_emit": 0.0}

    def _handle(line):
        line = line.strip()
        if not line:
            return
        tail.append(line)
        if len(tail) > 12:
            tail.pop(0)
        m = _NFRAMES_RE.search(line)
        if m:
            state["total"] = int(m.group(1))
            _emit("PROGRESS_MSG", line)
            return
        if any(k in line for k in _PHASE_MARKERS):
            _emit("PROGRESS_MSG", line)
            return
        mm = _FRAC_RE.search(line)
        if mm:
            done, tot = int(mm.group(1)), int(mm.group(2))
            now = time.time()
            if now - state["last_emit"] > 0.4 and tot > 0:
                _emit("PROGRESS", f"{min(done, tot)}:{tot}")
                state["last_emit"] = now
            return
        low = line.lower()
        if "face not detected" in low or "traceback" in low or "error" in low:
            _emit("WARN", line)

    logf = tempfile.NamedTemporaryFile(
        prefix="wav2lip_log_", suffix=".txt", delete=False, mode="w",
        encoding="utf-8", errors="replace")
    log_path = logf.name
    rc = 2
    try:
        try:
            proc = subprocess.Popen(
                cmd, cwd=repo,
                stdin=subprocess.DEVNULL,
                stdout=logf, stderr=subprocess.STDOUT,
                env=env, creationflags=CREATE_NO_WINDOW)
        except Exception as e:
            _emit("ERROR", f"Không khởi động được inference.py: {e}")
            sys.exit(2)
        # Tail file log: tqdm dùng '\r' nên tách theo cả \r lẫn \n
        rbuf = ""
        with open(log_path, "r", encoding="utf-8", errors="replace") as rf:
            while True:
                chunk = rf.read()
                if chunk:
                    rbuf += chunk
                    parts = re.split(r"[\r\n]+", rbuf)
                    rbuf = parts.pop()          # phần cuối có thể chưa trọn dòng
                    for ln in parts:
                        _handle(ln)
                elif proc.poll() is not None:
                    if rbuf.strip():
                        _handle(rbuf)
                    break
                else:
                    time.sleep(0.3)
        rc = proc.returncode
    finally:
        try:
            logf.close()
        except Exception:
            pass
        try:
            os.remove(log_path)
        except Exception:
            pass
    total = state["total"]
    if rc == 0 and os.path.isfile(out) and os.path.getsize(out) > 1024:
        _emit("PROGRESS", f"{total or 1}:{total or 1}")
        _emit("DONE", out)
        return
    # Thất bại — cố đưa ra nguyên nhân dễ hiểu
    ctx = " | ".join(tail[-6:])
    if any("face not detected" in t.lower() for t in tail):
        _emit("ERROR",
              "Wav2Lip không tìm thấy khuôn mặt trong MỌI khung hình. Dùng video "
              "cận cảnh 1 khuôn mặt rõ, hoặc tăng --pads. Chi tiết: " + ctx)
    else:
        _emit("ERROR", f"Wav2Lip thất bại (exit {rc}). {ctx}")
    sys.exit(2)


def main():
    ap = argparse.ArgumentParser(description="Wav2Lip lip-sync wrapper")
    ap.add_argument("--repo-dir", default="")
    ap.add_argument("--checkpoint", default="")
    ap.add_argument("--face", default="")
    ap.add_argument("--audio", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--pads", type=int, nargs=4, default=[0, 10, 0, 0],
                    help="top bottom left right (mặc định 0 10 0 0 — chừa cằm)")
    ap.add_argument("--resize-factor", type=int, default=1)
    ap.add_argument("--wav2lip-batch-size", type=int, default=128)
    ap.add_argument("--nosmooth", action="store_true")
    ap.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    ap.add_argument("--ffmpeg", default="")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        selftest(args)
        return
    for req, name in ((args.repo_dir, "--repo-dir"), (args.checkpoint, "--checkpoint"),
                      (args.face, "--face"), (args.audio, "--audio"),
                      (args.out, "--out")):
        if not req:
            _emit("ERROR", f"Thiếu tham số bắt buộc {name}")
            sys.exit(2)
    run(args)


if __name__ == "__main__":
    main()
