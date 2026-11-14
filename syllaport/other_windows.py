"""The other six windows.

Settings, Account, and Backup are real in R2 (presets, profile, and
backup actions all work). Schedule, Notebook, and Work Log open with
their real chrome plus honest states: they say plainly what arrives in
R6/R8/R9, show the real data they already have, and offer the real
actions that exist today. No fake data, no dead buttons.
"""

from __future__ import annotations

import os
from datetime import datetime

from PySide6.QtWidgets import (QCheckBox, QLabel, QListWidget, QListWidgetItem,
                               QPushButton, QVBoxLayout, QWidget)

from syllaport import data as data_mod
from syllaport import dialogs as dialogs_mod
from syllaport.windows import Card, SyllaportWindow, make_label


def _classes_card(store):
    """Read-only list of the user's classes (real data, shared helper)."""
    card = Card(store, radius=16)
    card.layout().addWidget(make_label("Your classes", "cardtitle"))
    courses = store.data.get("courses", [])
    if not courses:
        card.layout().addWidget(make_label(
            "No classes yet. Pick your first class in Courses.",
            "muted", wrap=True))
    else:
        for course in courses:
            card.layout().addWidget(make_label(
                "%s, %s" % (course["title"], course["source_name"]),
                wrap=True))
    return card


class ScheduleWindow(SyllaportWindow):
    key = "schedule"

    def build_content(self):
        self.content_layout.addWidget(make_label("Schedule", "title"))
        self.holder = QWidget()
        self.holder_layout = QVBoxLayout(self.holder)
        self.holder_layout.setContentsMargins(0, 0, 0, 0)
        self.holder_layout.setSpacing(16)
        self.content_layout.addWidget(self.holder, 1)
        self.refresh()

    def refresh(self):
        super().refresh()
        if not hasattr(self, "holder"):
            return
        while self.holder_layout.count():
            item = self.holder_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        card = Card(self.store, radius=20)
        card.layout().addWidget(make_label("Your schedule builder "
                                           "arrives in R6.", "cardtitle"))
        card.layout().addWidget(make_label(
            "R6 lets you build your own week: pick study days, set "
            "lanes, and watch projected finish dates move before you "
            "apply. What already works today is your start date, "
            "below, and your classes.", wrap=True))
        start = data_mod.term_start(self.store.data)
        if start is not None:
            card.layout().addWidget(make_label(
                "Your plan starts %s." % start.isoformat()))
        else:
            card.layout().addWidget(make_label(
                "Start date not set.", "muted"))
        button = QPushButton("Choose start date")
        button.clicked.connect(self._choose_date)
        card.layout().addWidget(button)
        self.holder_layout.addWidget(card)
        self.holder_layout.addWidget(_classes_card(self.store))
        self.holder_layout.addStretch(1)

    def _choose_date(self):
        dialogs_mod.StartDateDialog(self.store, self).exec()
        self.refresh()


class NotebookWindow(SyllaportWindow):
    key = "notebook"

    def build_content(self):
        self.content_layout.addWidget(make_label("Notebook", "title"))
        card = Card(self.store, radius=20)
        card.layout().addWidget(make_label("Your notebooks arrive "
                                           "in R8.", "cardtitle"))
        card.layout().addWidget(make_label(
            "R8 gives you one notebook per class plus a general one, "
            "with save and restore. Notes you write then export to "
            "Markdown from the File menu, which already works.",
            wrap=True))
        self.content_layout.addWidget(card)
        self.classes_holder = QWidget()
        self.classes_layout = QVBoxLayout(self.classes_holder)
        self.classes_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.addWidget(self.classes_holder, 1)
        self.refresh()

    def refresh(self):
        super().refresh()
        if not hasattr(self, "classes_holder"):
            return
        while self.classes_layout.count():
            item = self.classes_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.classes_layout.addWidget(_classes_card(self.store))
        self.classes_layout.addStretch(1)


