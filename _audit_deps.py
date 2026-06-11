# -*- coding: utf-8 -*-
"""Quét mọi phụ thuộc NẰM NGOÀI folder build nhưng app vẫn cần.
Phân loại: env venv, model local, runtime HF/torch cache, CLI ngoài.
In ✅/❌ theo thực tế máy này + cảnh báo cái nào sẽ thiếu khi copy sang máy khác."""
import os, sys, glob
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")

def exists_dir(p):  return bool(p) and os.path.isdir(p)
def exists_file(p): return bool(p) and os.path.isfile(p)

def find_beside(*subs):
    """Dò cạnh ROOT + 3 cấp cha (giống _install_dirs/_auto_find_dir)."""
    bases = [ROOT]
    p = ROOT
    for _ in range(3):
        p = os.path.dirname(p)
        if p and p not in bases:
            bases.append(p)
    for b in bases:
        for s in subs:
            parts = s if isinstance(s, tuple) else (s,)
            c = os.path.join(b, *parts)
            if os.path.isdir(c):
                return c
    return ""

print("="*70)
print("AUDIT PHỤ THUỘC NGOÀI FOLDER —", ROOT)
print("="*70)

def find_env_extra(env_name, extra_roots=()):
    """Dò env: cạnh app + 3 cấp cha (find_beside), RỒI cạnh các thư mục gốc thêm
    (leo lên tối đa 3 cấp) — khớp cách app _find_*_python() dò từ thư mục model."""
    found = find_beside(env_name)
    if found:
        return found
    for root in extra_roots:
        if not root:
            continue
        p = root
        for _ in range(4):           # chính nó + 3 cấp cha
            cand = os.path.join(p, env_name)
            if os.path.isdir(cand):
                return cand
            np = os.path.dirname(p)
            if np == p:
                break
            p = np
    return ""

# ---- 1) Các venv môi trường (mỗi engine 1 venv riêng) ----
print("\n[1] MÔI TRƯỜNG VENV (mỗi cái vài GB — KHÔNG nằm trong repo trừ rvc_env):")
# voxcpm_env hay nằm CẠNH model VoxCPM (vd E:\VoxCPM-1.5-VN\voxcpm_env) — app dò
# bằng cách leo lên từ thư mục ckpt, nên audit cũng phải dò thêm các gốc đó.
_vox_roots = [
    find_beside(("VoxCPM","pretrained","VoxCPM-1.5-VN"), "VoxCPM-1.5-VN", "VoxCPM-model"),
    r"E:\VoxCPM-1.5-VN", r"E:\VoxCPM-1.5-VN\VoxCPM\pretrained\VoxCPM-1.5-VN",
]
_env_roots = {"voxcpm_env": _vox_roots}
ENVS = ["rvc_env", "voxcpm_env", "vieneu_env", "f5tts_env", "omnivoice_env"]
for e in ENVS:
    found = find_env_extra(e, _env_roots.get(e, ()))
    py = os.path.join(found, "Scripts", "python.exe") if found else ""
    ok = exists_file(py)
    print(f"  {'✅' if ok else '❌'} {e:15s} -> {py or '(không thấy cạnh app / cạnh model)'}")

# ---- 2) Model local (folder model, không phải auto-download) ----
print("\n[2] MODEL LOCAL (folder chứa file model):")
# VoxCPM
vox = find_beside(("VoxCPM","pretrained","VoxCPM-1.5-VN"), "VoxCPM-1.5-VN", "VoxCPM-model") \
      or r"E:\VoxCPM-1.5-VN\VoxCPM\pretrained\VoxCPM-1.5-VN"
print(f"  {'✅' if exists_dir(vox) else '❌'} VoxCPM model   -> {vox}")
# F5-TTS (bắt buộc local, ship trong output\Portable)
f5 = find_beside("F5-TTS-Vietnamese-ViVoice")
f5_pt = ""
if f5:
    cands = glob.glob(os.path.join(f5, "*.pt")) + glob.glob(os.path.join(f5, "*.safetensors"))
    f5_pt = cands[0] if cands else ""
    vocab = os.path.join(f5, "vocab.txt")
    print(f"  {'✅' if f5_pt else '❌'} F5-TTS model   -> {f5} "
          f"(model={'có' if f5_pt else 'THIẾU .pt'}, vocab.txt={'có' if exists_file(vocab) else 'THIẾU'})")
