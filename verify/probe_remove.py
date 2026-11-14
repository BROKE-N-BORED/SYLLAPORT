"""Probe: reproduce the remove-class confirm flow with prints."""

import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.expanduser("~/workspace/syllaport"))

from PySide6.QtCore import Qt, QTimer  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton  # noqa: E402

from syllaport import data as data_mod  # noqa: E402
from syllaport import style as style_mod  # noqa: E402
from syllaport.store import Store  # noqa: E402
from syllaport.windows import WindowManager  # noqa: E402


def settle(app, ms=300):
    end = time.time() + ms / 1000.0
    while time.time() < end:
        app.processEvents()
        time.sleep(0.01)


def main():
    app = QApplication(sys.argv[:1])
    tmp = tempfile.TemporaryDirectory()
    store = Store(tmp.name)
    style_mod.apply_presets(app, store.data.get("presets", {}))
    manager = WindowManager(store, app)
    data_mod.add_course(store.data, "CS50x", "harvard-cs50", "Harvard CS50")
    store.save()
    manager.show_window(1)
    settle(app, 500)
    courses = manager.windows[1]
    print("list count:", courses.course_list.count())
    courses.course_list.setCurrentRow(0)
    settle(app, 200)
    remove = None
    for button in courses.findChildren(QPushButton):
        if button.text() == "Remove this class":
            remove = button
    print("remove button:", remove, "enabled:", remove.isEnabled() if remove else None,
          "visible:", remove.isVisible() if remove else None)

    state = {}

    def click_yes():
        boxes = [w for w in app.topLevelWidgets()
                 if isinstance(w, QMessageBox)]
        print("click_yes: message boxes:", len(boxes),
              "visible:", [b.isVisible() for b in boxes])
        for box in boxes:
            if box.isVisible():
                button = box.button(QMessageBox.StandardButton.Yes)
                print("click_yes: yes button:", button)
                state["clicked"] = True
                if button is not None:
                    QTest.mouseClick(button, Qt.LeftButton)
                    print("click_yes: clicked Yes")

    QTimer.singleShot(400, click_yes)
    print("clicking Remove...")
    QTest.mouseClick(remove, Qt.LeftButton)
    print("mouseClick returned; clicked =", state.get("clicked"))
    settle(app, 500)
    print("courses left:", len(store.data["courses"]))
    tmp.cleanup()
    return 0


if __name__ == "__main__":
    sys.exit(main())
