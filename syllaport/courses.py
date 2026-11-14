"""Courses window: my classes (entry 014 teach-by-playing).

Empty state offers three teaching choices that actually work: browse
the catalog, add a class you already know, start with a guided pick.
Once classes exist, the window lists them with real details, an open
link, and a safe remove (the confirm names what it keeps: log entries
stay as work history). Units and per-course progress arrive in R5.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QListWidget,
                               QListWidgetItem, QPushButton, QVBoxLayout,
                               QWidget)

from syllaport import data as data_mod
from syllaport import dialogs as dialogs_mod
from syllaport.dialogs import confirm_action
from syllaport.windows import Card, SyllaportWindow, make_label


class CoursesWindow(SyllaportWindow):
    key = "courses"

    def build_content(self):
        self.content_layout.addWidget(make_label("Courses", "title"))
        self.stack = QWidget()
        self.stack_layout = QVBoxLayout(self.stack)
        self.stack_layout.setContentsMargins(0, 0, 0, 0)
        self.stack_layout.setSpacing(16)
        self.content_layout.addWidget(self.stack, 1)
        self._selected_id = None
        self.refresh()

    def _clear_stack(self):
        while self.stack_layout.count():
            item = self.stack_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def refresh(self):
        super().refresh()
        if not hasattr(self, "stack"):
            return
        self._clear_stack()
        if not self.store.data.get("courses"):
            self._build_empty_state()
        else:
            self._build_list_state()

    # -- empty state: teach by playing (014) -----------------------------
    def _build_empty_state(self):
        card = Card(self.store, radius=20)
        card.layout().addWidget(make_label("No classes yet.", "cardtitle"))
        card.layout().addWidget(make_label(
            "Pick your first class and Syllaport starts working for "
            "you: pace, schedule, notes, and progress all build from "
            "your classes. Three ways to start:", wrap=True))
        choices = [
            ("Browse the catalog",
             "See every verified free class, search by word, and read "
             "what a class is before adding it.",
             self._browse_catalog),
            ("Add a class you already know",
             "You know the class name already. Tell Syllaport what it "
             "is and where it lives.",
             self._add_known_class),
            ("Start with a guided pick",
             "Pick what you want to learn. Syllaport shows the best "
             "verified free class for it.",
             self._guided_pick),
        ]
        for title, detail, slot in choices:
            card.layout().addWidget(make_label(title, "section"))
            card.layout().addWidget(make_label(detail, "muted", wrap=True))
            button = QPushButton(title)
            button.clicked.connect(slot)
            card.layout().addWidget(button)
        self.stack_layout.addWidget(card)
        self.stack_layout.addStretch(1)

    # -- list state ------------------------------------------------------
    def _build_list_state(self):
        self.course_list = QListWidget()
        courses = self.store.data.get("courses", [])
        for course in courses:
            item = QListWidgetItem("%s, %s" % (course["title"],
                                               course["source_name"]))
            item.setData(Qt.UserRole, course["id"])
            self.course_list.addItem(item)
        self.course_list.currentItemChanged.connect(self._show_details)
        self.stack_layout.addWidget(self.course_list, 1)
        self.details = QLabel("Pick a class to see it here.")
        self.details.setWordWrap(True)
        self.details.setProperty("role", "small")
        self.stack_layout.addWidget(self.details)
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        self.open_button = QPushButton("Open course site")
        self.open_button.setProperty("role", "quiet")
        self.open_button.setEnabled(False)
        self.open_button.clicked.connect(self._open_site)
        self.remove_button = QPushButton("Remove this class")
        self.remove_button.setProperty("role", "quiet")
        self.remove_button.setEnabled(False)
        self.remove_button.clicked.connect(self._remove_selected)
        self.add_button = QPushButton("Add a class")
        self.add_button.clicked.connect(self._browse_catalog)
        row_layout.addWidget(self.open_button)
        row_layout.addWidget(self.remove_button)
        row_layout.addStretch(1)
        row_layout.addWidget(self.add_button)
        self.stack_layout.addWidget(row)
        self.stack_layout.addWidget(make_label(
            "Units and progress tracking for each class arrive in R5. "
            "Your classes and your pace already live here.", "muted",
            wrap=True))
        if self._selected_id is not None:
            for row_index in range(self.course_list.count()):
                item = self.course_list.item(row_index)
                if item.data(Qt.UserRole) == self._selected_id:
                    self.course_list.setCurrentRow(row_index)
                    break

    def _selected_course(self):
        if not hasattr(self, "course_list"):
            return None
        item = self.course_list.currentItem()
        if item is None:
            return None
        return data_mod.course_by_id(self.store.data,
                                     item.data(Qt.UserRole))

    def _show_details(self):
        course = self._selected_course()
        if course is None:
            self.details.setText("Pick a class to see it here.")
            self.open_button.setEnabled(False)
            self.remove_button.setEnabled(False)
            return
        self._selected_id = course["id"]
        lines = ["%s" % course["title"],
                 "From: %s" % course["source_name"]]
        if course.get("blurb"):
            lines.append(course["blurb"])
        if course.get("certificate"):
            lines.append("Certificate: %s" % course["certificate"])
        lines.append("Added: %s" % course.get("added", "Not set"))
        self.details.setText("\n".join(lines))
        self.open_button.setEnabled(bool(course.get("url")))
        self.remove_button.setEnabled(True)

    def _open_site(self):
        course = self._selected_course()
        if course is not None and course.get("url"):
            QDesktopServices.openUrl(course["url"])

    def _remove_selected(self):
        course = self._selected_course()
        if course is None:
            return
        if not confirm_action(
                self, "Remove this class",
                "Remove %s from your classes? Your work log entries "
                "for it stay as work history; only the class listing "
                "goes." % course["title"]):
            return
        data_mod.remove_course(self.store.data, course["id"])
        self._selected_id = None
        self.store.save()
        self.set_status("Class removed.")
        self.refresh()

    # -- the three teaching choices --------------------------------------
    def _browse_catalog(self):
        dialogs_mod.CatalogPickerDialog(self.store, self).exec()
        self.refresh()

    def _add_known_class(self):
        dialogs_mod.AddKnownClassDialog(self.store, self).exec()
        self.refresh()

    def _guided_pick(self):
        dialogs_mod.GuidedPickDialog(self.store, self).exec()
        self.refresh()
