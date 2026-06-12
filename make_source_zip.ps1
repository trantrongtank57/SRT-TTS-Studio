# Zip mã nguồn SRT TTS Studio — chỉ source, loại model/artifact/secret
$ErrorActionPreference = "Stop"
$stamp = Get-Date -Format "yyyyMMdd_HHmm"
$zip   = "E:\SRT_TTS_Studio_source_$stamp.zip"

$files = @(
  # source chính + entry
  "apppp_integrated.py","srt_tts_launch.py",
  # 12 helper
  "rvc_helper.py","voxcpm_helper.py","vieneu_helper.py","f5tts_helper.py","omnivoice_helper.py",
  "whisper_stt.py","audio_enhancer.py","pdf_helper.py","srt_align_helper.py",
  "videocr_helper.py","video_stt_helper.py","translate_helper.py",
  # build/audit
  "build_all.bat","build_msi_protected.bat","gen_integrity.py","gen_self_hash.py",
  "_verify_security.py","_audit_deps.py","_strings_audit.py",
  # spec + wix
  "SRT_TTS_Studio.spec","SRT_TTS_Studio_onedir.spec","SRT_TTS_Studio_onefile.spec",
  "SRT_TTS_Studio_onefile_secured.spec","SRT_TTS_Studio_onefile_trial.spec","product.wxs",
  # asset
  "logo.ico","logo.png","license.rtf",
  "chungtakhongthuocvenhau.WAV","naycaugioi.WAV","toyeucaunhieulamday.WAV","error.wav",
  "build_type_portable.dat","build_type_secured.dat","build_type_trial.dat",
  # docs
  "CLAUDE.md","MOVE_CHECKLIST.txt",".gitignore","UI_redesign_mockup.html",
  "make_source_zip.ps1"
)

$exist = $files | Where-Object { Test-Path $_ }
$miss  = $files | Where-Object { -not (Test-Path $_) }
if ($miss) { Write-Host "[CANH BAO] thieu (bo qua): $($miss -join ', ')" -ForegroundColor Yellow }

if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path $exist -DestinationPath $zip -CompressionLevel Optimal
$mb = [math]::Round((Get-Item $zip).Length/1MB,1)
Write-Host "[OK] Tao xong: $zip  ($mb MB, $($exist.Count) file)" -ForegroundColor Green
