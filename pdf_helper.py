"""PDF text extractor helper — chạy bằng voxcpm_env/Scripts/python.exe."""
import argparse
import json
import re
import sys


def _split_chunks(text, max_chars=250):
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    paragraphs = text.split('\n\n')
    chunks = []
    for para in paragraphs:
        para = para.replace('\n', ' ').strip()
        if not para:
            continue
        if len(para) <= max_chars:
            chunks.append(para)
        else:
            sentences = re.split(r'(?<=[.!?…])\s+', para)
            current = ""
            for s in sentences:
                s = s.strip()
                if not s:
                    continue
                if len(current) + len(s) + 1 <= max_chars:
                    current = (current + ' ' + s).strip()
                else:
                    if current:
                        chunks.append(current)
                    if len(s) > max_chars:
                        for j in range(0, len(s), max_chars):
                            chunks.append(s[j:j + max_chars])
                        current = ""
                    else:
                        current = s
            if current:
                chunks.append(current)
    return [c for c in chunks if c.strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",     required=True, help="File PDF cần đọc")
    parser.add_argument("--output",    required=True, help="File JSON output (danh sách chunks)")
    parser.add_argument("--max-chars", type=int, default=250)
    args = parser.parse_args()

    try:
        from pypdf import PdfReader
    except ImportError:
        from PyPDF2 import PdfReader

    reader = PdfReader(args.input)
    page_count = len(reader.pages)
    pages_text = []
    for page in reader.pages:
        t = page.extract_text() or ""
        if t.strip():
            pages_text.append(t)

    full_text = "\n\n".join(pages_text)
    chunks = _split_chunks(full_text, args.max_chars)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({"pages": page_count, "chunks": chunks}, f, ensure_ascii=False, indent=2)

    print(f"DONE:{page_count}:{len(chunks)}", flush=True)


if __name__ == "__main__":
    main()
