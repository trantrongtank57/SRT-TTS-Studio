# -*- coding: utf-8 -*-
"""
Tai truyen ve may (doc offline ca nhan) — he SITE-ADAPTER.
truyenqq.com.vn co adapter rieng (do bu 100 chuong); trang la dung GENERIC
(best-effort). Them trang moi: copy 1 block trong ADAPTERS, sua match + 2 regex.

Cach dung:
    # Tai CA BO:
    python truyenqq_dl.py https://truyenqq.com.vn/cuoc-song-thuong-ngay

    # Tai vai chuong cu the (theo so chuong xuat hien tren web):
    python truyenqq_dl.py https://truyenqq.com.vn/cuoc-song-thuong-ngay --chapters 1 2 3

    # Tai 1 trang chuong rieng le:
    python truyenqq_dl.py https://truyenqq.com.vn/cuoc-song-thuong-ngay/chapter-1

    # Tai xong dong moi chuong thanh 1 file PDF (can: pip install pillow):
    python truyenqq_dl.py <url> --pdf
    # Moi chuong thanh 1 file CBZ:
    python truyenqq_dl.py <url> --cbz
    # GOP CA BO thanh 1 file PDF duy nhat:
    python truyenqq_dl.py <url> --merge-pdf
    # GOP CA BO thanh 1 file CBZ duy nhat:
    python truyenqq_dl.py <url> --merge-cbz

Yeu cau:  pip install requests
PDF tuy chon:  pip install pillow
"""

import os
import re
import sys
import time
import zipfile
import argparse
import urllib.parse

try:
    import requests
except ImportError:
    sys.exit("Thieu thu vien 'requests'. Chay:  pip install requests")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
BASE = "https://truyenqq.com.vn"   # fallback referer khi khong suy ra duoc

session = requests.Session()
session.headers.update({"User-Agent": UA})

# ============================ SITE ADAPTERS ============================
# Moi trang truyen = 1 cau hinh nho; logic tai/gop dung chung.
#   match           : cac chuoi ten mien de nhan dien trang
#   chapter_link_re : regex bat (href, nhan) cua tung link chuong
#   image_res       : danh sach regex thu lan luot de bat URL anh that;
#                     chon list cho NHIEU anh hop le nhat (anh lazy-load
#                     thuong o data-src, src chi la placeholder)
#   backfill        : co do bu cac chuong dau bi thieu khong (truyenqq
#                     chi render 100 chuong moi nhat, khong phan trang)
#   chap_url        : ham tao URL chuong tu (base, so) — chi can khi backfill
# Trang KHONG khai bao -> dung GENERIC (best-effort, chay duoc nhieu trang).
GENERIC = {
    "name": "generic",
    "match": [],
    "chapter_link_re": r'<a[^>]+href="([^"]*(?:chap|chuong)[^"]*)"[^>]*>(.*?)</a>',
    "image_res": [
        r'<img[^>]+data-src="([^"]+)"',
        r'<img[^>]+data-original="([^"]+)"',
        r'<img[^>]+data-lazy-src="([^"]+)"',
        r'<img[^>]+data-aload="([^"]+)"',
        r'<img[^>]+src="([^"]+\.(?:jpg|jpeg|png|webp)[^"]*)"',
    ],
    "backfill": False,
}

ADAPTERS = [
    {
        "name": "truyenqq",
        "match": ["truyenqq"],
        "chapter_link_re":
            r'<a\s+href="([^"]+)"\s+class="chapter-name[^"]*"[^>]*>(.*?)</a>',
        "image_res": [r'<img[^>]+data-(?:src|original)="([^"]+)"'],
        "backfill": True,
        "chap_url": lambda base, i: f"{base}/chapter-{i}",
    },
    # >>> Them trang khac: copy block tren, sua "match" + 2 regex la xong. <<<
]


