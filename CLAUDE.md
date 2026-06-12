# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SRT TTS Studio** — Windows desktop app (CustomTkinter) that converts SRT subtitle files and PDFs to TTS audio (MP3) via Microsoft Edge TTS and Vietnamese TTS APIs (FPT.AI, Vbee, Zalo AI, EverAI, MiniMax). Also includes RVC voice cloning, VoxCPM voice cloning, VieNeu-TTS voice cloning, F5-TTS-Vietnamese voice cloning, OmniVoice Vietnamese voice cloning, Video OCR, Speech-to-Text, video compression, audio→video muxing, and video repair utilities. Distributed as `.msi` installer and standalone `.exe` files via PyInstaller + WiX Toolset.

## Build Commands

```bat
:: Full build — all 4 outputs (recommended)
build_all.bat

:: MSI-only rebuild (skips onefile exes, faster for WiX iteration)
build_msi_protected.bat

:: Dev run (no build needed)
python apppp_integrated.py

:: Pre-build sanity: catch Cython compile errors WITHOUT a full 10-min build
python -m py_compile apppp_integrated.py   :: fast, but LESS strict than Cython
python -c "from Cython.Build import cythonize; cythonize('apppp_integrated.py', compiler_directives={'language_level':'3'}, build_dir='cython_build_test', quiet=True); print('CYTHON OK')"
:: then clean: cython_build_test\ + apppp_integrated.c

:: Post-build audit (these scripts live in repo root)
python _verify_security.py   :: PYZ has only the .pyd, no .pyc; onedir .pyd present; .integrity matches exe
python _audit_deps.py        :: every external env/model/cache resolvable on THIS machine

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

**Build interpreter:** the app is built with **Python 3.14** (system `C:\Python314\python.exe`), so Cython emits `apppp_integrated.cp314-win_amd64.pyd` and PyInstaller embeds a matching 3.14 runtime. The `.pyd` ABI tag (`cp314`) must match the bundled Python — if you rebuild with a different Python, the integrity hash, the embedded interpreter, and the `.pyd` all change together. This is **independent** of the companion-script venvs, which are separate external Pythons (`rvc_env`=3.10, `voxcpm_env`=3.11, `f5tts_env`/`omnivoice_env`=3.10, etc.) invoked as subprocesses.

**Verifying the build / security after `build_all.bat`** (the standalone onefile exes are what gets distributed, so check those — not just onedir):
```python
from PyInstaller.archive.readers import CArchiveReader
for exe in ("output/Portable/SRT_TTS_Studio_Portable.exe",
            "output/Portable/SRT_TTS_Studio_Secured.exe",
            "output/Portable/SRT_TTS_Studio_Trial.exe"):
    names = list(CArchiveReader(exe).toc.keys())
    hits = [n for n in names if "apppp_integrated" in n]
    assert hits == ["apppp_integrated.cp314-win_amd64.pyd"], (exe, hits)  # ONLY the .pyd, no .pyc
```
Two repo-root helper scripts automate the post-build checks (re-run after every build): **`_verify_security.py`** verifies all 3 onefile exes (only `.pyd` in the CArchive, no `.pyc`) AND the onedir build (`.pyd` is a **loose file** in `dist\SRT_TTS_Studio\_internal\`, NOT in a CArchive — so it's checked by file presence + "no leaked `apppp_integrated*.pyc`", not via `CArchiveReader`), plus that `SRT_TTS_Studio_Secured.exe.integrity` matches the freshly-built exe's SHA-256. **`_audit_deps.py`** confirms every external dependency is resolvable *the way the app resolves it* (e.g. `voxcpm_env` is found by walking up from the VoxCPM model dir, not just beside the exe) and reports what `output\Portable\` still needs hand-copying for another machine. **`_strings_audit.py`** is a manual forensic check — it scans the built `.pyd` (`dist\SRT_TTS_Studio\_internal\apppp_integrated.cp314-win_amd64.pyd`) for leaked ASCII runs (function names, the source filename, secret-like literals) to confirm Cython left nothing recoverable; run it ad-hoc after a build when auditing protection.

**Cython is stricter than CPython — `py_compile` passing does NOT mean the build will compile.** The one that bites: a guarded reference to a never-assigned module global, e.g. `_OK if '_OK' in globals() else default`, is valid Python (the guard is runtime) but Cython rejects it at **compile time** with `undeclared name not builtin: _OK` and aborts step 5. Use `globals().get("_OK", default)` instead (never names the symbol). (`'__file__' in globals()` is fine — Cython knows `__file__`.) Always run the `cythonize(...)` one-liner above before kicking off a 10-minute `build_all.bat`.

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
| **6G** | **FAIL-CLOSED** copy of 12 companion `.py` + `hubert_base.pt` + `rmvpe.pt` + `rvc_env\` into `dist\SRT_TTS_Studio\`; verifies each file landed; aborts if anything missing. Must run before step 7 so WiX Heat picks them up. |
| 6D/E/F | 3 onefile PyInstaller builds (Portable / Secured / Trial) |
| 9 (Portable pack) | Copies onefile exes + 12 companion `.py` + `hubert_base.pt` + `rmvpe.pt` + `rvc_env\` + **`F5-TTS-Vietnamese-ViVoice\` (F5 model, ~5.4 GB, robocopy if `model_last.pt` present)** into `output\Portable\`. The F5 model is the one large model the build copies — all other big envs/models are hand-copied (see output layout below). |
| 7–8 | WiX Heat → candle → light → MSI (source: `product.wxs`) |
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
    12× companion .py             ← must sit next to exe (also embedded in exe via datas)
    hubert_base.pt, rmvpe.pt
    rvc_env\
    F5-TTS-Vietnamese-ViVoice\    ← F5-TTS model (model_last.pt + vocab.txt); copied only if present in repo root
```

**Big external deps are NOT in `output\Portable\`** — they live outside the repo and must be hand-copied per `MOVE_CHECKLIST.txt`: `voxcpm_env\` (shared by VoxCPM/STT/audio-enhance/SRT-align/video-STT/offline-translate), VoxCPM model, `vieneu_env\`, `f5tts_env\`, `omnivoice_env\`, VideOCR CLI, plus runtime HF-cache models (`MOSS-Audio-Tokenizer-Nano`, `vocos-mel-24khz`, `faster-whisper-large-v3`, `demucs htdemucs`). `_run_startup_diagnostics()` flags each missing piece in the logbox at launch.

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

## Startup, Auth & Exit/Logout flow

Module import order (all at module level, before `app.mainloop()`): `_ensure_single_instance()` (Windows named mutex `Global\SRT_TTS_Studio_SingleInstance`, stored in `builtins._srt_studio_mutex`) → security checks → app window created **hidden** → `app.after(50, show_splash_then_auth)` → splash (3 s) → `run_auth()` shows the password dialog (`show_set_password_dialog` first-run / `show_login_dialog`) → on success `app.deiconify()`. The **login screen is the auth dialog at startup**; there is no separate post-launch login window.

**Splash screen** (`show_splash_then_auth`, near the end of the file just before `app.mainloop()`): a borderless 320×320 `Toplevel` poster — `logo.png`/`logo.ico` cover-fit via PIL, bottom scrim for text legibility, rounded corners via a magenta `#FF00FF` transparentcolor key (chosen because near-black keys speckle dark pixels in the image), animated rainbow title (`_rainbow_color`), plus startup music (`start_bg_music`). After 3 s `_close_splash()` runs the internet check (`check_internet()` — **hard-exits if offline**), then schedules `_report_startup_diagnostics` (200 ms), `run_auth` (100 ms), and `_session_check_on_startup` (1500 ms). The poster build is wrapped in try/except with an emoji-text fallback, so missing PIL/`ImageTk` (imported guarded) never blocks startup. `splash_preview.png` in the repo root is just a design-preview render, not loaded by the app.

Two ways to leave the running app — both live near the bottom of the file:

| Trigger | Function | Behavior |
|---|---|---|
| Window **X** button (`WM_DELETE_WINDOW`) | `on_app_close()` @15980 | Confirm dialog → `stop_all_processes()` → goodbye sound (`naycaugioi.wav`, sync) → `os._exit(0)`. Quits for good. |
| **Logout** button (`btn_exit`, top-right `_g6`) | `on_logout()` @16005 | Same X effect (confirm + stop processes + goodbye sound), but **relaunches** instead of exiting → returns to the login screen. |

**Logout relaunch must NOT use `os.execl`.** Under PyInstaller onefile, re-exec inherits the bootloader's injected env vars (`_MEIPASS`, `_PYI_*`, `SSL_CERT_FILE`/`SSL_CERT_DIR`) pointing at the temp extraction dir that gets cleaned up on exit → `FileNotFoundError` in `ssl`/`edge_tts` at next import. Instead `on_logout()`:
1. **Releases the single-instance mutex** (`ReleaseMutex` + `CloseHandle` on `builtins._srt_studio_mutex`) — else the fresh process hits "Phần mềm đang chạy!".
2. Spawns a brand-new process via `subprocess.Popen` with a **cleaned env** (those PyInstaller vars stripped so the new bootloader sets them fresh), handling both frozen `.exe` and dev `python` invocation.
3. `os._exit(0)` the current process.

## Codebase Structure

`apppp_integrated.py` (~17,000 lines) is the **entire application** — no modules, packages, or separate files for UI vs logic. All TTS providers, UI, video tools, auth, and utilities are inline.

> **Line anchors below are approximate** — the single file grows with every feature, so `@NNNN` references drift. Treat them as hints; locate symbols by name (`grep -n "^def name" apppp_integrated.py`) rather than trusting the exact number.

`app.mainloop()` runs at **module level** (not inside `__main__`), so `import apppp_integrated` starts the full app. This is intentional for the launcher entry-point pattern.

### High-level layout inside `apppp_integrated.py`