class WorkLogWindow(SyllaportWindow):
    key = "worklog"

    def build_content(self):
        self.content_layout.addWidget(make_label("Work Log", "title"))
        self.holder = QWidget()
        self.holder_layout = QVBoxLayout(self.holder)
        self.holder_layout.setContentsMargins(0, 0, 0, 0)
        self.holder_layout.setSpacing(16)
        self.content_layout.addWidget(self.holder, 1)
        self.refresh()

    def refresh(self):
        super().refresh()
        if not hasattr(self, "holder"):
            return
        while self.holder_layout.count():
            item = self.holder_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        card = Card(self.store, radius=20)
        card.layout().addWidget(make_label("Your work log arrives "
                                           "in R9.", "cardtitle"))
        card.layout().addWidget(make_label(
            "R9 gives you the log form, filters, and entries with edit "
            "and safe delete. The totals below are already real: they "
            "read from your data today.", wrap=True))
        data = self.store.data
        totals = Card(self.store, radius=16)
        totals.layout().addWidget(make_label("Totals so far", "cardtitle"))
        totals.layout().addWidget(make_label(
            "Time in: %s" % data_mod.fmt_minutes(
                data_mod.minutes_total(data))))
        totals.layout().addWidget(make_label(
            "This week: %s" % data_mod.fmt_minutes(
                data_mod.minutes_this_week(data))))
        totals.layout().addWidget(make_label(
            "Study sessions logged: %d" % len(data.get("sessions", []))))
        totals.layout().addWidget(make_label(
            "Day streak: %d" % data_mod.streak(data)))
        totals.layout().addWidget(make_label(
            "Units finished: %d" % data_mod.count_completed_units(data)))
        self.holder_layout.addWidget(card)
        self.holder_layout.addWidget(totals)
        self.holder_layout.addStretch(1)


class AccountWindow(SyllaportWindow):
    key = "account"

    def build_content(self):
        self.content_layout.addWidget(make_label("Account", "title"))
        self.holder = QWidget()
        self.holder_layout = QVBoxLayout(self.holder)
        self.holder_layout.setContentsMargins(0, 0, 0, 0)
        self.holder_layout.setSpacing(16)
        self.content_layout.addWidget(self.holder, 1)
        self.refresh()

    def refresh(self):
        super().refresh()
        if not hasattr(self, "holder"):
            return
        while self.holder_layout.count():
            item = self.holder_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        profile = self.store.data.get("profile") or {}
        name = profile.get("name") or "Not set"
        start = profile.get("start_date") or "Not set"
        card = Card(self.store, radius=20)
        card.layout().addWidget(make_label("Your profile", "cardtitle"))
        card.layout().addWidget(make_label("Name: %s" % name))
        card.layout().addWidget(make_label("Started: %s" % start))
        card.layout().addWidget(make_label(
            "Classes picked: %d"
            % len(self.store.data.get("courses", []))))
        card.layout().addWidget(make_label(
            "This profile lives on this computer only. Full accounts "
            "with sign in come in R3.", "muted", wrap=True))
        button = QPushButton("Edit profile")
        button.clicked.connect(self._edit_profile)
        card.layout().addWidget(button)
        self.holder_layout.addWidget(card)
        self.holder_layout.addStretch(1)

    def _edit_profile(self):
        dialogs_mod.ProfileDialog(self.store, self).exec()
        self.refresh()


class BackupWindow(SyllaportWindow):
    key = "backup"

    def build_content(self):
        self.content_layout.addWidget(make_label("Backup", "title"))
        card = Card(self.store, radius=20)
        card.layout().addWidget(make_label("Your data, safe", "cardtitle"))
        card.layout().addWidget(make_label(
            "Syllaport saves your data to one file and keeps the last "
            "five automatic backups beside it. Every save is atomic, "
            "so a crash mid-save never corrupts your data.", wrap=True))
        row = QWidget()
        row_layout = QVBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        self.backup_button = QPushButton("Back up now")
        self.backup_button.clicked.connect(
            lambda: (self.manager.backup_now_action(), self.refresh()))
        self.download_button = QPushButton("Download a copy")
        self.download_button.clicked.connect(
            lambda: (self.manager.download_backup_action(), self.refresh()))
        self.restore_button = QPushButton("Restore from a backup")
        self.restore_button.clicked.connect(
            lambda: (self.manager.restore_backup_action(), self.refresh()))
        row_layout.addWidget(self.backup_button)
        row_layout.addWidget(self.download_button)
        row_layout.addWidget(self.restore_button)
        card.layout().addWidget(row)
        self.content_layout.addWidget(card)
        self.list_card = Card(self.store, radius=16)
        self.list_card.layout().addWidget(
            make_label("Automatic backups", "cardtitle"))
        self.backup_list = QListWidget()
        self.list_card.layout().addWidget(self.backup_list)
        self.content_layout.addWidget(self.list_card, 1)
        self.refresh()

    def refresh(self):
        super().refresh()
        if not hasattr(self, "backup_list"):
            return
        self.backup_list.clear()
        backups = data_mod.list_backups(str(self.store.path))
        if not backups:
            self.backup_list.addItem(QListWidgetItem(
                "No automatic backups yet. Save something first."))
            return
        for filename, size, mtime in backups:
            when = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            self.backup_list.addItem(QListWidgetItem(
                "%s, %d bytes, %s" % (filename, size, when)))