def get_adapter(url):
    host = urllib.parse.urlsplit(url).netloc.lower()
    for a in ADAPTERS:
        if any(m in host for m in a["match"]):
            return a
    return GENERIC


def _base_of(url):
    sp = urllib.parse.urlsplit(url)
    return f"{sp.scheme}://{sp.netloc}" if sp.scheme else BASE


_IMG_JUNK = ("placeholder", "loading", "logo", "banner", "avatar",
             "/ads", "nocover", "blank", "/icon")


def _is_content_img(u):
    ul = u.lower()
    if any(j in ul for j in _IMG_JUNK):
        return False
    return ul.split("?")[0].endswith((".jpg", ".jpeg", ".png", ".webp"))


def extract_images(html, adapter):
    """Thu tung regex anh cua adapter, chon list nhieu anh hop le nhat."""
    best = []
    for rgx in adapter["image_res"]:
        urls = [u.strip() for u in re.findall(rgx, html, flags=re.I)]
        urls = [u for u in urls if _is_content_img(u)]
        if len(urls) > len(best):
            best = urls
    return best


def _extract_chap_num(href):
    """Rut so chuong tu URL: chapter-12 / chuong-12 / .../12 -> '12'."""
    for pat in (r"chapter-([\d.\-]+)", r"chuong-([\d.\-]+)", r"chap[-_]?([\d.\-]+)"):
        m = re.search(pat, href, flags=re.I)
        if m:
            return m.group(1)
    m = re.search(r"(\d+(?:[.\-]\d+)*)\D*$", href)
    return m.group(1) if m else href


def safe_name(s):
    """Bo ky tu khong hop le cho ten file/thu muc tren Windows."""
    return re.sub(r'[<>:"/\\|?*]', "_", s).strip().strip(".") or "untitled"


def get_html(url, referer=None):
    r = session.get(url, headers={"Referer": referer or _base_of(url)}, timeout=30)
    r.raise_for_status()
    r.encoding = "utf-8"
    return r.text


def _chap_key(num_str):
    """'120-4' -> (120,4); '28' -> (28,0). De sap xep dung thu tu chuong."""
    parts = [p for p in re.split(r"[-.]", num_str) if p.isdigit()]
    nums = [int(p) for p in parts]
    return tuple(nums) if nums else (10 ** 9,)


def _chapter_exists(url):
    """True neu trang chuong ton tai (HTTP 200, khong bi redirect ve trang khac)."""
    try:
        r = session.get(url, headers={"Referer": _base_of(url)}, timeout=20,
                        allow_redirects=False, stream=True)
        code = r.status_code
        r.close()
        return code == 200
    except Exception:
        return False


def list_chapters(series_url):
    """Tra ve [(ten_chuong, url)] theo thu tu chuong 1 -> moi nhat.

    Dung adapter theo ten mien. Voi cac trang gioi han so chuong hien thi
    (vd truyenqq render 100 chuong moi nhat) thi do tuan tu de bu chuong dau."""
    adapter = get_adapter(series_url)
    base = _base_of(series_url)
    html = get_html(series_url)
    pairs = re.findall(adapter["chapter_link_re"], html, flags=re.S | re.I)
    chapters = {}  # num_str -> (name, url)
    for href, label in pairs:
        href = href.strip()
        if not href or href.lower().startswith("javascript"):
            continue
        url = urllib.parse.urljoin(base, href)
        num = _extract_chap_num(href)
        name = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", label)).strip() \
            or f"Chapter {num}"
        chapters[num] = (name, url)

    if adapter.get("backfill"):
        int_chaps = [_chap_key(n)[0] for n in chapters if _chap_key(n)[0] < 10 ** 9]
        if int_chaps:
            mn = min(int_chaps)
            if mn > 1:
                print(f"   (Trang chi liet ke tu chuong {mn}; do tim chuong 1..{mn-1}...)")
                sbase = series_url.rstrip("/")
                cu = adapter.get("chap_url", lambda b, i: f"{b}/chapter-{i}")
                for i in range(1, mn):
                    if str(i) in chapters:
                        continue
                    curl = cu(sbase, i)
                    if _chapter_exists(curl):
                        chapters[str(i)] = (f"Chapter {i}", curl)

    return [chapters[k] for k in sorted(chapters, key=_chap_key)]


