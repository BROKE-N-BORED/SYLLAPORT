"""Window framework (Design Spec section 6).

One function, one window (U1). Every window carries the same chrome:
a real menu bar (U38), the eight-entry left nav rail, and a status bar
with a light plus small status text (U16). Geometry is remembered via
QSettings (U5). The View menu mirrors the rail and the Ctrl+1..8
shortcuts, so there are three ways to every window, all consistent.

The Presets submenu under View is an R2 addition (entry 015, R2 brief):
the same three toggles also live in the Settings window, and both stay
in sync through the store.
"""

from __future__ import annotations

import json
import os
import shutil

from PySide6.QtCore import QEvent, QSettings, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QShortcut, QKeySequence
from PySide6.QtWidgets import (QApplication, QDialog, QFileDialog, QFrame,
                               QHBoxLayout, QLabel, QMainWindow, QMessageBox,
                               QPushButton, QScrollArea, QStatusBar, QTextEdit,
                               QVBoxLayout, QWidget)

from syllaport import data as data_mod
from syllaport import debuglog
from syllaport import style as style_mod
from syllaport.dialogs import confirm_action

ORG = "BrokeNBored"
APP = "Syllaport"

WINDOW_DEFS = [
    ("dashboard", "Dashboard", "DA"),
    ("courses", "Courses", "CO"),
    ("schedule", "Schedule", "SC"),
    ("notebook", "Notebook", "NO"),
    ("worklog", "Work Log", "WL"),
    ("account", "Account", "AC"),
    ("backup", "Backup", "BA"),
    ("settings", "Settings", "SE"),
]

WINDOW_INDEX = {key: i for i, (key, _t, _a) in enumerate(WINDOW_DEFS)}

DEFAULT_WIDTH = 1100
DEFAULT_HEIGHT = 700


def make_label(text, role=None, wrap=False):
    label = QLabel(text)
    if role:
        label.setProperty("role", role)
    if wrap:
        label.setWordWrap(True)
    return label


class Card(QFrame):
    """Hard-shadow card (Spec section 1.3): 2 px ink border, 4 px hard
    offset shadow in ink, 0 blur. Painted by hand because Qt
    stylesheets have no box-shadow."""

    def __init__(self, store=None, radius=16, parent=None):
        super().__init__(parent)
        self._store = store
        self._radius = radius
        # Scoped to Card only: an unscoped "background: transparent;"
        # cascades to every child widget and wipes button backgrounds
        # (found by screenshot: hero buttons rendered invisible).
        self.setStyleSheet("Card { background: transparent; }")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

    def paintEvent(self, event):
        high_contrast = bool(
            self._store and self._store.preset("high_contrast"))
        ink = QColor(style_mod.HC_INK if high_contrast else style_mod.INK)
        card = QColor(style_mod.HC_CARD if high_contrast else style_mod.CARD)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(1, 1, -5, -5)
        painter.setPen(Qt.NoPen)
        painter.setBrush(ink)
        painter.drawRoundedRect(rect.translated(4, 4), self._radius,
                                self._radius)
        painter.setBrush(card)
        painter.setPen(QPen(ink, 2))
        painter.drawRoundedRect(rect, self._radius, self._radius)


