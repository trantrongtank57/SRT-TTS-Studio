"""OmniVoice Vietnamese batch voice-clone helper — chạy bằng omnivoice_env\\Scripts\\python.exe.

Mô hình: OmniVoice Vietnamese (https://huggingface.co/splendor1811/omnivoice-vietnamese).
Nhân bản giọng từ 1 audio mẫu + lời thoại mẫu (ref_text). Model TỰ TẢI từ HuggingFace
(`splendor1811/omnivoice-vietnamese`) lần đầu rồi cache; có thể trỏ thư mục model local.

Chạy trên **GPU NVIDIA (CUDA + PyTorch)** nếu có (dtype float16), không thì rơi về CPU (float32).

Giao thức stdout (giống vieneu_helper.py / f5tts_helper.py — app đọc từng dòng):
    DONE:{idx}            line_{idx:04d}.wav đã sẵn sàng
    ERROR:{idx}:{reason}  dòng lỗi (audio im lặng sau các lần thử)
    WARN:{idx}:{reason}   thử lại
    ALL_DONE              kết thúc batch
Dòng thông tin ghi ra stderr với tiền tố [OMNI].
"""
import argparse
import json
import os
import sys

# Ép stdout/stderr sang UTF-8 — nếu không, in tiếng Việt ra console cp1252 (Windows)
# sẽ ném UnicodeEncodeError và làm helper crash (exit 1) ngay ở nhánh báo lỗi.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# numpy/soundfile bắt buộc cho sinh audio, nhưng để --selftest còn báo cáo được
# khi env cài thiếu, ta không để ImportError làm crash ở mức module.
try:
    import numpy as np
except Exception as _e_np:
    np = None
    _NP_ERR = _e_np
try:
    import soundfile as sf
except Exception as _e_sf:
    sf = None
    _SF_ERR = _e_sf

# Model HF mặc định khi không trỏ thư mục model local
_DEFAULT_REPO = "splendor1811/omnivoice-vietnamese"
_SAMPLE_RATE = 24_000


def _log(msg):
    print(f"[OMNI] {msg}", file=sys.stderr, flush=True)


def _patch_torchaudio():
    """torchaudio 2.9+ giải mã/ghi audio qua **torchcodec** (cần FFmpeg DLL; trên
    Windows thường lỗi 'TorchCodec is required'). OmniVoice có thể gọi
    `torchaudio.load` để đọc audio mẫu → sẽ crash. Vá `torchaudio.load`/`save`
    dùng **soundfile** (giống f5tts_helper/vieneu_helper). Gọi TRƯỚC khi import omnivoice."""
    try:
        import torch
        import torchaudio

        def _load(path, *a, **k):
            data, sr = sf.read(str(path), dtype="float32", always_2d=True)
            return torch.from_numpy(data.T).contiguous(), sr

        def _save(path, tensor, sample_rate, *a, **k):
            arr = tensor.detach().cpu().numpy() if hasattr(tensor, "detach") else np.asarray(tensor)
            arr = np.asarray(arr, dtype="float32")
            if arr.ndim == 2:
                arr = arr.T
            sf.write(str(path), arr, int(sample_rate))

        torchaudio.load = _load
        torchaudio.save = _save
        _log("Đã vá torchaudio.load/save → soundfile (không cần torchcodec)")
    except Exception as e:
        _log(f"Không vá được torchaudio ({e})")


def _to_mono_np(audio):
    """Chuyển output generate() (tensor/list/ndarray, có thể [batch, ...]) → float32 1D."""
    # Lấy phần tử đầu (batch dim) nếu là list/tuple
    if isinstance(audio, (list, tuple)):
        audio = audio[0]
    # tensor → numpy
    if hasattr(audio, "detach"):
        audio = audio.detach().cpu().numpy()
    arr = np.asarray(audio, dtype="float32")
    # [batch, ...] hoặc [channels, frames] → gom về 1D
    while arr.ndim > 1:
        # nếu chiều đầu nhỏ (batch=1 hoặc channels<=2) thì bỏ/gộp
        if arr.shape[0] <= 2:
            arr = arr[0] if arr.shape[0] == 1 else arr.mean(axis=0)
        else:
            arr = arr.reshape(-1)
            break
    arr = np.asarray(arr, dtype="float32").reshape(-1)
    return np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)


