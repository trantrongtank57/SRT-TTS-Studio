"""
videocr_helper.py — companion script for SRT TTS Studio

Prints:
  PROGRESS:<message>   — informational (piped to logbox)
  DONE:<output_path>   — OCR completed successfully
  ERROR:<message>      — fatal error

Tim paddleocr binary + model files theo thu tu:
  1. VIDEOCR_INSTALL_DIR env var (user chon)
  2. Thu muc chua script nay (portable / auto-download destination)
  3. C:/Program Files/VideOCR (fallback neu da cai installer)
"""

import sys
import os
import argparse
import urllib.request
import urllib.error
import json
import zipfile

# ── Locate CLI package ────────────────────────────────────────────────────────
VIDEOCR_CLI_DIR = os.environ.get(
    "VIDEOCR_CLI_DIR",
    r"C:\Users\os\Downloads\Compressed\VideOCR-1.5.1\VideOCR-1.5.1\CLI"
)

if VIDEOCR_CLI_DIR and os.path.isdir(VIDEOCR_CLI_DIR):
    if VIDEOCR_CLI_DIR not in sys.path:
        sys.path.insert(0, VIDEOCR_CLI_DIR)
else:
    print(f"ERROR:Khong tim thay thu muc VideOCR CLI: {VIDEOCR_CLI_DIR}", flush=True)
    sys.exit(1)

try:
    from videocr import save_subtitles_to_file
    import videocr.utils as _vutils
    import videocr.api as _vapi
except ImportError as _e:
    print(f"ERROR:Khong import duoc videocr ({_e}). Kiem tra VIDEOCR_CLI_DIR va cai dat deps.", flush=True)
    sys.exit(1)

# Download destination = same folder as this script
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

GITHUB_API = "https://api.github.com/repos/timminator/VideOCR/releases/latest"


# ── Search dir list ───────────────────────────────────────────────────────────
def _search_dirs() -> list:
    dirs = []
    env = os.environ.get("VIDEOCR_INSTALL_DIR", "").strip()
    if env:
        dirs.append(env)
    dirs.append(_SCRIPT_DIR)
    pf = r"C:\Program Files\VideOCR"
    if pf not in dirs:
        dirs.append(pf)
    return dirs


# ── Monkeypatch videocr.utils ─────────────────────────────────────────────────
def _patched_find_executable(program_name: str) -> str:
    ext = ".exe" if sys.platform == "win32" else ".bin"
    exe = f"{program_name}{ext}"
    for d in _search_dirs():
        if not os.path.isdir(d):
            continue
        for entry in os.listdir(d):
            if entry.lower().startswith(f"{program_name.lower()}-"):
                path = os.path.join(d, entry, exe)
                if os.path.isfile(path):
                    return path
    raise FileNotFoundError(f"Khong tim thay {exe} trong: {_search_dirs()}")


_orig_resolve = _vutils.resolve_model_dirs

def _patched_resolve_model_dirs(lang: str, use_server_model: bool):
    for d in _search_dirs():
        if os.path.isdir(os.path.join(d, "PaddleOCR.PP-OCRv5.support.files")):
            _orig_argv0 = sys.argv[0]
            sys.argv[0] = os.path.join(d, "_ph")
            try:
                return _orig_resolve(lang, use_server_model)
            finally:
                sys.argv[0] = _orig_argv0
    raise FileNotFoundError(f"Khong tim thay PaddleOCR.PP-OCRv5.support.files trong: {_search_dirs()}")


_vutils.find_executable = _patched_find_executable
_vutils.resolve_model_dirs = _patched_resolve_model_dirs
_vapi.utils.find_executable = _patched_find_executable
_vapi.utils.resolve_model_dirs = _patched_resolve_model_dirs


