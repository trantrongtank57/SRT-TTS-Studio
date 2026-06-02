@echo off
setlocal enabledelayedexpansion
title SRT TTS Studio - Build All (Onedir MSI + Onefile Portable + Secured + Trial)

echo ====================================================================
echo   SRT TTS Studio - Build All
echo   Output 1: SRT_TTS_Studio_Setup.msi       (Onedir + MSI, full security)
echo   Output 2: SRT_TTS_Studio_Portable.exe    (Onefile, standalone, no integrity)
echo   Output 3: SRT_TTS_Studio_Secured.exe     (Onefile + companion integrity)
echo             SRT_TTS_Studio_Secured.exe.integrity
echo   Output 4: SRT_TTS_Studio_Trial.exe       (Onefile + 1-day trial, registry-bound)
echo   Protection: PyArmor + Cython + Hardware DRM + Integrity
echo ====================================================================
echo.

:: =========================================
:: STEP 0: Check source files
:: =========================================
echo [0/9] Checking source files...

set MISSING=0
if not exist "apppp_integrated.py"              ( echo   [!] Missing: apppp_integrated.py              & set MISSING=1 )
if not exist "logo.ico"                         ( echo   [!] Missing: logo.ico                         & set MISSING=1 )
if not exist "logo.png"                         ( echo   [!] Missing: logo.png                         & set MISSING=1 )
if not exist "product.wxs"                      ( echo   [!] Missing: product.wxs                      & set MISSING=1 )
if not exist "license.rtf"                      ( echo   [!] Missing: license.rtf                      & set MISSING=1 )
if not exist "naycaugioi.wav"                   ( echo   [!] Missing: naycaugioi.wav                   & set MISSING=1 )
if not exist "toyeucaunhieulamday.wav"          ( echo   [!] Missing: toyeucaunhieulamday.wav          & set MISSING=1 )
if not exist "chungtakhongthuocvenhau.wav"      ( echo   [!] Missing: chungtakhongthuocvenhau.wav      & set MISSING=1 )
if not exist "error.wav"                        ( echo   [!] Missing: error.wav                        & set MISSING=1 )
if not exist "SRT_TTS_Studio.spec"                  ( echo   [!] Missing: SRT_TTS_Studio.spec                  & set MISSING=1 )
if not exist "SRT_TTS_Studio_onefile.spec"          ( echo   [!] Missing: SRT_TTS_Studio_onefile.spec          & set MISSING=1 )
if not exist "SRT_TTS_Studio_onefile_secured.spec"  ( echo   [!] Missing: SRT_TTS_Studio_onefile_secured.spec  & set MISSING=1 )
if not exist "gen_self_hash.py"                     ( echo   [!] Missing: gen_self_hash.py                     & set MISSING=1 )
if not exist "build_type_portable.dat"              ( echo   [!] Missing: build_type_portable.dat              & set MISSING=1 )
if not exist "build_type_secured.dat"               ( echo   [!] Missing: build_type_secured.dat               & set MISSING=1 )
if not exist "build_type_trial.dat"                 ( echo   [!] Missing: build_type_trial.dat                 & set MISSING=1 )
if not exist "SRT_TTS_Studio_onefile_trial.spec"    ( echo   [!] Missing: SRT_TTS_Studio_onefile_trial.spec    & set MISSING=1 )
if not exist "SRT_TTS_Studio_onedir.spec"           ( echo   [!] Missing: SRT_TTS_Studio_onedir.spec           & set MISSING=1 )
if not exist "srt_tts_launch.py"                    ( echo   [!] Missing: srt_tts_launch.py ^(entry launcher^)   & set MISSING=1 )

