"""
manga_ocr_helper.py — companion script for SRT TTS Studio

OCR từng ảnh truyện tranh → text + bounding box, gom các dòng gần nhau thành
"khối" (bong bóng thoại) để câu dịch liền mạch. Chạy bằng EasyOCR (torch).

Chạy trong env có torch + easyocr (mặc định dùng voxcpm_env — đã có torch;
chỉ cần:  voxcpm_env\\Scripts\\python.exe -m pip install easyocr ).

Giao thức stdout (giống các helper khác):
  PROGRESS:<done>:<total>   — đã OCR xong ảnh thứ done/total
  DONE:<out_json>           — xong, đã ghi JSON kết quả
  ERROR:<message>           — lỗi nặng
  WARN:<message>            — cảnh báo (1 ảnh lỗi, vẫn tiếp tục)

JSON output:
  {"pages":[{"image": "<path>",
             "w": <int>, "h": <int>,
             "blocks":[{"box":[x1,y1,x2,y2], "text":"...", "conf":0.0}, ...]},
            ...]}

Args:
  --images-json <file>   JSON: ["path1.jpg", "path2.png", ...]
  --out-json <file>      nơi ghi kết quả
  --lang <code>          en | chinese_sim | chinese_cht | japan | korean
  --device <auto|cpu|cuda>
  --min-conf <float>     bỏ qua box có độ tin cậy < ngưỡng (mặc định 0.3)
  --selftest             chỉ kiểm tra env (python/torch/easyocr) rồi thoát
"""

import sys
import os
import io
import json
import argparse

# stdout/stderr UTF-8 (tránh crash khi in tiếng Việt/Nhật trên Windows cp1252)
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


# EasyOCR dùng mã ngôn ngữ riêng — map từ mã của app sang.
_LANG_MAP = {
    "en":          ["en"],
    "english":     ["en"],
    "chinese_sim": ["ch_sim", "en"],
    "chinese_cht": ["ch_tra", "en"],
    "japan":       ["ja", "en"],
    "japanese":    ["ja", "en"],
    "korean":      ["ko", "en"],
    "fr":          ["fr", "en"],
    "de":          ["de", "en"],
    "ru":          ["ru", "en"],
    "th":          ["th", "en"],
}


def _emit(msg):
    print(msg, flush=True)


def _resolve_device(want):
    try:
        import torch
        has_cuda = bool(torch.cuda.is_available())
    except Exception:
        has_cuda = False
    if want == "cpu":
        return False
    if want == "cuda":
        return has_cuda
    return has_cuda  # auto


def _to_rect(box):
    """4 điểm EasyOCR -> (x1,y1,x2,y2) trục thẳng."""
    xs = [float(p[0]) for p in box]
    ys = [float(p[1]) for p in box]
    return [int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))]


