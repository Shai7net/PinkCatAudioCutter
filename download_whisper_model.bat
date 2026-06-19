@echo off
setlocal
cd /d "%~dp0"

echo Downloading the local Whisper model for Pink Cat Audio Cutter...
echo This can take a few minutes on the first run.
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0launch_cat_audio_cutter_bundled.ps1" -DownloadModel -Model small

echo.
if errorlevel 1 (
    echo Model download failed. Check your internet connection and try again.
) else (
    echo Model download finished successfully.
)
pause
