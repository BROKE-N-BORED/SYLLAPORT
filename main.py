"""Syllaport entry point.

Single instance (U27): a second launch asks the running app to come
forward instead of starting a second copy. The app opens on the
Dashboard; first run shows the setup checklist there.

Usage:
    python main.py [--data-dir DIR] [--smoke]

--data-dir points the data file somewhere else (used by tests and the
verify drive). --smoke opens the Dashboard, waits briefly, and exits 0
(used by the fresh-extract check).
"""

from __future__ import annotations

import argparse
import sys

from PySide6.QtCore import QByteArray, QTimer
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import QApplication

from syllaport import __app_name__, __version__, debuglog, style as style_mod
from syllaport.store import Store
from syllaport.windows import WindowManager

SERVER_NAME = "syllaport-single-instance"


def _ping_running_instance():
    """True when another Syllaport is already running (and was told to
    come forward)."""
    sock = QLocalSocket()
    sock.connectToServer(SERVER_NAME)
    if not sock.waitForConnected(1000):
        return False
    sock.write(QByteArray(b"raise"))
    sock.waitForBytesWritten(1000)
    sock.disconnectFromServer()
    return True


class SingleInstanceServer(QLocalServer):
    """Listens for second launches and raises the Dashboard."""

    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self.manager = manager
        # A crashed run leaves its socket behind; clear it before listen.
        QLocalServer.removeServer(SERVER_NAME)
        self.newConnection.connect(self._on_connection)
        self.listen(SERVER_NAME)

    def _on_connection(self):
        sock = self.nextPendingConnection()
        if sock is not None:
            sock.readyRead.connect(lambda: sock.readAll())
            sock.disconnected.connect(sock.deleteLater)
        self.manager.show_window(0)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="syllaport")
    parser.add_argument("--data-dir", default=None,
                        help="Folder for the data file (default: app data)")
    parser.add_argument("--smoke", action="store_true",
                        help="Open, wait briefly, exit 0 (extract check)")
    args = parser.parse_args(argv)

    app = QApplication(sys.argv[:1])
    app.setApplicationName(__app_name__)
    app.setOrganizationName("BrokeNBored")
    app.setApplicationVersion(__version__)

    if _ping_running_instance():
        return 0

    store = Store(args.data_dir)
    debuglog.setup_logging(str(store.log_path))
    debuglog.log().info("Syllaport %s starting", __version__)
    style_mod.apply_presets(app, store.data.get("presets", {}))

    manager = WindowManager(store, app)
    server = SingleInstanceServer(manager)
    manager.show_window(0)

    if args.smoke:
        QTimer.singleShot(1500, app.quit)
    try:
        return app.exec()
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