def chapter_image_urls(chapter_url):
    """Lay danh sach URL anh that trong 1 chuong (qua adapter), dung thu tu."""
    adapter = get_adapter(chapter_url)
    html = get_html(chapter_url)
    return extract_images(html, adapter)


def download_image(url, dest, referer):
    if os.path.exists(dest) and os.path.getsize(dest) > 1024:
        return True  # da tai roi -> bo qua (cho phep chay lai de tai tiep)
    for attempt in range(3):
        try:
            r = session.get(url, headers={"Referer": referer}, timeout=60, stream=True)
            r.raise_for_status()
            tmp = dest + ".part"
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            os.replace(tmp, dest)
            return True
        except Exception as e:
            print(f"      ! loi ({attempt+1}/3): {e}")
            time.sleep(2)
    return False


def _img_files(folder):
    """Cac file anh trong 1 thu muc, sap xep theo so thu tu."""
    return sorted(
        [os.path.join(folder, f) for f in os.listdir(folder)
         if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))],
        key=lambda p: int(re.search(r"(\d+)", os.path.basename(p)).group(1))
        if re.search(r"(\d+)", os.path.basename(p)) else 0)


def images_to_pdf(img_paths, pdf_path):
    """Gop 1 danh sach anh (theo dung thu tu) thanh 1 file PDF."""
    try:
        from PIL import Image
    except ImportError:
        print("   (Bo qua PDF: chua cai pillow -> pip install pillow)")
        return False
    if not img_paths:
        return False
    pages = []
    for p in img_paths:
        try:
            im = Image.open(p)
            if im.mode in ("RGBA", "P", "LA"):
                im = im.convert("RGB")
            pages.append(im)
        except Exception as e:
            print(f"   ! bo qua anh loi {os.path.basename(p)}: {e}")
    if not pages:
        return False
    pages[0].save(pdf_path, save_all=True, append_images=pages[1:])
    print(f"   -> PDF: {pdf_path}")
    return True


def images_to_cbz(img_paths, cbz_path, prefix=False):
    """Gop 1 danh sach anh thanh 1 file CBZ (zip cua anh).
    prefix=True -> them so thu tu toan cuc de giu dung thu tu khi gop ca bo."""
    if not img_paths:
        return False
    with zipfile.ZipFile(cbz_path, "w", zipfile.ZIP_STORED) as z:
        for i, p in enumerate(img_paths):
            ext = os.path.splitext(p)[1] or ".jpg"
            arc = f"{i+1:05d}{ext}" if prefix else os.path.basename(p)
            z.write(p, arc)
    print(f"   -> CBZ: {cbz_path}")
    return True


def make_pdf(folder, pdf_path):
    images_to_pdf(_img_files(folder), pdf_path)


def make_cbz(folder, cbz_path):
    images_to_cbz(_img_files(folder), cbz_path)


