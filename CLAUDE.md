# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SRT TTS Studio** — Windows desktop app (CustomTkinter) that converts SRT subtitle files and PDFs to TTS audio (MP3) via Microsoft Edge TTS and Vietnamese TTS APIs (FPT.AI, Vbee, Zalo AI, EverAI, MiniMax). Also includes RVC voice cloning, VoxCPM voice cloning, Video OCR, Speech-to-Text, video compression, and video repair utilities. Distributed as `.msi` installer and standalone `.exe` files via PyInstaller + WiX Toolset.

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

### Spec files

| File | Purpose |
|---|---|
| `SRT_TTS_Studio_onedir.spec` | Onedir build → MSI via WiX |
| `SRT_TTS_Studio_onefile.spec` | Portable standalone exe |
| `SRT_TTS_Studio_onefile_secured.spec` | Secured exe + `.integrity` companion |
| `SRT_TTS_Studio_onefile_trial.spec` | Trial exe (24h, VM-blocked) |
| `SRT_TTS_Studio.spec` | Legacy / reference |

All specs use `srt_tts_launch.py` as entry and **must** contain the `a.pure` filter that strips `apppp_integrated` bytecode from the PYZ — removing it exposes the full source as recoverable marshal blob.

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

All 4 specs use `srt_tts_launch.py` as entry and include this critical filter:

```python
# Strip the plaintext bytecode of the main module from the PYZ —
# ship ONLY the one-way-compiled .pyd (native machine code).
a.pure = [x for x in a.pure
          if not (x[0] == 'apppp_integrated' or x[0].startswith('apppp_integrated.'))]
```

**Without this filter**: PyInstaller embeds `apppp_integrated.py` as recoverable bytecode (1 MB marshal blob). An attacker extracts all function names + `_HMAC_SECRET`/`_PBKDF2_SALT` byte literals in ~2 minutes via `pyinstxtractor` + `marshal.loads`. With the filter: only the PE DLL (`.pyd`) is in the archive; `marshal.loads` rejects it and no Python decompiler exists for Cython output.

**Cython string storage note**: Python string literals compiled by Cython are stored as `PyObject*` intern references in the `.pyd`, NOT as flat raw bytes. Searching the `.pyd` binary for string content will return no matches — this is correct and expected.

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

`apppp_integrated.py` (~8400 lines) is the **entire application** — no modules, packages, or separate files for UI vs logic. All TTS providers, UI, video tools, auth, and utilities are inline.

`app.mainloop()` runs at **module level** (not inside `__main__`), so `import apppp_integrated` starts the full app. This is intentional for the launcher entry-point pattern.

### High-level layout inside `apppp_integrated.py`

| Lines (approx.) | Section |
|---|---|
| 1–100 | Imports, constants (`CREATE_NO_WINDOW`), `get_ffmpeg()`, `get_ffprobe()`, `_detect_gpu()` |
| 100–850 | Security checks (`_check_integrity`, DRM, trial, VM detection), global state vars |
| 850–1100 | Settings load/save, CustomTkinter app/window creation, UI layout frames |
| 1100–2600 | Voice/provider UI, progress bar canvas, button rows `_brow0`–`_brow6` definition |
| 2600–3200 | Fireworks animation + sound, `log()`, `update_progress()`, helper utilities |
| 3200–5600 | Feature functions: TTS (Edge, FPT, Vbee, Zalo, EverAI, MiniMax), RVC, VoxCPM, PDF |
| 5600–7400 | Video tools (scan/repair/clean), Subtitle Edit, OCR, STT, video compress |
| 7400–7700 | UI widget instantiation for all button rows |
| 7700–8050 | `set_mode()` — the central UI state machine |
| 8050–end | `app.mainloop()` at module level |

## UI Architecture Patterns (apppp_integrated.py)