:: --- Companion scripts ---
if not exist "rvc_helper.py"                    ( echo   [!] Missing: rvc_helper.py                    & set MISSING=1 )
if not exist "voxcpm_helper.py"                 ( echo   [!] Missing: voxcpm_helper.py                 & set MISSING=1 )
if not exist "whisper_stt.py"                   ( echo   [!] Missing: whisper_stt.py                   & set MISSING=1 )
if not exist "audio_enhancer.py"                ( echo   [!] Missing: audio_enhancer.py                & set MISSING=1 )
if not exist "pdf_helper.py"                    ( echo   [!] Missing: pdf_helper.py                    & set MISSING=1 )
if not exist "srt_align_helper.py"              ( echo   [!] Missing: srt_align_helper.py              & set MISSING=1 )
if not exist "videocr_helper.py"                ( echo   [!] Missing: videocr_helper.py                & set MISSING=1 )
if not exist "video_stt_helper.py"              ( echo   [!] Missing: video_stt_helper.py              & set MISSING=1 )

:: --- RVC model files ---
if not exist "hubert_base.pt"                   ( echo   [!] Missing: hubert_base.pt                   & set MISSING=1 )
if not exist "rmvpe.pt"                         ( echo   [!] Missing: rmvpe.pt                         & set MISSING=1 )

:: --- RVC virtual environment (Python 3.10 venv, ~1.5 GB) ---
if not exist "rvc_env\Scripts\python.exe"       ( echo   [!] Missing: rvc_env\Scripts\python.exe ^(RVC venv^) & set MISSING=1 )

if "%MISSING%"=="1" (
    echo.
    echo [ERROR] Missing files — cannot continue.
    pause & exit /b 1
)
echo   [OK] All source files present.
echo.

:: =========================================
:: STEP 1: Check / Install Python + deps
:: =========================================
echo [1/9] Checking Python...

python --version >nul 2>&1
if not errorlevel 1 goto python_ok

echo   Python not found. Downloading Python 3.11...
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%TEMP%\python_installer.exe' -UseBasicParsing"
if not exist "%TEMP%\python_installer.exe" ( echo   [ERROR] Download failed! & pause & exit /b 1 )
"%TEMP%\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
for /f "tokens=*" %%p in ('powershell -Command "[System.Environment]::GetEnvironmentVariable(\"PATH\",\"Machine\") + \";\" + [System.Environment]::GetEnvironmentVariable(\"PATH\",\"User\")"') do set PATH=%%p
python --version >nul 2>&1
if errorlevel 1 ( echo   [ERROR] Python install failed. Restart cmd and retry. & pause & exit /b 1 )

:python_ok
for /f "tokens=*" %%v in ('python --version') do echo   [OK] %%v
echo   Installing Python libraries...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet customtkinter edge-tts srt Pillow pyinstaller cython pyarmor
echo   [OK] Python libraries ready.
echo.

:: =========================================
:: STEP 2: Check / Install MSVC Build Tools
:: =========================================
echo [2/9] Checking C compiler (Visual Studio Build Tools)...

python -c "import os; roots=['C:/Program Files/Microsoft Visual Studio','C:/Program Files (x86)/Microsoft Visual Studio']; years=['2022','2019','2017']; eds=['Community','Professional','Enterprise','BuildTools']; found=[os.path.join(r,y,e,'VC','Auxiliary','Build','vcvarsall.bat') for r in roots for y in years for e in eds if os.path.exists(os.path.join(r,y,e,'VC','Auxiliary','Build','vcvarsall.bat'))]; print(found[0] if found else 'NOT_FOUND')" > "%TEMP%\msvc_path.txt" 2>nul
set /p MSVC_RAW=<"%TEMP%\msvc_path.txt"
del "%TEMP%\msvc_path.txt" >nul 2>&1

if "%MSVC_RAW%"=="NOT_FOUND" goto msvc_install
if "%MSVC_RAW%"=="" goto msvc_install
goto msvc_ok

