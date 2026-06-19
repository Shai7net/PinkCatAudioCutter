$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$distRoot = Join-Path $projectRoot "dist"
$buildRoot = Join-Path $projectRoot "build"
$releaseRoot = Join-Path $projectRoot "release"
$appName = "PinkCatAudioCutter"
$appDist = Join-Path $distRoot $appName
$packageRoot = Join-Path $releaseRoot $appName

$ffmpegDir = "C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin"
$ffmpegExe = Join-Path $ffmpegDir "ffmpeg.exe"
$ffprobeExe = Join-Path $ffmpegDir "ffprobe.exe"

if (!(Test-Path $ffmpegExe) -or !(Test-Path $ffprobeExe)) {
    throw "ffmpeg or ffprobe not found in expected path: $ffmpegDir"
}

$optionalCollectArgs = @()
python -c "import openai" *> $null
if ($LASTEXITCODE -eq 0) {
    $optionalCollectArgs += @("--collect-all", "openai")
} else {
    Write-Warning "Python package 'openai' is not installed in the build environment. Azure Whisper will use the built-in HTTP fallback unless the package is installed before packaging."
}

if (Test-Path $buildRoot) { Remove-Item $buildRoot -Recurse -Force }
if (Test-Path $distRoot) { Remove-Item $distRoot -Recurse -Force }
if (Test-Path $releaseRoot) { Remove-Item $releaseRoot -Recurse -Force }

python -m PyInstaller `
    --noconfirm `
    --clean `
    --onedir `
    --windowed `
    --name $appName `
    --add-binary "${ffmpegExe};." `
    --add-binary "${ffprobeExe};." `
    --collect-all pyautogui `
    --collect-all pyscreeze `
    --collect-all pygetwindow `
    --collect-all pymsgbox `
    --collect-all mouseinfo `
    --collect-all pytweening `
    --collect-all faster_whisper `
    --collect-all ctranslate2 `
    --collect-all tokenizers `
    @optionalCollectArgs `
    --hidden-import pyperclip `
    --hidden-import tkinter `
    --distpath $distRoot `
    --workpath $buildRoot `
    "$projectRoot\cat_audio_cutter.pyw"

New-Item -ItemType Directory -Path $packageRoot | Out-Null
Copy-Item $appDist\* $packageRoot -Recurse -Force
Copy-Item "$projectRoot\README.md" "$releaseRoot\README.txt" -Force
Copy-Item "$projectRoot\install_cat_audio_cutter.bat" "$releaseRoot\install_cat_audio_cutter.bat" -Force

Write-Host ""
Write-Host "Release package ready at: $releaseRoot" -ForegroundColor Green
Write-Host "App folder: $packageRoot" -ForegroundColor Green
