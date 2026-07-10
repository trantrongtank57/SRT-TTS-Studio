# -*- mode: python ; coding: utf-8 -*-
# Onedir build with the Cython extension as the REAL executed code.
#
# Entry = srt_tts_launch.py (only does `import apppp_integrated`).
# Analysis traces dependencies from apppp_integrated.py (source, present in the
# repo root which is on pathex), then we STRIP the plaintext bytecode of
# apppp_integrated from the PYZ so ONLY the compiled .pyd ships.
#
# cython_out\ is NOT on pathex, so analysis resolves the .py source (for dep
# tracing) and never the .pyd. The .pyd is added explicitly as a binary and is
# what `import apppp_integrated` resolves to at runtime (from _internal/).
import glob

_pyd = glob.glob(r'cython_out\apppp_integrated*.pyd')
if not _pyd:
    raise FileNotFoundError(
        r"cython_out\apppp_integrated*.pyd not found — run the Cython compile (step 5) first."
    )
_pyd_src = _pyd[0]

a = Analysis(
    ['srt_tts_launch.py'],
    pathex=[],
    binaries=[(_pyd_src, '.')],
    datas=[
        ('logo.png',                    '.'),
        ('logo.ico',                    '.'),
        ('naycaugioi.wav',              '.'),
        ('toyeucaunhieulamday.wav',     '.'),
        ('chungtakhongthuocvenhau.wav', '.'),
        ('error.wav',                   '.'),
        ('CHANGELOG.md',                '.'),   # 🆕 dialog "Có gì mới"
    ],
    hiddenimports=[
        'edge_tts', 'edge_tts.communicate', 'srt',
        'customtkinter', 'PIL', 'PIL.Image', 'PIL.ImageTk',
        'speech_recognition', 'audioop', 'winreg',
        'pypdf', 'pypdf._reader', 'pypdf._writer', 'pypdf.generic',
        'fpdf', 'docx', 'psutil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# CRITICAL: drop the plaintext bytecode of the main module from the PYZ —
# ship ONLY the one-way-compiled .pyd. Without this line the original source
# would be recoverable as Python bytecode (decompilable), defeating Cython.
a.pure = [x for x in a.pure
          if not (x[0] == 'apppp_integrated' or x[0].startswith('apppp_integrated.'))]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SRT_TTS_Studio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SRT_TTS_Studio',
)