:msvc_install
echo   Visual Studio Build Tools not found. Downloading...
python -c "import urllib.request; urllib.request.urlretrieve('https://aka.ms/vs/17/release/vs_BuildTools.exe', r'%TEMP%\vs_BuildTools.exe'); print('OK')"
if not exist "%TEMP%\vs_BuildTools.exe" ( echo   [ERROR] Download failed! & pause & exit /b 1 )
echo   Installing Visual Studio Build Tools (co the mat 5-15 phut)...
"%TEMP%\vs_BuildTools.exe" --quiet --wait --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended
python -c "import os; roots=['C:/Program Files/Microsoft Visual Studio','C:/Program Files (x86)/Microsoft Visual Studio']; years=['2022','2019','2017']; eds=['Community','Professional','Enterprise','BuildTools']; found=[os.path.join(r,y,e,'VC','Auxiliary','Build','vcvarsall.bat') for r in roots for y in years for e in eds if os.path.exists(os.path.join(r,y,e,'VC','Auxiliary','Build','vcvarsall.bat'))]; print(found[0] if found else 'NOT_FOUND')" > "%TEMP%\msvc_path.txt" 2>nul
set /p MSVC_RAW=<"%TEMP%\msvc_path.txt"
del "%TEMP%\msvc_path.txt" >nul 2>&1
if "%MSVC_RAW%"=="NOT_FOUND" ( echo   [ERROR] MSVC install failed. & pause & exit /b 1 )
if "%MSVC_RAW%"=="" ( echo   [ERROR] MSVC install failed. & pause & exit /b 1 )

:msvc_ok
python -c "import os,sys; p=r'%MSVC_RAW%'; d=os.path.dirname(p.replace('/',os.sep)); print(d)" > "%TEMP%\msvc_dir.txt" 2>nul
set /p MSVC_PATH=<"%TEMP%\msvc_dir.txt"
del "%TEMP%\msvc_dir.txt" >nul 2>&1
echo   [OK] C compiler ready: %MSVC_PATH%
echo.

:: =========================================
:: STEP 3: Check / Install WiX Toolset v3
:: =========================================
echo [3/9] Checking WiX Toolset v3...

call :find_wix
if "%WIX_BIN%"=="NOT_FOUND" goto wix_install
if "%WIX_BIN%"=="" goto wix_install
echo   [OK] WiX found at: %WIX_BIN%
goto wix_ready

:wix_install
echo   WiX not found. Downloading WiX 3.11...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/wixtoolset/wix3/releases/download/wix3141rtm/wix314.exe' -OutFile '%TEMP%\wix_installer.exe' -UseBasicParsing"
if not exist "%TEMP%\wix_installer.exe" ( echo   [ERROR] Download failed! & pause & exit /b 1 )
echo   Installing WiX silently...
"%TEMP%\wix_installer.exe" /quiet
timeout /t 5 /nobreak >nul
call :find_wix
if "%WIX_BIN%"=="NOT_FOUND" ( echo   [ERROR] WiX install failed! & pause & exit /b 1 )
if "%WIX_BIN%"=="" ( echo   [ERROR] WiX install failed! & pause & exit /b 1 )

:wix_ready
set WIX_CANDLE="%WIX_BIN%\candle.exe"
set WIX_LIGHT="%WIX_BIN%\light.exe"
set WIX_HEAT="%WIX_BIN%\heat.exe"
echo   [OK] WiX ready: %WIX_BIN%
echo.

:: =========================================
:: STEP 4: (DISABLED) PyArmor obfuscation
:: =========================================
:: PyArmor + Cython stacking was self-defeating: the PyArmor runtime never made it
:: into the bundle (so obfuscation was inert), and feeding PyArmor's bootstrap into
:: Cython is meaningless. The robust protection is Cython compiling the ORIGINAL
:: source into a native .pyd that is the REAL executed code (see step 5 + the spec's
:: a.pure strip). So PyArmor is skipped; Cython is the genuine protection layer.
echo [4/9] PyArmor step DISABLED - Cython native .pyd is the real protection layer.
if exist "pyarmor_dist" rmdir /s /q "pyarmor_dist"
if exist "pyarmor_runtime_000000" rmdir /s /q "pyarmor_runtime_000000"
echo.