class SyllaportWindow(QMainWindow):
    """Base window: menu bar, rail, status bar, geometry memory."""

    key = "dashboard"

    def __init__(self, store, manager, parent=None):
        super().__init__(parent)
        self.store = store
        self.manager = manager
        self.view_actions = []
        self.preset_actions = {}
        self._rail_current_index = None
        title = WINDOW_DEFS[WINDOW_INDEX[self.key]][1]
        self.setWindowTitle("Syllaport, %s" % title)
        self.setMinimumSize(900, 560)
        self._build_chrome()
        self._restore_geometry()

    # -- chrome ---------------------------------------------------------
    def _build_chrome(self):
        central = QWidget()
        self._central_layout = QHBoxLayout(central)
        self._central_layout.setContentsMargins(0, 0, 0, 0)
        self._central_layout.setSpacing(0)
        self._build_rail()
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(16)
        # Every window's content scrolls: without this, a window whose
        # cards are taller than the window squashes them until labels
        # overlap buttons (Settings proved it by screenshot). The
        # scroll area gives each card its full size hint instead.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.content)
        self._central_layout.addWidget(self.rail, 0)
        self._central_layout.addWidget(scroll, 1)
        self.setCentralWidget(central)
        self._build_status_bar()
        self._build_menu_bar()
        self.build_content()

    def _build_rail(self):
        self.rail = QFrame()
        self.rail.setObjectName("rail")
        self.rail.setFixedWidth(200)
        rail_layout = QVBoxLayout(self.rail)
        rail_layout.setContentsMargins(8, 12, 8, 12)
        rail_layout.setSpacing(4)
        brand = QLabel("Syllaport")
        brand.setProperty("role", "cardtitle")
        brand.setStyleSheet("color: #f7f1e3; padding: 4px 8px;")
        rail_layout.addWidget(brand)
        sub = QLabel("Free university workstation")
        sub.setProperty("role", "small")
        sub.setStyleSheet("color: #f7f1e3; padding: 0px 8px 8px 8px;")
        sub.setWordWrap(True)
        rail_layout.addWidget(sub)
        self.rail_buttons = []
        for index, (key, title, abbr) in enumerate(WINDOW_DEFS):
            button = QPushButton(title)
            button.setProperty("role", "rail")
            button.setToolTip(title)
            button.clicked.connect(
                lambda _checked=False, i=index: self.manager.show_window(i))
            self.rail_buttons.append(button)
            rail_layout.addWidget(button)
        rail_layout.addStretch(1)
        self.rail_toggle = QPushButton("<<")
        self.rail_toggle.setProperty("role", "rail")
        self.rail_toggle.setToolTip("Collapse the side bar")
        self.rail_toggle.clicked.connect(self.manager.toggle_rail)
        rail_layout.addWidget(self.rail_toggle)
        self.rail_collapsed = False

    def _build_status_bar(self):
        bar = QStatusBar()
        self.status_light = QLabel()
        self.status_light.setFixedSize(12, 12)
        self.status_light.setStyleSheet(
            "background: #b6e61e; border: 2px solid #141414; "
            "border-radius: 6px;")
        self.status_text = QLabel("Ready")
        bar.addWidget(self.status_light)
        bar.addWidget(self.status_text, 1)
        self.setStatusBar(bar)

    def set_status(self, text):
        self.status_text.setText(text)

    # -- menu bar (Spec section 6.1) ------------------------------------
    def _build_menu_bar(self):
        bar = self.menuBar()
        manager = self.manager
        file_menu = bar.addMenu("&File")
        file_menu.addAction("Backup Now",
                            manager.backup_now_action)
        file_menu.addAction("Download Backup...",
                            manager.download_backup_action)
        file_menu.addAction("Restore from Backup...",
                            manager.restore_backup_action)
        file_menu.addSeparator()
        file_menu.addAction("Export Notes (.md)",
                            manager.export_notes_action)
        file_menu.addAction("Export Work Log (.csv)",
                            manager.export_log_action)
        file_menu.addSeparator()
        file_menu.addAction("&Quit", manager.quit_action)

        view_menu = bar.addMenu("&View")
        mnemonics = ["&Dashboard", "&Courses", "&Schedule", "&Notebook",
                     "&Work Log", "&Account", "&Backup", "Se&ttings"]
        for index, label in enumerate(mnemonics):
            action = view_menu.addAction(label)
            action.setCheckable(True)
            action.triggered.connect(
                lambda _checked=False, i=index: manager.show_window(i))
            self.view_actions.append(action)
        presets_menu = view_menu.addMenu("&Presets")
        for name, label in (("larger_text", "&Larger text"),
                            ("reduced_motion", "&Reduced motion"),
                            ("high_contrast", "&High contrast")):
            action = presets_menu.addAction(label)
            action.setCheckable(True)
            action.setChecked(self.store.preset(name))
            action.triggered.connect(
                lambda checked=False, n=name: manager.set_preset(n, checked))
            self.preset_actions[name] = action

        tools_menu = bar.addMenu("&Tools")
        tools_menu.addAction("&Debug Report...",
                             manager.debug_report_action)

        help_menu = bar.addMenu("&Help")
        help_menu.addAction("&How to Use Index",
                            manager.how_to_action)
        help_menu.addAction("&About Syllaport",
                            manager.about_action)

    # -- geometry (U5) --------------------------------------------------
    def _settings(self):
        return QSettings(ORG, APP)

    def _restore_geometry(self):
        settings = self._settings()
        geometry = settings.value("geometry/%s" % self.key)
        if geometry is not None:
            self.restoreGeometry(geometry)
        else:
            self.resize(DEFAULT_WIDTH, DEFAULT_HEIGHT)
            screen = QApplication.primaryScreen()
            if screen is not None:
                rect = screen.availableGeometry()
                self.move((rect.width() - DEFAULT_WIDTH) // 2,
                          (rect.height() - DEFAULT_HEIGHT) // 2)
        collapsed = settings.value("rail/collapsed", False, type=bool)
        if collapsed:
            self.set_rail_collapsed(True)

    def set_rail_collapsed(self, collapsed):
        self.rail_collapsed = collapsed
        if collapsed:
            self.rail.setFixedWidth(56)
            for button, (_k, _t, abbr) in zip(self.rail_buttons,
                                              WINDOW_DEFS):
                button.setText(abbr)
            self.rail_toggle.setText(">>")
            self.rail_toggle.setToolTip("Expand the side bar")
        else:
            self.rail.setFixedWidth(200)
            for button, (_k, title, _a) in zip(self.rail_buttons,
                                               WINDOW_DEFS):
                button.setText(title)
            self.rail_toggle.setText("<<")
            self.rail_toggle.setToolTip("Collapse the side bar")

    def closeEvent(self, event):
        self._settings().setValue("geometry/%s" % self.key,
                                  self.saveGeometry())
        super().closeEvent(event)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.ActivationChange and self.isActiveWindow():
            self.manager.note_active(self)

    # -- content (subclasses fill this in) ------------------------------
    def build_content(self):
        pass

    def refresh(self):
        """Re-read the store and update what this window shows."""
        active = self.manager.active_index
        if active == self._rail_current_index:
            return
        previous = self._rail_current_index
        self._rail_current_index = active
        # Re-polish only the two buttons whose state changed; polishing
        # all eight on every refresh is the slowest thing this method
        # does (a full stylesheet re-evaluation per button).
        for index in (previous, active):
            if index is None:
                continue
            button = self.rail_buttons[index]
            button.setProperty("current", index == active)
            button.style().unpolish(button)
            button.style().polish(button)


class DebugReportDialog(QDialog):
    """Tools > Debug Report: real facts, copyable (U12)."""

    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Debug Report")
        self.setModal(True)
        self.resize(640, 480)
        layout = QVBoxLayout(self)
        heading = make_label("Debug Report", "title")
        layout.addWidget(heading)
        note = make_label(
            "Facts about this install. Syllaport holds no passwords, "
            "tokens, or keys, so there is nothing secret to scrub from "
            "this report.", "small", wrap=True)
        layout.addWidget(note)
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setPlainText(debuglog.build_report(
            str(store.path), str(store.log_path)))
        layout.addWidget(self.text)
        row = QHBoxLayout()
        copy_button = QPushButton("Copy report")
        copy_button.clicked.connect(self.copy_report)
        close_button = QPushButton("Close")
        close_button.setProperty("role", "quiet")
        close_button.clicked.connect(self.accept)
        row.addStretch(1)
        row.addWidget(copy_button)
        row.addWidget(close_button)
        layout.addLayout(row)

    def copy_report(self):
        QApplication.clipboard().setText(self.text.toPlainText())
        self.setWindowTitle("Debug Report, copied")


class AboutDialog(QDialog):
    """Help > About Syllaport."""

    def __init__(self, parent=None):
        super().__init__(parent)
        from syllaport import __version__
        self.setWindowTitle("About Syllaport")
        self.setModal(True)
        layout = QVBoxLayout(self)
        layout.addWidget(make_label("Syllaport", "title"))
        layout.addWidget(make_label(
            "Free university workstation, version %s." % __version__,
            wrap=True))
        layout.addWidget(make_label(
            "Pick free classes from a verified catalog, build your own "
            "schedule, and track your pace, notes, and progress. "
            "Everything lives on this computer.", wrap=True))
        layout.addWidget(make_label(
            "Syllaport never asks for or stores any course password. "
            "You sign in on the provider's own site.", wrap=True))
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)


