"""
srt_align_helper.py — can lai moc thoi gian .srt theo giong noi that (VAD).

Dung faster-whisper (Silero VAD) + PyAV de doc audio truc tiep tu video,
phat hien cac doan co tieng noi, roi doi start/end cua moi dong OCR cho khop.

In ra:
  PROGRESS:<msg>   — thong tin tien trinh
  DONE:<srt_out>   — hoan tat
  ERROR:<msg>      — loi
"""

import sys
import os
import re
import argparse


def _log(prefix, msg):
    print(f"{prefix}:{msg}", flush=True)


def parse_ts(s: str) -> float:
    """'HH:MM:SS,mmm' -> seconds (float)."""
    s = s.strip().replace('.', ',')
    hms, ms = s.split(',')
    h, m, sec = hms.split(':')
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000.0


def fmt_ts(t: float) -> str:
    if t < 0:
        t = 0.0
    h = int(t // 3600); t -= h * 3600
    m = int(t // 60);   t -= m * 60
    sec = int(t)
    ms = int(round((t - sec) * 1000))
    if ms >= 1000:
        sec += 1; ms -= 1000
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def parse_srt(path: str):
    """Tra ve list [ [start_sec, end_sec, text], ... ]."""
    with open(path, encoding='utf-8-sig', errors='replace') as f:
        content = f.read()
    blocks = re.split(r'\r?\n\s*\r?\n', content.strip())
    subs = []
    for b in blocks:
        lines = [l for l in b.splitlines() if l.strip() != '']
        if len(lines) < 2:
            continue
        ts_idx = next((i for i, l in enumerate(lines) if '-->' in l), None)
        if ts_idx is None:
            continue
        try:
            a, b2 = lines[ts_idx].split('-->')
            st, en = parse_ts(a), parse_ts(b2)
        except Exception:
            continue
        text = '\n'.join(lines[ts_idx + 1:]).strip()
        if text:
            subs.append([st, en, text])
    return subs


def write_srt(path: str, subs):
    with open(path, 'w', encoding='utf-8') as f:
        for i, (st, en, text) in enumerate(subs, 1):
            f.write(f"{i}\n{fmt_ts(st)} --> {fmt_ts(en)}\n{text}\n\n")


def align(subs, speech, max_shift, pad, min_dur, gap):
    """Doi timing moi dong OCR cho khop doan giong noi overlap."""
    aligned = []
    moved = 0
    for st, en, text in subs:
        lo, hi = st - pad, en + pad
        ov = [(s, e) for (s, e) in speech if e >= lo and s <= hi]
        if ov:
            cand_s = min(s for s, _ in ov)
            cand_e = max(e for _, e in ov)
            new_s = cand_s if abs(cand_s - st) <= max_shift else st
            new_e = cand_e if abs(cand_e - en) <= max_shift else en
            if abs(new_s - st) > 1e-3 or abs(new_e - en) > 1e-3:
                moved += 1
        else:
            new_s, new_e = st, en   # text co tren man nhung khong co tieng -> giu nguyen
        if new_e <= new_s:
            new_e = new_s + min_dur
        aligned.append([new_s, new_e, text])

    aligned.sort(key=lambda x: (x[0], x[1]))

    # Khu chong lan kieu monotonic: moi dong bat dau sau khi dong truoc ket thuc
    # (cac doan VAD von khong chong nhau nen truong hop binh thuong khong bi doi).
    out = []
    prev_end = None
    for st, en, text in aligned:
        s = st
        if prev_end is not None and s < prev_end + gap:
            s = prev_end + gap
        e = en
        if e < s + min_dur:
            e = s + min_dur
        out.append([s, e, text])
        prev_end = e
    return out, moved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--video',   required=True, help='Video/audio nguon (de trich tieng noi)')
    ap.add_argument('--srt_in',  required=True)
    ap.add_argument('--srt_out', required=True)
    ap.add_argument('--max_shift',     type=float, default=2.0,  help='Doi toi da mỗi bien (giay)')
    ap.add_argument('--pad',           type=float, default=1.0,  help='Cua so tim doan tieng noi quanh dong sub (giay)')
    ap.add_argument('--min_dur',       type=float, default=0.3)
    ap.add_argument('--gap',           type=float, default=0.04)
    ap.add_argument('--vad_threshold', type=float, default=0.5)
    args = ap.parse_args()

    _log("PROGRESS", "Doc SRT OCR...")
    subs = parse_srt(args.srt_in)
    if not subs:
        _log("ERROR", "SRT rong hoac khong doc duoc")
        sys.exit(1)
    _log("PROGRESS", f"{len(subs)} dong sub")

    try:
        import faster_whisper
        from faster_whisper.vad import get_speech_timestamps, VadOptions
    except ImportError as e:
        _log("ERROR", f"Thieu faster-whisper trong moi truong nay: {e}")
        sys.exit(1)

    SR = 16000
    _log("PROGRESS", "Giai ma audio tu video (PyAV)...")
    try:
        audio = faster_whisper.decode_audio(args.video, sampling_rate=SR)
    except Exception as e:
        _log("ERROR", f"Khong giai ma duoc audio: {e}")
        sys.exit(1)

    _log("PROGRESS", "Chay VAD phat hien giong noi...")
    opts = VadOptions(
        threshold=args.vad_threshold,
        min_speech_duration_ms=200,
        min_silence_duration_ms=300,
        speech_pad_ms=120,
    )
    try:
        ts = get_speech_timestamps(audio, vad_options=opts, sampling_rate=SR)
    except TypeError:
        ts = get_speech_timestamps(audio, opts, SR)

    speech = [(t['start'] / SR, t['end'] / SR) for t in ts]
    _log("PROGRESS", f"{len(speech)} doan co tieng noi")

    if not speech:
        _log("PROGRESS", "Khong phat hien giong noi — giu nguyen timing, chi sap xep + khu chong lan")
        cleaned, _ = align(subs, [], args.max_shift, args.pad, args.min_dur, args.gap)
        write_srt(args.srt_out, cleaned)
        _log("DONE", args.srt_out)
        return

    aligned, moved = align(subs, speech, args.max_shift, args.pad, args.min_dur, args.gap)
    write_srt(args.srt_out, aligned)
    _log("PROGRESS", f"Da can {moved}/{len(subs)} dong theo giong noi that")
    _log("DONE", args.srt_out)


if __name__ == "__main__":
    main()
