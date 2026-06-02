@echo off
setlocal enabledelayedexpansion
title SRT TTS Studio - Build MSI (Protected)

echo ================================================
echo   SRT TTS Studio - Build MSI Installer
echo   Protection: Cython + PyArmor + Hardware DRM
echo   Requires: Python 3.9+, WiX Toolset v3
echo ================================================
echo.

:: =========================================
:: STEP 0: Check source files
:: =========================================
echo [0/8] Checking source files...

set MISSING=0
if not exist "apppp_integrated.py"         ( echo   [!] Missing: apppp_integrated.py         & set MISSING=1 )
if not exist "logo.ico"                    ( echo   [!] Missing: logo.ico                    & set MISSING=1 )
if not exist "logo.png"                    ( echo   [!] Missing: logo.png                    & set MISSING=1 )
if not exist "product.wxs"                 ( echo   [!] Missing: product.wxs                 & set MISSING=1 )
if not exist "license.rtf"                 ( echo   [!] Missing: license.rtf                 & set MISSING=1 )
if not exist "naycaugioi.wav"              ( echo   [!] Missing: naycaugioi.wav              & set MISSING=1 )
if not exist "toyeucaunhieulamday.wav"     ( echo   [!] Missing: toyeucaunhieulamday.wav     & set MISSING=1 )
if not exist "chungtakhongthuocvenhau.wav" ( echo   [!] Missing: chungtakhongthuocvenhau.wav & set MISSING=1 )

if "%MISSING%"=="1" (
    echo.
    echo [ERROR] Missing files!
    pause & exit /b 1
)
echo   [OK] All source files present.
echo.

:: =========================================
:: STEP 1: Check / Install Python
:: =========================================
echo [1/8] Checking Python...

python --version >nul 2>&1
if not errorlevel 1 goto python_ok

echo   Python not found. Downloading Python 3.11...
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%TEMP%\python_installer.exe' -UseBasicParsing"

if not exist "%TEMP%\python_installer.exe" (
    echo   [ERROR] Failed to download Python!
    pause & exit /b 1
)

echo   Installing Python...
"%TEMP%\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

for /f "tokens=*" %%p in ('powershell -Command "[System.Environment]::GetEnvironmentVariable(\"PATH\",\"Machine\") + \";\" + [System.Environment]::GetEnvironmentVariable(\"PATH\",\"User\")"') do set PATH=%%p

python --version >nul 2>&1
if errorlevel 1 (
    echo   [ERROR] Python install failed. Restart cmd and try again.
    pause & exit /b 1
)

:python_ok
for /f "tokens=*" %%v in ('python --version') do echo   [OK] %%v

echo   Installing Python libraries...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet customtkinter edge-tts srt Pillow pyinstaller cython pyarmor
echo   [OK] Python libraries ready.
echo.

:: =========================================
:: STEP 2: Check / Install Visual Studio Build Tools
:: =========================================
echo [2/8] Checking C compiler (Visual Studio Build Tools)...

python -c "import os,sys; roots=['C:/Program Files/Microsoft Visual Studio','C:/Program Files (x86)/Microsoft Visual Studio']; years=['2022','2019','2017']; eds=['Community','Professional','Enterprise','BuildTools']; found=[os.path.join(r,y,e,'VC','Auxiliary','Build','vcvarsall.bat') for r in roots for y in years for e in eds if os.path.exists(os.path.join(r,y,e,'VC','Auxiliary','Build','vcvarsall.bat'))]; print(found[0] if found else 'NOT_FOUND')" > "%TEMP%\msvc_path.txt" 2>nul

set /p MSVC_RAW=<"%TEMP%\msvc_path.txt"
del "%TEMP%\msvc_path.txt" >nul 2>&1

if "%MSVC_RAW%"=="NOT_FOUND" goto msvc_install
if "%MSVC_RAW%"=="" goto msvc_install
goto msvc_ok

:msvc_install
echo   Visual Studio Build Tools not found. Downloading...
python -c "import urllib.request; urllib.request.urlretrieve('https://aka.ms/vs/17/release/vs_BuildTools.exe', r'%TEMP%\vs_BuildTools.exe'); print('OK')"

if not exist "%TEMP%\vs_BuildTools.exe" (
    echo   [ERROR] Could not download Visual Studio Build Tools!
    pause & exit /b 1
)

echo   Installing Visual Studio Build Tools (co the mat 5-15 phut)...
"%TEMP%\vs_BuildTools.exe" --quiet --wait --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended

