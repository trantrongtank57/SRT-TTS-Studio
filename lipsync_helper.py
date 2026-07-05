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
import shutil
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


def _region_box(region, W, H):
    """Vùng khuôn mặt cần khớp (đa mặt): trả (x, y, w, h) CHẴN pixel, hoặc None.
    left/right = nửa trái/phải (2 người cạnh nhau); center = giữa; top/bottom =
    nửa trên/dưới. Wav2Lip chỉ dò 1 mặt/khung → crop vùng còn 1 mặt rồi dán lại."""
    ev = lambda v: int(v) - (int(v) % 2)          # toạ độ: chẵn, cho phép 0
    evd = lambda v: max(2, int(v) - (int(v) % 2))  # kích thước: chẵn, ≥2
    region = (region or "").lower()
    if region == "left":
        x, y, w, h = 0, 0, W // 2, H
    elif region == "right":
        x, y, w, h = W // 2, 0, W - W // 2, H
    elif region == "center":
        x, y, w, h = W // 4, 0, W // 2, H
    elif region == "top":
        x, y, w, h = 0, 0, W, H // 2
    elif region == "bottom":
        x, y, w, h = 0, H // 2, W, H - H // 2
    else:
        return None
    return (ev(x), ev(y), evd(w), evd(h))


def _probe_video(path):
    """(W, H, fps, nframes, duration_s) qua cv2. Lỗi → (0,0,25.0,0,0.0)."""
    try:
        import cv2
        cap = cv2.VideoCapture(os.path.abspath(path))
        W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
        cap.release()
        if fps <= 0:
            fps = 25.0
        return W, H, fps, n, (n / fps if n else 0.0)
    except Exception:
        return 0, 0, 25.0, 0, 0.0


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

    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"
    # ffmpeg: Wav2Lip gọi `ffmpeg` từ PATH — nối thư mục ffmpeg do app truyền vào
    if args.ffmpeg and os.path.isfile(args.ffmpeg):
        env["PATH"] = os.path.dirname(os.path.abspath(args.ffmpeg)) + os.pathsep + env.get("PATH", "")
    if args.device == "cpu":
        env["CUDA_VISIBLE_DEVICES"] = ""
    ffmpeg = args.ffmpeg if (args.ffmpeg and os.path.isfile(args.ffmpeg)) else "ffmpeg"

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
            if tot > 0 and now - state["last_emit"] > 0.4:
                gt = state.get("global_total") or 0
                if gt > 0:
                    # chế độ chia đoạn: quy đổi tiến độ trong-đoạn về tổng thể
                    frac = min(done, tot) / tot
                    g = state.get("offset", 0) + int(frac * state.get("chunk_frames", tot))
                    g = max(state.get("max_prog", 0), min(g, gt))
                    state["max_prog"] = g
                    _emit("PROGRESS", f"{g}:{gt}")
                else:
                    _emit("PROGRESS", f"{min(done, tot)}:{tot}")
                state["last_emit"] = now
            return
        low = line.lower()
        if "face not detected" in low or "traceback" in low or "error" in low:
            _emit("WARN", line)

    def _wav2lip_once(face_video, outfile, audio_path=None):
        """Chạy inference.py 1 lần trên face_video → outfile. → mã thoát (rc).
        KHÔNG dùng stdout=PIPE: inference.py gọi ffmpeg mux cuối qua
        subprocess.call(shell=True), ffmpeg con thừa kế pipe → DEADLOCK 0% CPU
        (đã bắt được khi test). Cho con ghi ra FILE LOG rồi tail; stdin=DEVNULL."""
        cmd = [sys.executable, inf,
               "--checkpoint_path", os.path.abspath(args.checkpoint),
               "--face", os.path.abspath(face_video),
               "--audio", os.path.abspath(audio_path or args.audio),
               "--outfile", os.path.abspath(outfile),
               "--wav2lip_batch_size", str(args.wav2lip_batch_size),
               "--face_det_batch_size", str(args.face_det_batch_size)]
        if args.resize_factor and args.resize_factor > 1:
            cmd += ["--resize_factor", str(args.resize_factor)]
        if args.pads:
            cmd += ["--pads"] + [str(x) for x in args.pads]
        if args.nosmooth:
            cmd += ["--nosmooth"]
        logf = tempfile.NamedTemporaryFile(
            prefix="wav2lip_log_", suffix=".txt", delete=False, mode="w",
            encoding="utf-8", errors="replace")
        log_path = logf.name
        rc = 2
        try:
            try:
                proc = subprocess.Popen(
                    cmd, cwd=repo, stdin=subprocess.DEVNULL,
                    stdout=logf, stderr=subprocess.STDOUT,
                    env=env, creationflags=CREATE_NO_WINDOW)
            except Exception as e:
                _emit("ERROR", f"Không khởi động được inference.py: {e}")
                return 2
            rbuf = ""      # tqdm dùng '\r' nên tách theo cả \r lẫn \n
            with open(log_path, "r", encoding="utf-8", errors="replace") as rf:
                while True:
                    chunk = rf.read()
                    if chunk:
                        rbuf += chunk
                        parts = re.split(r"[\r\n]+", rbuf)
                        rbuf = parts.pop()
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
        return rc

    def _fail(rc):
        ctx = " | ".join(tail[-6:])
        if any("face not detected" in t.lower() for t in tail):
            _emit("ERROR",
                  "Wav2Lip không tìm thấy khuôn mặt trong MỌI khung hình. Dùng "
                  "video cận cảnh 1 khuôn mặt rõ, tăng --pads, hoặc chọn đúng "
                  "vùng mặt (--region). Chi tiết: " + ctx)
        else:
            _emit("ERROR", f"Wav2Lip thất bại (exit {rc}). {ctx}")
        sys.exit(2)

    def _done(path):
        gt = state.get("global_total") or state.get("total") or 1
        _emit("PROGRESS", f"{gt}:{gt}")
        _emit("DONE", path)

    def _ff(cmd_tail, timeout=36000):
        """Chạy 1 lệnh ffmpeg (im lặng) → CompletedProcess."""
        return subprocess.run(
            [ffmpeg, "-y", "-v", "error"] + cmd_tail,
            stdin=subprocess.DEVNULL, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout,
            creationflags=CREATE_NO_WINDOW)

    def _run_full(out):
        """Chế độ cả-khung: HẠ độ phân giải + CHIA ĐOẠN trước khi đưa vào
        Wav2Lip — vì inference.py nạp TOÀN BỘ khung hình vào RAM cùng lúc
        (video 1080p dài → tràn RAM → Windows ghi pagefile → nghẽn đĩa)."""
        import math
        W, H, fps, nframes, dur = _probe_video(args.face)
        mh = args.max_height or 0
        chunk_s = args.chunk_seconds or 0
        do_scale = mh > 0 and H > mh
        scale_tail = (["-vf", f"scale=-2:{mh}:flags=bicubic"] if do_scale else [])
        state["global_total"] = 0

        # Video ngắn hoặc không đọc được thời lượng → chạy 1 lần (vẫn hạ nét nếu cần)
        if chunk_s <= 0 or dur <= 0 or dur <= chunk_s * 1.5:
            face_in, tmpd = args.face, None
            if do_scale:
                tmpd = tempfile.mkdtemp(prefix="wav2lip_scale_")
                face_in = os.path.join(tmpd, "scaled.mp4")
                _emit("PROGRESS_MSG",
                      f"Hạ độ phân giải {W}x{H} → cao {mh}px cho nhẹ RAM…")
                r = _ff(["-i", os.path.abspath(args.face)] + scale_tail +
                        ["-c:v", "libx264", "-crf", "18", "-preset", "ultrafast",
                         "-pix_fmt", "yuv420p", "-c:a", "copy", face_in])
                if r.returncode != 0 or not os.path.isfile(face_in):
                    _emit("WARN", f"Hạ độ phân giải lỗi, dùng gốc: {(r.stderr or '')[-160:]}")
                    face_in = args.face
            try:
                _emit("PROGRESS_MSG", "Bắt đầu Wav2Lip (dò mặt + khớp miệng)…")
                rc = _wav2lip_once(face_in, out)
                if rc == 0 and os.path.isfile(out) and os.path.getsize(out) > 1024:
                    _done(out)
                    return
                _fail(rc)
            finally:
                if tmpd:
                    shutil.rmtree(tmpd, ignore_errors=True)
            return

        # ── Chia đoạn: cắt (kèm hạ nét) → Wav2Lip từng đoạn → nối lại ──
        nseg = int(math.ceil(dur / chunk_s))
        state["global_total"] = nframes if nframes > 0 else int(dur * fps)
        state["offset"] = 0
        state["max_prog"] = 0
        _emit("PROGRESS_MSG",
              f"Chia {dur:.0f}s → {nseg} đoạn × {chunk_s}s"
              + (f", hạ xuống {mh}px" if do_scale else "")
              + " (chống tràn RAM)…")
        tmpd = tempfile.mkdtemp(prefix="wav2lip_seg_")
        seg_outs = []
        try:
            for i in range(nseg):
                t0 = i * chunk_s
                seg_dur = min(float(chunk_s), dur - t0)
                if seg_dur <= 0.05:
                    break
                seg_vid = os.path.join(tmpd, f"in_{i:04d}.mp4")
                seg_wav = os.path.join(tmpd, f"in_{i:04d}.wav")
                seg_out = os.path.join(tmpd, f"out_{i:04d}.mp4")
                _emit("PROGRESS_MSG", f"Đoạn {i + 1}/{nseg} — cắt + khớp khẩu hình…")
                rv = _ff(["-ss", f"{t0:.3f}", "-i", os.path.abspath(args.face),
                          "-t", f"{seg_dur:.3f}", "-an"] + scale_tail +
                         ["-c:v", "libx264", "-crf", "18", "-preset", "ultrafast",
                          "-pix_fmt", "yuv420p", seg_vid])
                if rv.returncode != 0 or not os.path.isfile(seg_vid):
                    _emit("ERROR", f"Cắt đoạn {i + 1} lỗi: {(rv.stderr or '')[-180:]}")
                    sys.exit(2)
                ra = _ff(["-ss", f"{t0:.3f}", "-i", os.path.abspath(args.audio),
                          "-t", f"{seg_dur:.3f}", "-vn", "-ac", "1", "-ar",
                          "16000", seg_wav])
                if ra.returncode != 0 or not os.path.isfile(seg_wav):
                    _emit("ERROR", f"Cắt tiếng đoạn {i + 1} lỗi: {(ra.stderr or '')[-180:]}")
                    sys.exit(2)
                state["chunk_frames"] = max(1, int(seg_dur * fps))
                rc = _wav2lip_once(seg_vid, seg_out, seg_wav)
                if rc != 0 or not (os.path.isfile(seg_out) and os.path.getsize(seg_out) > 1024):
                    # FAIL-OPEN theo đoạn: đoạn này khớp lỗi (vd không khung nào có
                    # mặt) → GIỮ NGUYÊN đoạn gốc, không làm chết cả video. Các đoạn
                    # còn lại vẫn được khớp khẩu hình.
                    _emit("WARN", f"Đoạn {i + 1}/{nseg} không khớp được "
                                  "(không thấy mặt?) — giữ nguyên đoạn gốc.")
                    try:
                        shutil.copyfile(seg_vid, seg_out)
                    except Exception:
                        seg_out = seg_vid
                seg_outs.append(seg_out)
                state["offset"] = min(state["global_total"],
                                      state["offset"] + state["chunk_frames"])
                state["max_prog"] = state["offset"]
                for f in (seg_vid, seg_wav):   # xoá input đoạn ngay → đỡ tốn đĩa
                    if f == seg_out:           # trừ khi đang dùng làm output đoạn
                        continue
                    try:
                        os.remove(f)
                    except Exception:
                        pass
            if not seg_outs:
                _emit("ERROR", "Không tạo được đoạn nào để khớp khẩu hình.")
                sys.exit(2)
            listf = os.path.join(tmpd, "concat.txt")
            with open(listf, "w", encoding="utf-8") as lf:
                for p in seg_outs:
                    lf.write("file '" + p.replace("\\", "/").replace("'", "'\\''") + "'\n")
            _emit("PROGRESS_MSG", f"Nối {len(seg_outs)} đoạn + ghép tiếng gốc…")
            # video = nối các đoạn (copy); audio = LẤY LẠI tiếng gốc chất lượng đầy đủ
            base = ["-f", "concat", "-safe", "0", "-i", listf,
                    "-i", os.path.abspath(args.audio),
                    "-map", "0:v:0", "-map", "1:a:0?",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart"]
            r2 = _ff(base + ["-c:v", "copy", out])
            if r2.returncode != 0 or not (os.path.isfile(out) and os.path.getsize(out) > 1024):
                r3 = _ff(base + ["-c:v", "libx264", "-crf", "18", "-preset",
                                 "veryfast", "-pix_fmt", "yuv420p", out])
                if r3.returncode != 0 or not (os.path.isfile(out) and os.path.getsize(out) > 1024):
                    _emit("ERROR", f"Nối đoạn lỗi: {(r3.stderr or r2.stderr or '')[-200:]}")
                    sys.exit(2)
            _done(out)
        finally:
            shutil.rmtree(tmpd, ignore_errors=True)

    region = (args.region or "full").lower()
    if region == "full":
        _run_full(out)
        return

    # ── Chế độ ĐA MẶT: crop vùng chọn (còn 1 mặt) → Wav2Lip → dán ngược ──
    try:
        import cv2
        cap = cv2.VideoCapture(os.path.abspath(args.face))
        W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
    except Exception as e:
        _emit("ERROR", f"Không đọc được kích thước video: {e}")
        sys.exit(2)
    box = _region_box(region, W, H)
    if not box or W <= 0 or H <= 0:
        _emit("ERROR", f"Vùng '{region}' không hợp lệ (khung {W}x{H}).")
        sys.exit(2)
    x, y, w, h = box
    _emit("PROGRESS_MSG",
          f"Đa mặt: cắt vùng '{region}' {w}x{h} @({x},{y}) rồi khớp khẩu hình…")
    tmpd = tempfile.mkdtemp(prefix="wav2lip_crop_")
    crop_vid = os.path.join(tmpd, "crop.mp4")
    synced = os.path.join(tmpd, "synced.mp4")
    try:
        r1 = subprocess.run(
            [ffmpeg, "-y", "-v", "error", "-i", os.path.abspath(args.face),
             "-filter:v", f"crop={w}:{h}:{x}:{y}", "-an",
             "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", crop_vid],
            stdin=subprocess.DEVNULL, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=36000,
            creationflags=CREATE_NO_WINDOW)
        if r1.returncode != 0 or not os.path.isfile(crop_vid):
            _emit("ERROR", f"Cắt vùng lỗi: {(r1.stderr or '')[-200:]}")
            sys.exit(2)
        rc = _wav2lip_once(crop_vid, synced)
        if rc != 0 or not (os.path.isfile(synced) and os.path.getsize(synced) > 1024):
            _fail(rc)
        _emit("PROGRESS_MSG", "Dán vùng đã khớp ngược vào video gốc…")
        r3 = subprocess.run(
            [ffmpeg, "-y", "-v", "error",
             "-i", os.path.abspath(args.face), "-i", synced,
             "-filter_complex", f"[0:v][1:v]overlay={x}:{y}[v]",
             "-map", "[v]", "-map", "1:a:0?",
             "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
             "-c:a", "aac", "-b:a", "192k",
             "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
            stdin=subprocess.DEVNULL, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=36000,
            creationflags=CREATE_NO_WINDOW)
        if r3.returncode == 0 and os.path.isfile(out) and os.path.getsize(out) > 1024:
            _done(out)
            return
        _emit("ERROR", f"Dán ngược lỗi: {(r3.stderr or '')[-200:]}")
        sys.exit(2)
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)


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
    ap.add_argument("--max-height", type=int, default=720,
                    help="hạ video xuống tối đa chiều cao này TRƯỚC khi khớp "
                         "(chống tràn RAM; 0 = giữ nguyên độ phân giải)")
    ap.add_argument("--chunk-seconds", type=int, default=30,
                    help="chia video thành đoạn dài ngần này giây, khớp từng "
                         "đoạn rồi nối (chặn RAM cho video dài; 0 = không chia)")
    ap.add_argument("--wav2lip-batch-size", type=int, default=16,
                    help="batch model Wav2Lip trên GPU (giảm nếu tràn VRAM; "
                         "128 gốc quá nặng cho GPU 8GB → tràn sang shared RAM)")
    ap.add_argument("--face-det-batch-size", type=int, default=4,
                    help="batch dò mặt S3FD trên GPU (thủ phạm chính ngốn VRAM; "
                         "giảm nếu tràn)")
    ap.add_argument("--nosmooth", action="store_true")
    ap.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    ap.add_argument("--ffmpeg", default="")
    ap.add_argument("--region", default="full",
                    choices=["full", "left", "right", "center", "top", "bottom"],
                    help="đa mặt: chỉ khớp mặt ở vùng này (crop→sync→dán ngược)")
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