class WindowManager:
    """Owns the eight windows, the menu actions, and window switching."""

    def __init__(self, store, app):
        self.store = store
        self.app = app
        self.windows = []
        self.active_index = 0
        self.how_to_window = None
        self._applied_presets = None
        self._create_windows()
        self._create_shortcuts()
        store.data_changed.connect(self.on_data_changed)

    def _create_windows(self):
        # Imported here: the window modules import this module for the base.
        from syllaport import courses as courses_mod
        from syllaport import dashboard as dashboard_mod
        from syllaport import other_windows as other_mod
        classes = [
            dashboard_mod.DashboardWindow,
            courses_mod.CoursesWindow,
            other_mod.ScheduleWindow,
            other_mod.NotebookWindow,
            other_mod.WorkLogWindow,
            other_mod.AccountWindow,
            other_mod.BackupWindow,
            other_mod.SettingsWindow,
        ]
        for cls in classes:
            self.windows.append(cls(self.store, self))

    def _create_shortcuts(self):
        home = self.windows[0]
        for index in range(8):
            shortcut = QShortcut(QKeySequence("Ctrl+%d" % (index + 1)), home)
            shortcut.setContext(Qt.ApplicationShortcut)
            shortcut.activated.connect(
                lambda i=index: self.show_window(i))

    # -- switching ------------------------------------------------------
    def show_window(self, index):
        window = self.windows[index]
        self.active_index = index
        window.show()
        window.raise_()
        window.activateWindow()
        window.refresh()
        self._sync_view_checks()
        self._sync_rail_current()

    def note_active(self, window):
        index = WINDOW_INDEX[window.key]
        if index != self.active_index:
            self.active_index = index
            self._sync_view_checks()
            self._sync_rail_current()

    def _sync_view_checks(self):
        for window in self.windows:
            for index, action in enumerate(window.view_actions):
                action.blockSignals(True)
                action.setChecked(index == self.active_index)
                action.blockSignals(False)

    def _sync_rail_current(self):
        for window in self.windows:
            window.refresh()

    def _sync_preset_checks(self):
        for window in self.windows:
            for name, action in window.preset_actions.items():
                action.blockSignals(True)
                action.setChecked(self.store.preset(name))
                action.blockSignals(False)

    def toggle_rail(self):
        collapsed = not self.windows[0].rail_collapsed
        QSettings(ORG, APP).setValue("rail/collapsed", collapsed)
        for window in self.windows:
            window.set_rail_collapsed(collapsed)

    def set_preset(self, name, value):
        self.store.set_preset(name, value)
        presets = dict(self.store.data.get("presets", {}))
        self._applied_presets = presets
        style_mod.apply_presets(self.app, presets)
        self._sync_preset_checks()
        debuglog.log().info("Preset %s set to %s", name, bool(value))

    def toggle_preset(self, name):
        self.set_preset(name, not self.store.preset(name))

    def refresh_all(self):
        for window in self.windows:
            window.refresh()

    def on_data_changed(self):
        # Re-apply the stylesheet only when the presets actually changed:
        # a full setStyleSheet re-polishes every widget, and most saves
        # do not touch presets.
        presets = dict(self.store.data.get("presets", {}))
        if presets != self._applied_presets:
            self._applied_presets = presets
            style_mod.apply_presets(self.app, presets)
            self._sync_preset_checks()
        self.refresh_all()
        active = self.windows[self.active_index]
        active.set_status("Saved")

    def active_window(self):
        return self.windows[self.active_index]

    # -- File menu actions (all real) -----------------------------------
    def backup_now_action(self):
        path = data_mod.backup_now(self.store.data, str(self.store.path))
        if path:
            self.active_window().set_status(
                "Backup saved: %s" % os.path.basename(path))
            debuglog.log().info("Manual backup: %s", path)
        else:
            self.active_window().set_status("Backup failed. Try again.")

    def download_backup_action(self):
        parent = self.active_window()
        filename, _ = QFileDialog.getSaveFileName(
            parent, "Download Backup", "syllaport-backup.json",
            "JSON files (*.json)")
        if not filename:
            return
        try:
            shutil.copyfile(str(self.store.path), filename)
            parent.set_status("Backup downloaded.")
        except OSError:
            parent.set_status("Could not write that file. Try another place.")

    def restore_backup_action(self):
        parent = self.active_window()
        filename, _ = QFileDialog.getOpenFileName(
            parent, "Restore from Backup", "", "JSON files (*.json)")
        if not filename:
            return
        try:
            with open(filename, "r", encoding="utf-8") as f:
                obj = json.load(f)
        except (OSError, ValueError):
            parent.set_status("That file could not be read.")
            return
        ok, reason = data_mod.validate_backup(obj)
        if not ok:
            parent.set_status(reason)
            return
        if not confirm_action(
                parent, "Restore from Backup",
                "This replaces all your Syllaport data with the backup "
                "file: your profile, classes, notes, and log. Your "
                "current data is kept as a backup first. Restore it?"):
            return
        data_mod.backup_now(self.store.data, str(self.store.path))
        self.store.replace_data(obj)
        self.refresh_all()
        parent.set_status("Backup restored.")
        debuglog.log().info("Restored from backup: %s", filename)

    def export_notes_action(self):
        parent = self.active_window()
        filename, _ = QFileDialog.getSaveFileName(
            parent, "Export Notes", "syllaport-notes.md",
            "Markdown files (*.md)")
        if not filename:
            return
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(data_mod.notes_markdown(self.store.data))
            parent.set_status("Notes exported.")
        except OSError:
            parent.set_status("Could not write that file. Try another place.")

    def export_log_action(self):
        parent = self.active_window()
        filename, _ = QFileDialog.getSaveFileName(
            parent, "Export Work Log", "syllaport-work-log.csv",
            "CSV files (*.csv)")
        if not filename:
            return
        try:
            with open(filename, "w", encoding="utf-8", newline="") as f:
                f.write(data_mod.log_csv(self.store.data))
            parent.set_status("Work log exported.")
        except OSError:
            parent.set_status("Could not write that file. Try another place.")

    def quit_action(self):
        for window in self.windows:
            window.close()
        QApplication.quit()

    # -- Tools and Help -------------------------------------------------
    def debug_report_action(self):
        dialog = DebugReportDialog(self.store, self.active_window())
        dialog.exec()

    def how_to_action(self):
        from syllaport import howto as howto_mod
        if self.how_to_window is None:
            self.how_to_window = howto_mod.HowToWindow(self.store, self)
        self.how_to_window.show()
        self.how_to_window.raise_()
        self.how_to_window.activateWindow()

    def about_action(self):
        dialog = AboutDialog(self.active_window())
        dialog.exec()
