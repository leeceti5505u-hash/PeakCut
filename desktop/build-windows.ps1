param(
    [string]$Python = "py",
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)
$ErrorActionPreference = "Stop"
Set-Location $ProjectRoot

Write-Host "== PeakCut Desktop: Windows build ==" -ForegroundColor Cyan
if (-not (Get-Command $Python -ErrorAction SilentlyContinue)) {
    throw "Python launcher '$Python' was not found. Install Python 3.10+ and try again."
}

$venv = Join-Path $ProjectRoot ".venv-desktop"
if (-not (Test-Path $venv)) {
    & $Python -3.12 -m venv $venv
    if ($LASTEXITCODE -ne 0) { & $Python -3 -m venv $venv }
}
$venvPython = Join-Path $venv "Scripts\python.exe"
if (-not (Test-Path $venvPython)) { throw "Could not create the build virtual environment." }

& $venvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }
& $venvPython -m pip install -r requirements.txt -r desktop\requirements.txt
if ($LASTEXITCODE -ne 0) { throw "Installing requirements failed." }

& $venvPython -m PyInstaller --noconfirm --clean --windowed `
    --name "PeakCut Desktop" `
    --collect-all PySide6 `
    --collect-all sherpa_onnx `
    --collect-all uvicorn `
    --collect-all fastapi `
    --collect-all sqlalchemy `
    --add-data "web;web" `
    --add-data "studio\fonts;studio\fonts" `
    --add-data "studio;studio" `
    --hidden-import "studio.desktop" `
    --hidden-import "studio.server" `
    --hidden-import "sherpa_onnx" `
    --collect-submodules "studio" `
    desktop\entrypoint.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed." }

Write-Host "Building the installer with Inno Setup..." -ForegroundColor Cyan
$iscc = Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"
if (-not (Test-Path $iscc)) {
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        choco install innosetup --yes --no-progress
    }
}
if (-not (Test-Path $iscc)) { throw "Inno Setup 6 is required. Install it from https://jrsoftware.org/isinfo.php and rerun this script." }
& $iscc "desktop\PeakCutDesktop.iss"
if ($LASTEXITCODE -ne 0) { throw "Inno Setup compilation failed." }

Write-Host "Build complete: $ProjectRoot\dist\PeakCut-Desktop-Setup.exe" -ForegroundColor Green
Write-Host "FFmpeg is required on PATH. The speech model downloads on first launch."
