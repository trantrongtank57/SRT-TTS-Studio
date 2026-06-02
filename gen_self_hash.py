"""gen_self_hash.py — Tạo companion .integrity cho onefile-secured build.

Usage:
    python gen_self_hash.py <path_to_exe>

Tạo file <exe>.integrity cạnh exe, chứa:
    {"h": "<sha256_of_exe>", "s": "<hmac_sig>"}

Companion file này được _check_self_integrity() trong app kiểm tra khi khởi động.
Phân phối exe mà không có companion → app thoát ngay (fail-closed).
"""

import os, sys, json, hashlib, hmac

if len(sys.argv) < 2:
    print("Usage: python gen_self_hash.py <exe_path>")
    sys.exit(1)

exe_path = sys.argv[1]

if not os.path.exists(exe_path):
    print(f"[ERROR] File not found: {exe_path}")
    sys.exit(1)

# ── Cùng XOR pairs với _HMAC_SECRET trong apppp_integrated.py ──────────────
_HS1 = b"\x4e\xc2\x57\x8a\x0d\x15\xfb\x3c\x67\xd4\xa9\x2b\x78\x1e\x65\xe0"
_HS2 = b"\xD1\xFE\xF6\xF1\x5F\xFD\xFF\xEA\xDC\xF5\xF7\xBC\xBB\x5E\xEA\xFA"
_HMAC_SECRET = bytes(a ^ b for a, b in zip(_HS1, _HS2))

# Khoá ký companion — khác khoá auth để phân tách mục đích
_key = hashlib.sha256(_HMAC_SECRET + b"self_integrity_v1").digest()

# ── Hash exe ────────────────────────────────────────────────────────────────
print(f"  Hashing {os.path.basename(exe_path)} ({os.path.getsize(exe_path) // (1024*1024)} MB)...")
h = hashlib.sha256()
with open(exe_path, "rb") as f:
    while True:
        chunk = f.read(65536)
        if not chunk:
            break
        h.update(chunk)
exe_hash = h.hexdigest()

# ── HMAC-sign hash ──────────────────────────────────────────────────────────
sig = hmac.new(_key, exe_hash.encode("utf-8"), hashlib.sha256).hexdigest()

# ── Ghi companion file ──────────────────────────────────────────────────────
companion_path = exe_path + ".integrity"
with open(companion_path, "w", encoding="utf-8") as f:
    json.dump({"h": exe_hash, "s": sig}, f, indent=2)

print(f"  [OK] {os.path.basename(companion_path)} written.")
print(f"       SHA-256: {exe_hash[:32]}...")
print(f"       HMAC:    {sig[:16]}...")