else:
    print(f"  ❌ F5-TTS model   -> (không thấy F5-TTS-Vietnamese-ViVoice cạnh app)")

# ---- 3) RVC model files (ship cạnh exe) ----
print("\n[3] FILE MODEL RVC (phải nằm cạnh exe):")
for f in ["hubert_base.pt", "rmvpe.pt"]:
    found = find_beside() and os.path.join(ROOT, f)
    print(f"  {'✅' if exists_file(os.path.join(ROOT,f)) else '❌'} {f}")

# ---- 4) Runtime model auto-download (HF cache + torch hub) ----
print("\n[4] MODEL AUTO-DOWNLOAD (HF/torch cache ~/.cache — KHÔNG nằm trong bất kỳ folder copy nào):")
hf_hub = os.path.join(HOME, ".cache", "huggingface", "hub")
def hf_has(repo):
    if not os.path.isdir(hf_hub): return False
    key = "models--" + repo.replace("/", "--")
    return os.path.isdir(os.path.join(hf_hub, key))
def hf_has_prefix(prefix):
    if not os.path.isdir(hf_hub): return False
    key = "models--" + prefix.replace("/", "--")
    return any(d.startswith(key) for d in os.listdir(hf_hub))

HF_MODELS = [
    ("OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano", "VoxCPM (BẮT BUỘC)"),
    ("charactr/vocos-mel-24khz",                "F5-TTS vocoder (BẮT BUỘC)"),
    ("pnnbao-ump/VieNeu-TTS-v3-Turbo",          "VieNeu (nếu không có model local)"),
    ("splendor1811/omnivoice-vietnamese",       "OmniVoice (nếu không có model local)"),
]
for repo, note in HF_MODELS:
    print(f"  {'✅' if hf_has(repo) else '❌'} {repo:42s} [{note}]")
print(f"  {'✅' if hf_has_prefix('Systran/faster-whisper') else '❌'} Systran/faster-whisper-* (STT + Video-STT)")

# torch hub: demucs htdemucs
th = os.path.join(HOME, ".cache", "torch", "hub", "checkpoints")
demucs = bool(glob.glob(os.path.join(th, "955717e8-*.th"))) if os.path.isdir(th) else False
print(f"  {'✅' if demucs else '❌'} demucs htdemucs (955717e8-*.th)   [Tách nhạc — torch hub cache]")

# ---- 5) CLI ngoài ----
print("\n[5] CLI NGOÀI:")
vc = find_beside(("VideOCR","CLI"), "VideOCR-CLI", ("VideOCR-1.5.1","VideOCR-1.5.1","CLI")) \
     or r"C:\Users\os\Downloads\Compressed\VideOCR-1.5.1\VideOCR-1.5.1\CLI"
print(f"  {'✅' if exists_dir(vc) else '❌'} VideOCR CLI    -> {vc}")

# ---- 6) Output build: cái gì ĐÃ được copy vào output\Portable ----
print("\n[6] OUTPUT BUILD (output\\Portable — cái gì build đã đóng gói sẵn):")
portable = os.path.join(ROOT, "output", "Portable")
if os.path.isdir(portable):
    for name in ["SRT_TTS_Studio_Portable.exe", "rvc_env", "hubert_base.pt",
                 "rmvpe.pt", "F5-TTS-Vietnamese-ViVoice"]:
        p = os.path.join(portable, name)
        ok = os.path.exists(p)
        print(f"  {'✅' if ok else '❌'} output\\Portable\\{name}")
    # các env KHÔNG được build copy → phải tay
    print("  --- (các env/model dưới đây build KHÔNG tự copy, phải copy tay):")
    for name in ["voxcpm_env", "vieneu_env", "f5tts_env", "omnivoice_env",
                 "VoxCPM-1.5-VN", "VideOCR"]:
        p = os.path.join(portable, name)
        print(f"  {'✅ có sẵn' if os.path.exists(p) else '⬜ chưa copy'} output\\Portable\\{name}")
else:
    print("  ❌ Chưa có output\\Portable — build chưa xong?")
print("\nDONE.")
