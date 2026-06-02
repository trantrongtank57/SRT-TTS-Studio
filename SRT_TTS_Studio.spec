# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['apppp_integrated.py'],
    pathex=[],
    binaries=[('apppp_integrated.cp314-win_amd64.pyd', '.')],
    datas=[('logo.png', '.'), ('logo.ico', '.'), ('naycaugioi.wav', '.'), ('toyeucaunhieulamday.wav', '.'), ('chungtakhongthuocvenhau.wav', '.'), ('error.wav', '.')],
    hiddenimports=['edge_tts', 'edge_tts.communicate', 'srt', 'customtkinter', 'PIL', 'PIL.Image', 'PIL.ImageTk'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
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
