# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SRT TTS Studio** — Windows desktop app (CustomTkinter) that converts SRT subtitle files and PDFs to TTS audio (MP3) via Microsoft Edge TTS and Vietnamese TTS APIs (FPT.AI, Vbee, Zalo AI, EverAI, MiniMax). Also includes RVC voice cloning, VoxCPM voice cloning, Video OCR, Speech-to-Text, and video repair utilities. Distributed as `.msi` installer and standalone `.exe` files via PyInstaller + WiX Toolset.

## Build Commands

```bat
:: Full build — all 4 outputs (recommended)
build_all.bat

:: Dev run (no build needed)
python apppp_integrated.py

:: Regenerate integrity manifest after modifying onedir dist
python gen_integrity.py

:: Regenerate secured-exe companion integrity
python gen_self_hash.py "dist\SRT_TTS_Studio_Secured.exe"
```

**To invoke `build_all.bat` from a script/automation** (git-bash converts `/c` to `C:/` — use this form):
```bash
MSYS_NO_PATHCONV=1 cmd.exe /c "E:\path\to\run_build.bat"
# where run_build.bat contains: cd /d <project_dir> && call "<abs_path>\build_all.bat"
```
Note: background shell processes do not inherit cwd — always use absolute path in `call`.

## Build Pipeline (build_all.bat, steps 0–9)

| Step | What happens |
|---|---|
| 0 | Source validation — aborts if any companion `.py`, model `.pt`, `rvc_env\Scripts\python.exe`, spec, `.dat`, or `srt_tts_launch.py` is missing |
| 1–3 | Python deps, MSVC Build Tools, WiX Toolset v3 (auto-install if absent) |
| 4 | **PyArmor DISABLED** — was inert (runtime never reached bundle); Cython is the real protection layer |
| 5 | Cython compiles `apppp_integrated.py` → `cython_out\apppp_integrated.cp3xx-win_amd64.pyd` (native DLL). The `.pyd` goes to `cython_out\` (off pathex) so PyInstaller's dep-tracing still reads the `.py` source. |
| 6A | PyInstaller onedir using `SRT_TTS_Studio_onedir.spec` |
| 6B | Bundle ffmpeg/ffprobe |
| 6C | `gen_integrity.py` |
| **6G** | **FAIL-CLOSED** copy of 8 companion `.py` + `hubert_base.pt` + `rmvpe.pt` + `rvc_env\` into `dist\SRT_TTS_Studio\`; verifies each file landed; aborts if anything missing. Must run before step 7 so WiX Heat picks them up. |
| 6D/E/F | 3 onefile PyInstaller builds (Portable / Secured / Trial) |
| 7–8 | WiX Heat → candle → light → MSI |
| 9 | `output\SRT_TTS_Studio_Setup.msi` + `output\Portable\` (exes + companion files + models + rvc_env) |

### Output layout
```
output\
  SRT_TTS_Studio_Setup.msi        ← self-contained installer (~900 MB with rvc_env)
  MOVE_CHECKLIST.txt
  Portable\
    SRT_TTS_Studio_Portable.exe   ← onefile
    SRT_TTS_Studio_Secured.exe    ← onefile + .integrity companion
    SRT_TTS_Studio_Trial.exe      ← onefile, 24h trial
    8× companion .py              ← must sit next to exe (also embedded in exe via datas)
    hubert_base.pt, rmvpe.pt
    rvc_env\
```

## Critical: Security / Code Protection Architecture

**The entry point is `srt_tts_launch.py`, not `apppp_integrated.py`.**

```python
# srt_tts_launch.py — entire content:
import apppp_integrated  # executes the whole app (mainloop is at module level)
```

All 4 specs (`SRT_TTS_Studio_onedir.spec`, `*_onefile.spec`, `*_secured.spec`, `*_trial.spec`) use `srt_tts_launch.py` as entry and include this critical filter:

```python
# Strip the plaintext bytecode of the main module from the PYZ —
# ship ONLY the one-way-compiled .pyd (native machine code).
a.pure = [x for x in a.pure
          if not (x[0] == 'apppp_integrated' or x[0].startswith('apppp_integrated.'))]
