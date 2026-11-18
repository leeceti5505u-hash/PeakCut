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

Write-Host "Build complete: $ProjectRoot\dist\PeakCut Desktop" -ForegroundColor Green
Write-Host "FFmpeg is required on PATH. The speech model downloads on first launch."