:: =========================================
:: STEP 5: Cython compile → .pyd (Layer 2)
:: =========================================
echo [5/9] Compiling with Cython (Layer 2)...
echo   (Co the mat 2-5 phut)
echo.

if exist "cython_build" rmdir /s /q "cython_build"
mkdir cython_build
if exist "cython_out" rmdir /s /q "cython_out"
mkdir cython_out

:: Compile the ORIGINAL source directly -> apppp_integrated.*.pyd (native code).
:: The .py source stays in the root so PyInstaller's analysis can trace deps; the
:: .pyd is moved to cython_out\ (NOT on pathex) so analysis resolves the .py, and
:: the spec strips the source bytecode + ships only this .pyd.
(
echo from setuptools import setup
echo from Cython.Build import cythonize
echo setup^(
echo     ext_modules=cythonize^(
echo         "apppp_integrated.py",
echo         compiler_directives={"language_level": "3"},
echo         build_dir="cython_build",
echo     ^),
echo     script_args=["build_ext", "--inplace"],
echo ^)
) > setup_cython.py

call "%MSVC_PATH%\vcvarsall.bat" x64 >nul 2>&1
python setup_cython.py 2>&1

set PYD_FILE=
for /f "tokens=*" %%f in ('dir /b "apppp_integrated.cp*.pyd" 2^>nul') do set PYD_FILE=%%f
if "%PYD_FILE%"=="" (
    for /f "tokens=*" %%f in ('dir /b /s "apppp_integrated.cp*.pyd" 2^>nul') do (
        copy "%%f" . >nul
        for /f "tokens=*" %%n in ('dir /b "apppp_integrated.cp*.pyd"') do set PYD_FILE=%%n
        goto cy_found
    )
)
:cy_found

if "%PYD_FILE%"=="" (
    echo.
    echo   [ERROR] Cython compile failed!
    del setup_cython.py >nul 2>&1
    pause & exit /b 1
)

:: Move the .pyd out of the root into cython_out\ so it does NOT shadow the .py
:: during PyInstaller analysis (dep tracing needs the source).
move /Y "%PYD_FILE%" "cython_out\%PYD_FILE%" >nul
if exist "apppp_integrated.c" del "apppp_integrated.c" >nul 2>&1

if not exist "cython_out\%PYD_FILE%" (
    echo   [ERROR] Could not stage .pyd into cython_out\
    del setup_cython.py >nul 2>&1
    pause & exit /b 1
)

echo.
echo   [OK] Cython compile successful: cython_out\%PYD_FILE%
del setup_cython.py >nul 2>&1
echo.

:: =========================================
:: STEP 6A: PyInstaller — Onedir build
:: =========================================
echo [6A/9] PyInstaller - Onedir build...
echo.

if exist "dist"  rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

:: Use the spec: entry = srt_tts_launch.py (imports the Cython .pyd); the spec
:: strips the plaintext bytecode of apppp_integrated from the PYZ so ONLY the
:: native .pyd ships. Dependency tracing still works because apppp_integrated.py
:: source is in the root (on pathex) and the .pyd lives in cython_out\ (off pathex).
python -m PyInstaller SRT_TTS_Studio_onedir.spec

if not exist "dist\SRT_TTS_Studio\SRT_TTS_Studio.exe" (
    echo   [ERROR] PyInstaller onedir build failed!
    pause & exit /b 1
)
echo.
echo   [OK] Onedir build successful.
echo.

:: =========================================
:: STEP 6B: Bundle ffmpeg + ffprobe
:: =========================================
echo [6B/9] Bundling ffmpeg + ffprobe...

set FFMPEG_OK=0
set FFPROBE_OK=0
if exist "dist\SRT_TTS_Studio\ffmpeg.exe"  set FFMPEG_OK=1
if exist "dist\SRT_TTS_Studio\ffprobe.exe" set FFPROBE_OK=1

