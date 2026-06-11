import re, collections

pyd = r"dist/SRT_TTS_Studio/_internal/apppp_integrated.cp314-win_amd64.pyd"
data = open(pyd, "rb").read()
print(f"pyd size: {len(data):,} bytes\n")

# Extract printable ASCII runs >= 5 chars
ascii_runs = re.findall(rb"[\x20-\x7e]{5,}", data)
strs = [s.decode("ascii", "ignore") for s in ascii_runs]
print(f"total ascii runs >=5: {len(strs):,}\n")

def show(label, pred, limit=40):
    hits = sorted({s for s in strs if pred(s)})
    print(f"=== {label}: {len(hits)} unique ===")
    for s in hits[:limit]:
        print("   ", s)
    if len(hits) > limit:
        print(f"    ... +{len(hits)-limit} more")
    print()

# 1) Function / def names (Cython mangles as __pyx_pf_... / __pyx_f_...)
show("function-ish names (def/_ prefixed words)",
     lambda s: bool(re.fullmatch(r"_[a-z][a-z0-9_]{3,}", s)), 60)

# 2) The original source filename + line markers
show("source-file references",
     lambda s: "apppp_integrated" in s or s.endswith(".py") or s.endswith(".pyx"))

# 3) URLs / endpoints
show("URLs / hosts",
     lambda s: "http" in s.lower() or ".ai" in s.lower() or "api." in s.lower() or ".com" in s.lower())

# 4) Vietnamese / UI / error strings (look for common words)
show("revealing literals (keywords)",
     lambda s: any(k in s.lower() for k in ("password","secret","key","token","auth","license","trial","integrity","hmac","pbkdf2","salt","fpt","vbee","zalo","everai","minimax")), 60)

# 5) docstrings markers
show("docstring-ish (sentences with spaces)",
     lambda s: " " in s and len(s) > 25 and re.search(r"[a-z]{3,}\s+[a-z]{3,}", s.lower()) is not None, 30)
