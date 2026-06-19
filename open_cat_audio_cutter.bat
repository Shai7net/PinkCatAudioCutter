@echo off
setlocal
cd /d "%~dp0"

if exist "%~dp0launch_cat_audio_cutter_bundled.ps1" (
    start "" powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0launch_cat_audio_cutter_bundled.ps1"
    exit /b
)

set "APP_EXE=%~dp0dist\PinkCatAudioCutter\PinkCatAudioCutter.exe"

if not exist "%APP_EXE%" (
    echo App launcher was not found:
    echo %APP_EXE%
    pause
    exit /b 1
)

start "" "%APP_EXE%"
exit /b
