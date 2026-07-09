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
  --lang <code>          en | chinese_sim | chinese_cht | japan | korean | vi | fr | de | ru | th
  --device <auto|cpu|cuda>
  --min-conf <float>     bỏ qua box có độ tin cậy < ngưỡng (mặc định 0.3)
  --selftest             chỉ kiểm tra env (python/torch/easyocr) rồi thoát
"""

import sys
import os
import io
import re
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
    # sách/tài liệu tiếng Việt (card 📷 Ảnh scan sách → Đọc) — EasyOCR có 'vi'
    "vi":          ["vi", "en"],
    "vietnamese":  ["vi", "en"],
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


# Từ nối tiếng Anh hay bị OCR nuốt dấu nháy — map trả lại ('its' bỏ qua vì
# trùng sở hữu cách; 'ill'/'id'/'were' bỏ qua vì trùng từ thật)
_APOS_FIX = {"hes": "he's", "shes": "she's", "thats": "that's",
             "dont": "don't", "didnt": "didn't", "doesnt": "doesn't",
             "cant": "can't", "couldnt": "couldn't", "wont": "won't",
             "wouldnt": "wouldn't", "isnt": "isn't", "arent": "aren't",
             "wasnt": "wasn't", "werent": "weren't", "im": "I'm",
             "ive": "I've", "youre": "you're", "theyre": "they're",
             "whats": "what's", "lets": "let's", "letis": "let's",
             "nows": "now's", "theres": "there's", "whos": "who's"}
_APOS_RE = re.compile(r"(?i)\b(" + "|".join(_APOS_FIX) + r")\b")

# '!' cuối từ bị EasyOCR đọc thành i/il/iii — chỉ khôi phục cho các từ thoại
# comic phổ biến (suffix phải BẮT ĐẦU bằng 'i' nên 'tool' không dính; 'me' bị
# loại khỏi list vì 'Mei' là tên nhân vật hay gặp).
_EXCL_WORDS = ("us|meet|okay|ok|now|stop|wait|go|run|help|look|out|fire|"
               "attack|move|come|here|there|die|kill|dodge|hurry|watch|"
               "careful|front|price|chance|time|too|you|them|him|her|up|"
               "down|away|enough|right|ready|first|fast|hard|again|back|"
               "no|yes|what|why|it|off|on|more|wall|shield|sword|leader")
_EXCL_RE = re.compile(r"(?i)\b(" + _EXCL_WORDS + r")(i[il]{0,2})\b")


def _clean_block_text(text):
    """Dọn lỗi OCR đặc trưng comic TRƯỚC khi đưa đi dịch — model dịch (nhất là
    NLLB offline) rất dễ loạn với text bẩn:
      • '!' cuối từ in hoa bị đọc thành 'i'/'l' (OFFi → OFF!)
      • ';' hầu hết là ','/'.' đọc sai; '_' lạc (thường là '...')
      • đuôi chữ số lạc (sfx dính vào khối)
      • hoa/thường lộn xộn (ThiS To Be) → chuẩn về sentence-case cho MT dễ nhai
        (comic vốn ALL-CAPS nên không mất thông tin; CJK không có hoa/thường
        nên các rule này vô hại với ja/ko/zh)."""
    t = text
    t = re.sub(r"\b([A-Z]{2,})[il]\b", r"\1!", t)      # OFFi / OFFl → OFF!
    t = re.sub(r"(?i)\b([a-z]*ff)i\b", r"\1!", t)      # Offi → Off!
    t = re.sub(r"(?i)\b([a-z]{2,}fu)!", r"\1l", t)     # carefu! → careful (OCR đổi chỗ l↔!)
    t = _EXCL_RE.sub(lambda m: m.group(1) + "!", t)    # usi/meetil/Okayil → us!/meet!/okay!
    t = re.sub(r"(?i)\bil!", "I'll", t)                # "il! take care" → "I'll take care"
    t = re.sub(r"(?i)\bill\b(?=\s+(?:make|take|be|do|get|go|show|give|kill|"
               r"let|have|never|not|deal|handle|finish|protect|end|see|come|"
               r"stay|find|hold|leave))", "I'll", t)   # "Ill make you pay" → "I'll ..."
    t = t.replace("_", " ")
    t = t.replace(";", ",")
    t = re.sub(r"(\s+\d{1,2})+\s*$", "", t)            # đuôi số lạc
    t = re.sub(r"\s+([,.!?])", r"\1", t)
    t = re.sub(r",\s*([.!?])", r"\1", t)               # ',.' → '.'
    t = re.sub(r"\s{2,}", " ", t).strip(" '\"")
    letters = [c for c in t if c.isalpha()]
    if letters:
        up = sum(1 for c in letters if c.isupper()) / len(letters)
        if up >= 0.3:                                  # lẫn nhiều hoa lộn xộn → sentence case
            t = t[:1].upper() + t[1:].lower()
    # OCR nuốt dấu ' của từ nối tiếng Anh (Hes/dont/cant) — trả lại cho MT dễ dịch
    def _apos(m):
        w = m.group(0)
        f = _APOS_FIX[w.lower()]
        return (f[0].upper() + f[1:]) if w[0].isupper() else f
    t = _APOS_RE.sub(_apos, t)
    t = re.sub(r"\bi\b", "I", t)                       # đại từ 'i' lẻ → 'I'
    return t.strip()


def _merge_lines(items):
    """Gom các dòng (rect,text,conf) thành khối bong bóng bằng UNION-FIND với
    ngưỡng theo TỪNG CẶP dòng (không dùng median toàn trang — webtoon trộn chữ
    to nhỏ làm median lệch). Hai dòng nối nhau khi:
      • trên/dưới cùng bóng: chồng ngang ≥25% bề rộng nhỏ + khe dọc ≤1.3 dòng
      • mảnh cùng MỘT dòng:  chồng dọc ≥50% chiều cao + khe ngang ≤1.5 dòng
    Text ghép theo hàng (trên→dưới, trái→phải); gạch nối cuối dòng dính từ lại."""
    if not items:
        return []
    n = len(items)
    parent = list(range(n))

    def _find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def _union(a, b):
        ra, rb = _find(a), _find(b)
        if ra != rb:
            parent[rb] = ra

    rects = [it[0] for it in items]
    for i in range(n):
        x1, y1, x2, y2 = rects[i]
        hi = max(12, y2 - y1)
        for j in range(i + 1, n):
            a1, b1, a2, b2 = rects[j]
            hj = max(12, b2 - b1)
            ph = min(hi, hj)
            ho = min(x2, a2) - max(x1, a1)   # chồng ngang (>0) / -khe ngang
            vo = min(y2, b2) - max(y1, b1)   # chồng dọc (>0) / -khe dọc
            wmin = max(1, min(x2 - x1, a2 - a1))
            if ho > 0.25 * wmin and -vo <= 1.3 * ph:
                _union(i, j)
            elif vo > 0.5 * ph and -ho <= 1.5 * ph:
                _union(i, j)

    groups = {}
    for k in range(n):
        groups.setdefault(_find(k), []).append(items[k])

    out = []
    for g in groups.values():
        g.sort(key=lambda it: it[0][1])
        # gom theo hàng: chồng dọc ≥50% với dòng trong hàng → cùng hàng
        rows = []
        for it in g:
            r = it[0]
            placed = False
            for row in rows:
                rr = row[-1][0]
                vo = min(rr[3], r[3]) - max(rr[1], r[1])
                if vo > 0.5 * min(max(1, rr[3] - rr[1]), max(1, r[3] - r[1])):
                    row.append(it)
                    placed = True
                    break
            if not placed:
                rows.append([it])
        text = ""
        for row in rows:
            row.sort(key=lambda it: it[0][0])
            pline = " ".join(t.strip() for _, t, _ in row if t.strip())
            if not pline:
                continue
            if text.endswith("-"):           # LAUNCH- + ING → LAUNCHING
                text = text[:-1] + pline
            else:
                text = (text + " " + pline).strip()
        text = _clean_block_text(text)
        if not text:
            continue
        xs1 = min(r[0] for r, _, _ in g)
        ys1 = min(r[1] for r, _, _ in g)
        xs2 = max(r[2] for r, _, _ in g)
        ys2 = max(r[3] for r, _, _ in g)
        confs = [c for _, _, c in g]
        out.append({"box": [xs1, ys1, xs2, ys2], "text": text,
                    "conf": round(sum(confs) / len(confs), 3)})
    out.sort(key=lambda b: b["box"][1])
    return out


# ── Cắt dải ảnh cao (webtoon strip) ──────────────────────────────────────────
# EasyOCR co ảnh về cạnh dài ≤ canvas_size (2560) TRƯỚC khi detect — webtoon
# 800×10000+ bị co ~4 lần, chữ còn vài px → sót/bắt vụn gần hết bong bóng.
# Fix: cắt thành các dải cao _BAND_H chồng nhau _BAND_OVERLAP (bóng thoại nằm
# vắt qua mép dải vẫn lọt trọn vào ít nhất 1 dải nếu cao ≤ overlap), OCR từng
# dải, cộng offset y, rồi khử trùng lặp vùng chồng.
_BAND_H = 2200
_BAND_OVERLAP = 600

_OCR_KW = dict(detail=1, paragraph=False,
               text_threshold=0.6, low_text=0.3, link_threshold=0.3,
               canvas_size=2560, mag_ratio=1.0)


def _dedupe_items(items):
    """Bỏ box trùng giữa 2 dải chồng nhau — giữ bản conf cao hơn."""
    items = sorted(items, key=lambda it: -it[2])
    kept = []
    for r, t, c in items:
        dup = False
        for kr, _, _ in kept:
            ix = min(r[2], kr[2]) - max(r[0], kr[0])
            iy = min(r[3], kr[3]) - max(r[1], kr[1])
            if ix > 0 and iy > 0:
                inter = ix * iy
                a1 = max(1, (r[2] - r[0]) * (r[3] - r[1]))
                a2 = max(1, (kr[2] - kr[0]) * (kr[3] - kr[1]))
                if inter > 0.55 * min(a1, a2):
                    dup = True
                    break
        if not dup:
            kept.append((r, t, c))
    return kept


def _block_keep(block, arr):
    """Lọc block rác sau khi gộp: hiệu ứng âm thanh / chữ vẽ trên nền tranh,
    số trang, mảnh 1 ký tự — dịch mấy thứ này chỉ đè bừa lên tranh.
    Nguyên tắc: bong bóng thoại = chữ trên nền TRẮNG; sfx nằm trên nền tranh
    tối/màu → đo tỷ lệ pixel trắng trong vùng block để phân biệt (giữ lại
    chữ-trắng-trên-nền-đen nếu conf cao — bóng hét/hồi tưởng)."""
    import re as _re
    text = block["text"]
    alnum = _re.sub(r"[\W_]+", "", text, flags=_re.UNICODE)
    if len(alnum) < 2:
        return False                 # 'A', '9', '?' — mảnh sfx
    if not _re.search(r"[^\W\d_]", text, flags=_re.UNICODE) and len(alnum) <= 4:
        return False                 # toàn chữ số ngắn ('16', '7 0') — sfx/số trang
    if len(alnum) <= 6 and block["conf"] < 0.35:
        return False                 # cụm ngắn + conf thấp → sfx ('Wuf 7 0');
                                     # thoại ngắn thật ('WHAT?') thường conf > 0.5
    try:
        x1, y1, x2, y2 = block["box"]
        h_arr, w_arr = arr.shape[0], arr.shape[1]
        x1 = max(0, min(int(x1), w_arr - 1))
        x2 = max(x1 + 1, min(int(x2), w_arr))
        y1 = max(0, min(int(y1), h_arr - 1))
        y2 = max(y1 + 1, min(int(y2), h_arr))
        region = arr[y1:y2:4, x1:x2:4]     # subsample ×4 cho nhanh
        white = float(((region > 205).all(axis=2)).mean())
    except Exception:
        return True
    if white < 0.30 and block["conf"] < 0.55:
        return False                 # nền tối + conf thấp → chữ vẽ/sfx
    return True


def _ocr_image(reader, img_path, min_conf):
    """OCR 1 ảnh (tự cắt dải nếu quá cao) → (w, h, [(rect, text, conf)], arr)."""
    from PIL import Image
    import numpy as np
    with Image.open(img_path) as im:
        im = im.convert("RGB")
        w, h = im.size
        arr = np.asarray(im)

    def _collect(results, y_off, into):
        for box, text, conf in results:
            if conf is None:
                conf = 0.0
            if float(conf) < min_conf or not str(text).strip():
                continue
            rect = _to_rect(box)
            rect[1] += y_off
            rect[3] += y_off
            into.append((rect, str(text), float(conf)))

    items = []
    if h <= int(_BAND_H * 1.2):
        _collect(reader.readtext(arr, **_OCR_KW), 0, items)
    else:
        step = _BAND_H - _BAND_OVERLAP
        y = 0
        while True:
            band = arr[y:min(y + _BAND_H, h)]
            _collect(reader.readtext(band, **_OCR_KW), y, items)
            if y + _BAND_H >= h:
                break
            y += step
        items = _dedupe_items(items)
    return w, h, items, arr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images-json")
    ap.add_argument("--out-json")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    # 0.15 (trước là 0.3): dòng giữa bong bóng hay rớt ở conf 0.2-0.3 làm câu
    # cụt; rác conf thấp đã có _block_keep lọc theo nền trắng/độ dài.
    ap.add_argument("--min-conf", type=float, default=0.15)
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
        with io.open(args.images_json, "r", encoding="utf-8-sig") as f:
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
            w, h, items, arr = _ocr_image(reader, img_path, args.min_conf)
            blocks = [b for b in _merge_lines(items) if _block_keep(b, arr)]
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