```

**Without this filter**: PyInstaller embeds `apppp_integrated.py` as recoverable bytecode (1 MB marshal blob). An attacker extracts all 474 function names + `_HMAC_SECRET`/`_PBKDF2_SALT` byte literals in ~2 minutes via `pyinstxtractor` + `marshal.loads`. With the filter: only the PE DLL (`.pyd`) is in the archive; `marshal.loads` rejects it and no Python decompiler exists for Cython output.

**Cython string storage note**: Python string literals compiled by Cython are stored as `PyObject*` intern references in the `.pyd`, NOT as flat raw bytes. Searching the `.pyd` binary for string content will return no matches — this is correct and expected. The strings are present logically and function correctly at runtime.

**Verifying the protection is working** (run after any build):
```python
from PyInstaller.archive.readers import CArchiveReader
import marshal
r = CArchiveReader("dist/SRT_TTS_Studio/SRT_TTS_Studio.exe")
names = list(r.toc.keys())
# Must be EMPTY — if 'apppp_integrated' appears as bytecode, the strip filter was lost
assert not any('apppp_integrated' in n for n in names if not n.endswith('.pyd'))
```

### Security layers at runtime
1. **Cython `.pyd`** — native x64 machine code; no Python decompiler exists
2. **Integrity check** (`_check_integrity`, line ~114) — SHA-256 of `.exe` + `.pyd` vs `.integrity` file; fail-closed; runs at import time before any UI
3. **Self-integrity** (Secured variant only) — SHA-256 + HMAC of exe vs companion `.integrity`
4. **Hardware DRM** — `auth.dat` HMAC-signed with CPU `ProcessorId` + C: volume serial
5. **PBKDF2 password** — 200k iterations; `_HMAC_SECRET` / `_PBKDF2_SALT` XOR-split across two byte literals in source (do NOT change after deployment — breaks existing `auth.dat`)
6. **Brute-force lockout** — 5 failures → 15-min lockout in `.lockout` file (HMAC-signed, hardware-bound)
7. **Trial** (Trial variant only) — 24h via registry×2 + `%LOCALAPPDATA%` file; anti-rollback; `_detect_vm()` blocks trial in VMs/sandboxes

Security checks run at **module import time** (top-level, before `if __name__`): `_check_integrity()` → `_check_self_integrity()` → `_check_trial()`.

### VM Detection (`_detect_vm`) Architecture

`_detect_vm()` is called only from `_check_trial()` and only when `build_type_trial.dat` is present in `sys._MEIPASS` (i.e., only the Trial variant blocks VMs). Non-trial builds skip it entirely.

Detection uses 6 independent layers — passing one layer is enough:

| Layer | Method | Covers |
|---|---|---|
| 0 | `USERNAME == WDAGUtilityAccount` env var + `WDAGAgent.exe` process | Windows Sandbox (100% definitive) |
| 1 | Registry keys: `vmicheartbeat`, `vmicshutdown`, `vmicvss`, `vmicrdv` services; `Virtual Machine\Guest\Parameters` | Hyper-V guest with Integration Services (guest-only keys, never on host) |
| 2 | BIOS registry: `SystemProductName`, `SystemManufacturer`, `BIOSVendor`, etc. containing vmware/virtualbox/qemu/parallels/bhyve/`virtual machine` | Standard VMs with default BIOS strings |
| 3 | MAC OUI (`_mac_oui_definitive`): VMware `000c29/005056`, VBox `080027`, Parallels `001c42`, QEMU `525400`, Xen `00163e` | All major VM platforms (OUIs never appear on real hardware) |
| 4 | Process list: `vmtoolsd`, `vboxservice`, `qemu-ga`, `prl_tools`, `xenservice`, `sbiesvc`, `wdagagent` | Guest tool processes |
| 5 | WMI `wmic` output: `virtual hd` (Hyper-V Gen1), `msft virtual disk` (Hyper-V Gen2/Sandbox), vendor strings | Hyper-V guests, Sandbox via disk caption |
| 6 | **Combined guard**: Hyper-V MAC OUI (`_mac_oui_hyperv`: `000d3a`, `001dd8`, `00155d`) + generic `virtual disk` in WMI — **both required** | Hyper-V guest without IS, custom BIOS |

**Hyper-V host false-positive risk (known issue)**: `00155d` vEthernet adapters appear on physical machines with Hyper-V enabled (Docker/WSL2). The combined guard (Layer 6) can false-positive if the host ALSO has Storage Spaces/iSCSI disks showing "Virtual Disk". Layer 6 is a fallback only; Layers 1–2 already cover standard Hyper-V guests reliably.

## Codebase Structure

`apppp_integrated.py` (~8200 lines) is the **entire application** — no modules, packages, or separate files for UI vs logic. All TTS providers, UI, video tools, auth, and utilities are inline.

`app.mainloop()` runs at **module level** (not inside `__main__`), so `import apppp_integrated` starts the full app. This is intentional for the launcher entry-point pattern.

## Companion Script System

8 scripts in the project root are invoked as **subprocesses** (not imported). Each `_find_*_helper()` function searches in this order: `sys._MEIPASS` → exe dir → script dir → PATH.

| Script | Interpreter | Purpose |
|---|---|---|
| `rvc_helper.py` | `rvc_env\Scripts\python.exe` (Python 3.10) | RVC voice conversion |
| `voxcpm_helper.py` | `voxcpm_env\Scripts\python.exe` (Python 3.11) | VoxCPM batch TTS |
| `whisper_stt.py` | voxcpm_env python | STT for reference audio (stderr: `PROGRESS:done_ms:total_ms`) |
| `audio_enhancer.py` | voxcpm_env python | Demucs/denoise/bandpass (stdout: `PCT:done:100`) |
| `pdf_helper.py` | any python with pypdf | PDF → JSON chunks |
| `srt_align_helper.py` | voxcpm_env python | VAD-based SRT timing alignment |
| `videocr_helper.py` | any python | Video OCR wrapper |
| `video_stt_helper.py` | voxcpm_env python | faster-whisper STT (stdout: `PROGRESS:N:M`, `DONE:path`) |

**Onefile exes embed all 8 `.py` files** via `datas` in the specs — `sys._MEIPASS` is checked first so no loose `.py` files are needed next to the exe. Models (`hubert_base.pt`, `rmvpe.pt`) and `rvc_env\` are NOT embedded (too large) — they must be in the same directory as the exe.

### Helper progress protocol
All long-running helpers stream progress so the UI bar tracks them. Use `subprocess.Popen` + line-by-line stdout read (never `communicate()` which blocks). Parse `PROGRESS:N:M` → `update_progress(N, M)`.

## Settings System (`settings.json`)

Loaded at startup via `_load_settings()`, saved via `show_settings_dialog()`. Lives next to the exe.

| Key | Global | Overrides |
|---|---|---|
| `ffmpeg_dir` | `FFMPEG_DIR` | Checked first in `get_ffmpeg()` / `get_ffprobe()` |
| `videocr_cli_dir` | `VIDEOCR_CLI_DIR` | Passed as env var to `videocr_helper.py` |
| `voxcpm_ckpt_dir` | `voxcpm_ckpt_var` | VoxCPM model path; seed for `_find_voxcpm_python()` |
| `voxcpm_env_override` | `VOXCPM_ENV_OVERRIDE` | Explicit python.exe; checked **first** in all `_find_*_python()` calls |
| `subtitle_edit_path` | `SUBTITLE_EDIT_PATH` | Prepended to Subtitle Edit search list |

## rvc_env Compatibility Patches

These patches must be re-applied if `rvc_env` is ever recreated (fairseq 0.12.2 + PyTorch 2.6+ compatibility):

| File | Patch |
|---|---|
| `fairseq/checkpoint_utils.py` (×2) | Add `weights_only=False` to `torch.load()` |
| `infer_rvc_python/main.py` | `weights_only=False`; add `index.nprobe = min(getattr(index, 'nlist', 16), 32)` after `faiss.read_index()` |
| `infer_rvc_python/lib/rmvpe.py` | `weights_only=False` |
| `torchcrepe/load.py` | `weights_only=False` |
| `infer_rvc_python/root_pipe.py` | `np.square(1 / score)` → `np.square(1 / (score + 1e-6))` |

Never run `rvc_helper.py` with Python 3.11 — fairseq 0.12.2 requires Python 3.10.

## Deployment: What Needs Manual Setup on Target Machine

The MSI installs everything bundled. These components are too large to bundle and must be copied + configured via ⚙ Cài đặt:

| Component | Size | Needed for |
|---|---|---|
| `voxcpm_env\` | ~6–8 GB | VoxCPM TTS, STT, audio enhance, SRT align, PDF |
| VoxCPM model (`VoxCPM-1.5-VN/`) | ~3.5 GB | VoxCPM TTS |
| VideOCR CLI | small | Video OCR |

Default paths hardcoded in source (override via ⚙ Cài đặt):
- `VIDEOCR_CLI_DIR`: `C:\Users\os\Downloads\Compressed\VideOCR-1.5.1\...\CLI`
- VoxCPM ckpt seed: `E:\VoxCPM-1.5-VN\VoxCPM\pretrained\VoxCPM-1.5-VN`

See `MOVE_CHECKLIST.txt` for the step-by-step checklist when moving to a new machine.