### Button rows
The button panel uses 7 fixed rows (`_brow0`–`_brow6`) created once at startup and populated later. All rows are `ctk.CTkFrame` packed into `button_frame`. When adding a new feature, add a new `_browN` at the row-definition block (~line 2610) **and** populate it in the widget-instantiation block (~line 7400).

### set_mode() — UI state machine
`set_mode(mode)` is the single function that enables/disables all buttons and controls. It must be called from the main thread (use `app.after(0, lambda: set_mode("..."))` from worker threads). Every new feature needs:
1. Its buttons added to a `_feature_btns` list inside `set_mode`
2. New `elif mode == "feature_ready":` / `"feature_running":` / `"feature_done":` branches
3. The feature's buttons included in the disable sweep of all unrelated modes

Current modes: `srt`, `pdf`, `pdf_tts_done`, `video`, `reset`, `tts_running`, `tts_stopped`, `tts_done`, `scanning`, `scan_done`, `scan_done_clean`, `repairing`, `repair_done`, `cleaning`, `clean_done`, `videocr`, `videocr_running`, `videocr_done`, `video_stt`, `video_stt_running`, `video_stt_done`, `compress_ready`, `compressing`, `compress_done`.

### Thread safety
All UI mutations **must** happen on the main thread. From any worker thread:
```python
app.after(0, lambda: log("message"))
app.after(0, lambda: set_mode("done"))
update_progress(current, total)  # safe — internally uses app.after
```
Never call `log()`, `set_mode()`, or any CTk widget method directly from a thread.

### Progress bar
Always use `update_progress(current, total)` — never manipulate `progress_var` or `progress_bar` directly. The function is thread-safe and drives the animated canvas bar. Parse ffmpeg progress from stderr via `re.search(r"time=(\d+):(\d+):([\d.]+)", line)` and convert to percentage of total duration.

### Completion effect
Call `app.after(0, show_fireworks)` when any major operation completes successfully. This is the convention used by all TTS, OCR, STT, and compress flows.

### Subprocess rules

**Always pre-check executable existence before `Popen`** — on Windows, `Popen` with `CREATE_NO_WINDOW` on a missing executable can hang waiting for Windows Error Reporting instead of raising `FileNotFoundError` immediately:
```python
# Correct pattern (see _check_ffmpeg_exists())
ffmpeg_ok, ffmpeg_path, guide = _check_ffmpeg_exists()
if not ffmpeg_ok:
    for line in guide.splitlines():
        app.after(0, lambda l=line: log(l))
    app.after(0, lambda: set_mode("compress_ready"))
    return
# Only now is it safe to call Popen
proc = subprocess.Popen([ffmpeg_path, ...], creationflags=CREATE_NO_WINDOW)
```

Check pattern: `os.path.isfile(path) or shutil.which(path)`.

**Always use `CREATE_NO_WINDOW`** on all subprocess calls to prevent console windows flashing.

**Never use `communicate()`** for long-running processes — it blocks until completion with no progress. Always use `Popen` + line-by-line `for line in proc.stdout:`.

### Launching external applications
Use `ctypes.windll.shell32.ShellExecuteW(None, "open", exe, args, None, 1)` instead of `subprocess.Popen` to launch GUI apps like Subtitle Edit. This launches them as independent processes (not child processes) so that the Windows IME (Unikey/EVKey Vietnamese input) works correctly. If launched as a child process via `Popen`, UIPI blocks IME keystrokes to the child window.

## Voice Clone Pre-flight Validation Pattern

All TTS entry points that support RVC or VoxCPM **must** validate voice clone components **before** calling `set_mode("tts_running")`. If validation fails, log the error and `return` — the UI stays in its pre-run state (no stuck "running" mode).

### RVC pre-flight — `_check_rvc_preflight()`

A shared helper (defined just before `_apply_rvc_sync`) that validates:
1. Model (.pth) field not empty
2. Model file exists on disk
3. Index file exists on disk (if the field is non-empty)
4. `rvc_helper.py` findable next to app/exe or `sys._MEIPASS`
5. `rvc_env\Scripts\python.exe` found within 3 parent directories of the exe

