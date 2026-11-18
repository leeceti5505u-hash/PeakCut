# PeakCut Desktop (Windows)

Native Windows shell around the existing PeakCut local server. It keeps the clipping engine and dashboard intact and displays the existing dashboard in a desktop window.

## Requirements
- Windows 10/11 x64
- Python 3.10+ (Python 3.12 recommended) for local builds
- FFmpeg on PATH (`winget install Gyan.FFmpeg`)

## Run from source
From the repository root:

```powershell
py -3.12 -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install --upgrade pip
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt -r desktop/requirements.txt
.\\.venv\\Scripts\\python.exe -m studio.desktop
```

The first start downloads the speech model (~480 MB) into PeakCut's data folder. The desktop window opens the local dashboard at `http://127.0.0.1:8765`.

## Build the Windows installer
Run `powershell -ExecutionPolicy Bypass -File desktop\\build-windows.ps1` from the repository root. It builds the app and creates:

```
dist\\PeakCut-Desktop-Setup.exe
```

The script uses Inno Setup 6 to create the installer. On GitHub, the **Build PeakCut Desktop (Windows)** workflow also creates this installer automatically; download it from the workflow run's Artifacts section.

## Data
For installed builds, keys, settings, videos and clips are stored under your Windows Local AppData folder, separate from the program files so reinstalling or uninstalling the app does not remove your personal PeakCut data. Source runs use PeakCut's normal local data folder. The service binds to 127.0.0.1 only.

FFmpeg remains an external requirement. The speech model is downloaded on first launch to avoid an oversized installer. Keep source checkouts in a short path such as `D:\\peakcut` to avoid Windows long-path issues with speech libraries.