| Lines (approx.) | Section |
|---|---|
| 1–110 | Imports, constants (`CREATE_NO_WINDOW`), `get_ffmpeg()`, `get_ffprobe()`, `_detect_gpu()` |
| ~110–1060 | Security checks (`_check_integrity` @114, DRM, trial, VM detection), global state vars (incl. translate / OCR-control / Edit-Studio globals), settings load/save (`_load_settings`/`_save_settings`), `_load_settings()` call @1062 |
| ~1060–1470 | CustomTkinter app/window creation, UI layout frames (`_left_col` @1249, `button_frame` alias @1273), global title-bar controls (`_CTRL_GROUPS` decl @1389, `g_btn_*` @1459+) |
| ~1470–3060 | Voice/provider UI + the five local-engine panels (RVC, VoxCPM, VieNeu, F5-TTS, OmniVoice) + `_apply_voice_exclusivity`, Voice Profiles + glossary (@2793–2920) |
| ~3060–4380 | Telex IME (`_telex_transform` @3057), Quick TTS (`_quick_tts_run` @3246), progress-bar canvas, scrollable `button_frame`/`ws_content` |
| ~4380–5010 | Sidebar-workspace (`# BO CUC SIDEBAR-WORKSPACE` @4378, `show_workspace` @4403, `_make_section` @4510), `show_fireworks` (@4762) |
| ~5010–5320 | `show_settings_dialog` (@5014) — scrollable settings dialog |
| ~5320–6390 | **Translation to Vietnamese** (LLM online + offline) — `_translate_active_key` (@5324), `_translate_segments` (@5569), `translate_srt` (@5868), `translate_pdf/doc`, `_write_translated_doc`, `_read_text_smart` |
| ~6390–10050 | Feature functions: `update_progress` (@6398), `_split_text_chunks` (@6524), **Video OCR** (`_run_videocr_thread` @6789 + pause/stop), STT export (`_stt_export_format` @7054), **Mux** (`load_mux_video` @7617 … `start_mux_video` @7813), TTS providers (Edge/FPT/Vbee/Zalo/EverAI/MiniMax), RVC, VoxCPM, **PDF + Word/TXT TTS** (`load_pdf` @7935, `load_doc_tts` @8007), QC dashboard, compress |
| ~10050–11700 | Local voice-clone batch backends: VieNeu (`_vieneu_preflight` @10057), **F5-TTS** (`_f5tts_preflight` @10408, `_run_f5tts_batch` @10466), OmniVoice, Queue + **Auto-dubbing wizard** (`run_autodub_chain` ~11300–11650), regenerate paths |
| ~11700–15370 | `merge_ffmpeg` (@11708), **Edit Studio** (`open_edit_studio` @12757 + sequential playlist), remaining video tools, UI widget instantiation for all button rows, `_CTRL_GROUPS` population (@15248) / `_WS_OUTPUT` (@15348) |
| ~15370–16950 | `set_mode()` (@15373) — the central UI state machine — plus late-bound widgets (`btn_reset_mode`, Logout button), the exit / Logout flow (`on_app_close` @15980, `on_logout` @16005), and `_run_startup_diagnostics` (@16605) |
| ~16950–end | Splash screen (`show_splash_then_auth` @17369), `app.withdraw()` + splash scheduling, `app.mainloop()` (@17536) at module level |

## UI Architecture Patterns (apppp_integrated.py)

### Sidebar-workspace layout (replaced the old flat `_brow*` rows)

The UI was **redesigned** into a sidebar-navigation + paged-workspace layout (~line 4378, `# BO CUC SIDEBAR-WORKSPACE`). The old flat button rows `_brow0`–`_brow8` **no longer exist** — features are now grouped into "pages" reached from a left sidebar. (`_brow*` greps now only match `_browse_*` file-picker callbacks.)

- **Two columns** (~line 1249): `_left_col` (width 232, navy sidebar) holds `ws_nav`; `_right_col` splits via grid into a console area (`_vpane`, row 0) on top and the scrollable function area `ws_content` (row 1) below. `button_frame = ws_content` is kept as a **backward-compat alias** (line 1273) so older code referencing `button_frame` still works.
- **Pages** (`ws_pages`, ~line 4397): one `CTkFrame` per key in `_WS_KEYS = ["tts","voice","textaudio","doc","extract","translate","video","editstudio","tools","system"]`. `show_workspace(key)` (~4403) `pack_forget`s all pages and packs the chosen one, and highlights the active sidebar button. Sidebar items + captions come from `_WS_NAV_ITEMS` (~4419).
- **Sections (cards)** — `_make_section(title, subtitle, accent, ws=KEY)` (~4510) creates a titled card **inside `ws_pages[ws]`** and returns its `body` frame. Helpers `_sec_row(parent)` (horizontal) / `_sec_col(parent)` (equal-width column, `expand=True`) / `_sec_sublabel(parent, text)` build the layout inside a card. Buttons still pack `side="left", expand=True, fill="x"` for equal width within a row.
- **Console toggle** — `toggle_console()` (~4464) hides/shows the `_vpane` row and reallocates grid weight to the function area.

**To add a new feature button/group:** call `_make_section(..., ws="<page>")` to get a card body (pick the page it belongs to, or add a new key to `_WS_KEYS` + an entry to `_WS_NAV_ITEMS`), then pack widgets into `_sec_row`/`_sec_col` frames within it. **Widget variable names were kept identical across the redesign** — so existing handlers and `set_mode()` did not need changes.

### Global title-bar controls (Pause/Resume/Stop/Start-Over + Output) — `_CTRL_GROUPS` / `_WS_OUTPUT`

The per-page Pause/Resume/Stop/Start-Over rows and the per-page "Chọn/Mở Output" pairs were consolidated into **global icon buttons on the title bar** (`g_btn_pause`/`g_btn_resume`/`g_btn_stop`/`g_btn_restart`, `g_btn_choose_out`/`g_btn_open_out`, defined ~line 1400–1530). The original per-page buttons **still exist** — they're just `pack_forget`-hidden (just before the `_CTRL_GROUPS` population ~15248) and kept alive so `set_mode()` and the `pause_tts`/`_videocr_pause`/etc. logic need no changes. The global buttons are thin dispatchers over them:

- **`_CTRL_GROUPS`** (populated ~line 15248, `[:]`-assigned after all `btn_` names are bound) — a list of dicts, one per running-job type (SRT TTS, Doc→Audio, Video OCR, Video STT, Video tools). Each maps `pause`/`resume`/`stop`/`restart` → the real handler fn and `pause_btn`/…/`restart_btn` → the (hidden) per-page button used to read enabled-state. `restart` is `None` for jobs with no Start-Over.
- **`_g_dispatch(action, btn_key)`** finds the **first group whose hidden button is `state=="normal"`** (i.e. the job currently running) and calls its handler. `_g_pause/_g_resume/_g_stop/_g_restart` wrap it.
- **`_sync_global_controls()`** enables each global button iff `_CURRENT_MODE` is in `_RUNNING_MODES` (`tts_running`, `videocr_running`, `video_stt_running`, `compressing`, `muxing`) AND some group's matching hidden button is enabled. `set_mode()` sets `_CURRENT_MODE` and calls it at the end; it's also called once at startup.
- **`_WS_OUTPUT`** (populated ~line 15348) maps a workspace page key → `(choose_fn, open_fn)`; `_g_choose_output`/`_g_open_output` dispatch by the **current page** (`_ws_current["key"]`), and `_sync_output_buttons()` (called from `show_workspace`) enables/disables the 2 global buttons per page. Only pages with one clear output are registered (`tts`/`doc`/`textaudio`/`translate`); Video/Extract pages keep their own per-function Output buttons.

**When adding a new long-running job:** add a dict to `_CTRL_GROUPS` mapping its pause/resume/stop/restart handlers + the (possibly hidden) per-page buttons, add its running-mode to `_RUNNING_MODES`, and (if it has a single output dir) register its page in `_WS_OUTPUT`. The translate controls (`btn_tr_*`) are deliberately **separate** — they're not in `_CTRL_GROUPS` because translate is decoupled from `set_mode`.

### set_mode() — UI state machine
`set_mode(mode)` is the single function that enables/disables all buttons and controls. It must be called from the main thread (use `app.after(0, lambda: set_mode("..."))` from worker threads). Every new feature needs:
1. Its buttons added to a `_feature_btns` list inside `set_mode`
2. New `elif mode == "feature_ready":` / `"feature_running":` / `"feature_done":` branches
3. The feature's buttons included in the disable sweep of all unrelated modes

Current modes: `srt`, `pdf`, `pdf_tts_done`, `video`, `reset`, `tts_running`, `tts_stopped`, `tts_done`, `scanning`, `scan_done`, `scan_done_clean`, `repairing`, `repair_done`, `cleaning`, `clean_done`, `videocr`, `videocr_running`, `videocr_done`, `video_stt`, `video_stt_running`, `video_stt_done`, `compress_ready`, `compressing`, `compress_done`, `mux_idle`, `mux_ready`, `muxing`, `mux_done`.

### Video OCR pause/stop/resume (process-tree control)

"Tách Sub Cứng (OCR)" runs the external **VideOCR CLI** as a subprocess (`_run_videocr_thread`), which spawns its own worker children — so pause/resume can't go through stdin. Instead, the OCR control row (`_g3_ocr_ctrl` in the "extract" page) has 3 buttons (`btn_videocr_pause`/`resume`/`stop`) that act on the **whole process tree** via `_proc_tree_action(proc, action)`: uses `psutil` (`Process.children(recursive=True)` → `suspend`/`resume`/`kill`) when available, else falls back to `ctypes` `NtSuspendProcess`/`NtResumeProcess` (main pid only) for pause/resume and `taskkill /T /F` for stop. The running proc is stored in `_VIDEOCR_PROC`; flags `VIDEOCR_PAUSED`/`VIDEOCR_STOP`. Buttons enabled only in `videocr_running`. On stop, `_run_videocr_thread` sees `VIDEOCR_STOP` and returns to `videocr` mode (no error log, no fireworks). Progress already streams to logbox + bar by parsing the CLI's `Step 1/3`…`Step 3/3` lines (mapped to 0–33/33–66/66–100%). `psutil` added to build_all.bat pip line + spec `hiddenimports`.

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

**ETA**: `update_progress` keeps a sliding window of the last 30 `(time.monotonic(), value)` samples (`_ETA_SAMPLES`, main-thread only inside `_update`) → average speed → `progress_bar.eta_text` ("còn ~5p12s"), drawn next to the `%` above the knob. Resets when value drops >0.05 (new/restarted job) or hits 1.0; shown only after ≥3 samples spanning >2s. Any flow using `update_progress` gets ETA for free.

### Logging
`log()` / `log_color()` are thread-safe (they `app.after` to the main thread). Every line is ALSO appended to `logs/session_YYYY-MM-DD.txt` next to `settings.json` via `_file_log()` (called inside `_append_log` and `log_color._do`, i.e. main thread only — no lock needed; lazy-opened handle in `_FILE_LOG`, rotates daily, writes a session header on first open, all failures swallowed). Use this file when debugging a user's "it failed yesterday" report.

### Completion effect
Call `app.after(0, show_fireworks)` when any major operation completes successfully. This is the convention used by all TTS, OCR, STT, and compress flows.

