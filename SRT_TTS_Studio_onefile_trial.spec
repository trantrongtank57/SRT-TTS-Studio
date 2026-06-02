# -*- mode: python ; coding: utf-8 -*-
# Trial onefile build — produces SRT_TTS_Studio_Trial.exe
# Contains build_type_trial.dat marker; _check_trial() enforces 24-hour time limit.
# Trial data stored in HKCU registry (2 locations), HMAC-signed & hardware-bound.
# No companion .integrity needed — trial check runs independently.
#
# Prerequisite: run the onedir build (SRT_TTS_Studio.spec) first so that
#   dist\SRT_TTS_Studio\_internal\apppp_integrated*.pyd exists.

import glob, os

_pyd_matches = glob.glob(r'dist\SRT_TTS_Studio\_internal\apppp_integrated*.pyd')
if not _pyd_matches:
    raise FileNotFoundError(
        "apppp_integrated*.pyd not found in dist\\SRT_TTS_Studio\\_internal\\\n"
        "Run the onedir build (SRT_TTS_Studio.spec) first."
    )
_pyd_src = _pyd_matches[0]

a = Analysis(
    ['srt_tts_launch.py'],
    pathex=[],
    binaries=[
        (_pyd_src,                               '.'),
        (r'dist\SRT_TTS_Studio\ffmpeg.exe',  '.'),
        (r'dist\SRT_TTS_Studio\ffprobe.exe', '.'),
    ],
    datas=[
        ('logo.png',                   '.'),
        ('logo.ico',                   '.'),
        ('naycaugioi.wav',             '.'),
        ('toyeucaunhieulamday.wav',    '.'),
        ('chungtakhongthuocvenhau.wav', '.'),
        ('error.wav',                  '.'),
        ('build_type_trial.dat',       '.'),   # marker: trial build
        # Companion scripts — run as subprocesses; resolved via sys._MEIPASS first.
        ('rvc_helper.py',              '.'),
        ('voxcpm_helper.py',           '.'),
        ('whisper_stt.py',             '.'),
        ('audio_enhancer.py',          '.'),
        ('pdf_helper.py',              '.'),
        ('srt_align_helper.py',        '.'),
        ('videocr_helper.py',          '.'),
        ('video_stt_helper.py',        '.'),
    ],
    hiddenimports=[
        'edge_tts', 'edge_tts.communicate', 'srt',
        'customtkinter', 'PIL', 'PIL.Image', 'PIL.ImageTk',
        'speech_recognition', 'audioop',
        'winreg',
        'pypdf', 'pypdf._reader', 'pypdf._writer', 'pypdf.generic',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
# CRITICAL: drop the plaintext bytecode of the main module — ship ONLY the .pyd.
a.pure = [x for x in a.pure
          if not (x[0] == 'apppp_integrated' or x[0].startswith('apppp_integrated.'))]
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SRT_TTS_Studio_Trial',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo.ico'],
)
# No COLLECT() — everything is packed inside the single exe