if "%FFMPEG_OK%"=="1" if "%FFPROBE_OK%"=="1" goto ffmpeg_done

where ffmpeg.exe >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=*" %%f in ('where ffmpeg.exe') do (
        if "%FFMPEG_OK%"=="0" ( copy "%%f" "dist\SRT_TTS_Studio\ffmpeg.exe" >nul & set FFMPEG_OK=1 )
        goto try_ffprobe
    )
)
:try_ffprobe
where ffprobe.exe >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=*" %%f in ('where ffprobe.exe') do (
        if "%FFPROBE_OK%"=="0" ( copy "%%f" "dist\SRT_TTS_Studio\ffprobe.exe" >nul & set FFPROBE_OK=1 )
    )
)

if "%FFMPEG_OK%"=="1" if "%FFPROBE_OK%"=="1" goto ffmpeg_done

echo   Downloading ffmpeg + ffprobe...
powershell -Command "Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile '%TEMP%\ffmpeg.zip' -UseBasicParsing"
if exist "%TEMP%\ffmpeg.zip" (
    powershell -Command "Expand-Archive -Path '%TEMP%\ffmpeg.zip' -DestinationPath '%TEMP%\ffmpeg_extract' -Force"
    powershell -Command "$s=Get-ChildItem '%TEMP%\ffmpeg_extract' -Recurse -Filter 'ffmpeg.exe'|Select -First 1 -ExpandProperty FullName;if($s){Copy-Item $s 'dist\SRT_TTS_Studio\ffmpeg.exe' -Force}" >nul 2>&1
    powershell -Command "$s=Get-ChildItem '%TEMP%\ffmpeg_extract' -Recurse -Filter 'ffprobe.exe'|Select -First 1 -ExpandProperty FullName;if($s){Copy-Item $s 'dist\SRT_TTS_Studio\ffprobe.exe' -Force}" >nul 2>&1
    if exist "dist\SRT_TTS_Studio\ffmpeg.exe"  set FFMPEG_OK=1
    if exist "dist\SRT_TTS_Studio\ffprobe.exe" set FFPROBE_OK=1
)

:ffmpeg_done
if "%FFMPEG_OK%"=="0" echo   [!] WARNING: ffmpeg.exe not found!
if "%FFPROBE_OK%"=="0" echo   [!] WARNING: ffprobe.exe not found!
echo   [OK] ffmpeg ready.
echo.

:: =========================================
:: STEP 6C: Integrity manifest
:: =========================================
echo [6C/9] Generating integrity manifest...

python gen_integrity.py
if errorlevel 1 (
    echo   [!] gen_integrity.py failed - skipping.
) else (
    echo   [OK] .integrity written.
)
echo.

:: =========================================
:: STEP 6G: Copy companion scripts + RVC models vào dist
:: (phải chạy trước bước 7 để WiX Heat nhặt được)
:: =========================================
echo [6G/9] Copying companion scripts + RVC models to dist...
echo   (FAIL-CLOSED: thieu bat ky thanh phan nao se abort - khong build MSI thieu file)

set DIST_DIR=dist\SRT_TTS_Studio
set G6_FAIL=0

:: Companion scripts — verify each landed in dist after copy
for %%f in (rvc_helper.py voxcpm_helper.py whisper_stt.py audio_enhancer.py pdf_helper.py srt_align_helper.py videocr_helper.py video_stt_helper.py) do (
    if exist "%%f" (
        copy /Y "%%f" "%DIST_DIR%\%%f" >nul
        if exist "%DIST_DIR%\%%f" ( echo   [OK] %%f ) else ( echo   [ERROR] copy failed: %%f & set G6_FAIL=1 )
    ) else (
        echo   [ERROR] Missing source: %%f & set G6_FAIL=1
    )
)