def _merge_lines(items):
    """Gom các dòng (rect,text,conf) gần nhau theo chiều dọc + chồng ngang
    thành khối thoại. items đã lọc theo conf."""
    if not items:
        return []
    # sắp theo y trên cùng
    items = sorted(items, key=lambda it: it[0][1])
    heights = sorted(r[3] - r[1] for r, _, _ in items)
    med_h = heights[len(heights) // 2] or 18
    gap_lim = med_h * 0.9          # khoảng dọc tối đa giữa 2 dòng cùng khối

    blocks = []  # mỗi block: {"rect":[..], "lines":[(rect,text,conf)]}
    for rect, text, conf in items:
        placed = False
        for b in blocks:
            bx1, by1, bx2, by2 = b["rect"]
            # chồng ngang?
            overlap = min(bx2, rect[2]) - max(bx1, rect[0])
            wmin = min(bx2 - bx1, rect[2] - rect[0])
            horiz = overlap > 0.3 * max(1, wmin)
            # đủ gần theo dọc (dòng mới nằm ngay dưới khối)?
            vgap = rect[1] - by2
            near = -med_h * 0.6 <= vgap <= gap_lim
            if horiz and near:
                b["lines"].append((rect, text, conf))
                b["rect"] = [min(bx1, rect[0]), min(by1, rect[1]),
                             max(bx2, rect[2]), max(by2, rect[3])]
                placed = True
                break
        if not placed:
            blocks.append({"rect": list(rect), "lines": [(rect, text, conf)]})

    out = []
    for b in blocks:
        lines = sorted(b["lines"], key=lambda it: it[0][1])
        text = " ".join(t.strip() for _, t, _ in lines if t.strip())
        if not text:
            continue
        confs = [c for _, _, c in lines]
        out.append({"box": b["rect"], "text": text,
                    "conf": round(sum(confs) / len(confs), 3)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images-json")
    ap.add_argument("--out-json")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    ap.add_argument("--min-conf", type=float, default=0.3)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    _emit(f"PROGRESS_MSG:python {sys.version.split()[0]}")
    try:
        import torch
        _emit(f"PROGRESS_MSG:torch {torch.__version__} cuda={torch.cuda.is_available()}")
    except Exception as e:
        _emit(f"PROGRESS_MSG:torch chưa cài ({e})")
    try:
        import easyocr  # noqa: F401
        _emit("PROGRESS_MSG:easyocr OK")
    except Exception as e:
        _emit(f"ERROR:Chưa cài easyocr trong env này ({e}). "
              f"Cài:  python -m pip install easyocr")
        sys.exit(2)

    if args.selftest:
        _emit("DONE:selftest")
        return

    if not args.images_json or not args.out_json:
        _emit("ERROR:Thiếu --images-json hoặc --out-json")
        sys.exit(1)

    try:
        with io.open(args.images_json, "r", encoding="utf-8") as f:
            images = json.load(f)
    except Exception as e:
        _emit(f"ERROR:Không đọc được danh sách ảnh: {e}")
        sys.exit(1)

    langs = _LANG_MAP.get(args.lang.lower(), ["en"])
    gpu = _resolve_device(args.device)
    _emit(f"PROGRESS_MSG:EasyOCR lang={langs} gpu={gpu} — đang nạp model (lần đầu sẽ tải)...")

    import easyocr
    try:
        reader = easyocr.Reader(langs, gpu=gpu)
    except Exception as e:
        # CUDA hỏng → thử lại CPU
        _emit(f"WARN:Nạp model GPU lỗi ({e}) — thử CPU")
        try:
            reader = easyocr.Reader(langs, gpu=False)
        except Exception as e2:
            _emit(f"ERROR:Không nạp được EasyOCR: {e2}")
            sys.exit(1)

    pages = []
    total = len(images)
    for i, img_path in enumerate(images):
        try:
            from PIL import Image
            with Image.open(img_path) as im:
                w, h = im.size
            results = reader.readtext(img_path, detail=1, paragraph=False)
            items = []
            for box, text, conf in results:
                if conf is None:
                    conf = 0.0
                if float(conf) < args.min_conf:
                    continue
                if not str(text).strip():
                    continue
                items.append((_to_rect(box), str(text), float(conf)))
            blocks = _merge_lines(items)
            pages.append({"image": img_path, "w": w, "h": h, "blocks": blocks})
        except Exception as e:
            _emit(f"WARN:Ảnh lỗi {os.path.basename(str(img_path))}: {e}")
            pages.append({"image": img_path, "w": 0, "h": 0, "blocks": []})
        _emit(f"PROGRESS:{i + 1}:{total}")

    try:
        with io.open(args.out_json, "w", encoding="utf-8") as f:
            json.dump({"pages": pages}, f, ensure_ascii=False)
    except Exception as e:
        _emit(f"ERROR:Không ghi được kết quả: {e}")
        sys.exit(1)
    _emit(f"DONE:{args.out_json}")


if __name__ == "__main__":
    main()
