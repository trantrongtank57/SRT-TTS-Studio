# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SRT TTS Studio** — Windows desktop app (CustomTkinter) that converts SRT subtitle files and PDFs to TTS audio (MP3) via Microsoft Edge TTS and Vietnamese TTS APIs (FPT.AI, Vbee, Zalo AI, EverAI, MiniMax). Also includes RVC voice cloning, VoxCPM voice cloning, Video OCR, Speech-to-Text, video compression, audio→video muxing, and video repair utilities. Distributed as `.msi` installer and standalone `.exe` files via PyInstaller + WiX Toolset.

## Build Commands

```bat
:: Full build — all 4 outputs (recommended)
build_all.bat

:: MSI-only rebuild (skips onefile exes, faster for WiX iteration)
build_msi_protected.bat

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
| **6G** | **FAIL-CLOSED** copy of 9 companion `.py` + `hubert_base.pt` + `rmvpe.pt` + `rvc_env\` into `dist\SRT_TTS_Studio\`; verifies each file landed; aborts if anything missing. Must run before step 7 so WiX Heat picks them up. |
| 6D/E/F | 3 onefile PyInstaller builds (Portable / Secured / Trial) |
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
    9× companion .py              ← must sit next to exe (also embedded in exe via datas)
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

`apppp_integrated.py` (~11550 lines) is the **entire application** — no modules, packages, or separate files for UI vs logic. All TTS providers, UI, video tools, auth, and utilities are inline.

`app.mainloop()` runs at **module level** (not inside `__main__`), so `import apppp_integrated` starts the full app. This is intentional for the launcher entry-point pattern.

### High-level layout inside `apppp_integrated.py`

| Lines (approx.) | Section |
|---|---|
| 1–110 | Imports, constants (`CREATE_NO_WINDOW`), `get_ffmpeg()`, `get_ffprobe()`, `_detect_gpu()` |
| 110–890 | Security checks (`_check_integrity` @114, DRM, trial, VM detection), global state vars (incl. translate / OCR-control / Edit-Studio globals) |
| 890–1160 | Settings load/save (`_load_settings` @894, `_save_settings` @933), CustomTkinter app/window creation, UI layout frames |
| 1160–2760 | Voice/provider UI, progress bar canvas, scrollable `button_frame` (@2703) + button-row (`_brow0`–`_brow8b`) definitions |
| 2760–3240 | Fireworks animation + sound (`show_fireworks` @2762), `show_settings_dialog` (@3014), `log()`, helper utilities |
| 3240–3960 | **Translation to Vietnamese** (LLM online + offline) — `_translate_active_key` (@3246), `_llm_call_*` (@3262), `_translate_segments`, `translate_srt/pdf/doc` (@3759), `_write_translated_doc`, `_read_text_smart` |
| 3960–7100 | Feature functions: `update_progress` (@4172), TTS (Edge, FPT, Vbee, Zalo, EverAI, MiniMax), RVC, VoxCPM, `_split_text_chunks` (@4297), **Video OCR** (`_run_videocr_thread` @4562 + pause/stop), **PDF + Word/TXT TTS** (`load_pdf` @5528, `load_doc_tts`), STT, compress, mux |
| 7100–10150 | `merge_ffmpeg` (@7114), **Edit Studio** (`open_edit_studio` @7727 + sequential playlist), remaining video tools, UI widget instantiation for all button rows (`_brow0` widgets @9857) |
| 10150–11530 | `set_mode()` (@10158) — the central UI state machine — plus late-bound widgets (`btn_reset_mode`, quick-TTS dimming) |
| 11531–end | `app.mainloop()` at module level |

## UI Architecture Patterns (apppp_integrated.py)

### Button rows
The button panel uses fixed rows (`_brow0`, `_brow0b`, `_brow1`–`_brow8`, `_brow8b`, plus `_brow4b`) created once at startup (~line 2700) and populated later in the widget-instantiation block (~line 9857). When adding a new feature, add a new `_browN` at the row-definition block **and** populate it there. (`_brow8` = SRT/PDF/Word-TXT translation row; `_brow8b` = translate pause/resume/stop; `_brow4b` = OCR pause/resume/stop.)

`button_frame` is a **`CTkScrollableFrame`** (fixed `height=340`, ~line 2703), not a plain frame — extra rows scroll instead of being clipped off the bottom of the window. Each `_browN` is a transparent `ctk.CTkFrame` packed `fill="x"`.

**Uniform-width rule:** every button packs `side="left", expand=True, fill="x"` (no fixed `width`), so within a row all buttons share the width equally. Buttons are *not* assigned a fixed pixel width — a previous attempt at uniform fixed-width caused overflow (10-button rows ran off-screen) and large gaps on 3-button rows. To keep button sizes even *across* rows, keep button counts per row similar (this is why the original 10-button SRT/TTS row was split into `_brow0` + `_brow0b`, 5 buttons each). Mixed rows (`_brow5`/`_brow6`/`_brow7`) interleave `CTkOptionMenu`/`CTkLabel`/`CTkEntry`/`CTkCheckBox` (fixed `width`, packed without `expand`) between the expanding buttons.

### set_mode() — UI state machine
`set_mode(mode)` is the single function that enables/disables all buttons and controls. It must be called from the main thread (use `app.after(0, lambda: set_mode("..."))` from worker threads). Every new feature needs:
1. Its buttons added to a `_feature_btns` list inside `set_mode`
2. New `elif mode == "feature_ready":` / `"feature_running":` / `"feature_done":` branches
3. The feature's buttons included in the disable sweep of all unrelated modes

Current modes: `srt`, `pdf`, `pdf_tts_done`, `video`, `reset`, `tts_running`, `tts_stopped`, `tts_done`, `scanning`, `scan_done`, `scan_done_clean`, `repairing`, `repair_done`, `cleaning`, `clean_done`, `videocr`, `videocr_running`, `videocr_done`, `video_stt`, `video_stt_running`, `video_stt_done`, `compress_ready`, `compressing`, `compress_done`, `mux_idle`, `mux_ready`, `muxing`, `mux_done`.

### Video OCR pause/stop/resume (process-tree control)

"Tách Sub Cứng (OCR)" runs the external **VideOCR CLI** as a subprocess (`_run_videocr_thread`), which spawns its own worker children — so pause/resume can't go through stdin. Instead, row `_brow4b` has 3 buttons (`btn_videocr_pause`/`resume`/`stop`) that act on the **whole process tree** via `_proc_tree_action(proc, action)`: uses `psutil` (`Process.children(recursive=True)` → `suspend`/`resume`/`kill`) when available, else falls back to `ctypes` `NtSuspendProcess`/`NtResumeProcess` (main pid only) for pause/resume and `taskkill /T /F` for stop. The running proc is stored in `_VIDEOCR_PROC`; flags `VIDEOCR_PAUSED`/`VIDEOCR_STOP`. Buttons enabled only in `videocr_running`. On stop, `_run_videocr_thread` sees `VIDEOCR_STOP` and returns to `videocr` mode (no error log, no fireworks). Progress already streams to logbox + bar by parsing the CLI's `Step 1/3`…`Step 3/3` lines (mapped to 0–33/33–66/66–100%). `psutil` added to build_all.bat pip line + spec `hiddenimports`.

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

**RVC output is QC'd twice over**: once on the provider-TTS audio feeding into RVC (full retry loop), then again on the RVC output (detection + rename, label `[RVC]`). RVC preserves duration so the second pass mainly catches `novoice` (RVC producing silence without raising).

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

Branch logic inside both (matching the batch flows): `VOXCPM_ENABLED` → single-line via `_voxcpm_generate_one_sync(index, text, out_prefix)` + QC; `RVC_ENABLED` → provider TTS + QC-retry → RVC → QC again; else provider TTS + QC-retry.

**`_voxcpm_generate_one_sync(index, text, out_prefix="line_")`** — shared single-line VoxCPM helper. The `voxcpm_helper.py` always writes `line_{idx:04d}.wav` (filename driven by the JSON `index`); this fn converts it to `{out_prefix}{idx:04d}.mp3` (`"line_"` for SRT, `"pdf_line_"` for PDF).

**Word/TXT TTS reuses the PDF pipeline**: `load_doc_tts()` (`btn_load_doc_tts`, row 3) extracts text (`.docx` → `python-docx` paragraphs; `.txt` → `_read_text_smart`), chunks it with `_split_text_chunks()` (~250 chars at sentence boundaries — same sizing as PDF), then sets `PDF_CHUNKS` + `set_mode("pdf")`. From there the existing "Đọc PDF (TTS)" / "Merge PDF Audio" / "Regenerate đoạn PDF" buttons all work unchanged (output `pdf_line_*.mp3`). `btn_load_doc_tts` is registered in `_pdf_btns` so `set_mode` toggles it like the other PDF buttons.

When adding a new per-line/per-chunk regenerate, register its button in `_pdf_btns`/`_srt_btns` (auto-disable sweep) AND the explicit disable spots in the SRT/`tts_running` modes (those toggle PDF buttons individually, not via the list).

## Timeline Dubbing — anti voice-overlap (`merge_ffmpeg`)

`merge_ffmpeg()` (line ~7114) is the **only** timeline-merge path: it places each `line_{i:04d}.mp3` at its subtitle start via `adelay={start_ms}` then `amix`-es all together into `final.mp3`. (PDF merge is a plain sequential `concat` — no timeline, no overlap problem.)

**Root overlap bug (fixed):** TTS audio (esp. Vietnamese / Edge TTS) is often longer than a subtitle's time slot, so `amix` overlays adjacent lines → "đè giọng / chồng giọng" (voice stacking) + timeline drift.

**Fix — time-stretch to fit the slot:** for each line, `slot = next_sub.start − this.start`; if the real duration (`_probe_duration_sec` via ffprobe) exceeds `slot − _DUB_GAP_MS`, prepend an `atempo` chain (`_atempo_chain`, capped at `_DUB_MAX_SPEED = 2.0×`) before `adelay`. Each line then ends before the next begins → no overlap, start times preserved. Lines that still overflow at max speed (or whose source subtitles already overlap) are collected and logged with their 1-based line numbers so the user can fix the SRT timing/text. `_DUB_MAX_SPEED` / `_DUB_GAP_MS` are module-level constants just above `merge_ffmpeg`.

## Mux Audio → Video (`_run_mux_thread`)

Row `_brow7` — "Ghép Audio Final vào Video": pick a video + a final audio track (e.g. `final.mp3` from Merge FFmpeg), adjust per-source volume, then mux into `<video>_dubbed.mp4`. Functions live just after `open_compress_folder` (`load_mux_video` @5226, `_parse_volume` @5275, `_run_mux_thread` @5289, `start_mux_video` @5406); globals `MUX_VIDEO_FILE` / `MUX_AUDIO_FILE` / `MUX_OUTPUT_DIR` next to the `COMPRESS_*` globals.

- **Volume controls** (`mux_video_vol_var` / `mux_audio_vol_var`): `_parse_volume()` accepts `1.0`, `0.5`, `150%`, `0` → ffmpeg `volume=` factor.
- **Keep-original-audio checkbox** (`mux_keep_orig_var`): when checked **and** the video has an audio track, both streams are `amix`-ed (`amix=inputs=2:duration=longest:normalize=0`); otherwise the final audio replaces the original. Falls back to replace-mode with a warning if the video has no audio.
- ffmpeg uses `-c:v copy` (no video re-encode → fast) + AAC 192k audio; progress parsed from `time=` like the compress flow.
- Modes: `mux_idle` (only video or only audio picked) → `mux_ready` (both picked, run enabled) → `muxing` → `mux_done`. `_mux_ready_mode()` returns `mux_ready`/`mux_idle` based on which files are loaded. Mutually exclusive with the compress flow (each disables the other's buttons while busy). Completion uses the standard `show_fireworks` + `open_mux_folder`, identical to TTS/compress.

## Edit Studio (`open_edit_studio`)

A Toplevel preview/verify window (line ~7727) that plays video frames (ffmpeg raw-frame pipe → PIL → Canvas) with MCI audio as the master clock. State lives in the `es` dict; all playback runs through the audio thread (`_audio_loop`) + `seek_to()`.

Toolbar load buttons: **Load SRT**, **Load Video**, **Load Audio Folder** (per-line `line_*.mp3`, timeline-placed), **Load Audio File**, **Load nhiều Audio** (sequential playlist).

**Load Audio File** (`_load_audio_file`) loads a single full-length track — typically `final.mp3` after Merge FFmpeg (file dialog defaults to `OUTPUT_DIR/final.mp3`). It builds a temp WAV (waveaudio = MCI master clock), sets `es['audio_wav']`/`wav_ready`, then `seek_to(0)`:
- **With video loaded** → **keeps the original video audio** and `amix`-es the loaded track on top (`[0:a][1:a]amix=inputs=2:duration=longest:normalize=0`, video + dub → one master WAV), so you hear original music/SFX *and* the dub. Falls back to dub-only if the video has no audio track.
- **No video** → audio-only mode: `_seek_audio_only()` plays the track as master; clicking a subtitle row seeks to its timecode; `_toggle_play` (Play/Pause) and the ticker's end-of-track reset both branch on `not es['video_path'] and es['audio_wav']`. Temp WAV is tracked in `es['_tmp_wav']` and removed in `_on_close`.

**Load nhiều Audio** (`_load_audio_seq`) — sequential **playlist**, NOT concatenation and NOT timeline: pick many files, they play **one after another** (each file finishes → next starts immediately). Files are natural-sorted by name (`line_0000`, `line_0001`, …). Implemented in the MCI audio thread via a dedicated alias `_ALIAS_SEQ` + handlers `_h_seq_play/pause/resume/stop` (queue ops `seq_play/seq_pause/seq_resume/seq_stop`). **Auto-advance**: the `_audio_loop` poll watches `_mci_mode(_ALIAS_SEQ)` — once it has seen `playing`, a transition to `stopped` triggers `_h_seq_play(idx+1)` (runs on the audio thread → MCI-safe). State: `seq_files`/`seq_idx`/`seq_active`/`_seq_mode`. The ticker updates the current-file status and resets Play when the list ends. `_toggle_play` has a `_seq_mode` branch (pause/resume; restart from 0 if finished). Other loaders call `_exit_seq_mode()` to leave playlist mode. No temp files (nothing is merged). **List UI**: the side Audio tab shows the playlist — `_build_audio()` branches to `_build_seq_list()` when `_seq_mode`, rendering one row per file (name + ▶) into `_aud_rows`; ▶/row-click → `_seq_play_from(idx)` (play sequentially from that file). The ticker highlights the currently-playing row via `_hl_audio(seq_idx)`.

## Companion Script System

9 scripts in the project root are invoked as **subprocesses** (not imported). Each `_find_*_helper()` function searches in this order: `sys._MEIPASS` → exe dir → script dir → PATH.

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
| `translate_helper.py` | voxcpm_env python (torch+transformers+sentencepiece) | Offline translation → Vietnamese (NLLB/M2M/envit5/generic seq2seq auto-detect). Input JSON file `{"segments":[...]}`, stdout `PROGRESS:N:M` + `DONE:path` (+ `STOPPED`/`LOAD_ERR`/`BATCH_ERR`), JSON out `{"translations":[...], "stopped":bool}`. Reads `PAUSE`/`RESUME`/`STOP` control lines on **stdin** |

**Onefile exes embed all 9 `.py` files** via `datas` in the specs — `sys._MEIPASS` is checked first so no loose `.py` files are needed next to the exe. Models (`hubert_base.pt`, `rmvpe.pt`) and `rvc_env\` are NOT embedded (too large) — they must be in the same directory as the exe.

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
| `translate_env_override` | `TRANSLATE_ENV_OVERRIDE` | Dedicated python.exe for offline translation; checked **before** `voxcpm_env` in `_translate_segments_local()`. Needed for envit5 (see tokenizer gotcha below) |
| `local_translate_model_dir` / `local_translate_src_lang` | `LOCAL_TRANSLATE_MODEL_DIR` / `LOCAL_TRANSLATE_SRC_LANG` | Offline model dir (or HF id) + NLLB source-lang code |
| `subtitle_edit_path` | `SUBTITLE_EDIT_PATH` | Prepended to Subtitle Edit search list |
| `anthropic_api_key` / `gemini_api_key` / `openai_api_key` | `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` / `OPENAI_API_KEY` | LLM keys for SRT/PDF translation (masked `show="*"` in dialog) |
| `translate_provider` | `TRANSLATE_PROVIDER` | `Claude` \| `Gemini` \| `OpenAI`; set by the row-8 dropdown (`set_translate_provider`) |
| `translate_model` | `TRANSLATE_MODEL` | Optional model override; empty → `_TRANSLATE_DEFAULT_MODEL[provider]`. Settings dialog shows a **dropdown** of `Provider — model-id` labels (not a path — these are cloud APIs, no local files); `_resolve_model()` strips the label back to the bare id before saving |

**Note:** `_save_settings()` now takes the translate params as keyword args defaulting to `None` = "keep current". `set_translate_provider()` persists only the provider (passes other paths through unchanged), so it must read `voxcpm_ckpt_var`/`FFMPEG_DIR`/etc. to avoid wiping them.

## SRT / PDF Translation to Vietnamese (LLM)

Row 8 (`_brow8`) — translate SRT / PDF / **Word `.docx` / `.txt`** to natural Vietnamese via Claude / Gemini / OpenAI / Offline. Three buttons (`btn_translate_srt` / `btn_translate_pdf` / `btn_translate_doc`), toggled together by `_set_translate_buttons()`. **Decoupled from `set_mode()`**: always enabled (no entry in any disable sweep) and self-lock only during their own run (re-enabled in `finally`). They operate on a freshly file-dialog-picked file, NOT `subtitles_cache`/`PDF_CHUNKS`, so they never conflict with a running TTS job.

| Piece | Detail |
|---|---|
| `_translate_active_key()` | Resolves `(provider, key, model)`; raises if the selected provider's key is blank |
| `_llm_call_claude/gemini/openai()` | Plain `urllib` POST (no SDK dep). Claude `/v1/messages` + `anthropic-version: 2023-06-01`; Gemini `:generateContent?key=`; OpenAI `/v1/chat/completions` |
| `_translate_segments(segments, context, …)` | Batches `_TRANSLATE_BATCH` (40) lines/call using `[[n]] text` markers; parses back with `_parse_marked`; **any missing/empty line → per-line fallback retry**, then keeps source text if still failing (never drops content) |
| `translate_srt()` | Parses `.srt`, translates `clean_text(content)`, writes `<name>_vi.srt` preserving timestamps |
| `translate_pdf()` | Extracts chunks via `pdf_helper.py` (same as `load_pdf`), writes `<name>_vi.{txt\|pdf\|docx}` via `_write_translated_doc()` (Row-8 `translate_pdf_format_var` dropdown, label "Ra (PDF/Word/TXT)" — shared by PDF + Word/TXT). PDF output = reflowed text only (no original layout) using `fpdf2` + a Windows Unicode TTF (`_find_unicode_font`, Arial/Segoe/Times); DOCX uses `python-docx`. Missing lib → auto-fallback to `.txt`. `fpdf2`+`python-docx` added to build_all.bat pip line + spec `hiddenimports` (`fpdf`, `docx`) |
| `translate_doc()` | Translates **Word `.docx` / `.txt`** input. `.docx` → paragraphs via `python-docx`; `.txt` → non-empty lines via `_read_text_smart` (handles UTF-16/BOM). Same translate + `_write_translated_doc` output pipeline, format dropdown, pause/stop, and `_reveal_output` as `translate_pdf`. Button `btn_translate_doc` in row `_brow8` |

**Bilingual mode** (`translate_bilingual_var` checkbox): SRT line becomes `original\ntranslated`; PDF writes both. **Context field** (`translate_context_var`) feeds the system prompt for consistent pronouns/xưng hô — the single biggest quality lever for VN subtitles (online providers only).

### Pause / Resume / Stop (row `_brow8b`)

Three controls (`btn_tr_pause`/`btn_tr_resume`/`btn_tr_stop`) drive module flags `TRANSLATE_PAUSED` / `TRANSLATE_STOP` (enabled only while a translate job runs, toggled via `_translate_set_controls`). **Online**: `_translate_segments` checks the flags between each 40-line batch (waits while paused, breaks on stop). **Offline**: the flags can't reach the running subprocess, so the controls also send `PAUSE`/`RESUME`/`STOP` lines to `translate_helper.py` via its **stdin** (`_translate_send_proc`, using the stored `_TRANSLATE_PROC`); the helper runs a daemon stdin-reader thread (`_CTRL`) and checks it between batches. On stop, **partial output is still saved** — untranslated tail keeps the source text (both the helper and the online path back-fill `None`/missing with the original), so the file stays valid. Stop → no fireworks but still reveals the file; normal finish → fireworks + reveal. Progress shows in both the bar and the logbox (`_make_translate_progress_cb`, throttled to 10% steps); on finish the output folder opens via `_reveal_output` (`explorer /select,`).

### Offline (local) translation — provider `"Offline"`

The Row-8 dropdown has a 4th option **`Offline`** that translates fully on-device via `translate_helper.py` (no API/network). `_translate_segments()` dispatches: `TRANSLATE_PROVIDER == "Offline"` → `_translate_segments_local()`, else the LLM path. Local mode ignores the context field (NLLB/envit5 take no instructions).

- **Model**: any HuggingFace seq2seq dir (or HF id) set in ⚙ Cài đặt → `local_translate_model_dir`. Helper auto-detects: `nllb`/`m2m` → `forced_bos_token_id` for `--tgt-lang vie_Latn`; `envit5` → `en: ` prefix, EN→VI only; else generic `generate()`. Recommended: `facebook/nllb-200-distilled-600M` (multilingual) or `VietAI/envit5-translation` (EN→VI, best VN style).
- **Source language** (`local_translate_src_lang`, NLLB only) is a friendly dropdown in settings mapping to codes (`eng_Latn`, `zho_Hans`, `jpn_Jpan`, …); envit5 ignores it.
- **Env**: `_translate_segments_local()` picks the interpreter in this order: `TRANSLATE_ENV_OVERRIDE` (settings `translate_env_override`, an explicit `python.exe`) → `_find_voxcpm_python()`. Needs `torch`+`transformers`+`sentencepiece`. `translate_helper.py` is the **9th companion script** (added to all 3 onefile spec `datas`, build_all.bat step-0 validation + both copy loops, step-6G fail-closed copy).
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
| VideOCR CLI | small | Video OCR |
| Offline translate model (NLLB-600M / envit5) | ~1.5–2.5 GB | Offline SRT/PDF translation (only if using provider `Offline`; reuses `voxcpm_env` + needs `transformers`/`sentencepiece`) |

Default paths hardcoded in source (override via ⚙ Cài đặt):
- `VIDEOCR_CLI_DIR`: `C:\Users\os\Downloads\Compressed\VideOCR-1.5.1\...\CLI`
- VoxCPM ckpt seed: `E:\VoxCPM-1.5-VN\VoxCPM\pretrained\VoxCPM-1.5-VN`

See `MOVE_CHECKLIST.txt` for the step-by-step checklist when moving to a new machine.
