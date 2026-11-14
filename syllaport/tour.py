"""The guided tour (checklist step 5, entry 014 teach-by-playing).

A short walk through the eight windows. Each step can show the real
window it describes, so the tour is a real run of the app, not text
about it. Modeless: the user can look around while the tour stays open.
Skipping the tour leaves the step undone (honest: the tour was not
taken); the checklist itself can still be dismissed from the Dashboard.
"""

from __future__ import annotations

from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QPushButton,
                               QVBoxLayout, QWidget)

STEPS = [
    (None, "Welcome to Syllaport",
     "Syllaport has eight windows, one per job. This tour shows each "
     "one in turn. Press Show me to open the window a step talks about."),
    (0, "Dashboard",
     "The Dashboard is home. It shows what to do today, your pace, "
     "your classes, your streak, and your time in, at a glance."),
    (1, "Courses",
     "Courses holds your classes. Pick them from the verified free "
     "catalog, and track each one as you work through it."),
    (2, "Schedule",
     "Schedule holds your week and your journey. The schedule builder "
     "arrives in R6; your start date already lives here."),
    (3, "Notebook",
     "Notebook holds your notes, one notebook per class plus a general "
     "one. Notebooks arrive in R8."),
    (4, "Work Log",
     "Work Log holds what you did and your pace over time. The full "
     "log arrives in R9."),
    (5, "Account",
     "Account holds who you are: your profile today, and sign in with "
     "full accounts in R3."),
    (6, "Backup",
     "Backup keeps your data safe: automatic backups, download a copy, "
     "and restore from a backup."),
    (7, "Settings",
     "Settings holds how Syllaport behaves: your pace, your start "
     "date, and the accessibility presets."),
    (None, "That is the whole app",
     "Eight windows, one job each. The How to Use index in the Help "
     "menu covers everything again whenever you need it."),
]


class TourDialog(QDialog):
    """Modeless tour window. Needs the WindowManager to show windows."""

    def __init__(self, store, manager, parent=None):
        super().__init__(parent)
        self.store = store
        self.manager = manager
        self.setWindowTitle("Tour of Syllaport")
        self.setModal(False)
        self.index = 0
        layout = QVBoxLayout(self)
        self.title_label = QLabel("")
        self.title_label.setProperty("role", "title")
        layout.addWidget(self.title_label)
        self.body_label = QLabel("")
        self.body_label.setWordWrap(True)
        layout.addWidget(self.body_label)
        self.count_label = QLabel("")
        self.count_label.setProperty("role", "muted")
        layout.addWidget(self.count_label)
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        self.back_button = QPushButton("Back")
        self.back_button.setProperty("role", "quiet")
        self.back_button.clicked.connect(self.go_back)
        self.show_button = QPushButton("Show me")
        self.show_button.setProperty("role", "quiet")
        self.show_button.clicked.connect(self.show_window)
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.go_next)
        self.finish_button = QPushButton("Finish tour")
        self.finish_button.clicked.connect(self.finish)
        row_layout.addWidget(self.back_button)
        row_layout.addWidget(self.show_button)
        row_layout.addStretch(1)
        row_layout.addWidget(self.next_button)
        row_layout.addWidget(self.finish_button)
        layout.addWidget(row)
        self.skip_button = QPushButton("Skip tour")
        self.skip_button.setProperty("role", "link")
        self.skip_button.clicked.connect(self.reject)
        layout.addWidget(self.skip_button)
        self.refresh()

    def refresh(self):
        window_index, title, body = STEPS[self.index]
        self.title_label.setText(title)
        self.body_label.setText(body)
        self.count_label.setText("Step %d of %d" % (self.index + 1,
                                                    len(STEPS)))
        self.back_button.setEnabled(self.index > 0)
        self.show_button.setVisible(window_index is not None)
        last = self.index == len(STEPS) - 1
        self.next_button.setVisible(not last)
        self.finish_button.setVisible(last)

    def go_back(self):
        if self.index > 0:
            self.index -= 1
            self.refresh()

    def go_next(self):
        if self.index < len(STEPS) - 1:
            self.index += 1
            self.refresh()

    def show_window(self):
        window_index = STEPS[self.index][0]
        if window_index is not None and self.manager is not None:
            self.manager.show_window(window_index)
            self.raise_()
            self.activateWindow()

    def finish(self):
        self.store.complete_step("tour")
        self.accept()
