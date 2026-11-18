"""Native Windows desktop launcher for PeakCut.

Run from the repository root with: python -m studio.desktop
The existing FastAPI app remains the source of truth; this module starts it locally
and displays the existing dashboard in a native Qt WebEngine window.
"""
from __future__ import annotations

import logging
import socket
import sys
import threading
import traceback
import urllib.error
import urllib.request
from pathlib import Path

from PySide6.QtCore import QUrl, Qt, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QMessageBox, QProgressBar, QToolBar, QVBoxLayout, QWidget
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView

from . import config

APP_NAME = "PeakCut Desktop"
BASE_URL = f"http://127.0.0.1:{config.PORT}"


def _port_is_open(host: str, port: int) -> bool:
    with socket.socket() as sock:
        sock.settimeout(0.25)
        return sock.connect_ex((host, port)) == 0


def _health_ok() -> bool:
    try:
        request = urllib.request.Request(f"{BASE_URL}/healthz", headers={"User-Agent": APP_NAME})
        with urllib.request.urlopen(request, timeout=1.5) as response:
            return 200 <= response.status < 400
    except (OSError, urllib.error.URLError):
        return False


class PeakCutWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1440, 920)
        self.setMinimumSize(960, 640)
        self._server_thread = None
        self._server_started_here = False
        self._server_error = None

        self.web = QWebEngineView(self)
        settings = self.web.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        self.web.setPage(QWebEnginePage(self.web))
        self.web.loadFinished.connect(self._page_loaded)

        self.status_label = QLabel("Starting PeakCut…")
        self.status_label.setObjectName("statusLabel")
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setMaximumHeight(3)
        self.progress.setTextVisible(False)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.web, 1)
        layout.addWidget(self.progress)
        layout.addWidget(self.status_label)
        self.setCentralWidget(central)

        toolbar = QToolBar("PeakCut")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        for label, callback in (
            ("Back", self.web.back),
            ("Forward", self.web.forward),
            ("Reload", self.web.reload),
            ("Dashboard", lambda: self.web.setUrl(QUrl(BASE_URL + "/app"))),
        ):
            action = QAction(label, self)
            action.triggered.connect(callback)
            toolbar.addAction(action)

        self.setStyleSheet("""
            QMainWindow { background: #101114; }
            QToolBar { background: #17191e; border: 0; spacing: 8px; padding: 8px; }
            QToolButton { color: #e7e9ee; background: #23262d; border: 0; border-radius: 6px; padding: 7px 12px; }
            QToolButton:hover { background: #30343d; }
            QLabel#statusLabel { color: #a9afba; background: #17191e; padding: 5px 10px; }
            QProgressBar { background: #17191e; border: 0; }
            QProgressBar::chunk { background: #a7f36b; }
        """)

        if _health_ok():
            self.status_label.setText("Connected to an already running PeakCut service.")
            self.web.setUrl(QUrl(BASE_URL + "/app"))
        elif _port_is_open("127.0.0.1", config.PORT):
            self._server_error = (
                f"Port {config.PORT} is already in use by another program. "
                "Close it or change PEAKCUT_PORT in your .env file."
            )
        else:
            self._start_server()

        self._poll = QTimer(self)
        self._poll.timeout.connect(self._check_server)
        self._poll.start(500)

    def _start_server(self):
        def run_server():
            try:
                # Uvicorn's bundled default dictConfig formatter can fail in a
                # frozen PyInstaller build if its formatter class is not resolved.
                # Use Python's plain logging setup and disable Uvicorn dictConfig.
                logging.basicConfig(
                    level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s",
                )
                import uvicorn
                from .server import app
                uvicorn.run(
                    app,
                    host="127.0.0.1",
                    port=config.PORT,
                    log_config=None,
                    log_level=None,
                    access_log=False,
                )
            except Exception as exc:
                details = traceback.format_exc()
                try:
                    log_path = Path(config.DATA_DIR) / "desktop-startup.log"
                    log_path.parent.mkdir(parents=True, exist_ok=True)
                    log_path.write_text(details, encoding="utf-8")
                    log_note = f"\\n\\nFull details saved to:\\n{log_path}"
                except Exception:
                    log_note = ""
                self._server_error = f"{type(exc).__name__}: {exc}{log_note}"

        self._server_started_here = True
        self._server_thread = threading.Thread(target=run_server, name="PeakCutServer", daemon=True)
        self._server_thread.start()
        self.status_label.setText("Launching the local PeakCut service…")

    def _check_server(self):
        if self._server_error:
            self._poll.stop()
            self.progress.hide()
            QMessageBox.critical(self, APP_NAME, self._server_error)
            self.status_label.setText("Could not start PeakCut.")
            return
        if _health_ok():
            self._poll.stop()
            self.progress.hide()
            self.status_label.setText("PeakCut is running locally. Your videos and settings stay on this PC.")
            self.web.setUrl(QUrl(BASE_URL + "/app"))

    def _page_loaded(self, ok):
        if ok:
            self.progress.hide()

    def closeEvent(self, event):  # noqa: N802
        self._poll.stop()
        # The server runs in a daemon thread in this process. Exiting the app ends it
        # and leaves the user's data untouched.
        event.accept()


def main():
    import os
    os.environ.setdefault("PEAKCUT_HOST", "127.0.0.1")
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("PeakCut")
    app.setStyle("Fusion")
    window = PeakCutWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