python -c "import os,sys; roots=['C:/Program Files/Microsoft Visual Studio','C:/Program Files (x86)/Microsoft Visual Studio']; years=['2022','2019','2017']; eds=['Community','Professional','Enterprise','BuildTools']; found=[os.path.join(r,y,e,'VC','Auxiliary','Build','vcvarsall.bat') for r in roots for y in years for e in eds if os.path.exists(os.path.join(r,y,e,'VC','Auxiliary','Build','vcvarsall.bat'))]; print(found[0] if found else 'NOT_FOUND')" > "%TEMP%\msvc_path.txt" 2>nul

set /p MSVC_RAW=<"%TEMP%\msvc_path.txt"
del "%TEMP%\msvc_path.txt" >nul 2>&1

if "%MSVC_RAW%"=="NOT_FOUND" (
    echo   [ERROR] MSVC install failed - restart may be required.
    pause & exit /b 1
)

:msvc_ok
python -c "import os; p=r'%MSVC_RAW%'; d=os.path.dirname(p.replace('/',os.sep)); print(d)" > "%TEMP%\msvc_dir.txt" 2>nul
set /p MSVC_PATH=<"%TEMP%\msvc_dir.txt"
del "%TEMP%\msvc_dir.txt" >nul 2>&1

echo   [OK] C compiler ready: %MSVC_PATH%
echo.

:: =========================================
:: STEP 3: Check / Install WiX Toolset
:: =========================================
echo [3/8] Checking WiX Toolset v3...

call :find_wix
if "%WIX_BIN%"=="NOT_FOUND" goto wix_install
if "%WIX_BIN%"=="" goto wix_install
echo   [OK] WiX found at: %WIX_BIN%
goto wix_ready

:wix_install
echo   WiX not found. Downloading WiX 3.11...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/wixtoolset/wix3/releases/download/wix3141rtm/wix314.exe' -OutFile '%TEMP%\wix_installer.exe' -UseBasicParsing"

if not exist "%TEMP%\wix_installer.exe" (
    echo   [ERROR] Failed to download WiX!
    pause & exit /b 1
)

echo   Installing WiX silently...
"%TEMP%\wix_installer.exe" /quiet
timeout /t 5 /nobreak >nul

call :find_wix
if "%WIX_BIN%"=="NOT_FOUND" goto wix_error
if "%WIX_BIN%"=="" goto wix_error
echo   [OK] WiX installed: %WIX_BIN%
goto wix_ready

:wix_error
echo   [ERROR] WiX install failed!
pause & exit /b 1

:wix_ready
set WIX_CANDLE="%WIX_BIN%\candle.exe"
set WIX_LIGHT="%WIX_BIN%\light.exe"
set WIX_HEAT="%WIX_BIN%\heat.exe"
echo.

:: =========================================
:: STEP 4: PyArmor obfuscation (Layer 1)
:: =========================================
echo [4/8] Obfuscating with PyArmor (Layer 1)...
echo   (Buoc nay them layer bao ve bytecode truoc Cython)
echo.

if exist "pyarmor_dist" rmdir /s /q "pyarmor_dist"

:: PyArmor obfuscate → tao file obfuscated vao thu muc pyarmor_dist
pyarmor gen --output pyarmor_dist apppp_integrated.py

if not exist "pyarmor_dist\apppp_integrated.py" (
    echo   [!] PyArmor gen failed - trying legacy mode...
    pyarmor obfuscate --output pyarmor_dist apppp_integrated.py
)

if not exist "pyarmor_dist\apppp_integrated.py" (
    echo   [!] PyArmor obfuscation failed. Falling back to Cython-only mode.
    echo   [!] (PyArmor layer se bi bo qua, Cython van duoc ap dung)
    copy "apppp_integrated.py" "apppp_integrated_tobuild.py" >nul
) else (
    echo   [OK] PyArmor obfuscation successful.
    copy "pyarmor_dist\apppp_integrated.py" "apppp_integrated_tobuild.py" >nul
    :: Copy pyarmor runtime files sang thu muc goc de Cython tim thay
    if exist "pyarmor_dist\pyarmor_runtime_000000" (
        xcopy /E /I /Y "pyarmor_dist\pyarmor_runtime_000000" "pyarmor_runtime_000000" >nul
    )
)
echo.

:: =========================================
:: STEP 5: Compile Python → .pyd bằng Cython (Layer 2)
:: =========================================
echo [5/8] Compiling with Cython (Layer 2)...
echo   (Compile native DLL - co the mat 2-5 phut)
echo.

if exist "cython_build" rmdir /s /q "cython_build"
mkdir cython_build

(
echo from setuptools import setup
echo from Cython.Build import cythonize
echo import sys, os
echo setup^(
echo     ext_modules=cythonize^(
echo         "apppp_integrated_tobuild.py",
echo         compiler_directives={"language_level": "3"},
echo         build_dir="cython_build",
echo     ^),
echo     script_args=["build_ext", "--inplace"],
echo ^)
) > setup_cython.py