# ── Auto-download ─────────────────────────────────────────────────────────────
def _download_file(url: str, dest: str, label: str) -> None:
    """Download url -> dest, in progress every 10%."""
    last_pct = [-1]

    def _hook(count, block, total):
        if total <= 0:
            return
        pct = min(count * block * 100 // total, 100)
        if pct // 10 != last_pct[0] // 10:
            mb_done = count * block // 1_048_576
            mb_total = total // 1_048_576
            print(f"PROGRESS:  {label}: {pct}% ({mb_done}/{mb_total} MB)", flush=True)
            last_pct[0] = pct

    req = urllib.request.Request(url, headers={"User-Agent": "SRT-TTS-Studio/1.0"})
    urllib.request.urlretrieve(url, dest, reporthook=_hook)


def _already_have(program_name: str) -> bool:
    try:
        _patched_find_executable(program_name)
        return True
    except FileNotFoundError:
        return False


def _support_files_exist() -> bool:
    return any(
        os.path.isdir(os.path.join(d, "PaddleOCR.PP-OCRv5.support.files"))
        for d in _search_dirs()
    )


def _auto_download(use_gpu: bool) -> bool:
    """
    Fetch latest VideOCR release from GitHub, download & extract:
      - paddleocr-GPU-* or paddleocr-CPU-* binary zip
      - PaddleOCR.PP-OCRv5.support.files zip (model weights)
    Both extracted into _SCRIPT_DIR.
    Returns True on success.
    """
    print("PROGRESS:Dang lay thong tin release tu GitHub...", flush=True)
    try:
        req = urllib.request.Request(GITHUB_API, headers={"User-Agent": "SRT-TTS-Studio/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            release = json.loads(r.read())
    except Exception as exc:
        print(f"ERROR:Khong the ket noi GitHub API: {exc}", flush=True)
        return False

    tag = release.get("tag_name", "?")
    assets = release.get("assets", [])
    print(f"PROGRESS:Release {tag} — {len(assets)} files", flush=True)

    # Classify assets
    binary_asset = None
    support_asset = None
    for a in assets:
        name_lo = a["name"].lower()
        if not name_lo.endswith(".zip"):
            continue
        if "paddleocr" in name_lo and "support" not in name_lo:
            is_gpu = "gpu" in name_lo
            # Pick GPU asset if requested, CPU otherwise; prefer exact match
            if use_gpu and is_gpu:
                binary_asset = a
            elif not use_gpu and not is_gpu and "cpu" in name_lo:
                binary_asset = a
            elif binary_asset is None:
                binary_asset = a   # any paddleocr binary as fallback
        elif "support" in name_lo and "paddleocr" in name_lo:
            support_asset = a

    queue = []
    if not _already_have("paddleocr"):
        if binary_asset:
            queue.append(binary_asset)
        else:
            print("ERROR:Khong tim thay paddleocr binary asset tren GitHub release", flush=True)
            return False

    if not _support_files_exist():
        if support_asset:
            queue.append(support_asset)
        else:
            print("PROGRESS:Canh bao: khong tim thay support files asset — co the loi khi chay OCR", flush=True)

    if not queue:
        print("PROGRESS:Tat ca binary da co san, khong can tai them", flush=True)
        return True

    for a in queue:
        name = a["name"]
        url = a["browser_download_url"]
        size_mb = a.get("size", 0) / 1_048_576
        tmp = os.path.join(_SCRIPT_DIR, f"_dl_{name}")

        print(f"PROGRESS:Tai {name} ({size_mb:.0f} MB)...", flush=True)
        try:
            _download_file(url, tmp, name)
        except Exception as exc:
            print(f"ERROR:Loi khi tai {name}: {exc}", flush=True)
            if os.path.exists(tmp):
                os.remove(tmp)
            return False

        print(f"PROGRESS:Giai nen {name}...", flush=True)
        try:
            with zipfile.ZipFile(tmp, "r") as zf:
                zf.extractall(_SCRIPT_DIR)
        except Exception as exc:
            print(f"ERROR:Loi giai nen {name}: {exc}", flush=True)
            os.remove(tmp)
            return False
        os.remove(tmp)
        print(f"PROGRESS:{name} hoan tat", flush=True)

    return True


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video",            required=True)
    parser.add_argument("--output",           required=True)
    parser.add_argument("--lang",             default="vi")
    parser.add_argument("--ocr_engine",       default="paddleocr", choices=["paddleocr", "google_lens"])
    parser.add_argument("--use_gpu",          action="store_true")
    parser.add_argument("--use_fullframe",    action="store_true")
    parser.add_argument("--use_angle_cls",    action="store_true")
    parser.add_argument("--time_start",       default="0:00")
    parser.add_argument("--time_end",         default="")
    parser.add_argument("--conf_threshold",   type=int,   default=75)
    parser.add_argument("--sim_threshold",    type=int,   default=80)
    parser.add_argument("--ssim_threshold",   type=int,   default=92)
    parser.add_argument("--frames_to_skip",   type=int,   default=1)
    parser.add_argument("--brightness_threshold", type=int, default=None)
    parser.add_argument("--min_sub_duration", type=float, default=0.2)
    args = parser.parse_args()

    print(f"PROGRESS:Video: {os.path.basename(args.video)}", flush=True)
    print(f"PROGRESS:Engine={args.ocr_engine} | Lang={args.lang} | GPU={args.use_gpu}", flush=True)

    # Auto-download binary if missing
    needs_dl = not _already_have("paddleocr") or not _support_files_exist()
    if needs_dl:
        print("PROGRESS:Chua tim thay VideOCR binary — bat dau tu dong tai...", flush=True)
        if not _auto_download(use_gpu=args.use_gpu):
            sys.exit(1)
        # Verify after download
        try:
            _patched_find_executable("paddleocr")
        except FileNotFoundError as exc:
            print(f"ERROR:Van khong tim thay binary sau khi tai: {exc}", flush=True)
            sys.exit(1)
    else:
        print(f"PROGRESS:Tim thay binary tai: {_search_dirs()}", flush=True)

    try:
        save_subtitles_to_file(
            video_path=args.video,
            file_path=args.output,
            ocr_engine=args.ocr_engine,
            lang=args.lang,
            time_start=args.time_start,
            time_end=args.time_end,
            conf_threshold=args.conf_threshold,
            sim_threshold=args.sim_threshold,
            use_fullframe=args.use_fullframe,
            use_gpu=args.use_gpu,
            use_angle_cls=args.use_angle_cls,
            ssim_threshold=args.ssim_threshold,
            frames_to_skip=args.frames_to_skip,
            brightness_threshold=args.brightness_threshold,
            min_subtitle_duration_sec=args.min_sub_duration,
        )
        if os.path.isfile(args.output):
            print(f"DONE:{args.output}", flush=True)
        else:
            print(f"ERROR:OCR hoan tat nhung file SRT khong duoc tao: {args.output}", flush=True)
            sys.exit(1)
    except Exception as exc:
        print(f"ERROR:{exc}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