def _import_omnivoice():
    """Import lớp model OmniVoice một cách chịu lỗi — thử nhiều tên lớp/đường dẫn
    phòng khi gói 'omnivoice' đặt tên hơi khác tài liệu."""
    import importlib
    candidates = [
        ("omnivoice", "OmniVoice"),
        ("omnivoice", "OmniVoiceTTS"),
        ("omnivoice", "OmniVoiceModel"),
        ("omnivoice", "Omnivoice"),
        ("omnivoice.model", "OmniVoice"),
        ("omnivoice.tts", "OmniVoice"),
    ]
    last_err = None
    for mod_name, cls_name in candidates:
        try:
            mod = importlib.import_module(mod_name)
        except Exception as e:
            last_err = e
            continue
        cls = getattr(mod, cls_name, None)
        if cls is not None:
            _log(f"Dùng lớp model: {mod_name}.{cls_name}")
            return cls
    # Fallback: quét module gốc tìm lớp có 'omni' trong tên + có from_pretrained/generate
    try:
        mod = importlib.import_module("omnivoice")
        for name in dir(mod):
            if "omni" in name.lower():
                cls = getattr(mod, name)
                if isinstance(cls, type) and (hasattr(cls, "from_pretrained")
                                              or hasattr(cls, "generate")):
                    _log(f"Dùng lớp model (auto-dò): omnivoice.{name}")
                    return cls
    except Exception as e:
        last_err = e
    if last_err is not None:
        _log(f"Lỗi import omnivoice: {last_err}")
    return None


def _load_model(OmniVoice, model_ref, device_map, dtype, device):
    """Load model thử nhiều chữ ký from_pretrained khác nhau (device_map/dtype/device/
    torch_dtype...), rồi tới constructor trực tiếp. Ném exception nếu tất cả đều lỗi."""
    errors = []
    if hasattr(OmniVoice, "from_pretrained"):
        kw_variants = [
            {"device_map": device_map, "dtype": dtype},
            {"device_map": device_map, "torch_dtype": dtype},
            {"device": device, "dtype": dtype},
            {"device": device},
            {"device_map": device_map},
            {},
        ]
        for kw in kw_variants:
            try:
                model = OmniVoice.from_pretrained(model_ref, **kw)
                _log(f"from_pretrained OK với kwargs={list(kw.keys())}")
                model = _move_to_device(model, device)
                return model
            except TypeError as e:
                errors.append(f"from_pretrained({list(kw.keys())}): {e}")
            except Exception as e:
                # Lỗi không phải do chữ ký (vd tải mạng) → ném ngay, khỏi thử tiếp vô ích
                if not _looks_like_signature_error(e):
                    raise
                errors.append(f"from_pretrained({list(kw.keys())}): {e}")
    # Constructor trực tiếp
    for kw in ({"device": device}, {}):
        try:
            model = OmniVoice(model_ref, **kw)
            _log(f"constructor OK với kwargs={list(kw.keys())}")
            return _move_to_device(model, device)
        except TypeError as e:
            errors.append(f"__init__({list(kw.keys())}): {e}")
        except Exception as e:
            if not _looks_like_signature_error(e):
                raise
            errors.append(f"__init__({list(kw.keys())}): {e}")
    raise RuntimeError("không khớp chữ ký nào: " + " | ".join(errors[-4:]))


def _looks_like_signature_error(e):
    s = str(e).lower()
    return ("argument" in s or "keyword" in s or "positional" in s
            or "unexpected" in s or "missing" in s)


def _move_to_device(model, device):
    """Cố gắng .to(device)/.eval() nếu là nn.Module; bỏ qua nếu không hỗ trợ."""
    for meth, arg in (("to", device), ("eval", None)):
        fn = getattr(model, meth, None)
        if callable(fn):
            try:
                fn(arg) if arg is not None else fn()
            except Exception:
                pass
    return model