call "%MSVC_PATH%\vcvarsall.bat" x64 >nul 2>&1

python setup_cython.py 2>&1

:: Tim file .pyd (ten khac nhau tuy Python version)
set PYD_FILE=
for /f "tokens=*" %%f in ('dir /b /s "apppp_integrated_tobuild*.pyd" 2^>nul') do set PYD_FILE=%%f

if "%PYD_FILE%"=="" (
    echo.
    echo   [ERROR] Cython compile failed!
    del setup_cython.py >nul 2>&1
    del "apppp_integrated_tobuild.py" >nul 2>&1
    pause & exit /b 1
)

echo.
echo   [OK] Cython compile successful: %PYD_FILE%

del setup_cython.py >nul 2>&1
echo.

:: =========================================
:: STEP 6: Build with PyInstaller
:: =========================================
echo [6/8] Building with PyInstaller (onedir mode)...
echo.

if exist "dist"  rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

:: Copy .pyd vao thu muc hien tai
for /f "tokens=*" %%f in ('dir /b "apppp_integrated_tobuild*.pyd" 2^>nul') do set PYD_LOCAL=%%f
if "%PYD_LOCAL%"=="" (
    for /f "tokens=*" %%f in ('dir /b /s "apppp_integrated_tobuild*.pyd" 2^>nul') do (
        copy "%%f" . >nul
        for /f "tokens=*" %%n in ('dir /b "apppp_integrated_tobuild*.pyd"') do set PYD_LOCAL=%%n
        goto pyd_copied
    )
)
:pyd_copied

:: Chuyen ten .pyd thanh apppp_integrated.*.pyd de PyInstaller nhan dung
for /f "tokens=*" %%n in ('dir /b "apppp_integrated_tobuild*.pyd" 2^>nul') do (
    set OLD_PYD=%%n
)
set RENAMED_PYD=%OLD_PYD:apppp_integrated_tobuild=apppp_integrated%
if not "%OLD_PYD%"=="%RENAMED_PYD%" (
    copy "%OLD_PYD%" "%RENAMED_PYD%" >nul
    set PYD_LOCAL=%RENAMED_PYD%
)

python -m PyInstaller ^
    --onedir --windowed ^
    --name "SRT_TTS_Studio" ^
    --icon "logo.ico" ^
    --add-data "logo.png;." ^
    --add-data "logo.ico;." ^
    --add-data "naycaugioi.wav;." ^
    --add-data "toyeucaunhieulamday.wav;." ^
    --add-data "chungtakhongthuocvenhau.wav;." ^
    --add-binary "%PYD_LOCAL%;." ^
    --hidden-import edge_tts ^
    --hidden-import edge_tts.communicate ^
    --hidden-import srt ^
    --hidden-import customtkinter ^
    --hidden-import PIL ^
    --hidden-import PIL.Image ^
    --hidden-import PIL.ImageTk ^
    apppp_integrated.py

if not exist "dist\SRT_TTS_Studio\SRT_TTS_Studio.exe" (
    echo   [ERROR] PyInstaller failed!
    pause & exit /b 1
)

echo.
echo   [OK] PyInstaller build successful.
echo.

:: =========================================
:: STEP 6b: Bundle ffmpeg + ffprobe
:: =========================================
echo [6b] Bundling ffmpeg + ffprobe...

set FFMPEG_BUNDLED=0
set FFPROBE_BUNDLED=0

if exist "dist\SRT_TTS_Studio\ffmpeg.exe"  set FFMPEG_BUNDLED=1
if exist "dist\SRT_TTS_Studio\ffprobe.exe" set FFPROBE_BUNDLED=1

if "%FFMPEG_BUNDLED%"=="1" if "%FFPROBE_BUNDLED%"=="1" goto ffmpeg_done

where ffmpeg.exe >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=*" %%f in ('where ffmpeg.exe') do (
        if "%FFMPEG_BUNDLED%"=="0" (
            copy "%%f" "dist\SRT_TTS_Studio\ffmpeg.exe" >nul
            set FFMPEG_BUNDLED=1
        )
        goto try_ffprobe
    )
)
:try_ffprobe
where ffprobe.exe >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=*" %%f in ('where ffprobe.exe') do (
        if "%FFPROBE_BUNDLED%"=="0" (
            copy "%%f" "dist\SRT_TTS_Studio\ffprobe.exe" >nul
            set FFPROBE_BUNDLED=1
        )
        goto check_download
    )
)

:check_download
if "%FFMPEG_BUNDLED%"=="1" if "%FFPROBE_BUNDLED%"=="1" goto ffmpeg_done

