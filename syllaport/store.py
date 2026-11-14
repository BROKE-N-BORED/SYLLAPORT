"""Store: the data file plus change signals (Qt side of data.py).

One Store per app run. Windows read store.data and call store.save()
after changing it; save() writes atomically and emits data_changed, so
every open window refreshes. Data lives in the platform app-data
folder (Windows: %APPDATA%/Syllaport, Linux: ~/.local/share/Syllaport)
via QStandardPaths, so no path is ever hardcoded per platform.
"""

from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import QObject, QStandardPaths, Signal

from syllaport import data as data_mod


def default_data_dir():
    """The platform app-data folder for Syllaport (pathlib, cross-platform)."""
    base = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    if not base:
        base = str(Path.home() / ".syllaport")
    return Path(base)


class Store(QObject):
    data_changed = Signal()

    def __init__(self, data_dir=None, parent=None):
        super().__init__(parent)
        self.data_dir = Path(data_dir) if data_dir else default_data_dir()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.data_dir / "data.json"
        self.log_path = self.data_dir / "syllaport.log"
        self.data = data_mod.load_data(str(self.path))

    def save(self):
        """Write the data file and tell every window to refresh."""
        data_mod.save_data(self.data, str(self.path))
        self.data_changed.emit()

    def replace_data(self, new_data):
        """Swap in a whole new data dict (restore) and persist it."""
        self.data = data_mod.normalize_data(new_data)
        self.save()

    # -- checklist ------------------------------------------------------
    def complete_step(self, step):
        from syllaport import checklist as checklist_mod
        if checklist_mod.mark_done(self.data, step):
            self.save()
            return True
        return False

    def dismiss_checklist(self):
        self.data["checklist_dismissed"] = True
        self.save()

    def reopen_checklist(self):
        self.data["checklist_dismissed"] = False
        self.save()

    # -- presets --------------------------------------------------------
    def set_preset(self, name, value):
        presets = self.data.setdefault("presets", {})
        presets[name] = bool(value)
        self.save()

    def preset(self, name):
        return bool(self.data.get("presets", {}).get(name, False))
