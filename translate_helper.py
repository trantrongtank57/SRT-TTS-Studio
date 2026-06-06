# -*- coding: utf-8 -*-
"""translate_helper.py — dịch offline (local) sang tiếng Việt bằng HuggingFace.

Chạy như subprocess bởi apppp_integrated.py (interpreter = voxcpm_env python,
cần torch + transformers + sentencepiece).

Tự nhận diện loại model:
  • NLLB / M2M100  → đặt src_lang + forced_bos_token_id = tgt_lang (mặc định vie_Latn)
  • VietAI envit5  → prefix "en: " ở input, bỏ prefix "vi:" ở output (chỉ Anh→Việt)
  • Model seq2seq khác → generate trực tiếp

Giao thức stdout (giống các helper khác):
  PROGRESS:<done>:<total>   — tiến độ theo số dòng/đoạn
  DONE:<output_path>        — xong, đã ghi JSON {"translations":[...]}
  BATCH_ERR:<msg>           — 1 batch lỗi (giữ nguyên bản gốc, vẫn tiếp tục)

I/O: --input là JSON {"segments":[...]}, --output là JSON {"translations":[...]}.
"""
import sys
import os
import json
import argparse


def _err(msg):
    print(msg, file=sys.stderr, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True, help='Thư mục model local hoặc HF model id')
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--src-lang', default='eng_Latn', help='Mã ngôn ngữ nguồn cho NLLB')
    ap.add_argument('--tgt-lang', default='vie_Latn', help='Mã ngôn ngữ đích cho NLLB')
    ap.add_argument('--device', default='auto', choices=['auto', 'cpu', 'cuda'])
    ap.add_argument('--batch', type=int, default=16)
    args = ap.parse_args()

    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    except Exception as e:
        _err(f'IMPORT_ERR: thiếu thư viện ({e}). '
             f'Cài trong env: pip install transformers sentencepiece torch')
        sys.exit(2)

    device = args.device
    if device == 'auto':
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

    with open(args.input, encoding='utf-8') as f:
        segments = json.load(f).get('segments', [])
    total = len(segments)
    if total == 0:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump({'translations': []}, f, ensure_ascii=False)
        print(f'DONE:{args.output}', flush=True)
        return

    _err(f'Loading model: {args.model} (device={device})')
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model)
    model.to(device).eval()

    name = os.path.basename(str(args.model).rstrip('/\\')).lower()
    arch = ''
    try:
        arch = (model.config.architectures or [''])[0].lower()
    except Exception:
        pass

    is_envit5 = ('envit5' in name) or ('envit' in name)
    is_nllb = (not is_envit5) and (
        'nllb' in name or 'm2m' in name or 'm2m100' in arch
        or hasattr(tok, 'lang_code_to_id')
    )

    forced_bos = None
    if is_nllb:
        try:
            tok.src_lang = args.src_lang
        except Exception:
            pass
        try:
            forced_bos = tok.convert_tokens_to_ids(args.tgt_lang)
        except Exception:
            forced_bos = None
        if forced_bos in (None, getattr(tok, 'unk_token_id', None)):
            try:
                forced_bos = tok.lang_code_to_id[args.tgt_lang]
            except Exception:
                pass
        _err(f'NLLB mode: src={args.src_lang} tgt={args.tgt_lang} forced_bos={forced_bos}')
    elif is_envit5:
        _err('envit5 mode: English -> Vietnamese')
    else:
        _err('generic seq2seq mode')

    def translate_batch(texts):
        inp = ['en: ' + t for t in texts] if is_envit5 else texts
        enc = tok(inp, return_tensors='pt', padding=True,
                  truncation=True, max_length=512).to(device)
        gen_kwargs = dict(max_length=512, num_beams=4)
        if forced_bos is not None:
            gen_kwargs['forced_bos_token_id'] = forced_bos
        with torch.no_grad():
            out = model.generate(**enc, **gen_kwargs)
        res = tok.batch_decode(out, skip_special_tokens=True)
        if is_envit5:
            cleaned = []
            for r in res:
                if r.lower().startswith('vi:'):
                    r = r.split(':', 1)[1]
                cleaned.append(r.strip())
            res = cleaned
        return res

    results = []
    done = 0
    bs = max(1, args.batch)
    for i in range(0, total, bs):
        chunk = segments[i:i + bs]
        safe = [c if (isinstance(c, str) and c.strip()) else ' ' for c in chunk]
        try:
            tr = translate_batch(safe)
        except Exception as e:
            _err(f'BATCH_ERR:{e}')
            print(f'BATCH_ERR:{e}', flush=True)
            tr = list(chunk)  # giữ nguyên bản gốc
        # khôi phục dòng rỗng + đảm bảo đủ độ dài
        out_chunk = []
        for j, src in enumerate(chunk):
            if not (isinstance(src, str) and src.strip()):
                out_chunk.append('')
            elif j < len(tr):
                out_chunk.append(tr[j])
            else:
                out_chunk.append(src)
        results.extend(out_chunk)
        done += len(chunk)
        print(f'PROGRESS:{done}:{total}', flush=True)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump({'translations': results}, f, ensure_ascii=False)
    print(f'DONE:{args.output}', flush=True)


if __name__ == '__main__':
    main()