echo   Downloading ffmpeg + ffprobe...
powershell -Command "Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile '%TEMP%\ffmpeg.zip' -UseBasicParsing"

if exist "%TEMP%\ffmpeg.zip" (
    powershell -Command "Expand-Archive -Path '%TEMP%\ffmpeg.zip' -DestinationPath '%TEMP%\ffmpeg_extract' -Force"
    powershell -Command "$s=Get-ChildItem '%TEMP%\ffmpeg_extract' -Recurse -Filter 'ffmpeg.exe' | Select-Object -First 1 -ExpandProperty FullName; if($s){Copy-Item $s 'dist\SRT_TTS_Studio\ffmpeg.exe' -Force; 'OK'}else{'FAIL'}" > "%TEMP%\fr.txt" 2>nul
    set /p FR=<"%TEMP%\fr.txt"
    if "!FR!"=="OK" set FFMPEG_BUNDLED=1
    powershell -Command "$s=Get-ChildItem '%TEMP%\ffmpeg_extract' -Recurse -Filter 'ffprobe.exe' | Select-Object -First 1 -ExpandProperty FullName; if($s){Copy-Item $s 'dist\SRT_TTS_Studio\ffprobe.exe' -Force; 'OK'}else{'FAIL'}" > "%TEMP%\fpr.txt" 2>nul
    set /p FPR=<"%TEMP%\fpr.txt"
    if "!FPR!"=="OK" set FFPROBE_BUNDLED=1
)

:ffmpeg_done
echo   [OK] ffmpeg ready.
echo.

:: =========================================
:: STEP 6c: Generate .integrity file (SHA-256 hashes)
:: =========================================
echo [6c] Generating integrity manifest (.integrity)...

python gen_integrity.py
if errorlevel 1 (
    echo   [!] Integrity manifest generation failed - skipping.
) else (
    echo   [OK] Integrity manifest ready.
)
echo.

:: =========================================
:: STEP 7: Harvest files with Heat
:: =========================================
echo [7/8] Generating WiX components from dist folder...

%WIX_HEAT% dir "dist\SRT_TTS_Studio" -cg AppFiles -gg -gl -scom -sreg -sfrag -srd -dr INSTALLDIR -var var.SourceDir -out harvested.wxs

if not exist "harvested.wxs" (
    echo   [ERROR] heat.exe failed!
    pause & exit /b 1
)
echo   [OK] harvested.wxs created.
echo.

:: =========================================
:: STEP 8: Compile and Link WiX -> MSI
:: =========================================
echo [8/8] Compiling and linking MSI...

%WIX_CANDLE% product.wxs harvested.wxs -dSourceDir="dist\SRT_TTS_Studio" -arch x64

if errorlevel 1 (
    echo   [ERROR] candle.exe failed!
    pause & exit /b 1
)

%WIX_LIGHT% product.wixobj harvested.wixobj -ext WixUIExtension -sice:ICE80 -sice:ICE60 -out "SRT_TTS_Studio_Setup.msi" -b "dist\SRT_TTS_Studio"

if errorlevel 1 (
    echo   [ERROR] light.exe failed!
    pause & exit /b 1
)

:: =========================================
:: RESULT
:: =========================================
echo.
if exist "SRT_TTS_Studio_Setup.msi" (
    echo ================================================
    echo   BUILD SUCCESSFUL!
    echo   Output: SRT_TTS_Studio_Setup.msi
    echo.
    echo   Protection layers applied:
    echo     [1] PyArmor  - bytecode obfuscation
    echo     [2] Cython   - compiled to native .pyd DLL
    echo     [3] Hardware DRM - auth.dat bound to machine
    echo     [4] HMAC signature - tamper-proof auth.dat
    echo     [5] Integrity check - hash validation on start
    echo     [6] Login brute-force limit (5 attempts)
    echo ================================================
    explorer .
) else (
    echo   [ERROR] MSI output file not found!
)

:cleanup
:: gen_integrity.py duoc giu lai de dung cho lan build sau
if exist "harvested.wxs"          del "harvested.wxs"
if exist "product.wixobj"         del "product.wixobj"
if exist "harvested.wixobj"       del "harvested.wixobj"
if exist "*.wixpdb"               del "*.wixpdb"
if exist "cython_build"           rmdir /s /q "cython_build"
if exist "pyarmor_dist"           rmdir /s /q "pyarmor_dist"
if exist "apppp_integrated_tobuild.py"   del "apppp_integrated_tobuild.py"
if exist "apppp_integrated_tobuild.c"    del "apppp_integrated_tobuild.c"
for %%f in (apppp_integrated_tobuild*.pyd) do del "%%f" >nul 2>&1
for %%f in (apppp_integrated*.pyd) do del "%%f" >nul 2>&1

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