def _call_flexible(fn, kwargs_variants=(), args_variants=()):
    """Gọi fn thử lần lượt các bộ kwargs rồi positional args; trả về kết quả của
    bộ đầu tiên chạy được. Ném lỗi cuối nếu tất cả thất bại."""
    last = None
    for kw in kwargs_variants:
        try:
            return fn(**kw)
        except TypeError as e:
            last = e
        except Exception as e:
            if not _looks_like_signature_error(e):
                raise
            last = e
    for ar in args_variants:
        try:
            return fn(*ar)
        except TypeError as e:
            last = e
        except Exception as e:
            if not _looks_like_signature_error(e):
                raise
            last = e
    if last is not None:
        raise last
    raise RuntimeError("không có biến thể tham số nào để gọi")


def _split_audio_sr(ret):
    """generate() có thể trả về audio, hoặc (audio, sr), hoặc dict. Tách (audio, sr)."""
    sr = None
    if isinstance(ret, dict):
        for k in ("audio", "wav", "waveform", "samples"):
            if k in ret:
                audio = ret[k]
                break
        else:
            audio = next(iter(ret.values()))
        for k in ("sample_rate", "sampling_rate", "sr"):
            if k in ret:
                sr = ret[k]
                break
        return audio, sr
    if isinstance(ret, (list, tuple)) and len(ret) == 2 and np.isscalar(ret[1]):
        # (audio, sr)
        return ret[0], ret[1]
    return ret, None


def _generate_one(model, text, language, ref_audio, ref_text, voice_prompt, gen_state):
    """Sinh 1 câu, thử nhiều chữ ký generate(). Ghi nhớ biến thể chạy được vào
    gen_state['ok_call'] để các câu sau gọi thẳng. Trả về (audio, sr)."""
    # Nếu đã biết cách gọi chạy được → dùng lại
    if gen_state.get("ok_call") is not None:
        ret = gen_state["ok_call"](text)
        return _split_audio_sr(ret)

    # Dựng danh sách biến thể (ưu tiên voice_prompt nếu đã cache)
    kw_variants = []
    if voice_prompt is not None:
        kw_variants += [
            {"text": text, "language": language, "voice_clone_prompt": voice_prompt},
            {"text": text, "voice_clone_prompt": voice_prompt},
        ]
    kw_variants += [
        {"text": text, "language": language, "ref_audio": ref_audio, "ref_text": ref_text},
        {"text": text, "ref_audio": ref_audio, "ref_text": ref_text},
        {"text": text, "language": language,
         "reference_audio": ref_audio, "reference_text": ref_text},
        {"text": text, "language": language,
         "prompt_audio": ref_audio, "prompt_text": ref_text},
        {"text": text, "ref_audio": ref_audio},
        {"text": text},
    ]

    last = None
    for kw in kw_variants:
        try:
            ret = model.generate(**kw)
            # Ghi nhớ closure cho các câu sau
            _keys = {k: v for k, v in kw.items() if k != "text"}
            gen_state["ok_call"] = lambda t, _kw=_keys: model.generate(text=t, **_kw)
            _log(f"generate() OK với kwargs={list(kw.keys())}")
            return _split_audio_sr(ret)
        except TypeError as e:
            last = e
        except Exception as e:
            if not _looks_like_signature_error(e):
                raise
            last = e
    if last is not None:
        raise last
    raise RuntimeError("không có biến thể generate() nào chạy được")