Returns `True` if all checks pass; logs `❌` guidance and returns `False` otherwise.

**Usage pattern** (all 4 voice-enabled TTS entry points):
```python
# Inside generate_tts() / _generate_pdf_tts() / _quick_tts_run._run()
if RVC_ENABLED and not _check_rvc_preflight():
    return  # logged already — UI unchanged, no set_mode("tts_running") called yet
app.after(0, lambda: set_mode("tts_running"))
```

### VoxCPM pre-flight — inline in each batch function

`_run_voxcpm_batch()` and `_run_voxcpm_batch_pdf()` validate inline (before `set_mode("tts_running")`):
1. `ckpt_dir` not empty
2. `ckpt_dir` is an existing directory
3. `ref_audio` file exists (if field is non-empty)
4. `voxcpm_env` python found via `_find_voxcpm_python()`
5. `voxcpm_helper.py` found in the standard search list

### No-voice detection — `_detect_novoice()` / `_rename_novoice()`

After every successful MP3 is produced (provider TTS, RVC, or VoxCPM), the file is checked for missing voice using `ffmpeg -af volumedetect`:

```python
_is_nv, _mean_db = _detect_novoice(filepath)   # or await run_in_executor(...) in async
if _is_nv:
    _rename_novoice(filepath, idx, _mean_db)
    FAIL_COUNT += 1
```

**`_detect_novoice(filepath, mean_threshold=-40.0)`** — runs ffmpeg volumedetect, parses `mean_volume`, returns `(True, mean_db)` when `mean_db < threshold`. Normal TTS speech: mean ≈ -20 to -35 dB. No-voice / noise-only: mean < -40 dB.

**`_rename_novoice(filepath, idx, mean_db, label="")`** — renames `line_0002.mp3` → `line_0002_novoice.mp3` and logs a warning. Because the original filename no longer exists, the next Resume/re-run regenerates that line automatically.

Applied to all 4 TTS flows, always on the **final** file after any post-processing (RVC or VoxCPM wav→mp3 conversion):

| Flow | Check point |
|---|---|
| `generate_tts()` — SRT + Provider ± RVC | After `save_tts` + optional RVC |
| `_generate_pdf_tts()` — PDF + Provider ± RVC | After `save_tts` + optional RVC |
| `_run_voxcpm_batch()` — SRT + VoxCPM | After ffmpeg wav→mp3 succeeds |
| `_run_voxcpm_batch_pdf()` — PDF + VoxCPM | After ffmpeg wav→mp3 succeeds |

### Error handling during generation (FAIL + continue)

When a voice clone step fails **during** a batch run (not pre-flight), the convention is to log the error and **continue** to the next line — never stop the whole process:

```python
# RVC failure mid-batch — FAIL + continue
except Exception as _rvc_err:
    log(f"❌ RVC thất bại tại dòng {current_index}: {_rvc_err}")
    log(f"FAIL {current_index}")
    FAIL_COUNT += 1
# (no return, loop continues)

# VoxCPM helper ERROR:{idx}:... signal — FAIL + continue
elif line.startswith("ERROR:"):
    _fail_idx = int(line.split(":", 2)[1])
    log(f"❌ VoxCPM {line}")
    log(f"FAIL {_fail_idx}")
    FAIL_COUNT += 1
    done_count += 1
    update_progress(done_count, len(items))
```

`voxcpm_helper.py` stdout protocol:
| Signal | Meaning |
|---|---|
| `DONE:{idx}` | Line generated — wav ready to convert to mp3 |
| `ERROR:{idx}:{reason}` | Line failed (audio silent after retries) — main app logs FAIL, continues |
| `WARN:{idx}:{reason}` | Silent attempt, retrying |
| `ALL_DONE` | Batch finished |

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