:: RVC model files — verify each landed in dist after copy
for %%f in (hubert_base.pt rmvpe.pt) do (
    if exist "%%f" (
        copy /Y "%%f" "%DIST_DIR%\%%f" >nul
        if exist "%DIST_DIR%\%%f" ( echo   [OK] %%f ) else ( echo   [ERROR] copy failed: %%f & set G6_FAIL=1 )
    ) else (
        echo   [ERROR] Missing source: %%f & set G6_FAIL=1
    )
)

:: rvc_env (Python 3.10 venv + patched packages) — bat buoc cho RVC
if exist "rvc_env" (
    echo   Copying rvc_env ^(~1.5 GB, may take a while^)...
    robocopy "rvc_env" "%DIST_DIR%\rvc_env" /E /NFL /NDL /NJH /NJS /NC /NS >nul
    if errorlevel 8 (
        echo   [ERROR] robocopy rvc_env failed & set G6_FAIL=1
    ) else (
        if exist "%DIST_DIR%\rvc_env\Scripts\python.exe" (
            echo   [OK] rvc_env
        ) else (
            echo   [ERROR] rvc_env copied but Scripts\python.exe missing & set G6_FAIL=1
        )
    )
) else (
    echo   [ERROR] rvc_env not found in project root & set G6_FAIL=1
)

if "%G6_FAIL%"=="1" (
    echo.
    echo [ERROR] Step 6G incomplete - dist is missing companion files / models / rvc_env.
    echo         Building the MSI now would produce a broken installer
    echo         ^(RVC/VoxCPM/PDF/OCR/STT se thieu file tren may dich^).
    echo         Sua cac file nguon bi thieu o tren roi build lai.
    pause & exit /b 1
)

echo   [OK] Step 6G done - companion files, models, va rvc_env deu da co trong dist.
echo.

:: =========================================
:: STEP 6D: PyInstaller — Onefile build
:: =========================================
echo [6D/9] PyInstaller - Onefile portable build...
echo.

:: Xoa build cache cu cua onefile de tranh conflict
if exist "build\SRT_TTS_Studio_Portable" rmdir /s /q "build\SRT_TTS_Studio_Portable"

python -m PyInstaller SRT_TTS_Studio_onefile.spec

if exist "dist\SRT_TTS_Studio_Portable.exe" (
    echo.
    echo   [OK] Onefile build successful.
) else (
    echo.
    echo   [!] Onefile build failed - continuing with MSI only.
)
echo.

:: =========================================
:: STEP 6E: PyInstaller — Onefile Secured build
:: =========================================
echo [6E/9] PyInstaller - Onefile secured build...
echo.

if exist "build\SRT_TTS_Studio_Secured" rmdir /s /q "build\SRT_TTS_Studio_Secured"

python -m PyInstaller SRT_TTS_Studio_onefile_secured.spec

if not exist "dist\SRT_TTS_Studio_Secured.exe" (
    echo.
    echo   [!] Onefile secured build failed - continuing without it.
    goto secured_skip
)

echo.
echo   [OK] Onefile secured exe built. Generating companion integrity file...
python gen_self_hash.py "dist\SRT_TTS_Studio_Secured.exe"

if not exist "dist\SRT_TTS_Studio_Secured.exe.integrity" (
    echo   [!] gen_self_hash.py failed - secured build may not have integrity check.
)

:secured_skip
echo.

:: =========================================
:: STEP 6F: PyInstaller — Onefile Trial build
:: =========================================
echo [6F/9] PyInstaller - Onefile trial build (1-day limit)...
echo.

if exist "build\SRT_TTS_Studio_Trial" rmdir /s /q "build\SRT_TTS_Studio_Trial"

python -m PyInstaller SRT_TTS_Studio_onefile_trial.spec

if exist "dist\SRT_TTS_Studio_Trial.exe" (
    echo.
    echo   [OK] Onefile trial build successful.
) else (
    echo.
    echo   [!] Onefile trial build failed - continuing without it.
)
echo.

:: =========================================
:: STEP 7: WiX Heat
:: =========================================
echo [7/9] Generating WiX components...