def _run_selftest():
    """Kiểm tra môi trường mà KHÔNG sinh audio: import gói, dò lớp model, in chữ ký
    from_pretrained/generate + thiết bị CUDA. Trả về exit code (0 = OK)."""
    import inspect
    print("=== OmniVoice helper self-test ===")
    # 1) Python + soundfile/numpy
    print(f"python      : {sys.version.split()[0]} @ {sys.executable}")
    print(f"numpy       : {np.__version__ if np is not None else '❌ thiếu ('+str(globals().get('_NP_ERR'))+')'}")
    print(f"soundfile   : {getattr(sf, '__version__', None) if sf is not None else '❌ thiếu ('+str(globals().get('_SF_ERR'))+')'}")

    # 2) torch + CUDA
    try:
        import torch
        cuda = torch.cuda.is_available()
        gpu = torch.cuda.get_device_name(0) if cuda else "-"
        print(f"torch       : {torch.__version__} | CUDA={cuda} | GPU={gpu}")
    except Exception as e:
        print(f"torch       : LỖI {e}")

    # 3) gói omnivoice + lớp model
    OmniVoice = _import_omnivoice()
    if OmniVoice is None:
        print("omnivoice   : ❌ KHÔNG import được lớp OmniVoice "
              "(pip install omnivoice trong omnivoice_env?)")
        return 3
    print(f"omnivoice   : ✅ lớp = {OmniVoice.__module__}.{OmniVoice.__name__}")

    # 4) chữ ký các method quan trọng
    for meth in ("from_pretrained", "generate", "create_voice_clone_prompt"):
        fn = getattr(OmniVoice, meth, None)
        if fn is None:
            print(f"  {meth:<26}: (không có)")
            continue
        try:
            sig = str(inspect.signature(fn))
        except Exception:
            sig = "(không đọc được signature)"
        print(f"  {meth:<26}: {sig}")
    print("=== self-test xong — KHÔNG tải model, KHÔNG sinh audio ===")
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--texts-json",     default="",    help="JSON [{index, text}]")
    parser.add_argument("--output-dir",     default="",    help="Thư mục lưu line_NNNN.wav")
    parser.add_argument("--model-dir",      default="",    help="Thư mục model local (rỗng = tự tải từ HF)")
    parser.add_argument("--reference",      default="",    help="File audio giọng mẫu (nhân bản)")
    parser.add_argument("--reference-text", default="",    help="Lời thoại audio mẫu")
    parser.add_argument("--language",       default="vietnamese")
    parser.add_argument("--device",         default="auto", help="auto | cuda | cpu")
    parser.add_argument("--selftest",       action="store_true",
                        help="Chỉ kiểm tra env + chữ ký API rồi thoát (không sinh audio)")
    args = parser.parse_args()

    if args.selftest:
        sys.exit(_run_selftest())

    # Sinh audio cần numpy + soundfile
    if np is None:
        print(f"ERROR:-1:thiếu numpy ({globals().get('_NP_ERR')}) — pip install numpy trong omnivoice_env", flush=True)
        sys.exit(3)
    if sf is None:
        print(f"ERROR:-1:thiếu soundfile ({globals().get('_SF_ERR')}) — pip install soundfile trong omnivoice_env", flush=True)
        sys.exit(3)

    # Các tham số bắt buộc cho chế độ sinh audio (không áp dụng cho --selftest)
    _missing = [n for n, v in (("--texts-json", args.texts_json),
                               ("--output-dir", args.output_dir),
                               ("--reference",  args.reference)) if not v.strip()]
    if _missing:
        print(f"ERROR:-1:thiếu tham số bắt buộc: {', '.join(_missing)}", flush=True)
        sys.exit(2)

    with open(args.texts_json, encoding="utf-8-sig") as f:
        items = json.load(f)

    if not items:
        print("ALL_DONE", flush=True)
        return

    ref_audio = args.reference.strip()
    if not ref_audio or not os.path.isfile(ref_audio):
        print(f"ERROR:-1:không tìm thấy audio mẫu: {ref_audio}", flush=True)
        sys.exit(2)

    model_ref = args.model_dir.strip()
    if model_ref and not os.path.isdir(model_ref):
        print(f"ERROR:-1:thư mục model không tồn tại: {model_ref}", flush=True)
        sys.exit(2)
    if not model_ref:
        model_ref = _DEFAULT_REPO

    # Auto chọn thiết bị
    req = args.device.strip().lower()
    device = "cpu"
    if req in ("auto", "cuda"):
        try:
            import torch
            if torch.cuda.is_available():
                device = "cuda"
                _log(f"GPU: {torch.cuda.get_device_name(0)} → dùng CUDA")
            elif req == "cuda":
                _log("Yêu cầu CUDA nhưng không thấy GPU → dùng CPU")
        except Exception as e:
            _log(f"Không nạp được PyTorch CUDA ({e}) → dùng CPU")
    if device == "cpu":
        _log("Thiết bị: CPU")

    _patch_torchaudio()   # đọc/ghi audio bằng soundfile, không cần torchcodec

    import torch

    OmniVoice = _import_omnivoice()
    if OmniVoice is None:
        print("ERROR:-1:không import được lớp OmniVoice từ gói 'omnivoice' "
              "(kiểm tra: pip install omnivoice trong omnivoice_env)", flush=True)
        sys.exit(3)

    device_map = "cuda:0" if device == "cuda" else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32

    _log(f"Đang load model OmniVoice ({model_ref})...")
    try:
        model = _load_model(OmniVoice, model_ref, device_map, dtype, device)
    except Exception as e:
        # In traceback ra stderr để dễ chẩn đoán; báo ERROR rồi thoát fail-closed.
        import traceback
        _log("Traceback load model:\n" + traceback.format_exc())
        print(f"ERROR:-1:không load được model OmniVoice: {e}", flush=True)
        sys.exit(3)
    _log(f"Model loaded | device: {device}")

    ref_text = args.reference_text.strip()

    # Tối ưu: cache voice prompt 1 lần để khỏi mã hoá lại mỗi câu (nếu API hỗ trợ)
    voice_prompt = None
    for _meth in ("create_voice_clone_prompt", "make_voice_clone_prompt",
                  "create_voice_prompt", "clone_voice"):
        fn = getattr(model, _meth, None)
        if not callable(fn):
            continue
        try:
            voice_prompt = _call_flexible(
                fn,
                kwargs_variants=[
                    {"ref_audio": ref_audio, "ref_text": ref_text},
                    {"reference_audio": ref_audio, "reference_text": ref_text},
                    {"audio": ref_audio, "text": ref_text},
                ],
                args_variants=[(ref_audio, ref_text)],
            )
            _log(f"Đã cache voice prompt ({_meth})")
            break
        except Exception as e:
            _log(f"Không cache được voice prompt qua {_meth} ({e})")
            voice_prompt = None

    os.makedirs(args.output_dir, exist_ok=True)

    MAX_RETRIES = 3
    # Ghi nhớ chữ ký generate() chạy được ở câu đầu để các câu sau gọi thẳng,
    # khỏi dò lại — nhưng vẫn an toàn nếu None (sẽ dò mỗi lần).
    gen_state = {"ok_call": None}

    produced = 0
    for item in items:
        idx  = item["index"]
        text = item["text"]
        out_wav = os.path.join(args.output_dir, f"line_{idx:04d}.wav")

        best_audio = None
        best_sr    = _SAMPLE_RATE
        best_peak  = 0.0
        last_err   = ""

        for attempt in range(MAX_RETRIES):
            try:
                audio, sr = _generate_one(
                    model, text, args.language, ref_audio, ref_text,
                    voice_prompt, gen_state)
                audio_np = _to_mono_np(audio)
                peak = float(np.abs(audio_np).max()) if audio_np.size else 0.0

                if peak > best_peak:
                    best_peak  = peak
                    best_audio = audio_np
                    best_sr    = int(sr) if sr else _SAMPLE_RATE

                if peak > 1e-6:
                    break
                else:
                    print(f"WARN:{idx}:silent attempt {attempt + 1}/{MAX_RETRIES} "
                          f"(peak={peak:.2e})", flush=True)
            except Exception as e:
                last_err = str(e)
                print(f"WARN:{idx}:attempt {attempt + 1} error: {e}", flush=True)

        if best_audio is None or best_peak < 1e-6:
            _reason = "audio silent" if not last_err else last_err.replace("\n", " ")[:160]
            print(f"ERROR:{idx}:{_reason} (sau {MAX_RETRIES} lần thử)", flush=True)
            continue

        best_audio = (best_audio / best_peak * 0.95).astype("float32")
        try:
            sf.write(out_wav, best_audio, best_sr)
        except Exception as e:
            print(f"ERROR:{idx}:ghi file wav lỗi: {e}", flush=True)
            continue
        produced += 1
        print(f"DONE:{idx}", flush=True)

    if produced == 0 and items:
        _log("Không tạo được câu nào — có thể chữ ký generate() của gói khác tài liệu.")
    print("ALL_DONE", flush=True)


if __name__ == "__main__":
    main()
