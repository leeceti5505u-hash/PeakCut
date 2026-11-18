"""Frozen-app bootstrap. Keep personal data outside the installation directory."""
import os
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    user_data = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))) / "PeakCut"
    os.environ.setdefault("PEAKCUT_DATA", str(user_data / "data"))
    os.environ.setdefault("PEAKCUT_STORAGE_FILE", str(user_data / "storage.json"))

from studio.desktop import main

if __name__ == "__main__":
    raise SystemExit(main())