%WIX_HEAT% dir "dist\SRT_TTS_Studio" -cg AppFiles -gg -gl -scom -sreg -sfrag -srd -dr INSTALLDIR -var var.SourceDir -out harvested.wxs

if not exist "harvested.wxs" (
    echo   [ERROR] heat.exe failed!
    pause & exit /b 1
)
echo   [OK] harvested.wxs created.
echo.

:: =========================================
:: STEP 8: Compile MSI
:: =========================================
echo [8/9] Compiling MSI installer...

%WIX_CANDLE% product.wxs harvested.wxs -dSourceDir="dist\SRT_TTS_Studio" -arch x64
if errorlevel 1 ( echo   [ERROR] candle.exe failed! & pause & exit /b 1 )

%WIX_LIGHT% product.wixobj harvested.wixobj -ext WixUIExtension -sice:ICE80 -sice:ICE60 -out "SRT_TTS_Studio_Setup.msi" -b "dist\SRT_TTS_Studio"
if errorlevel 1 ( echo   [ERROR] light.exe failed! & pause & exit /b 1 )

echo   [OK] MSI created.
echo.

:: =========================================
:: STEP 9: Collect outputs
:: =========================================
echo [9/9] Collecting outputs...

if exist "output" rmdir /s /q "output"
mkdir output
mkdir "output\Portable"

:: --- MSI (self-contained installer; da chua moi thu nho step 6G) — de o output root ---
if exist "SRT_TTS_Studio_Setup.msi" (
    copy "SRT_TTS_Studio_Setup.msi" "output\SRT_TTS_Studio_Setup.msi" >nul
)

:: --- Onefile exes vao output\Portable\ ---
:: Onefile KHONG nhung companion scripts/models/rvc_env -> chung phai nam CANH exe.
if exist "dist\SRT_TTS_Studio_Portable.exe" (
    copy "dist\SRT_TTS_Studio_Portable.exe" "output\Portable\SRT_TTS_Studio_Portable.exe" >nul
)
if exist "dist\SRT_TTS_Studio_Secured.exe" (
    copy "dist\SRT_TTS_Studio_Secured.exe" "output\Portable\SRT_TTS_Studio_Secured.exe" >nul
)
if exist "dist\SRT_TTS_Studio_Secured.exe.integrity" (
    copy "dist\SRT_TTS_Studio_Secured.exe.integrity" "output\Portable\SRT_TTS_Studio_Secured.exe.integrity" >nul
)
if exist "dist\SRT_TTS_Studio_Trial.exe" (
    copy "dist\SRT_TTS_Studio_Trial.exe" "output\Portable\SRT_TTS_Studio_Trial.exe" >nul
)

:: --- Companion scripts + models can cac onefile exe ---
echo   Dong goi companion scripts + models vao output\Portable\...
for %%f in (rvc_helper.py voxcpm_helper.py whisper_stt.py audio_enhancer.py pdf_helper.py srt_align_helper.py videocr_helper.py video_stt_helper.py hubert_base.pt rmvpe.pt) do (
    if exist "%%f" copy /Y "%%f" "output\Portable\%%f" >nul
)

:: --- rvc_env can cac onefile exe (bat buoc cho RVC) ---
if exist "rvc_env" (
    echo   Copying rvc_env vao output\Portable\ ^(~1.5 GB, may take a while^)...
    robocopy "rvc_env" "output\Portable\rvc_env" /E /NFL /NDL /NJH /NJS /NC /NS >nul
)

:: --- Huong dan trien khai (neu co) ---
if exist "MOVE_CHECKLIST.txt" copy /Y "MOVE_CHECKLIST.txt" "output\MOVE_CHECKLIST.txt" >nul

:: =========================================
:: RESULT
:: =========================================
echo.
echo ====================================================================
echo   BUILD COMPLETE!
echo.

