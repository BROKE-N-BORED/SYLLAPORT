"""How to Use index (U22): built-in, in the Help menu.

A non-modal window: it stays open while you work. Every topic covers
what exists today; windows that arrive in later tasks say so plainly
instead of describing features that do not exist yet.
"""

from __future__ import annotations

from PySide6.QtWidgets import (QHBoxLayout, QListWidget, QListWidgetItem,
                               QTextEdit, QVBoxLayout, QWidget)

from syllaport.windows import make_label

TOPICS = [
    ("First run",
     "When Syllaport opens the first time, the Dashboard shows a setup "
     "checklist with five steps: create your profile, pick your first "
     "class, set your weekly pace, choose your start date, and take "
     "the tour. Each step does something real and saves it. You can "
     "skip setup and come back to it from Settings."),
    ("Dashboard",
     "The Dashboard is home. It shows what to do today, your pace, "
     "your classes, your day streak, your time in, and your next "
     "milestone. Pace starts at the setting you chose and switches to "
     "your measured pace once you have finished two units."),
    ("Courses",
     "Courses holds your classes. Pick them from the verified free "
     "catalog: browse every class, add one you already know, or start "
     "with a guided pick. Every class in the catalog is free to learn "
     "from, with no card and no phone check. Open a class to read "
     "what it is, then add it. Removing a class keeps your work log "
     "entries for it."),
    ("Schedule",
     "Schedule will hold your week and your journey. The schedule "
     "builder arrives in R6. Your start date already lives here, and "
     "you can change it."),
    ("Notebook",
     "Notebook will hold your notes, one per class plus a general "
     "one, with save and restore. Notebooks arrive in R8. Notes "
     "export to Markdown from the File menu."),
    ("Work Log",
     "Work Log will hold what you did and your pace over time, with "
     "filters and safe delete. The full log arrives in R9. The totals "
     "on that window are already real."),
    ("Account",
     "Account holds your profile: your name, your start date, and "
     "how many classes you have picked. Full accounts with sign in "
     "come in R3. Syllaport never asks for or stores any course "
     "password."),
    ("Backup",
     "Backup keeps your data safe. Syllaport saves your data to one "
     "file and keeps the last five automatic backups beside it. Back "
     "up now, download a copy, or restore from a backup. Restoring "
     "asks first and keeps your current data as a backup."),
    ("Settings",
     "Settings holds your weekly pace, your start date, and the "
     "accessibility presets: larger text, reduced motion, and high "
     "contrast. Each preset applies at once. Settings also brings "
     "back the setup checklist."),
    ("Presets",
     "Presets live in Settings and in the View menu, under Presets. "
     "Larger text makes all text bigger. Reduced motion turns off "
     "animation; state changes still happen, instantly. High contrast "
     "switches to black text on white surfaces."),
    ("Keyboard",
     "Every window opens from the View menu, the left side bar, or "
     "Ctrl+1 through Ctrl+8. Tab moves through controls in reading "
     "order. Enter activates a button. Esc closes a dialog and leaves "
     "things untouched."),
    ("Your data",
     "Everything lives on this computer, in one data file. Nothing "
     "leaves the computer unless you export it. Syllaport works "
     "fully offline; the only time it touches the web is when you "
     "press Open course site."),
]


class HowToWindow(QWidget):
    """The index: topic list on the left, plain-words text on the right."""

    def __init__(self, store, manager, parent=None):
        super().__init__(parent)
        self.store = store
        self.manager = manager
        self.setWindowTitle("Syllaport, How to Use")
        self.setMinimumSize(800, 500)
        self.resize(900, 600)
        layout = QVBoxLayout(self)
        layout.addWidget(make_label("How to Use", "title"))
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        self.topic_list = QListWidget()
        for title, _body in TOPICS:
            self.topic_list.addItem(QListWidgetItem(title))
        self.topic_list.setCurrentRow(-1)
        self.topic_list.currentItemChanged.connect(self._show_topic)
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setPlainText("Pick a topic to read it.")
        row_layout.addWidget(self.topic_list, 1)
        row_layout.addWidget(self.text, 2)
        layout.addWidget(row, 1)

    def _show_topic(self):
        item = self.topic_list.currentItem()
        if item is None:
            self.text.setPlainText("Pick a topic to read it.")
            return
        for title, body in TOPICS:
            if title == item.text():
                self.text.setPlainText(body)
                return