class SettingsWindow(SyllaportWindow):
    key = "settings"

    def build_content(self):
        self.content_layout.addWidget(make_label("Settings", "title"))
        study = Card(self.store, radius=16)
        study.layout().addWidget(make_label("Your study", "cardtitle"))
        self.pace_label = QLabel("")
        study.layout().addWidget(self.pace_label)
        pace_button = QPushButton("Change pace")
        pace_button.clicked.connect(self._change_pace)
        study.layout().addWidget(pace_button)
        self.date_label = QLabel("")
        study.layout().addWidget(self.date_label)
        date_button = QPushButton("Change start date")
        date_button.clicked.connect(self._change_date)
        study.layout().addWidget(date_button)
        self.content_layout.addWidget(study)

        presets = Card(self.store, radius=16)
        presets.layout().addWidget(make_label("Presets", "cardtitle"))
        presets.layout().addWidget(make_label(
            "One tap each. They apply at once and stay on until you "
            "turn them off.", "muted", wrap=True))
        self.preset_boxes = {}
        for name, label, detail in (
                ("larger_text", "Larger text",
                 "Bigger text everywhere in the app."),
                ("reduced_motion", "Reduced motion",
                 "No animation. State changes still happen, instantly."),
                ("high_contrast", "High contrast",
                 "Black text on white surfaces, stronger borders.")):
            box = QCheckBox(label)
            box.stateChanged.connect(
                lambda _state, n=name: self._toggle_preset(n))
            presets.layout().addWidget(box)
            presets.layout().addWidget(make_label(detail, "muted",
                                                  wrap=True))
            self.preset_boxes[name] = box
        self.content_layout.addWidget(presets)

        setup = Card(self.store, radius=16)
        setup.layout().addWidget(make_label("Setup", "cardtitle"))
        self.setup_label = QLabel("")
        self.setup_label.setWordWrap(True)
        setup.layout().addWidget(self.setup_label)
        self.setup_button = QPushButton("Show the setup checklist again")
        self.setup_button.clicked.connect(self._reopen_checklist)
        setup.layout().addWidget(self.setup_button)
        self.content_layout.addWidget(setup)
        self.content_layout.addStretch(1)
        self.refresh()

    def _toggle_preset(self, name):
        # The checkbox already shows the new state; persist exactly that.
        box = self.preset_boxes[name]
        self.manager.set_preset(name, box.isChecked())

    def _change_pace(self):
        dialogs_mod.PaceDialog(self.store, self).exec()
        self.refresh()

    def _change_date(self):
        dialogs_mod.StartDateDialog(self.store, self).exec()
        self.refresh()

    def _reopen_checklist(self):
        self.store.reopen_checklist()
        self.manager.show_window(0)
        self.set_status("Setup checklist is back on the Dashboard.")

    def refresh(self):
        super().refresh()
        if not hasattr(self, "pace_label"):
            return
        pace = data_mod.seed_pace(self.store.data)
        self.pace_label.setText("Weekly pace: %.1f units a week." % pace)
        start = data_mod.term_start(self.store.data)
        if start is not None:
            self.date_label.setText("Start date: %s." % start.isoformat())
        else:
            self.date_label.setText("Start date: Not set.")
        for name, box in self.preset_boxes.items():
            box.blockSignals(True)
            box.setChecked(self.store.preset(name))
            box.blockSignals(False)
        from syllaport import checklist as checklist_mod
        if checklist_mod.is_complete(self.store.data):
            self.setup_label.setText("Setup is complete. All 5 steps done.")
            self.setup_button.setText("Show the setup checklist again")
        elif checklist_mod.is_dismissed(self.store.data):
            done = checklist_mod.done_count(self.store.data)
            self.setup_label.setText(
                "Setup is %d of 5 steps done and hidden." % done)
            self.setup_button.setText("Show the setup checklist again")
        else:
            done = checklist_mod.done_count(self.store.data)
            self.setup_label.setText(
                "Setup is %d of 5 steps done, on the Dashboard." % done)
            self.setup_button.setText("Go to the setup checklist")