Sound files bundled in the project root are played by `show_fireworks` and error handlers:
- `chungtakhongthuocvenhau.WAV`, `toyeucaunhieulamday.WAV`, `naycaugioi.WAV` — success/fireworks sounds (randomly selected)
- `error.wav` — played on critical errors

### Button hover colors
CTkButton does not support a built-in hover-color parameter for arbitrary colors. Use Tkinter `<Enter>`/`<Leave>` bindings instead:
```python
btn.bind("<Enter>", lambda e: btn.configure(fg_color="#8B5CF6"))
btn.bind("<Leave>", lambda e: btn.configure(fg_color=["#3B8ED0", "#1F6AA5"]))
```
`["#3B8ED0", "#1F6AA5"]` is the CTkButton default (light/dark mode). Always restore via the list form so dark mode is respected.

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

All TTS entry points that support RVC, VoxCPM, VieNeu, or F5-TTS **must** validate voice clone components **before** calling `set_mode("tts_running")`. If validation fails, log the error and `return` — the UI stays in its pre-run state (no stuck "running" mode).

**Mutual exclusivity:** the six voice paths (Provider online ↔ RVC ↔ VoxCPM ↔ VieNeu ↔ F5-TTS ↔ OmniVoice) are mutually exclusive. `_apply_voice_exclusivity()` disables the other engines' checkboxes/controls whenever one is ticked. Dispatch order in `start_tts()` / the PDF entry: `if VOXCPM_ENABLED → elif VIENEU_ENABLED → elif F5TTS_ENABLED → elif OMNIVOICE_ENABLED → else provider(+optional RVC)`. All five local engines auto-pick device (no manual CPU/GPU UI): RVC resolves `rvc_device_var="auto"` → `cuda:0` if `DETECTED_GPU` else `cpu`; VoxCPM auto-detects in its helper; VieNeu, F5-TTS, and OmniVoice via `--device auto` in their helpers.

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

### VieNeu pre-flight — `_vieneu_preflight()`

Shared helper (just before `_run_vieneu_batch`) returning `(ok, model_dir, vieneu_py, helper)`. Unlike VoxCPM, the **model dir is optional** (empty = auto-download from HF). Validates: model dir empty OR an existing dir; `ref_audio` exists if non-empty; `vieneu_env` python via `_find_vieneu_python()`; `vieneu_helper.py` found. Used by `_run_vieneu_batch` / `_run_vieneu_batch_pdf` / `_vieneu_generate_one_sync` (regen) / Quick TTS. Command built by the shared `_vieneu_build_cmd()` (model-dir optional; `--reference`+`--reference-text` for cloning, else `--voice` for a preset, else default voice; `--emotion`).

**VieNeu UI panel** (in `voice_frame`, toggled by `_toggle_vieneu_panel`): Model (optional) + Audio mẫu rows; an audio-filter row (`vieneu_separate/denoise/filter_var` + "Xử lý Audio" → `_enhance_vieneu_ref_audio()`, runs `audio_enhancer.py`); a ref-text row with an **STT** button (`_vieneu_transcribe_audio()` → fills `vieneu_reftext_var`), a **preset-voice dropdown** (`_VIENEU_PRESET_VOICES`, 10 built-in voices; sentinel `(Giọng mặc định)` = no `--voice`), and an emotion menu. STT + audio-enhance reuse `whisper_stt.py` / `audio_enhancer.py` with **voxcpm_env python preferred** (whisper/demucs live there), falling back to `vieneu_env`.

### F5-TTS-Vietnamese pre-flight — `_f5tts_preflight()`

Shared helper (just before `_f5tts_find_helper`/`_run_f5tts_batch`) returning `(ok, model_dir, f5tts_py, helper)`. F5-TTS is a **pure voice-cloning** engine: unlike VieNeu, **both the model dir AND the ref audio are required** (no preset voices, no auto-download). Validates: model dir non-empty + existing dir; `ref_audio` non-empty + existing file; `f5tts_env` python via `_find_f5tts_python()`; `f5tts_helper.py` found. Used by `_run_f5tts_batch` / `_run_f5tts_batch_pdf` / `_f5tts_generate_one_sync` (regen) / Quick TTS. Command built by the shared `_f5tts_build_cmd()` (`--model-dir`, `--reference` always; `--reference-text` if non-empty — **empty = F5-TTS auto-transcribes the ref audio via its own ASR**; `--speed`; `--device auto`).

