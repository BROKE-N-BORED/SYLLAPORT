"""Dialogs for the first-run steps and the teach-by-playing flows.

Every field explains itself in plain words directly underneath it
(U20). Nothing is selected by default (U6): pickers start unselected,
and dialogs prefill a stored value only when the user has set that
value before (the matching checklist step is done). Bad input gets a
friendly plain error in the dialog, never a dead end (U29).
"""

from __future__ import annotations

from datetime import date, timedelta

from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QComboBox, QDateEdit, QDialog, QDialogButtonBox,
                               QDoubleSpinBox, QGroupBox, QHBoxLayout, QLabel,
                               QLineEdit, QListWidget, QListWidgetItem,
                               QMessageBox, QPushButton, QRadioButton,
                               QVBoxLayout, QWidget)

from syllaport import catalog as catalog_mod
from syllaport import checklist as checklist_mod
from syllaport import data as data_mod


def field_row(label_text, widget, explanation):
    """Label above, widget, plain-words explanation underneath (U20)."""
    box = QWidget()
    layout = QVBoxLayout(box)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)
    label = QLabel(label_text)
    label.setProperty("role", "section")
    layout.addWidget(label)
    layout.addWidget(widget)
    note = QLabel(explanation)
    note.setProperty("role", "muted")
    note.setWordWrap(True)
    layout.addWidget(note)
    return box


def _next_monday(today=None):
    today = today or date.today()
    return today + timedelta(days=(7 - today.weekday()) % 7 or 7)


def confirm_action(parent, title, text):
    """Yes/No confirm. Destructive confirmations default to No (U23)."""
    box = QMessageBox(parent)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    box.setDefaultButton(QMessageBox.No)
    box.setEscapeButton(QMessageBox.No)
    return box.exec() == QMessageBox.Yes


class _BaseDialog(QDialog):
    """Dialog with a title, a body, and an inline message line (U29)."""

    def __init__(self, store, title, parent=None):
        super().__init__(parent)
        self.store = store
        self.setWindowTitle(title)
        self.setModal(True)
        self.body = QVBoxLayout(self)
        heading = QLabel(title)
        heading.setProperty("role", "title")
        self.body.addWidget(heading)
        self.message = QLabel("")
        self.message.setProperty("role", "small")
        self.message.setWordWrap(True)
        self.message.hide()
        self.body.addWidget(self.message)

    def say(self, text):
        """Show a friendly plain message inside the dialog (U29)."""
        self.message.setText(text)
        self.message.show()

    def clear_message(self):
        self.message.setText("")
        self.message.hide()