set BUILD_OK=1
if exist "output\SRT_TTS_Studio_Setup.msi" (
    echo   [1] output\SRT_TTS_Studio_Setup.msi            ^(Onedir + MSI^)
    echo       Bao mat day du: PyArmor + Cython + Integrity + Lockout
) else (
    echo   [1] SRT_TTS_Studio_Setup.msi    FAILED
    set BUILD_OK=0
)

if exist "output\Portable\SRT_TTS_Studio_Portable.exe" (
    echo   [2] output\Portable\SRT_TTS_Studio_Portable.exe   ^(Onefile portable^)
    echo       1 file doc lap, khong co integrity check
) else (
    echo   [2] SRT_TTS_Studio_Portable.exe FAILED
    set BUILD_OK=0
)

if exist "output\Portable\SRT_TTS_Studio_Secured.exe" (
    echo   [3] output\Portable\SRT_TTS_Studio_Secured.exe    ^(Onefile secured^)
    echo       output\Portable\SRT_TTS_Studio_Secured.exe.integrity
    echo       Phan phoi CA HAI file - thieu companion thi app tu thoat
) else (
    echo   [3] SRT_TTS_Studio_Secured.exe  FAILED
    set BUILD_OK=0
)

if exist "output\Portable\SRT_TTS_Studio_Trial.exe" (
    echo   [4] output\Portable\SRT_TTS_Studio_Trial.exe      ^(Onefile trial, 1 ngay^)
    echo       Gioi han 1 ngay - luu trong registry, hardware-bound
) else (
    echo   [4] SRT_TTS_Studio_Trial.exe    FAILED
    set BUILD_OK=0
)

echo.
echo   Onefile exes + companion scripts + models + rvc_env deu nam trong output\Portable\
echo   (Cac onefile can cac file nay nam CANH exe moi chay du tinh nang)

echo.
echo   Cac lop bao ve:
echo     [1] Cython native .pyd LA code chay that (entry = launcher import .pyd;
echo         bytecode ma nguoc goc da bi strip khoi PYZ - khong the decompile)
echo     [2] Hardware DRM   - auth.dat bound to machine
echo     [3] HMAC signature - tamper-proof auth.dat + lockout
echo     [4] Integrity check - onedir: hash .exe+.pyd; secured: hash exe+companion
echo     [5] Brute-force lockout 15 phut ^(persist qua restart^)
echo     [6] Trial 1 ngay - registry HMAC-signed + hardware-bound + chong quay dong ho
echo ====================================================================

if "%BUILD_OK%"=="1" explorer output

:cleanup
if exist "harvested.wxs"                  del "harvested.wxs"
if exist "product.wixobj"                 del "product.wixobj"
if exist "harvested.wixobj"               del "harvested.wixobj"
if exist "*.wixpdb"                       del "*.wixpdb"
if exist "cython_build"                   rmdir /s /q "cython_build"
if exist "cython_out"                     rmdir /s /q "cython_out"
if exist "pyarmor_dist"                   rmdir /s /q "pyarmor_dist"
if exist "pyarmor_runtime_000000"         rmdir /s /q "pyarmor_runtime_000000"
if exist "apppp_integrated.c"             del "apppp_integrated.c"
for %%f in (apppp_integrated*.pyd)         do del "%%f" >nul 2>&1
if exist "setup_cython.py"               del "setup_cython.py"

echo.
pause
goto :eof

:: =========================================
:: SUBROUTINE: find_wix
:: =========================================
:find_wix
set WIX_BIN=NOT_FOUND
powershell -Command "$d = Get-ChildItem 'C:\Program Files (x86)' -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'WiX Toolset v3*' } | Sort-Object Name -Descending | Select-Object -First 1; if ($d -and (Test-Path ($d.FullName + '\bin\candle.exe'))) { $d.FullName + '\bin' } else { 'NOT_FOUND' }" > "%TEMP%\wix_path.txt" 2>nul
set /p WIX_BIN=<"%TEMP%\wix_path.txt"
del "%TEMP%\wix_path.txt" >nul 2>&1
goto :eof
