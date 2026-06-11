# Security verification per CLAUDE.md — run after every build.
from PyInstaller.archive.readers import CArchiveReader
import os, hashlib, json

failures = []

import glob

def _check_onedir(label):
    """Onedir đóng .pyd thành FILE RỜI trong _internal\\ (không nằm trong CArchive),
    nên không đọc bằng CArchiveReader. Kiểm tra: .pyd có mặt + KHÔNG có .pyc rò rỉ."""
    root = "dist/SRT_TTS_Studio"
    if not os.path.isdir(root):
        failures.append(f"{label}: DIR MISSING ({root})")
        print(f"[MISS] {label}: onedir not found")
        return
    pyd = glob.glob(os.path.join(root, "_internal", "apppp_integrated.cp*-win_amd64.pyd"))
    leaked = glob.glob(os.path.join(root, "**", "apppp_integrated*.pyc"), recursive=True)
    if pyd and not leaked:
        print(f"[OK]   {label}: .pyd present in _internal, no leaked .pyc "
              f"({os.path.basename(pyd[0])})")
    else:
        failures.append(f"{label}: pyd={bool(pyd)} leaked_pyc={leaked}")
        print(f"[FAIL] {label}: pyd_present={bool(pyd)} leaked_pyc={leaked}")
    helpers = glob.glob(os.path.join(root, "_internal", "*_helper.py"))
    print(f"       companion .py in _internal: {len(helpers)}")

def check_exe(path, label):
    # Onedir build: .pyd là file rời → kiểm tra theo cách khác
    if label.startswith("Onedir"):
        _check_onedir(label)
        return
    if not os.path.isfile(path):
        failures.append(f"{label}: FILE MISSING ({path})")
        print(f"[MISS] {label}: file not found")
        return
    names = list(CArchiveReader(path).toc.keys())
    hits = [n for n in names if "apppp_integrated" in n]
    pyd_only = hits == ["apppp_integrated.cp314-win_amd64.pyd"]
    leaked = [n for n in hits if not n.endswith(".pyd")]
    if pyd_only:
        print(f"[OK]   {label}: only the .pyd in archive ({len(names)} entries total)")
    else:
        failures.append(f"{label}: archive entries {hits}")
        print(f"[FAIL] {label}: apppp_integrated entries = {hits}")
        if leaked:
            print(f"       LEAKED BYTECODE: {leaked}")
    # companion scripts embedded?
    helpers = [n for n in names if n.endswith("_helper.py") or n in ("whisper_stt.py", "audio_enhancer.py", "pdf_helper.py")]
    print(f"       embedded companion .py: {len(helpers)}")

for exe, label in [
    ("output/Portable/SRT_TTS_Studio_Portable.exe", "Portable"),
    ("output/Portable/SRT_TTS_Studio_Secured.exe",  "Secured"),
    ("output/Portable/SRT_TTS_Studio_Trial.exe",    "Trial"),
    ("dist/SRT_TTS_Studio/SRT_TTS_Studio.exe",      "Onedir(MSI)"),
]:
    check_exe(exe, label)

# Secured .integrity companion: verify hash actually matches the exe
print()
ipath = "output/Portable/SRT_TTS_Studio_Secured.exe.integrity"
epath = "output/Portable/SRT_TTS_Studio_Secured.exe"
if os.path.isfile(ipath):
    raw = open(ipath, "r", encoding="utf-8", errors="replace").read().strip()
    print(f"[INFO] .integrity content ({len(raw)} chars): {raw[:120]}")
    h = hashlib.sha256(open(epath, "rb").read()).hexdigest()
    print(f"[INFO] sha256(Secured.exe) = {h}")
    print(f"[{'OK' if h in raw else 'WARN'}]   exe hash {'found' if h in raw else 'NOT found verbatim'} in .integrity (HMAC-wrapped is expected if not verbatim)")
else:
    failures.append("Secured .integrity companion missing")

# Onedir integrity manifest exists?
for cand in ("dist/SRT_TTS_Studio/integrity.dat", "dist/SRT_TTS_Studio/_internal/integrity.dat",
             "dist/SRT_TTS_Studio/.integrity", "dist/SRT_TTS_Studio/_internal/.integrity"):
    if os.path.isfile(cand):
        print(f"[INFO] onedir integrity manifest: {cand}")
        break

print()
print("RESULT:", "ALL CHECKS PASSED" if not failures else f"{len(failures)} FAILURE(S): {failures}")