**F5-TTS UI panel** (in `voice_frame`, toggled by `_toggle_f5tts_panel`): Model (required, folder with `model_last.pt` + `vocab.txt`) + Audio mẫu rows; an audio-filter row (`f5tts_separate/denoise/filter_var` + "Xử lý Audio" → `_enhance_f5tts_ref_audio()`); a ref-text row with an **STT** button (`_f5tts_transcribe_audio()` → fills `f5tts_reftext_var`) and a **speed** entry (`f5tts_speed_var`). STT + audio-enhance reuse `whisper_stt.py` / `audio_enhancer.py` with **voxcpm_env python preferred**, falling back to `f5tts_env`. Source: [nguyenthienhy/F5-TTS-Vietnamese](https://github.com/nguyenthienhy/F5-TTS-Vietnamese), checkpoint [hynt/F5-TTS-Vietnamese-ViVoice](https://huggingface.co/hynt/F5-TTS-Vietnamese-ViVoice). The helper uses `f5_tts.api.F5TTS` (model arch `F5TTS_Base`) and applies optional `vinorm.TTSnorm` Vietnamese text normalization if installed.

### OmniVoice Vietnamese pre-flight — `_omnivoice_preflight()`

Shared helper (just before `_omnivoice_find_helper`/`_run_omnivoice_batch`) returning `(ok, model_dir, omni_py, helper)`. OmniVoice is a **voice-cloning** engine like F5-TTS, but the **model dir is OPTIONAL** (like VieNeu — empty = auto-download `splendor1811/omnivoice-vietnamese` from HF, cached); the **ref audio is required**. Validates: model dir empty OR an existing dir; `ref_audio` non-empty + existing file; `omnivoice_env` python via `_find_omnivoice_python()`; `omnivoice_helper.py` found. Used by `_run_omnivoice_batch` / `_run_omnivoice_batch_pdf` / `_omnivoice_generate_one_sync` (regen) / Quick TTS. Command built by the shared `_omnivoice_build_cmd()` (`--reference` always, `--device auto`; `--model-dir` only if non-empty; `--reference-text` if non-empty). No speed/emotion controls.

**OmniVoice UI panel** (in `voice_frame`, toggled by `_toggle_omnivoice_panel`): Model (optional, empty = auto-download) + Audio mẫu rows; an audio-filter row (`omnivoice_separate/denoise/filter_var` + "Xử lý Audio" → `_enhance_omnivoice_ref_audio()`); a ref-text row with an **STT** button (`_omnivoice_transcribe_audio()` → fills `omnivoice_reftext_var`). STT + audio-enhance reuse `whisper_stt.py` / `audio_enhancer.py` with **voxcpm_env python preferred**, falling back to `omnivoice_env`. Source/checkpoint: [splendor1811/omnivoice-vietnamese](https://huggingface.co/splendor1811/omnivoice-vietnamese). The helper uses `omnivoice.OmniVoice.from_pretrained(...).generate(text=, language="vietnamese", ref_audio=, ref_text=)` (caching a `create_voice_clone_prompt` when available), float16 on CUDA / float32 on CPU, 24 kHz output.

### Audio quality check — `_audio_quality_check()` / `_rename_bad_audio()` / `_sanitize_tts_text()`

After every successful MP3 is produced, it's QC'd with **one** `ffmpeg -af volumedetect` call that yields both `mean_volume` and `Duration`. Three failure modes are detected — silence alone is not enough, because Edge TTS hallucination produces audio that is *loud* but far too long:

**`_audio_quality_check(filepath, text="")` → `(is_bad, reason, detail)`**, `reason ∈ {"", "novoice", "toolong", "tooshort"}`:
- **novoice** — `mean_volume < -40 dB` (silent/noise). Normal speech ≈ -12 to -35 dB.
- **toolong** — `dur > 5s` AND `dur > expected*3 + 1.5s` → hallucination / repeat / runaway. (`expected = 0.3 + nchar*0.09`; VN speech ≈ 0.08 s/char measured.)
- **tooshort** — `nchar >= 12` AND `dur < expected*0.30` → truncated / missing content vs subtitle.

Triggers in source text — ellipsis `...` and dialog dashes `- ` — are the common cause of both toolong and tooshort.

**Key runtime fact: Edge TTS is non-deterministic** — the *same* text that produced 35s of garbage in one run produces correct 3.6s audio on retry. So the handling is a **QC + retry loop** (`_QC_MAX_RETRIES = 2`, i.e. 3 attempts) in the provider-TTS flows:

```python
for _qc_attempt in range(_QC_MAX_RETRIES + 1):
    # same text on early attempts (non-determinism fixes it);
    # sanitized text only on the LAST attempt as last resort
    _gen_text = _sanitize_tts_text(text) if _qc_attempt == _QC_MAX_RETRIES else text
    ok = await save_tts(_gen_text, filename)
    if not ok: break
    _bad, _reason, _detail = await run_in_executor(None, _audio_quality_check, filename, text)
    if not _bad: break
    # delete + retry
# if still bad after all attempts → _rename_bad_audio() + FAIL_COUNT += 1
```

**`_sanitize_tts_text(text)`** — used only on the final retry: collapses `...`/`…` → `, ` and strips leading dialog dashes, preserving spoken content. (Don't apply it on attempt 0 — it occasionally trips Edge TTS "No audio received", and plain retry already recovers most cases.)

**`_rename_bad_audio(filepath, idx, reason, detail, label="")`** — renames to `line_0002_novoice.mp3` / `_toolong` / `_tooshort`. Original name no longer exists → next Resume regenerates that line, and the suffix tells the user which lines to inspect.

Applied to all 4 TTS flows, QC'd on the **final** file. Provider flows get the full retry loop; VoxCPM flows get detection + rename only (the helper does its own silence-retry internally, and re-running a single line mid-batch isn't feasible — text is passed via an `idx → text` map built from `items`):

| Flow | QC point | Retry loop? |
|---|---|---|
| `generate_tts()` — SRT + Provider | After `save_tts`, before RVC | ✅ |
| `_generate_pdf_tts()` — PDF + Provider | After `save_tts`, before RVC | ✅ |
| …both, when RVC enabled | Again on RVC **output** | detection + rename only |
| `_run_voxcpm_batch()` — SRT + VoxCPM | After ffmpeg wav→mp3 | detection + rename only |
| `_run_voxcpm_batch_pdf()` — PDF + VoxCPM | After ffmpeg wav→mp3 | detection + rename only |
| `_run_vieneu_batch()` / `_run_vieneu_batch_pdf()` — VieNeu | After ffmpeg wav→mp3 | detection + rename only |
| `_run_f5tts_batch()` / `_run_f5tts_batch_pdf()` — F5-TTS | After ffmpeg wav→mp3 | detection + rename only |

**RVC output is QC'd twice over**: once on the provider-TTS audio feeding into RVC (full retry loop), then again on the RVC output (detection + rename, label `[RVC]`). RVC preserves duration so the second pass mainly catches `novoice` (RVC producing silence without raising).

### TTS text pre-processing — `_apply_glossary()` does BOTH glossary AND number reading

Despite the name, `_apply_glossary(text)` is the single TTS text pre-processing hook (called from `save_tts` + all 16 local-engine texts-json dumps): ① glossary substitution, then ② **Vietnamese number normalization** (`_vi_num_normalize`, gated by the `vi_num_var` checkbox "Đọc số tiền/ngày/giờ kiểu Việt" on `voice_row1b`, default ON). `_vi_int_words(n)` converts integers to Vietnamese words (mười lăm / hai mươi mốt / một trăm linh năm / không-trăm-linh rule for inner groups, up to nghìn tỷ). Patterns are deliberately narrow to avoid false positives: money needs a đ/đồng/vnđ/₫ suffix (with `(?!\w)` so "5điểm"/"đô" don't match), dates need full `dd/mm/yyyy` (so "3/4" fractions survive; skips the "ngày " prefix if already present), times are `NhMM`/`Nh` with range checks (24h/19h99 left untouched). Any normalization exception falls back to the original text — pre-processing must never block TTS.

### Edge TTS rate/pitch (`edge_rate_var` / `edge_pitch_var`)

`save_tts`'s Edge branch no longer hardcodes `rate="+10%"` — it reads `_edge_rate()`/`_edge_pitch()`, which sanitize the two `voice_row1b` entries ("+20%" / "-2Hz" style; auto-prepends `+`, malformed input falls back to +10% / +0Hz). Both vars are captured/applied by Voice Profiles (`edge_rate`/`edge_pitch` keys; absent in old profiles → skipped).

### Auto-retry FAIL after batch (`auto_retry_fail_var`)

Checkbox "Tự tạo lại dòng FAIL khi xong" (`voice_row1b`, default OFF). `_maybe_auto_retry_fail()` is called at the three provider-batch epilogues (parallel + sequential `generate_tts`, `_generate_pdf_tts`): if the box is ticked and `FAIL_COUNT > 0` it schedules `qc_retry_missing_lines()` (`app.after(800,...)`). It refuses while wizard/queue/casting/QC are running — those chains handle FAILs their own way. Local-engine batches are NOT hooked (their FAILs route through the helper protocol; user retries via 🧩).

### Windows toast on completion (`_notify_windows` / `_notify_if_background`)

`show_fireworks()` first calls `_notify_if_background()`: if the app is minimized (`app.state()=="iconic"`) or focus is in another app (`app.focus_displayof() is None`), it fires a Windows toast via a PowerShell WinRT one-shot (`ToastNotificationManager` — note BOTH assembly-load lines are required, `Windows.UI.Notifications` AND `Windows.Data.Xml.Dom.XmlDocument`; verified on this machine). No extra pip deps; all failures swallowed. Since every major flow already calls `show_fireworks`, every completion gets the toast for free.

### Edge TTS parallel generation (`_TTS_PARALLEL_N = 4`)

`generate_tts()` (SRT + provider) branches at the top: **Edge TTS without RVC** runs `_generate_tts_parallel()` — gathers the missing lines, then `asyncio.gather` over `_tts_par_one()` workers gated by a `Semaphore(_TTS_PARALLEL_N)`. Each worker is a faithful copy of the sequential per-line block (same QC + retry + `_sanitize_tts_text` last resort + `_rename_bad_audio` + FAIL-continue); the anti-throttle delay (`delay_min/max_var`) is kept **per slot** (each worker sleeps between its own lines). Pause = workers holding the semaphore sleep (everything drains); Stop = in-flight lines finish, queued workers early-return, then "PROCESS STOPPED". Netdown/quota set flags in the shared `state` dict → the chain aborts and `generate_tts` maps them to the same `tts_stopped` handling as the sequential path. asyncio is single-threaded so `FAIL_COUNT`/`state` need no locks. **All other providers and any RVC run keep the original sequential loop** (paid-API rate limits; RVC subprocess is heavy) — and `_generate_pdf_tts` is sequential-only for now. `current_index` is not advanced in parallel mode (completion resets it to 0; mid-run Stop + Resume relies on the skip-existing scan, which is order-independent).

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

### Single-line regenerate — `regenerate_line()` / `regenerate_pdf_line()`

Two parallel regenerate paths exist, both mirroring the **full** generation pipeline (VoxCPM / RVC / QC + retry / sanitize / rename), not just a bare `save_tts`:

| Function | Target file | Source text | UI entry |
|---|---|---|---|
| `regenerate_line(index, text)` | `line_{index:04d}.mp3` | `subtitles_cache` (SRT) | `ask_line_edit()` → "Regenerate Line" btn; also `open_editor` save |
| `regenerate_pdf_line(index, text)` | `pdf_line_{index:04d}.mp3` | `PDF_CHUNKS` | `ask_pdf_chunk_edit()` → "Regenerate đoạn PDF" btn (`btn_pdf_regen`, row 3) |

Branch logic inside both (matching the batch flows): `VOXCPM_ENABLED` → `_voxcpm_generate_one_sync(index, text, out_prefix)` + QC; `VIENEU_ENABLED` → `_vieneu_generate_one_sync(index, text, out_prefix)` + QC; `F5TTS_ENABLED` → `_f5tts_generate_one_sync(index, text, out_prefix)` + QC; `RVC_ENABLED` → provider TTS + QC-retry → RVC → QC again; else provider TTS + QC-retry.

**`_voxcpm_generate_one_sync(index, text, out_prefix="line_")`** — shared single-line VoxCPM helper. The `voxcpm_helper.py` always writes `line_{idx:04d}.wav` (filename driven by the JSON `index`); this fn converts it to `{out_prefix}{idx:04d}.mp3` (`"line_"` for SRT, `"pdf_line_"` for PDF).

**Word/TXT TTS reuses the PDF pipeline**: `load_doc_tts()` (`btn_load_doc_tts`, in the "doc" page) extracts text (`.docx` → `python-docx` paragraphs; `.txt` → `_read_text_smart`), chunks it with `_split_text_chunks()` (~250 chars at sentence boundaries — same sizing as PDF), then sets `PDF_CHUNKS` + `set_mode("pdf")`. From there the existing "Đọc PDF (TTS)" / "Merge PDF Audio" / "Regenerate đoạn PDF" buttons all work unchanged (output `pdf_line_*.mp3`). `btn_load_doc_tts` is registered in `_pdf_btns` so `set_mode` toggles it like the other PDF buttons.

When adding a new per-line/per-chunk regenerate, register its button in `_pdf_btns`/`_srt_btns` (auto-disable sweep) AND the explicit disable spots in the SRT/`tts_running` modes (those toggle PDF buttons individually, not via the list).

## Workflow features (Voice Profiles · Casting · QC Dashboard · Queue · Session · Preview)

A cluster of features added 2026-06, all built on the existing single-line/batch primitives. They follow the **translate-button pattern**: always enabled, NOT registered in any `set_mode` disable sweep, self-locked while running via a `[False]` mutable flag (`_QC_REGEN_RUNNING` / `_MULTIVOICE_RUNNING` / `_QUEUE_RUNNING`).

| Feature | Entry | Key functions | State file |
|---|---|---|---|
| **Voice Profiles** ("Hồ sơ giọng") | dropdown + 💾/🗑 row at the bottom of `voice_frame` | `_voice_profile_capture()` snapshots ALL voice vars + active engine; `_voice_profile_apply(p)` restores them and re-toggles the 5 engine panels + `_apply_voice_exclusivity()` | `voice_profiles.json` (separate file so `_save_settings()` can't wipe it) |
| **Multi-voice casting** ("🎭 Phân vai") | `btn_cast` → `open_casting_dialog()` | `CASTING_RULES` = list of `{"from","to","profile"}` (0-based, last match wins, `_casting_resolve`); `run_multivoice_batch()` groups lines by profile (minimizes engine switches), applies each profile via `_apply_profile_blocking()` (main-thread + `threading.Event`), then per line deletes the mp3 and `asyncio.run(regenerate_line(...))` | — (in-memory only) |
| **QC Dashboard** | `btn_qc_report` / `btn_qc_regen` / `btn_qc_missing` (SRT page, io column) | `_qc_scan_bad_files()` scans `OUTPUT_DIR` for `_QC_BAD_RE` (`(line_|pdf_line_)NNNN_(novoice|toolong|tooshort).mp3` — i.e. `_rename_bad_audio` output, works across app restarts); `qc_show_report()` summarizes per reason **+ missing-file FAILs**; `qc_regen_bad_lines()` deletes each bad file then re-runs `regenerate_line`/`regenerate_pdf_line` (needs the matching SRT/PDF loaded — checks and refuses otherwise) | — |
| **Retry FAIL lines** ("🧩 Tạo lại dòng thiếu") | `btn_qc_missing` (SRT page, io column) | `_scan_missing_lines()` finds lines whose text is non-empty but `line_/pdf_line_NNNN.mp3` is absent from `OUTPUT_DIR` (= batch FAIL); only scans a kind (SRT/PDF) if ≥1 file of that prefix already exists (avoids stale `PDF_CHUNKS` false-positives) and skips QC-renamed bad files (those belong to `btn_qc_regen`); `qc_retry_missing_lines()` re-runs each via `regenerate_line`/`regenerate_pdf_line`, sharing the `_QC_REGEN_RUNNING` lock. For a long stopped-midway tail, TTS/Resume is faster (batch skips existing files); this button is for scattered FAILs after a full run | — |
| **Pronunciation glossary** ("📖 Từ điển phát âm") | button on `voice_profile_row` → `open_glossary_dialog()` (one `term = reading` per line; `#` starts a comment — full-line or trailing; entries with an empty reading are skipped on save). Dialog button "🔍 Gợi ý từ" → `_glossary_suggest_terms()` scans the loaded SRT/PDF for foreign-looking tokens (Latin, no diacritics; auto-candidate if it has uppercase/digits/`+.-`, else needs freq ≥5; groups case variants; skips terms already in the glossary) and appends top-30 as `term =        # xuất hiện N lần` lines for the user to fill | `_apply_glossary(text)` — single compiled regex (`_glossary_compile()`: longest-term-first, case-insensitive, whole-word via `(?<!\w)/(?!\w)` only when term edges are alnum, so `C++` works); applied at **TTS generation only**: top of `save_tts()` (all provider flows incl. regen/quick/casting/queue) + every local-engine texts-json dump (`_glossary_items(items)` for the 8 batch dumps, inline `_apply_glossary(text)` for the 4 quick-TTS + 4 single-line dumps). NOT applied to translation, SRT files, or displayed text. QC expected-duration still uses the original text (tolerances absorb the small length delta) | `glossary.json` (separate file, same reason as `voice_profiles.json`) |
| **Queue** ("📚 Hàng đợi") | `btn_queue` → `open_queue_dialog()` | `QUEUE_FILES` list; `run_queue_batch(do_merge)` loops: per SRT sets `SRT_FILE`/`OUTPUT_DIR=<name>_tts/`, loads subs via `app.after` + Event wait, then `_dispatch_tts_blocking()` (same engine dispatch as `start_tts` but synchronous, for the queue's worker thread) and optionally `merge_ffmpeg()` | — |
| **Session resume** | `btn_restore` + startup hint | `_session_save()` called from `load_subtitles` / `choose_output_folder` / `start_tts`; `_session_check_on_startup()` (scheduled `app.after(1500,...)` next to `run_auth`) logs the previous file + done-count; `restore_session()` reloads SRT+OUTPUT_DIR with `current_index=0` (the batch loop's existing SKIP-existing-files logic does the actual resume) | `session.json` |
| **Quick TTS preview** ("🎧 Nghe thử" / "⏹ Dừng nghe") | buttons in `_qt_row2` | `_quick_tts_run(preview=True)` → writes `%TEMP%\srt_tts_preview_{seq}.mp3` (unique per press) and plays via `_play_audio_file()`; `_quick_tts_stop_preview()` stops playback + stales the in-flight run. See "Quick TTS (Text → Audio) panel" below | — |
| **Auto-dubbing wizard** ("🎬 Lồng tiếng tự động") | `btn_autodub` (SRT page, create column) + `btn_autodub_vid` (video page, mux card) → `open_autodub_dialog()` | `run_autodub_chain(video, stt_model, stt_lang, do_translate, keep_orig)` — 5 steps in one worker thread, ALL reusing existing primitives (no new pipelines): ① `_autodub_run_stt()` runs `video_stt_helper.py` synchronously, sharing `_VIDEO_STT_PROC` + `VIDEO_STT_*` flags + `video_stt_running` mode so the existing STT pause/stop buttons control it; ② `_autodub_translate()` = non-bilingual `_translate_segments` with the translate pause/stop controls enabled (skipped if checkbox off); ③ TTS via the queue pattern (`SRT_FILE`/`OUTPUT_DIR=<video>_dub/`, main-thread `load_subtitles` + `threading.Event`, `_dispatch_tts_blocking()`); ④ `merge_ffmpeg()` (respects the loudnorm checkbox); ⑤ sets `MUX_VIDEO/AUDIO/OUTPUT` globals + maps the wizard's keep-orig checkbox onto `mux_keep_orig_var` + sets `MUX_BURN_SRT` when "Gắn phụ đề cứng" is ticked (cleared in `finally`), then calls `_run_mux_thread()` synchronously (its own pause/stop/fireworks/open-folder all work); ends with a 📊 summary block built from `_LAST_MERGE_REPORT` + `FAIL_COUNT` (lines merged, stretched/centered/overflow line numbers, FAIL repair hint) after verifying `<video>_dubbed.mp4` exists. Fail-early preflights before the thread starts (ffmpeg, whisper python + helper, `_translate_active_key()` unless Offline, VieNeu/F5/Omni/RVC preflights — VoxCPM validates inside its batch); each step's stop flag aborts the chain; `FAIL_COUNT > 0` warns but continues (user can 🧩-retry then re-Merge+Mux). Re-running the wizard re-does STT/translate but TTS resumes (skip-existing). Locked via `_AUTODUB_RUNNING`; also refuses when `_CURRENT_MODE in _RUNNING_MODES` or queue/casting/QC running | — |

Notes:
- `voice_profiles.json` / `session.json` live next to `settings.json` (derived from `_SETTINGS_FILE` dirname). Do NOT fold them into `settings.json` — `_save_settings()` rewrites that file wholesale.
- Casting, QC-regen, and retry-missing spawn one helper subprocess per line for local engines (inherent to the single-line path) — slow but correct; the speed cost is expected, not a bug.
- `merge_ffmpeg` reads `merge_center_var`/`merge_format_var` (defined in the UI block ~14930) at call time — safe because merges only run post-mainloop.

### Quick TTS (Text → Audio) panel

The "textaudio" workspace page. Input is **`quick_tts_textbox`** (multi-line `CTkTextbox`, ~140px, wrap=word) — NOT an entry and NOT backed by a StringVar; read it with `quick_tts_textbox.get("1.0", "end").strip()`. Buttons: Chọn/Mở Output, 🎧 Nghe thử, ⏹ Dừng nghe, 🔊 Gen Audio. `_quick_tts_run()` mirrors the full engine dispatch (VoxCPM/VieNeu/F5/OmniVoice/provider+RVC) with inline pre-flights.

**Built-in Telex IME** (defined just after `_quick_tts_output_var`, ~line 3057): Unikey/EVKey's hook sometimes never reaches the Tk window, so raw telex (`chaof`) lands in the widget. `_telex_transform(word)` + `_attach_telex_input(ctk_widget, enabled_var)` implement Telex composition in pure Python (tones s/f/r/x/j, z-remove, aa/ee/oo, dd, w incl. `uow→ươ`, qu/gi exclusion, Unikey-style double-tap revert so `class` stays `clas`). `_attach_telex_input` auto-detects CTkEntry vs CTkTextbox (via `_entry`/`_textbox` + `mark_set`) and composes the word before the cursor on `<KeyRelease>` — reusable for any other input field. Toggled by the `quick_tts_telex_var` checkbox "Gõ Telex (VN)" (default on).

**MCI thread-affinity gotcha (preview playback)**: MCI `mpegvideo` devices belong to the thread that `open`ed them — if that thread exits (a per-run worker), `close <alias>` from any other thread **silently fails**, so old audio can't be stopped (overlapping voices) and the file stays locked (`Errno 13`). All Nghe thử MCI commands therefore go through **one persistent daemon audio thread** (`_qt_audio_send` + queue, same pattern as Edit Studio's `_audio_loop`); `_play_audio_file`/`_qt_preview_close` just enqueue. Apply this pattern to ANY new MCI playback feature. Two more guards: each press gets a **unique temp file** `srt_tts_preview_{seq}.mp3` (old in-flight gen can't collide), and the `_QT_PREVIEW_SEQ` token ensures only the **latest** press plays — a slower older run logs "Bỏ qua audio cũ" and exits.

## Timeline Dubbing — anti voice-overlap (`merge_ffmpeg`)

`merge_ffmpeg()` (~11708) is the **only** timeline-merge path: it places each `line_{i:04d}.mp3` at its subtitle start via `adelay={start_ms}` then `amix`-es all together into `final.mp3`. (PDF merge is a plain sequential `concat` — no timeline, no overlap problem.)

**Root overlap bug (fixed):** TTS audio (esp. Vietnamese / Edge TTS) is often longer than a subtitle's time slot, so `amix` overlays adjacent lines → "đè giọng / chồng giọng" (voice stacking) + timeline drift.

**Fix — time-stretch to fit the slot:** for each line, `slot = next_sub.start − this.start`; if the real duration (`_probe_duration_sec` via ffprobe) exceeds `slot − _DUB_GAP_MS`, prepend an `atempo` chain (`_atempo_chain`, capped at `_DUB_MAX_SPEED = 2.0×`) before `adelay`. Each line then ends before the next begins → no overlap, start times preserved. Lines that still overflow at max speed (or whose source subtitles already overlap) are collected and logged with their 1-based line numbers so the user can fix the SRT timing/text. `_DUB_MAX_SPEED` / `_DUB_GAP_MS` / `_DUB_CENTER_MAX_S` are module-level constants just above `merge_ffmpeg`.

**Silence-centering (optional, `merge_center_var` checkbox "Căn giữa khe lặng")**: when a line is much *shorter* than its slot (`target − actual > 0.3s`), its `adelay` start is pushed forward by `min((target−actual)/2, _DUB_CENTER_MAX_S = 0.8s)` so the voice sits centered in the silence gap instead of hugging the slot start. Off by default (exact subtitle-start sync).

**Output format (`merge_format_var` dropdown "Ra:")**: `_MERGE_FORMATS` maps `mp3/wav/m4a/opus` → (`final.<ext>`, codec args) and is substituted into the generated `run_ffmpeg.bat`. Other features that default to `final.mp3` (Mux, Edit Studio "Load Audio File") still work via their file pickers.

**Loudness normalize (`merge_loudnorm_var` checkbox, row `_merge_opt_row2`)**: appends `,loudnorm=I=-16:TP=-1.5:LRA=11` to the end of the amix chain in `filter.txt` (same chain — no extra label needed) → final hits -16 LUFS (YouTube standard). Off by default.

**`_LAST_MERGE_REPORT`** (module global next to `_MERGE_FORMATS`): every `merge_ffmpeg()` run stores `{lines, total, stretched, centered, overflow:[1-based]}` — the auto-dubbing wizard reads it for its end-of-chain summary.

## Mux Audio → Video (`_run_mux_thread`)

"Ghép Audio Final vào Video" (in the "video" page) — pick a video + a final audio track (e.g. `final.mp3` from Merge FFmpeg), adjust per-source volume, then mux into `<video>_dubbed.mp4`. Functions live just after `open_compress_folder` (`load_mux_video` @7617, `_parse_volume` @7666, `_run_mux_thread` @7680, `start_mux_video` @7813); globals `MUX_VIDEO_FILE` / `MUX_AUDIO_FILE` / `MUX_OUTPUT_DIR` next to the `COMPRESS_*` globals.

- **Volume controls** (`mux_video_vol_var` / `mux_audio_vol_var`): `_parse_volume()` accepts `1.0`, `0.5`, `150%`, `0` → ffmpeg `volume=` factor.
- **Keep-original-audio checkbox** (`mux_keep_orig_var`): when checked **and** the video has an audio track, both streams are `amix`-ed (`amix=inputs=2:duration=longest:normalize=0`); otherwise the final audio replaces the original. Falls back to replace-mode with a warning if the video has no audio.
- ffmpeg uses `-c:v copy` (no video re-encode → fast) + AAC 192k audio; progress parsed from `time=` like the compress flow.
- **Burn-in subtitles (`MUX_BURN_SRT` module global)**: when set to an existing `.srt` (only the auto-dubbing wizard sets it, via its "Gắn phụ đề cứng" checkbox; cleared in a `finally`), `_run_mux_thread` prepends `[0:v]subtitles='…'[vout]` to the **same** `filter_complex` (ffmpeg forbids mixing `-vf` with `-filter_complex`) and switches to `-c:v libx264 -crf 20 -preset veryfast` (filters force re-encode). Path escaping via `_ff_sub_filterpath()` (backslash→`/`, `:`→`\:`, `'`→`\'`, wrapped in single quotes).
- Modes: `mux_idle` (only video or only audio picked) → `mux_ready` (both picked, run enabled) → `muxing` → `mux_done`. `_mux_ready_mode()` returns `mux_ready`/`mux_idle` based on which files are loaded. Mutually exclusive with the compress flow (each disables the other's buttons while busy). Completion uses the standard `show_fireworks` + `open_mux_folder`, identical to TTS/compress.

## Edit Studio (`open_edit_studio`)

A Toplevel preview/verify window (`open_edit_studio` ~12757) that plays video frames (ffmpeg raw-frame pipe → PIL → Canvas) with MCI audio as the master clock. State lives in the `es` dict; all playback runs through the audio thread (`_audio_loop`) + `seek_to()`.

Toolbar load buttons: **Load SRT**, **Load Video**, **Load Audio Folder** (per-line `line_*.mp3`, timeline-placed), **Load Audio File**, **Load nhiều Audio** (sequential playlist).

**Load Audio File** (`_load_audio_file`) loads a single full-length track — typically `final.mp3` after Merge FFmpeg (file dialog defaults to `OUTPUT_DIR/final.mp3`). It builds a temp WAV (waveaudio = MCI master clock), sets `es['audio_wav']`/`wav_ready`, then `seek_to(0)`:
- **With video loaded** → **keeps the original video audio** and `amix`-es the loaded track on top (`[0:a][1:a]amix=inputs=2:duration=longest:normalize=0`, video + dub → one master WAV), so you hear original music/SFX *and* the dub. Falls back to dub-only if the video has no audio track.
- **No video** → audio-only mode: `_seek_audio_only()` plays the track as master; clicking a subtitle row seeks to its timecode; `_toggle_play` (Play/Pause) and the ticker's end-of-track reset both branch on `not es['video_path'] and es['audio_wav']`. Temp WAV is tracked in `es['_tmp_wav']` and removed in `_on_close`.

**Load nhiều Audio** (`_load_audio_seq`) — sequential **playlist**, NOT concatenation and NOT timeline: pick many files, they play **one after another** (each file finishes → next starts immediately). Files are natural-sorted by name (`line_0000`, `line_0001`, …). Implemented in the MCI audio thread via a dedicated alias `_ALIAS_SEQ` + handlers `_h_seq_play/pause/resume/stop` (queue ops `seq_play/seq_pause/seq_resume/seq_stop`). **Auto-advance**: the `_audio_loop` poll watches `_mci_mode(_ALIAS_SEQ)` — once it has seen `playing`, a transition to `stopped` triggers `_h_seq_play(idx+1)` (runs on the audio thread → MCI-safe). State: `seq_files`/`seq_idx`/`seq_active`/`_seq_mode`. The ticker updates the current-file status and resets Play when the list ends. `_toggle_play` has a `_seq_mode` branch (pause/resume; restart from 0 if finished). Other loaders call `_exit_seq_mode()` to leave playlist mode. No temp files (nothing is merged). **List UI**: the side Audio tab shows the playlist — `_build_audio()` branches to `_build_seq_list()` when `_seq_mode`, rendering one row per file (name + ▶) into `_aud_rows`; ▶/row-click → `_seq_play_from(idx)` (play sequentially from that file). The ticker highlights the currently-playing row via `_hl_audio(seq_idx)`.

## Companion Script System

12 scripts in the project root are invoked as **subprocesses** (not imported). Each `_find_*_helper()` function searches in this order: `sys._MEIPASS` → exe dir → script dir → PATH.

| Script | Interpreter | Purpose |
|---|---|---|
| `rvc_helper.py` | `rvc_env\Scripts\python.exe` (Python 3.10) | RVC voice conversion |
| `voxcpm_helper.py` | `voxcpm_env\Scripts\python.exe` (Python 3.11) | VoxCPM batch TTS |
| `vieneu_helper.py` | `vieneu_env\Scripts\python.exe` | VieNeu-TTS batch TTS (v3 Turbo, 48 kHz). **Auto device** (`--device auto`): CUDA available → GPU (`backend=pytorch`); else → CPU (`backend=onnx`, torch-free). **Reconfigures stdout/stderr to UTF-8** at startup (else Vietnamese error prints crash on Windows cp1252 → silent exit 1). **Patches `huggingface_hub.utils._headers.get_token_to_send`** (`_patch_hf_anon_token()`) before model load: vieneu's v3-Turbo loader calls `hf_hub_download(..., token=True)` and huggingface_hub ≥1.18 raises `LocalTokenNotFoundError` when `token=True` with no stored token — even for the **public** VieNeu repo. The patch degrades to anonymous (token=None) so the public model downloads with **no HF account/login needed**. Also **patches `torchaudio.load` → soundfile** (`_patch_torchaudio_load()`): torch 2.11's torchaudio decodes audio via **torchcodec**, whose `libtorchcodec_core*.dll` fails to load on Windows (needs FFmpeg shared libs) → voice-cloning from a ref audio raises `TorchCodec is required for load_with_torchcodec`. The soundfile patch (same trick as voxcpm_helper) reads the ref wav/flac/ogg without torchcodec. So **do not install torchcodec**. (GPU needs a CUDA build of torch **≥2.11**, e.g. `--index-url .../whl/cu128`; cu124 tops out at torch 2.6 which is too old for vieneu's triton/transformers.) Same stdout protocol as voxcpm_helper: `DONE:{idx}`/`ERROR:{idx}:..`/`WARN:{idx}:..`/`ALL_DONE`. Writes `line_{idx:04d}.wav`. Model dir **optional** (rỗng = auto-download `pnnbao-ump/VieNeu-TTS-v3-Turbo` from HF, cached). Args: `--model-dir` `--onnx-dir` `--reference` `--reference-text` `--voice` (preset name) `--emotion` `--device`. The two `_run_vieneu_batch*` loops log any unmatched stdout line (surfaces tracebacks). |
| `f5tts_helper.py` | `f5tts_env\Scripts\python.exe` (Python 3.10) | F5-TTS-Vietnamese batch voice clone. Uses `f5_tts.api.F5TTS` (arch `F5TTS_Base`) from the [nguyenthienhy/F5-TTS-Vietnamese](https://github.com/nguyenthienhy/F5-TTS-Vietnamese) fork; checkpoint [hynt/F5-TTS-Vietnamese-ViVoice](https://huggingface.co/hynt/F5-TTS-Vietnamese-ViVoice). **Auto device** (`--device auto`): CUDA → GPU, else CPU. **Reconfigures stdout/stderr to UTF-8** at startup. Model dir **required** — auto-finds `model_last.pt` (or any `.pt`/`.safetensors`) + `vocab.txt` inside (the ViVoice repo ships the vocab as `config.json` — rename it to `vocab.txt`). Ref audio **required** (pure cloning); `--reference-text` optional (empty = F5-TTS auto-ASR of the ref). Applies optional `vinorm.TTSnorm` VN text normalization if installed. **Patches `torchaudio.load`+`torchaudio.save` → soundfile** (`_patch_torchaudio()`, same trick as voxcpm/vieneu) before importing `f5_tts`: the fork pulls torchaudio ≥2.9 which routes load/save through **torchcodec** (`ModuleNotFoundError: torchcodec` / `TorchCodec is required` on Windows), and F5-TTS calls `torchaudio.load` on the ref audio — so **do not install torchcodec**, the patch handles it. **torch/GPU pinning gotcha:** the fork's `pip install -e .` pulls **torch 2.12 + transformers 5.10**, and transformers 5.10 needs `torch.float8_e8m0fnu` (**torch ≥ 2.7**), so you can't downgrade below 2.7 (torch 2.6 → `AttributeError: float8_e8m0fnu` at `from f5_tts.api import F5TTS`). torch 2.12 has no Windows CUDA wheel on the cu124 index → default install is **CPU** (~5 min/short line). For GPU, install a matched ≥2.7 CUDA pair: **`pip install torch==2.7.1 torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cu126`** (verified on an RTX 4060 → ~10 s/short line, ≈30× faster; torchaudio 2.7 still loads natively, and the helper's soundfile patch covers it regardless). Same stdout protocol: `DONE:{idx}`/`ERROR:{idx}:..`/`WARN:{idx}:..`/`ALL_DONE`. Writes `line_{idx:04d}.wav`. Args: `--model-dir` `--ckpt-file` `--vocab-file` `--model` `--reference` `--reference-text` `--speed` `--nfe-step` `--device`. The two `_run_f5tts_batch*` loops log any unmatched stdout line. |
| `omnivoice_helper.py` | `omnivoice_env\Scripts\python.exe` (Python 3.10/3.11) | OmniVoice Vietnamese batch voice clone. Uses `omnivoice.OmniVoice` (`pip install omnivoice`); checkpoint [splendor1811/omnivoice-vietnamese](https://huggingface.co/splendor1811/omnivoice-vietnamese). **Auto device** (`--device auto`): CUDA → GPU (dtype float16), else CPU (float32). **Reconfigures stdout/stderr to UTF-8** at startup. Model dir **optional** (rỗng = auto-download `splendor1811/omnivoice-vietnamese` from HF, cached); ref audio **required**, `--reference-text` recommended (matches the ref audio). Loads via `OmniVoice.from_pretrained(model_ref, device_map=, dtype=)`, then per line `model.generate(text=, language="vietnamese", ref_audio=, ref_text=)` — caches a `create_voice_clone_prompt(ref_audio, ref_text)` once when the API exposes it (then passes `voice_clone_prompt=`). **Patches `torchaudio.load`+`torchaudio.save` → soundfile** (`_patch_torchaudio()`, same trick as voxcpm/vieneu/f5tts) before importing `omnivoice` — so **do not install torchcodec**. Output 24 kHz. Same stdout protocol: `DONE:{idx}`/`ERROR:{idx}:..`/`WARN:{idx}:..`/`ALL_DONE`. Writes `line_{idx:04d}.wav`. Args: `--texts-json` `--output-dir` `--model-dir` `--reference` `--reference-text` `--language` `--device` `--selftest`. **`--selftest`** verifies the env without generating audio (prints python/numpy/soundfile/torch+CUDA, resolves the model class, and dumps the `from_pretrained`/`generate`/`create_voice_clone_prompt` signatures) — run `omnivoice_env\Scripts\python.exe omnivoice_helper.py --selftest` to confirm a machine before a real batch. The helper is **API-defensive**: it auto-discovers the `OmniVoice` class across module/name variants, tries multiple `from_pretrained` + `generate` signatures (remembering the first that works), parses `audio` / `(audio, sr)` / `dict` returns, and re-raises non-signature errors with a traceback rather than silently retrying. The two `_run_omnivoice_batch*` loops log any unmatched stdout line. |
| `whisper_stt.py` | voxcpm_env python | STT for reference audio (stderr: `PROGRESS:done_ms:total_ms`) |
| `audio_enhancer.py` | voxcpm_env python | Demucs/denoise/bandpass (stdout: `PCT:done:100`) |
| `pdf_helper.py` | any python with pypdf | PDF → JSON chunks |
| `srt_align_helper.py` | voxcpm_env python | VAD-based SRT timing alignment |
| `videocr_helper.py` | any python | Video OCR wrapper |
| `video_stt_helper.py` | voxcpm_env python | faster-whisper STT (stdout: `PROGRESS:N:M`, `DONE:path`). Helper always writes `_stt.srt` + `_stt.txt`; the app's `_stt_export_format(srt, txt, fmt, log_cb)` (@~7054) builds the user-chosen output format (`srt`/`txt`/`docx`/`pdf`) from the transcript TXT (Word via `python-docx`, PDF via `fpdf2`+`_find_unicode_font`) and returns the main file to open/preview. Video-STT also has pause/resume/stop (`_video_stt_pause`/`resume`/`stop`, wired into the global `_CTRL_GROUPS`) |
| `translate_helper.py` | voxcpm_env python (torch+transformers+sentencepiece) | Offline translation → Vietnamese (NLLB/M2M/envit5/generic seq2seq auto-detect). Input JSON file `{"segments":[...]}`, stdout `PROGRESS:N:M` + `DONE:path` (+ `STOPPED`/`LOAD_ERR`/`BATCH_ERR`), JSON out `{"translations":[...], "stopped":bool}`. Reads `PAUSE`/`RESUME`/`STOP` control lines on **stdin** |

**Onefile exes embed all 12 `.py` files** via `datas` in the specs — `sys._MEIPASS` is checked first so no loose `.py` files are needed next to the exe. Models (`hubert_base.pt`, `rmvpe.pt`) and `rvc_env\` are NOT embedded (too large) — they must be in the same directory as the exe.

### Helper progress protocol
All long-running helpers stream progress so the UI bar tracks them. Use `subprocess.Popen` + line-by-line stdout read (never `communicate()` which blocks). Parse `PROGRESS:N:M` → `update_progress(N, M)`.

## Settings System (`settings.json`)

Loaded at startup via `_load_settings()`, saved via `show_settings_dialog()`. Lives next to the exe. Two sibling state files live in the same directory but are deliberately **separate** (because `_save_settings()` rewrites `settings.json` wholesale): `voice_profiles.json` (Voice Profiles) and `session.json` (Resume session) — see the Workflow-features section.

| Key | Global | Overrides |
|---|---|---|
| `ffmpeg_dir` | `FFMPEG_DIR` | Checked first in `get_ffmpeg()` / `get_ffprobe()` |
| `videocr_cli_dir` | `VIDEOCR_CLI_DIR` | Passed as env var to `videocr_helper.py` |
| `voxcpm_ckpt_dir` | `voxcpm_ckpt_var` | VoxCPM model path; seed for `_find_voxcpm_python()` |
| `voxcpm_env_override` | `VOXCPM_ENV_OVERRIDE` | Explicit python.exe; checked **first** in all `_find_*_python()` calls |
| `vieneu_env_override` / `vieneu_model_dir` | `VIENEU_ENV_OVERRIDE` / `VIENEU_MODEL_DIR` | VieNeu `vieneu_env\Scripts\python.exe` override + optional local model dir (empty = auto-download from HF). `_find_vieneu_python()` resolves env. UI vars: `vieneu_model_var`/`vieneu_ref_var`/`vieneu_reftext_var`/`vieneu_voice_var`/`vieneu_emotion_var` |
| `f5tts_env_override` / `f5tts_model_dir` | `F5TTS_ENV_OVERRIDE` / `F5TTS_MODEL_DIR` | F5-TTS `f5tts_env\Scripts\python.exe` override + **required** local model dir (folder with `model_last.pt` + `vocab.txt`). `_find_f5tts_python()` resolves env. UI vars: `f5tts_model_var`/`f5tts_ref_var`/`f5tts_reftext_var`/`f5tts_speed_var` |
| `omnivoice_env_override` / `omnivoice_model_dir` | `OMNIVOICE_ENV_OVERRIDE` / `OMNIVOICE_MODEL_DIR` | OmniVoice `omnivoice_env\Scripts\python.exe` override + **optional** local model dir (empty = auto-download from HF). `_find_omnivoice_python()` resolves env. UI vars: `omnivoice_model_var`/`omnivoice_ref_var`/`omnivoice_reftext_var` |
| `translate_env_override` | `TRANSLATE_ENV_OVERRIDE` | Dedicated python.exe for offline translation; checked **before** `voxcpm_env` in `_translate_segments_local()`. Needed for envit5 (see tokenizer gotcha below) |
| `local_translate_model_dir` / `local_translate_src_lang` | `LOCAL_TRANSLATE_MODEL_DIR` / `LOCAL_TRANSLATE_SRC_LANG` | Offline model dir (or HF id) + NLLB source-lang code |
| `subtitle_edit_path` | `SUBTITLE_EDIT_PATH` | Prepended to Subtitle Edit search list |
| `anthropic_api_key` / `gemini_api_key` / `openai_api_key` | `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` / `OPENAI_API_KEY` | LLM keys for SRT/PDF translation (masked `show="*"` in dialog) |
| `translate_provider` | `TRANSLATE_PROVIDER` | `Claude` \| `Gemini` \| `OpenAI`; set by the row-8 dropdown (`set_translate_provider`) |
| `translate_model` | `TRANSLATE_MODEL` | Optional model override; empty → `_TRANSLATE_DEFAULT_MODEL[provider]`. Settings dialog shows a **dropdown** of `Provider — model-id` labels (not a path — these are cloud APIs, no local files); `_resolve_model()` strips the label back to the bare id before saving |

**Note:** `_save_settings()` now takes the translate params as keyword args defaulting to `None` = "keep current". `set_translate_provider()` persists only the provider (passes other paths through unchanged), so it must read `voxcpm_ckpt_var`/`FFMPEG_DIR`/etc. to avoid wiping them.

## SRT / PDF Translation to Vietnamese (LLM)

The "translate" page — translate SRT / PDF / **Word `.docx` / `.txt`** to natural Vietnamese via Claude / Gemini / OpenAI / Offline. Three buttons (`btn_translate_srt` / `btn_translate_pdf` / `btn_translate_doc`), toggled together by `_set_translate_buttons()`. **Decoupled from `set_mode()`**: always enabled (no entry in any disable sweep) and self-lock only during their own run (re-enabled in `finally`). They operate on a freshly file-dialog-picked file, NOT `subtitles_cache`/`PDF_CHUNKS`, so they never conflict with a running TTS job.

| Piece | Detail |
|---|---|
| `_translate_active_key()` | Resolves `(provider, key, model)`; raises if the selected provider's key is blank |
| `_llm_call_claude/gemini/openai()` | Plain `urllib` POST (no SDK dep). Claude `/v1/messages` + `anthropic-version: 2023-06-01`; Gemini `:generateContent?key=`; OpenAI `/v1/chat/completions` |
| `_translate_segments(segments, context, …)` | Batches `_TRANSLATE_BATCH` (40) lines/call using `[[n]] text` markers; parses back with `_parse_marked`; **any missing/empty line → per-line fallback retry**, then keeps source text if still failing (never drops content) |
| `translate_srt()` | Parses `.srt`, translates `clean_text(content)`, writes `<name>_vi.srt` preserving timestamps |
| `translate_pdf()` | Extracts chunks via `pdf_helper.py` (same as `load_pdf`), writes `<name>_vi.{txt\|pdf\|docx}` via `_write_translated_doc()` (Row-8 `translate_pdf_format_var` dropdown, label "Ra (PDF/Word/TXT)" — shared by PDF + Word/TXT). PDF output = reflowed text only (no original layout) using `fpdf2` + a Windows Unicode TTF (`_find_unicode_font`, Arial/Segoe/Times); DOCX uses `python-docx`. Missing lib → auto-fallback to `.txt`. `fpdf2`+`python-docx` added to build_all.bat pip line + spec `hiddenimports` (`fpdf`, `docx`) |
| `translate_doc()` | Translates **Word `.docx` / `.txt`** input. `.docx` → paragraphs via `python-docx`; `.txt` → non-empty lines via `_read_text_smart` (handles UTF-16/BOM). Same translate + `_write_translated_doc` output pipeline, format dropdown, pause/stop, and `_reveal_output` as `translate_pdf`. Button `btn_translate_doc` in the "translate" page |

**Bilingual mode** (`translate_bilingual_var` checkbox): SRT line becomes `original\ntranslated`; PDF writes both. **Context field** (`translate_context_var`) feeds the system prompt for consistent pronouns/xưng hô — the single biggest quality lever for VN subtitles (online providers only).

**Translate→TTS chaining** (`translate_then_tts_var` checkbox "Dịch xong đọc luôn (SRT)"): on successful (non-stopped) `translate_srt()`, `_chain_translate_to_tts(out_path)` runs on the main thread — sets `SRT_FILE` to the `_vi.srt`, resets `current_index`, `load_subtitles(force_select=False)`, `set_mode("srt")`, then `start_tts()`. Warns (but proceeds) if bilingual is on, since TTS would read both languages.

### Pause / Resume / Stop (translate controls)

Three controls (`btn_tr_pause`/`btn_tr_resume`/`btn_tr_stop`) drive module flags `TRANSLATE_PAUSED` / `TRANSLATE_STOP` (enabled only while a translate job runs, toggled via `_translate_set_controls`). **Online**: `_translate_segments` checks the flags between each 40-line batch (waits while paused, breaks on stop). **Offline**: the flags can't reach the running subprocess, so the controls also send `PAUSE`/`RESUME`/`STOP` lines to `translate_helper.py` via its **stdin** (`_translate_send_proc`, using the stored `_TRANSLATE_PROC`); the helper runs a daemon stdin-reader thread (`_CTRL`) and checks it between batches. On stop, **partial output is still saved** — untranslated tail keeps the source text (both the helper and the online path back-fill `None`/missing with the original), so the file stays valid. Stop → no fireworks but still reveals the file; normal finish → fireworks + reveal. Progress shows in both the bar and the logbox (`_make_translate_progress_cb`, throttled to 10% steps); on finish the output folder opens via `_reveal_output` (`explorer /select,`).

### Offline (local) translation — provider `"Offline"`

The Row-8 dropdown has a 4th option **`Offline`** that translates fully on-device via `translate_helper.py` (no API/network). `_translate_segments()` dispatches: `TRANSLATE_PROVIDER == "Offline"` → `_translate_segments_local()`, else the LLM path. Local mode ignores the context field (NLLB/envit5 take no instructions).

- **Model**: any HuggingFace seq2seq dir (or HF id) set in ⚙ Cài đặt → `local_translate_model_dir`. Helper auto-detects: `nllb`/`m2m` → `forced_bos_token_id` for `--tgt-lang vie_Latn`; `envit5` → `en: ` prefix, EN→VI only; else generic `generate()`. Recommended: `facebook/nllb-200-distilled-600M` (multilingual) or `VietAI/envit5-translation` (EN→VI, best VN style).
- **Source language** (`local_translate_src_lang`, NLLB only) is a friendly dropdown in settings mapping to codes (`eng_Latn`, `zho_Hans`, `jpn_Jpan`, …); envit5 ignores it.
- **Env**: `_translate_segments_local()` picks the interpreter in this order: `TRANSLATE_ENV_OVERRIDE` (settings `translate_env_override`, an explicit `python.exe`) → `_find_voxcpm_python()`. Needs `torch`+`transformers`+`sentencepiece`. `translate_helper.py` is one of the **12 companion scripts** (added to all 3 onefile spec `datas`, build_all.bat step-0 validation + both copy loops, step-6G fail-closed copy).
- **Tokenizer-version gotcha**: `voxcpm_env` ships `transformers 5.x`/`tokenizers 0.22.x`, which **loads NLLB/Marian fine but FAILS on envit5** (T5/unigram SentencePiece) with `argument 'vocab': 'dict' object cannot be converted to 'Sequence'`. To use envit5, point `translate_env_override` at a **separate venv** with older pins (`transformers==4.41.2` + matching `tokenizers` + `sentencepiece` + CPU `torch`). The helper catches model-load failures → prints `LOAD_ERR:` (exit 3) so the app shows a clear message instead of "mã 1".

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
| `vieneu_env\` | ~2–6 GB | VieNeu-TTS. **`pip install vieneu`** (Python 3.10/3.11). Runs on **CPU (ONNX, torch-free)** out of the box; add a **CUDA build of torch** (`pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu124`) to auto-use GPU. **Do NOT use the `[gpu]` extra** — it pulls `lmdeploy` (a different backend) which has no Windows/py3.14 wheel. Place beside the exe; `_find_vieneu_python()` auto-detects |
| `f5tts_env\` | ~6–8 GB | F5-TTS-Vietnamese. Python 3.10. Install: `git clone https://github.com/nguyenthienhy/F5-TTS-Vietnamese && cd F5-TTS-Vietnamese && pip install -e .` (provides the `f5_tts` package). For **GPU**, then run `pip install torch==2.7.1 torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cu126` (the base install is CPU-only torch 2.12; see the torch-pinning gotcha in the companion-script section). Optionally `pip install vinorm` for VN text normalization. Place `f5tts_env\` beside the exe; `_find_f5tts_python()` auto-detects (in the **built exe**, set the path in ⚙ Cài đặt → `f5tts_env python.exe` if it's not within 3 parent dirs) |
| `omnivoice_env\` | ~6–8 GB | OmniVoice Vietnamese. Python 3.10/3.11. Install: `pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128` then `pip install omnivoice`. Model **auto-downloads** from HF (`splendor1811/omnivoice-vietnamese`) on first run + cached. Place `omnivoice_env\` beside the exe; `_find_omnivoice_python()` auto-detects (in the **built exe**, set the path in ⚙ Cài đặt → `omnivoice_env python.exe` if it's not within 3 parent dirs) |
| OmniVoice model | auto-download | OmniVoice Vietnamese — pulled from HF (`splendor1811/omnivoice-vietnamese`) on first run + cached; only needs a manual local dir for fully-offline machines |
| F5-TTS model | ~1.3 GB | F5-TTS-Vietnamese. Download `model_last.pt` + `vocab.txt` from `hynt/F5-TTS-Vietnamese-ViVoice` into a folder; set it in ⚙ Cài đặt → F5-TTS model folder (or the F5-TTS panel Model field). **Required** — no auto-download |
| VieNeu model | auto-download | VieNeu-TTS — pulled from HF (`pnnbao-ump/VieNeu-TTS-v3-Turbo`) on first run + cached; only needs a manual local dir for fully-offline machines |
| VideOCR CLI | small | Video OCR |
| Offline translate model (NLLB-600M / envit5) | ~1.5–2.5 GB | Offline SRT/PDF translation (only if using provider `Offline`; reuses `voxcpm_env` + needs `transformers`/`sentencepiece`) |

**Runtime auto-download models (NOT bundled, NOT in any copied folder)** — these land in `%USERPROFILE%\.cache\huggingface\hub` / `%USERPROFILE%\.cache\torch\hub`, so a target machine needs internet on first use **or** a hand-copied cache. The most-forgotten ones (a fresh machine silently fails without them):
- `OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano` — **required** for VoxCPM
- `charactr/vocos-mel-24khz` — **required** for F5-TTS (vocoder)
- `pnnbao-ump/VieNeu-TTS-v3-Turbo`, `splendor1811/omnivoice-vietnamese` — VieNeu / OmniVoice models (when no local model dir set)
- `Systran/faster-whisper-large-v3` (+ medium/small) — STT (`whisper_stt.py`) and Video-STT (`video_stt_helper.py`), pulled into `voxcpm_env`'s cache
- `demucs htdemucs` (torch hub `checkpoints/955717e8-*.th`) — audio-enhance "Tách nhạc" (`audio_enhancer.py`)

`_run_startup_diagnostics()` surfaces **all** of these in the logbox:
- The four strict HF models above via `_hf_checks` + `_hf_cache_has()` (#12).
- **faster-whisper** (#12b) via `_hf_cache_has_prefix("Systran/faster-whisper")` — passes if **any** size (small/medium/large-v3) is cached.
- **Demucs htdemucs** (#12c) via `_torch_hub_has("955717e8")` — this model lives in the **torch hub** cache (`~/.cache/torch/hub/checkpoints/955717e8-*.th`), **not** HF cache, so `_hf_cache_has` can't see it; `_torch_hub_dirs()` checks `TORCH_HOME`/`XDG_CACHE_HOME`/`~/.cache/torch/...`.
- **Model dịch Offline** (#12d) — only checked when `TRANSLATE_PROVIDER == "Offline"` or `LOCAL_TRANSLATE_MODEL_DIR` is set (a local dir → `isdir`, or an HF id → `_hf_cache_has`).
- **PaddleOCR PP-OCRv5** (#9, nested under the VideOCR check) — `PaddleOCR.PP-OCRv5.support.files` searched in the VideOCR CLI dir / `VIDEOCR_INSTALL_DIR` / `C:\Program Files\VideOCR`.

(Silero VAD for SRT-align needs no separate check — `srt_align_helper.py` uses `faster_whisper.vad`, which ships inside the faster-whisper package, so #12b covers it.) When adding a new engine with a runtime HF download, add its repo id to `_hf_checks` (or a dedicated check if it caches outside HF) so the startup logbox flags it.

### Relative auto-detect (added) — copy beside the exe, no Settings needed

Resolution order for the 3 big external folders is now: **settings.json → relative auto-detect beside the exe → hardcoded `E:\`/`C:\Users\os\` default**. Two module-level helpers drive this (defined just above the `VIDEOCR_CLI_DIR` global):

- `_install_dirs()` — returns the exe dir (frozen) / script dir plus up to 3 parent levels, as the search roots.
- `_auto_find_dir(*subpaths)` — returns the first existing subdir under any install root (`""` if none).

Wired in at three points so dropping the folders next to the `.exe` "just works":
| Dep | Auto-detected subpaths (beside exe / parents) | Fallback |
|---|---|---|
| `VIDEOCR_CLI_DIR` | `VideOCR\CLI`, `VideOCR-CLI`, `VideOCR-1.5.1\VideOCR-1.5.1\CLI` | hardcoded `C:\Users\os\...` |
| VoxCPM model (`voxcpm_ckpt_var` default) | `VoxCPM\pretrained\VoxCPM-1.5-VN`, `VoxCPM-1.5-VN`, `VoxCPM-model` | hardcoded `E:\VoxCPM-1.5-VN\...` |
| `voxcpm_env` python (`_find_voxcpm_python`) | walks up from ckpt **then** `voxcpm_env\Scripts\python.exe` under each `_install_dirs()` root | `None` |

`_run_startup_diagnostics()` calls `_find_voxcpm_python(ckpt)` unconditionally now (even with no model dir) so a beside-exe `voxcpm_env` shows ✅.

Default paths hardcoded in source (final fallback; override via ⚙ Cài đặt):
- `VIDEOCR_CLI_DIR`: `C:\Users\os\Downloads\Compressed\VideOCR-1.5.1\...\CLI`
- VoxCPM ckpt seed: `E:\VoxCPM-1.5-VN\VoxCPM\pretrained\VoxCPM-1.5-VN`

See `MOVE_CHECKLIST.txt` for the step-by-step checklist when moving to a new machine.
