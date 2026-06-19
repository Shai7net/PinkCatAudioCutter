@echo off
setlocal
cd /d "%~dp0"

set "PYTHONW=%LocalAppData%\Programs\Python\Python311\pythonw.exe"
if not exist "%PYTHONW%" set "PYTHONW=pythonw.exe"

if exist "%~dp0run_cat_audio_cutter_silent.vbs" (
    start "" wscript.exe "%~dp0run_cat_audio_cutter_silent.vbs"
) else (
    start "" "%PYTHONW%" "%~dp0cat_audio_cutter.pyw"
)
exit /b