def download_chapter(name, url, out_root, make_pdf_flag, make_cbz_flag, delay):
    """Tai 1 chuong. Tra ve thu muc da luu (de gop ca bo sau do), None neu loi."""
    folder = os.path.join(out_root, safe_name(name))
    os.makedirs(folder, exist_ok=True)
    imgs = chapter_image_urls(url)
    if not imgs:
        print(f"   [!] Khong tim thay anh trong {url}")
        return None
    print(f"   {len(imgs)} trang...")
    ok = 0
    for i, img_url in enumerate(imgs):
        ext = os.path.splitext(urllib.parse.urlparse(img_url).path)[1] or ".jpg"
        dest = os.path.join(folder, f"{i+1:03d}{ext}")
        if download_image(img_url, dest, referer=url):
            ok += 1
        time.sleep(delay)
    print(f"   xong {ok}/{len(imgs)} trang")
    if make_pdf_flag:
        make_pdf(folder, folder + ".pdf")
    if make_cbz_flag:
        make_cbz(folder, folder + ".cbz")
    return folder


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url", help="URL bo truyen hoac URL 1 chuong")
    ap.add_argument("--chapters", nargs="*", help="So chuong cu the (vd: 1 2 5). Bo trong = tai het")
    ap.add_argument("--out", default="downloads", help="Thu muc luu (mac dinh: downloads)")
    ap.add_argument("--pdf", action="store_true", help="Dong moi chuong thanh 1 PDF")
    ap.add_argument("--cbz", action="store_true", help="Dong moi chuong thanh 1 CBZ")
    ap.add_argument("--merge-pdf", action="store_true", help="GOP CA BO thanh 1 PDF duy nhat")
    ap.add_argument("--merge-cbz", action="store_true", help="GOP CA BO thanh 1 CBZ duy nhat")
    ap.add_argument("--delay", type=float, default=0.3, help="Nghi giua moi anh (giay)")
    args = ap.parse_args()

    # Truong hop URL la 1 chuong rieng le
    if "/chapter-" in args.url or "/chuong-" in args.url:
        title = safe_name(args.url.rstrip("/").split("/")[-2])
        out_root = os.path.join(args.out, title)
        os.makedirs(out_root, exist_ok=True)
        name = args.url.rstrip("/").split("/")[-1]
        print(f"Tai 1 chuong: {name}")
        download_chapter(name, args.url, out_root, args.pdf, args.cbz, args.delay)
        return

    # Truong hop URL la ca bo
    title = safe_name(args.url.rstrip("/").split("/")[-1])
    out_root = os.path.join(args.out, title)
    os.makedirs(out_root, exist_ok=True)

    chapters = list_chapters(args.url)
    if not chapters:
        sys.exit("Khong lay duoc danh sach chuong (cau truc trang co the da doi).")
    print(f"Bo truyen: {title} | tong {len(chapters)} chuong")

    if args.chapters:
        want = set(args.chapters)
        # khop theo so chuong rut tu URL (chapter-120 / chuong-120 -> '120')
        sel = []
        for name, url in chapters:
            num = _extract_chap_num(url)
            base_num = num.split(".")[0].split("-")[0]
            if num in want or base_num in want or name.split()[-1] in want:
                sel.append((name, url))
        if not sel:
            sys.exit("Khong khop chuong nao voi --chapters da nhap.")
        chapters = sel

    done_folders = []
    for idx, (name, url) in enumerate(chapters, 1):
        print(f"[{idx}/{len(chapters)}] {name}")
        try:
            folder = download_chapter(name, url, out_root, args.pdf, args.cbz, args.delay)
            if folder:
                done_folders.append(folder)
        except Exception as e:
            print(f"   [LOI] bo qua chuong nay: {e}")
        time.sleep(args.delay)

    # Gop ca bo thanh 1 file duy nhat (theo dung thu tu chuong -> trang)
    if (args.merge_pdf or args.merge_cbz) and done_folders:
        all_imgs = []
        for folder in done_folders:          # done_folders da theo thu tu chuong
            all_imgs.extend(_img_files(folder))
        print(f"\nGop ca bo: {len(all_imgs)} trang tu {len(done_folders)} chuong...")
        if args.merge_pdf:
            images_to_pdf(all_imgs, os.path.join(args.out, title + ".pdf"))
        if args.merge_cbz:
            images_to_cbz(all_imgs, os.path.join(args.out, title + ".cbz"), prefix=True)

    print("\nHoan tat. File luu tai:", os.path.abspath(out_root))


if __name__ == "__main__":
    main()
