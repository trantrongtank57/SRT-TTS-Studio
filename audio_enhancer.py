"""Audio enhancement helper — chạy bằng voxcpm_env/Scripts/python.exe.

Pipeline (theo thứ tự):
  1. Tách nhạc   --separate : Demucs htdemucs, chỉ giữ stem vocals
  2. Giảm ồn     --denoise  : noisereduce spectral gating
  3. Lọc giọng   --filter   : bandpass scipy 80–8000 Hz
"""
import argparse
import io
import os
import sys
import tempfile

import numpy as np
import soundfile as sf

sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def load_mono(path):
    data, sr = sf.read(str(path), dtype="float32", always_2d=True)
    return data.mean(axis=1), sr


def load_stereo(path):
    """Đọc audio giữ 2 kênh → [2, T] (mono thì nhân đôi kênh)."""
    data, sr = sf.read(str(path), dtype="float32", always_2d=True)   # [T, C]
    if data.shape[1] == 1:
        data = np.repeat(data, 2, axis=1)
    return np.ascontiguousarray(data[:, :2].T), sr


def step_separate(audio, sr, device="cpu", keep="vocals"):
    """Tách nguồn bằng Demucs htdemucs. keep="vocals" (mặc định — audio mẫu
    voice clone) hoặc keep="music" (nhạc nền sạch = drums+bass+other, KHÔNG
    lời thoại — dùng cho mux lồng tiếng). audio nhận mono 1-D hoặc stereo [2,T];
    trả về cùng dạng."""
    import torch
    from demucs.pretrained import get_model
    from demucs.apply import apply_model

    print(f"[Enhance] Tách nhạc (Demucs htdemucs, giữ {keep})...",
          file=sys.stderr, flush=True)
    model = get_model("htdemucs")
    model.eval()
    model.to(device)

    # Demucs cần stereo float32 tensor [1, 2, T]
    was_mono = (audio.ndim == 1)
    stereo = np.stack([audio, audio], axis=0) if was_mono else audio   # [2, T]
    wav = torch.from_numpy(stereo).unsqueeze(0)        # [1, 2, T]

    with torch.no_grad():
        sources = apply_model(model, wav, device=device, shifts=1, overlap=0.25)
    # sources shape: [1, stems, 2, T]; stems = drums/bass/other/vocals
    stem_names = model.sources
    if keep == "music":
        idxs = [i for i, n in enumerate(stem_names) if n != "vocals"]
        out = sources[0, idxs].sum(dim=0)              # [2, T]
    else:
        out = sources[0, stem_names.index("vocals")]   # [2, T]
    if was_mono:
        return out.mean(dim=0).cpu().numpy(), sr       # mono float32
    return out.cpu().numpy(), sr                       # [2, T] float32


def step_denoise(audio, sr):
    """Giảm tiếng ồn nền bằng noisereduce spectral gating."""
    import noisereduce as nr
    print("[Enhance] Giảm tiếng ồn (noisereduce)...", file=sys.stderr, flush=True)
    reduced = nr.reduce_noise(y=audio, sr=sr, stationary=False, prop_decrease=0.85)
    return reduced.astype(np.float32), sr


def step_filter_voice(audio, sr):
    """Bandpass 80–8000 Hz — loại tần số ngoài vùng giọng người."""
    from scipy.signal import butter, sosfilt
    print("[Enhance] Lọc tần số giọng (80–8000 Hz)...", file=sys.stderr, flush=True)
    nyq = sr / 2.0
    low  = max(80,   1) / nyq
    high = min(8000, nyq - 1) / nyq
    sos = butter(4, [low, high], btype="band", output="sos")
    filtered = sosfilt(sos, audio).astype(np.float32)
    return filtered, sr


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",    required=True)
    parser.add_argument("--output",   required=True)
    parser.add_argument("--separate", action="store_true", help="Tách nhạc")
    parser.add_argument("--denoise",  action="store_true", help="Giảm tiếng ồn")
    parser.add_argument("--filter",   action="store_true", help="Lọc tần số giọng")
    parser.add_argument("--keep", choices=["vocals", "music"], default="vocals",
                        help="Stem giữ lại khi --separate (music = nhạc nền không lời)")
    parser.add_argument("--stereo", action="store_true",
                        help="Giữ 2 kênh (chỉ dùng với --separate đơn lẻ)")
    args = parser.parse_args()

    if not args.separate and not args.denoise and not args.filter:
        print("ERROR:Không có bước nào được chọn (--separate/--denoise/--filter)", flush=True)
        sys.exit(1)

    # ── Lập lịch tiến trình theo các bước được bật ────────────────────────
    # Mỗi bước có "trọng số" thời gian tương đối; thanh nhích theo tổng trọng
    # số đã hoàn thành. Phát PCT:done:100 ra stdout để app kéo thanh.
    _w = {"load": 5, "separate": 60, "denoise": 20, "filter": 10, "write": 5}
    _total = _w["load"] + _w["write"]
    if args.separate:
        _total += _w["separate"]
    if args.denoise:
        _total += _w["denoise"]
    if args.filter:
        _total += _w["filter"]
    _done = [0]

    def _step(name):
        _done[0] += _w.get(name, 0)
        print(f"PCT:{min(int(_done[0] * 100 / max(_total, 1)), 100)}:100", flush=True)

    if args.stereo and (args.denoise or args.filter):
        # denoise/filter là pipeline mono — stereo chỉ hỗ trợ --separate đơn lẻ
        print("[Enhance] ⚠ --stereo bỏ qua --denoise/--filter (chỉ tách nhạc)",
              file=sys.stderr, flush=True)
        args.denoise = args.filter = False

    print("PCT:0:100", flush=True)
    print(f"[Enhance] Load: {args.input}", file=sys.stderr, flush=True)
    audio, sr = load_stereo(args.input) if args.stereo else load_mono(args.input)
    _step("load")

    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"

    if args.separate:
        audio, sr = step_separate(audio, sr, device=device, keep=args.keep)
        _step("separate")

    if args.denoise:
        audio, sr = step_denoise(audio, sr)
        _step("denoise")

    if args.filter:
        audio, sr = step_filter_voice(audio, sr)
        _step("filter")

    # Normalize để tránh clip. Nhạc nền (keep=music) chỉ hạ khi vượt trần —
    # KHÔNG khuếch đại lên 0.95 (đẩy nhạc nền to hơn bản gốc phá cân bằng mix).
    peak = np.abs(audio).max()
    if args.keep == "music":
        if peak > 0.95:
            audio = audio / peak * 0.95
    elif peak > 0:
        audio = audio / peak * 0.95

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    sf.write(args.output, audio if audio.ndim == 1 else audio.T, sr)
    _step("write")
    print("PCT:100:100", flush=True)
    print(f"DONE:{args.output}", flush=True)


if __name__ == "__main__":
    main()