class ProfileDialog(_BaseDialog):
    """Checklist step 1: create your local profile.

    Name plus the day you started with Syllaport. This is a lightweight
    local profile; full accounts with sign in come in R3. The profile
    start date is not the study start date (step 4): the first says
    when you joined, the second says when your first study week begins.
    """

    def __init__(self, store, parent=None):
        super().__init__(store, "Create your profile", parent)
        done_before = checklist_mod.checklist_state(store.data).get("profile")
        profile = store.data.get("profile") or {}
        self.name_edit = QLineEdit()
        if done_before:
            self.name_edit.setText(profile.get("name", ""))
        self.body.addWidget(field_row(
            "Your name", self.name_edit,
            "What Syllaport calls you. It stays on this computer."))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        if done_before and profile.get("start_date"):
            try:
                self.date_edit.setDate(date.fromisoformat(
                    profile["start_date"]))
            except ValueError:
                self.date_edit.setDate(date.today())
        else:
            self.date_edit.setDate(date.today())
        self.body.addWidget(field_row(
            "Start date", self.date_edit,
            "The day you started with Syllaport. Your study plan can "
            "start on a different day; that is step 4."))
        buttons = QDialogButtonBox(QDialogButtonBox.Save
                                   | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        self.body.addWidget(buttons)

    def save(self):
        name = self.name_edit.text().strip()
        if not name:
            self.say("Give your profile a name first. Any name you like.")
            self.name_edit.setFocus()
            return
        self.store.data["profile"] = {
            "name": name,
            "start_date": self.date_edit.date().toPython().isoformat(),
        }
        self.store.save()
        self.store.complete_step("profile")
        self.accept()


class PaceDialog(_BaseDialog):
    """Checklist step 3: set your weekly pace."""

    CHOICES = [
        (0.5, "Half a unit a week, a slow and steady start"),
        (1.0, "One unit a week, a calm pace"),
        (2.0, "Two units a week, a steady push"),
        (3.0, "Three units a week, a fast pace"),
    ]

    def __init__(self, store, parent=None):
        super().__init__(store, "Set your weekly pace", parent)
        done_before = checklist_mod.checklist_state(store.data).get("pace")
        intro = QLabel(
            "Pace is how many units of a class you aim to finish each "
            "week. Syllaport measures your real pace once you have "
            "finished two units, and the measured pace takes over from "
            "this setting. You can change it any time in Settings.")
        intro.setWordWrap(True)
        self.body.addWidget(intro)
        self.radios = []
        current = data_mod.seed_pace(store.data) if done_before else None
        for value, text in self.CHOICES:
            radio = QRadioButton("%s units a week" % _fmt_pace(value))
            radio.setProperty("pace_value", value)
            if current is not None and abs(current - value) < 1e-9:
                radio.setChecked(True)
            self.radios.append(radio)
            self.body.addWidget(field_row("", radio, text))
        custom_row = QWidget()
        custom_layout = QHBoxLayout(custom_row)
        custom_layout.setContentsMargins(0, 0, 0, 0)
        self.custom_radio = QRadioButton("Custom pace")
        self.custom_spin = QDoubleSpinBox()
        self.custom_spin.setRange(0.5, 7.0)
        self.custom_spin.setSingleStep(0.5)
        self.custom_spin.setValue(1.0)
        self.custom_spin.setEnabled(False)
        self.custom_radio.toggled.connect(self.custom_spin.setEnabled)
        custom_layout.addWidget(self.custom_radio)
        custom_layout.addWidget(self.custom_spin)
        self.body.addWidget(field_row(
            "", custom_row, "Pick your own number of units a week."))
        buttons = QDialogButtonBox(QDialogButtonBox.Save
                                   | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        self.body.addWidget(buttons)

    def chosen_pace(self):
        for radio in self.radios:
            if radio.isChecked():
                return radio.property("pace_value")
        if self.custom_radio.isChecked():
            return self.custom_spin.value()
        return None

    def save(self):
        pace = self.chosen_pace()
        if pace is None:
            self.say("Pick a pace first. One unit a week is a calm start.")
            return
        self.store.data.setdefault("settings", {})["seed_pace"] = pace
        self.store.save()
        self.store.complete_step("pace")
        self.accept()


def _fmt_pace(value):
    if float(value).is_integer():
        return "%d" % int(value)
    return "%g" % value


class StartDateDialog(_BaseDialog):
    """Checklist step 4: choose your start date.

    This is the first day of the study plan, not the profile start
    date (step 1). The schedule builder (R6) builds from this date.
    """

    def __init__(self, store, parent=None):
        super().__init__(store, "Choose your start date", parent)
        done_before = checklist_mod.checklist_state(
            store.data).get("start_date")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        start = data_mod.term_start(store.data)
        if done_before and start is not None:
            self.date_edit.setDate(start)
        else:
            self.date_edit.setDate(_next_monday())
        self.body.addWidget(field_row(
            "First day of your study plan", self.date_edit,
            "Your schedule is built from this date. Next Monday is "
            "suggested; change it if you like."))
        buttons = QDialogButtonBox(QDialogButtonBox.Save
                                   | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        self.body.addWidget(buttons)

    def save(self):
        picked = self.date_edit.date().toPython()
        self.store.data.setdefault("settings", {})["term_start"] = \
            picked.isoformat()
        self.store.save()
        self.store.complete_step("start_date")
        self.accept()


class CatalogPickerDialog(_BaseDialog):
    """Pick a class from the verified catalog.

    Used by checklist step 2 and by Courses. Browse by subject, search
    by word, read what a class is before adding it. Nothing is selected
    by default (U6).
    """

    def __init__(self, store, parent=None, on_added=None):
        super().__init__(store, "Pick a class", parent)
        self.on_added = on_added
        intro = QLabel(
            "Every class here is free to learn from. No card, no phone "
            "check. Syllaport never asks for a course password; you sign "
            "in on the provider's own site.")
        intro.setWordWrap(True)
        self.body.addWidget(intro)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search by word, school, or subject")
        self.search.textChanged.connect(self.refresh_list)
        self.body.addWidget(field_row(
            "Search", self.search, "Type to narrow the list."))
        self.subject_combo = QComboBox()
        self.subject_combo.addItems(catalog_mod.SUBJECTS)
        self.subject_combo.setCurrentIndex(-1)
        self.subject_combo.setPlaceholderText("Filter by subject")
        self.subject_combo.currentIndexChanged.connect(self.refresh_list)
        self.body.addWidget(field_row(
            "Subject", self.subject_combo,
            "Pick a subject to see only those classes, or leave it "
            "blank to see all of them."))
        self.course_list = QListWidget()
        self.course_list.currentItemChanged.connect(self.show_details)
        self.body.addWidget(self.course_list)
        self.details = QLabel("Pick a class to see what it is.")
        self.details.setWordWrap(True)
        self.details.setProperty("role", "small")
        self.body.addWidget(self.details)
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        self.open_button = QPushButton("Open course site")
        self.open_button.setProperty("role", "quiet")
        self.open_button.setEnabled(False)
        self.open_button.clicked.connect(self.open_site)
        self.add_button = QPushButton("Add this class")
        self.add_button.setEnabled(False)
        self.add_button.clicked.connect(self.add_selected)
        row_layout.addWidget(self.open_button)
        row_layout.addWidget(self.add_button)
        self.body.addWidget(row)
        close_row = QDialogButtonBox(QDialogButtonBox.Close)
        close_row.rejected.connect(self.reject)
        self.body.addWidget(close_row)
        self._courses = []
        self.refresh_list()

    def _filtered(self):
        courses = catalog_mod.search_courses(self.search.text())
        subject = self.subject_combo.currentText() \
            if self.subject_combo.currentIndex() >= 0 else ""
        if subject:
            courses = [c for c in courses if c["subject"] == subject]
        return courses

    def refresh_list(self):
        self._courses = self._filtered()
        self.course_list.clear()
        for course in self._courses:
            source = catalog_mod.SOURCE_BY_ID[course["source_id"]]
            item = QListWidgetItem("%s, %s" % (course["title"],
                                               source["name"]))
            item.setData(Qt.UserRole, course["id"])
            self.course_list.addItem(item)
        self.course_list.setCurrentRow(-1)
        self.details.setText("Pick a class to see what it is.")
        self.open_button.setEnabled(False)
        self.add_button.setEnabled(False)

    def selected_course(self):
        item = self.course_list.currentItem()
        if item is None:
            return None
        return catalog_mod.COURSE_BY_ID.get(item.data(Qt.UserRole))

    def show_details(self):
        course = self.selected_course()
        if course is None:
            self.details.setText("Pick a class to see what it is.")
            self.open_button.setEnabled(False)
            self.add_button.setEnabled(False)
            return
        source = catalog_mod.SOURCE_BY_ID[course["source_id"]]
        length = course["length"] or "Length not listed"
        self.details.setText(
            "%s\n%s\nLength: %s\nCertificate: %s\nSign up: %s" % (
                course["title"], course["blurb"], length,
                course["certificate"], source["signup"]))
        self.open_button.setEnabled(True)
        self.add_button.setEnabled(True)

    def open_site(self):
        course = self.selected_course()
        if course is not None and course.get("url"):
            QDesktopServices.openUrl(course["url"])

    def add_selected(self):
        course = self.selected_course()
        if course is None:
            return
        source = catalog_mod.SOURCE_BY_ID[course["source_id"]]
        data_mod.add_course(
            self.store.data, course["title"], course["source_id"],
            source["name"], url=course["url"],
            certificate=course["certificate"], blurb=course["blurb"])
        self.store.save()
        self.store.complete_step("first_class")
        if self.on_added is not None:
            self.on_added(course)
        self.accept()


class GuidedPickDialog(_BaseDialog):
    """Teach-by-playing choice 3: start with a guided pick.

    Pick a subject, see the report's top verified pick for it (and the
    runner-up where one exists), add it. Guided choices (U39 analog):
    the app shows what fits, the user never guesses.
    """

    def __init__(self, store, parent=None, on_added=None):
        super().__init__(store, "Start with a guided pick", parent)
        self.on_added = on_added
        intro = QLabel(
            "Pick what you want to learn. Syllaport shows the best "
            "verified free class for it, from the catalog research.")
        intro.setWordWrap(True)
        self.body.addWidget(intro)
        self.subject_list = QListWidget()
        for subject in catalog_mod.SUBJECTS:
            self.subject_list.addItem(QListWidgetItem(subject))
        self.subject_list.setCurrentRow(-1)
        self.subject_list.currentItemChanged.connect(self.show_pick)
        self.body.addWidget(field_row(
            "What do you want to learn?", self.subject_list,
            "Pick one subject to see its best free class."))
        self.pick_box = QGroupBox("Best pick")
        pick_layout = QVBoxLayout(self.pick_box)
        self.pick_text = QLabel("Pick a subject first.")
        self.pick_text.setWordWrap(True)
        pick_layout.addWidget(self.pick_text)
        self.pick_button = QPushButton("Add this class")
        self.pick_button.setEnabled(False)
        self.pick_button.clicked.connect(self.add_pick)
        pick_layout.addWidget(self.pick_button)
        self.body.addWidget(self.pick_box)
        self.runner_box = QGroupBox("Runner-up")
        runner_layout = QVBoxLayout(self.runner_box)
        self.runner_text = QLabel("")
        self.runner_text.setWordWrap(True)
        runner_layout.addWidget(self.runner_text)
        self.runner_button = QPushButton("Add this class instead")
        self.runner_button.setEnabled(False)
        self.runner_button.clicked.connect(self.add_runner)
        runner_layout.addWidget(self.runner_button)
        self.runner_box.hide()
        self.body.addWidget(self.runner_box)
        close_row = QDialogButtonBox(QDialogButtonBox.Close)
        close_row.rejected.connect(self.reject)
        self.body.addWidget(close_row)
        self._pick = None
        self._runner = None

    def _describe(self, course):
        source = catalog_mod.SOURCE_BY_ID[course["source_id"]]
        length = course["length"] or "Length not listed"
        return "%s\n%s\n%s\nLength: %s\nCertificate: %s" % (
            course["title"], source["name"], course["blurb"], length,
            course["certificate"])

    def show_pick(self):
        item = self.subject_list.currentItem()
        if item is None:
            self.pick_text.setText("Pick a subject first.")
            self.pick_button.setEnabled(False)
            self.runner_box.hide()
            self._pick = None
            self._runner = None
            return
        pick_id, runner_id = catalog_mod.SUBJECT_PICKS[item.text()]
        self._pick = catalog_mod.COURSE_BY_ID[pick_id]
        self.pick_text.setText(self._describe(self._pick))
        self.pick_button.setEnabled(True)
        if runner_id:
            self._runner = catalog_mod.COURSE_BY_ID[runner_id]
            self.runner_text.setText(self._describe(self._runner))
            self.runner_button.setEnabled(True)
            self.runner_box.show()
        else:
            self._runner = None
            self.runner_box.hide()

    def _add(self, course):
        source = catalog_mod.SOURCE_BY_ID[course["source_id"]]
        data_mod.add_course(
            self.store.data, course["title"], course["source_id"],
            source["name"], url=course["url"],
            certificate=course["certificate"], blurb=course["blurb"])
        self.store.save()
        self.store.complete_step("first_class")
        if self.on_added is not None:
            self.on_added(course)
        self.accept()

    def add_pick(self):
        if self._pick is not None:
            self._add(self._pick)

    def add_runner(self):
        if self._runner is not None:
            self._add(self._runner)


class AddKnownClassDialog(_BaseDialog):
    """Teach-by-playing choice 2: add a class you already know."""

    def __init__(self, store, parent=None, on_added=None):
        super().__init__(store, "Add a class you already know", parent)
        self.on_added = on_added
        self.name_edit = QLineEdit()
        self.body.addWidget(field_row(
            "Class name", self.name_edit,
            "The name of the class as the provider calls it."))
        self.source_combo = QComboBox()
        self.source_combo.addItems([s["name"] for s in catalog_mod.SOURCES])
        self.source_combo.addItem("Another source")
        self.source_combo.setCurrentIndex(-1)
        self.source_combo.setPlaceholderText("Pick the source")
        self.body.addWidget(field_row(
            "Source", self.source_combo,
            "Where the class lives. Pick Another source if it is not "
            "in the verified catalog."))
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://...")
        self.body.addWidget(field_row(
            "Course link (optional)", self.url_edit,
            "The page where the class lives, so you can open it from "
            "Syllaport. Leave it blank if you do not have it."))
        buttons = QDialogButtonBox(QDialogButtonBox.Save
                                   | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        self.body.addWidget(buttons)

    def save(self):
        name = self.name_edit.text().strip()
        if not name:
            self.say("Give the class a name first.")
            self.name_edit.setFocus()
            return
        if self.source_combo.currentIndex() < 0:
            self.say("Pick the source, or choose Another source.")
            self.source_combo.setFocus()
            return
        index = self.source_combo.currentIndex()
        if index < len(catalog_mod.SOURCES):
            source = catalog_mod.SOURCES[index]
            source_id, source_name = source["id"], source["name"]
        else:
            source_id, source_name = "other", "Another source"
        url = self.url_edit.text().strip()
        course = data_mod.add_course(
            self.store.data, name, source_id, source_name, url=url)
        self.store.save()
        self.store.complete_step("first_class")
        if self.on_added is not None:
            self.on_added(course)
        self.accept()
