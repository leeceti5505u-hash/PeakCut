# PeakCut Desktop (Windows)

Native Windows shell around the existing PeakCut local server. It keeps the clipping engine and dashboard intact and displays the existing dashboard in a desktop window.

## Requirements
- Windows 10/11 x64
- Python 3.10+ (Python 3.12 recommended)
- FFmpeg on PATH (`winget install Gyan.FFmpeg`)

## Run from source
From the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r desktop/requirements.txt
.\.venv\Scripts\python.exe -m studio.desktop
```

The first start downloads the speech model (~480 MB) into PeakCut's data folder. The desktop window opens the local dashboard at `http://127.0.0.1:8765`.

## Build
Run `powershell -ExecutionPolicy Bypass -File desktop\build-windows.ps1` from the repository root. The build is placed in `dist\PeakCut Desktop\`. Run `desktop\install-shortcut.ps1` to create Desktop and Start Menu shortcuts.

The app and Python runtime are bundled. FFmpeg is an external requirement and the speech model is downloaded on first run to avoid a very large installer.

## Data
Keys, settings, videos and clips remain in PeakCut's normal local data folder. The service binds to 127.0.0.1 only. Closing the desktop app ends its locally launched server process. Keep the project in a short path such as `D:\peakcut` to avoid Windows long-path issues with speech libraries.
