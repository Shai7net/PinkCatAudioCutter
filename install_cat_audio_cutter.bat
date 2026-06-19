@echo off
setlocal
cd /d "%~dp0"

set "APP_NAME=Pink Cat Audio Cutter"
set "SOURCE_DIR=%~dp0PinkCatAudioCutter"
set "TARGET_DIR=%LocalAppData%\Programs\PinkCatAudioCutter"
set "EXE_PATH=%TARGET_DIR%\PinkCatAudioCutter.exe"
set "DESKTOP_SHORTCUT=%UserProfile%\Desktop\Pink Cat Audio Cutter.lnk"
set "STARTMENU_DIR=%AppData%\Microsoft\Windows\Start Menu\Programs"
set "STARTMENU_SHORTCUT=%STARTMENU_DIR%\Pink Cat Audio Cutter.lnk"

if not exist "%SOURCE_DIR%\PinkCatAudioCutter.exe" (
    echo Could not find packaged app folder: "%SOURCE_DIR%"
    pause
    exit /b 1
)

if exist "%TARGET_DIR%" rmdir /s /q "%TARGET_DIR%"
mkdir "%TARGET_DIR%"
xcopy "%SOURCE_DIR%\*" "%TARGET_DIR%\" /E /I /Y >nul

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$desktop = $ws.CreateShortcut('%DESKTOP_SHORTCUT%'); " ^
  "$desktop.TargetPath = '%EXE_PATH%'; " ^
  "$desktop.WorkingDirectory = '%TARGET_DIR%'; " ^
  "$desktop.IconLocation = '%EXE_PATH%,0'; " ^
  "$desktop.Save(); " ^
  "$start = $ws.CreateShortcut('%STARTMENU_SHORTCUT%'); " ^
  "$start.TargetPath = '%EXE_PATH%'; " ^
  "$start.WorkingDirectory = '%TARGET_DIR%'; " ^
  "$start.IconLocation = '%EXE_PATH%,0'; " ^
  "$start.Save()"

echo.
echo %APP_NAME% installed successfully.
echo Installed to: %TARGET_DIR%
echo You can now open it from the desktop shortcut.
pause
