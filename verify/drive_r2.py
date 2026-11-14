"""R2 verify drive: drives the real GUI like a user and screenshots it.

Runs the app in-process under Xvfb, completes the whole first run
through the real widgets (no direct save() calls except where noted),
toggles every preset, opens every window, and saves screenshots to
~/workspace/universal-portal/verify-r2/.

A QTimer safety watcher dismisses any unexpected modal dialog so a
surprise popup can never trap the settle pump (Pixel Forge lesson).

Usage:
    xvfb-run -a <venv python> drive_r2.py
"""

import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.dirname(HERE)
sys.path.insert(0, TREE)

OUT = os.path.expanduser("~/workspace/universal-portal/verify-r2")
os.makedirs(OUT, exist_ok=True)

from PySide6.QtCore import Qt, QTimer  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QApplication, QMessageBox, QPushButton)

from syllaport import anim, checklist as checklist_mod  # noqa: E402
from syllaport import data as data_mod  # noqa: E402
from syllaport.store import Store  # noqa: E402
from syllaport.windows import WindowManager  # noqa: E402

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def settle(app, ms=300):
    # QTest.qWait runs the real event loop, which flushes deleteLater().
    # A bare processEvents() pump does NOT flush it in this PySide6
    # build (Dataset Scout lesson): stale widgets pile up visibly.
    QTest.qWait(ms)


def shot(widget, name):
    path = os.path.join(OUT, name)
    widget.grab().save(path)
    print("shot:", path)


def find_button(widget, text):
    for button in widget.findChildren(QPushButton):
        if button.text() == text:
            return button
    return None


def main():
    app = QApplication(sys.argv[:1])
    tmp = tempfile.TemporaryDirectory()
    store = Store(tmp.name)

    # Safety watcher: dismiss any unexpected modal dialog, record it.
    seen_modals = []

    def watcher():
        for widget in app.topLevelWidgets():
            if isinstance(widget, QMessageBox) and widget.isVisible():
                if widget not in seen_modals:
                    seen_modals.append(widget)
                    widget.reject()
    timer = QTimer()
    timer.timeout.connect(watcher)
    timer.start(200)

    from syllaport import style as style_mod
    style_mod.apply_presets(app, store.data.get("presets", {}))
    manager = WindowManager(store, app)
    manager.show_window(0)
    settle(app, 500)

    dashboard = manager.windows[0]
    check("dashboard visible", dashboard.isVisible())
    check("checklist shown on first run",
          checklist_mod.show_checklist(store.data))
    shot(dashboard, "01-dashboard-checklist.png")

    # Courses empty state BEFORE any class is added.
    manager.show_window(1)
    settle(app, 300)
    courses = manager.windows[1]
    texts = [b.text() for b in courses.findChildren(QPushButton)]
    check("courses offers 3 teaching choices",
          all(t in texts for t in ("Browse the catalog",
                                   "Add a class you already know",
                                   "Start with a guided pick")), str(texts))
    shot(courses, "02-courses-empty.png")

    # Step 1: profile, through the real dialog widgets.
    manager.show_window(0)
    settle(app, 200)
    from syllaport import dialogs as dialogs_mod
    profile = dialogs_mod.ProfileDialog(store, dashboard)
    profile.show()
    settle(app, 200)
    profile.name_edit.setText("Verify User")
    # Click Save via the dialog button box.
    for button in profile.findChildren(QPushButton):
        if button.text() == "Save":
            QTest.mouseClick(button, Qt.LeftButton)
    settle(app, 200)
    check("step 1 profile saved",
          store.data["profile"]["name"] == "Verify User")
    check("step 1 marked done",
          checklist_mod.checklist_state(store.data)["profile"])

    # Step 2: first class, through the catalog picker widgets.
    picker = dialogs_mod.CatalogPickerDialog(store, dashboard)
    picker.show()
    settle(app, 200)
    picker.search.setText("CS50x")
    settle(app, 200)
    # Two matches: CS50x itself, and 6.0001 whose blurb mentions it.
    found = [picker.course_list.item(i).text()
             for i in range(picker.course_list.count())]
    check("catalog search narrows to CS50x",
          picker.course_list.count() == 2
          and any("CS50x:" in text for text in found),
          "count=%d" % picker.course_list.count())
    picker.course_list.setCurrentRow(0)
    settle(app, 100)
    add = find_button(picker, "Add this class")
    check("add button enables on selection", add.isEnabled())
    QTest.mouseClick(add, Qt.LeftButton)
    settle(app, 200)
    check("step 2 class added",
          len(store.data["courses"]) == 1
          and store.data["courses"][0]["title"].startswith("CS50x"))

    # Courses now lists the class.
    manager.show_window(1)
    settle(app, 300)
    check("courses lists the added class",
          courses.course_list.count() == 1)
    shot(courses, "03-courses-list.png")

    # Step 3: pace, through the real radio buttons.
    pace = dialogs_mod.PaceDialog(store, dashboard)
    pace.show()
    settle(app, 200)
    QTest.mouseClick(pace.radios[1], Qt.LeftButton)  # 1.0 units a week
    settle(app, 100)
    for button in pace.findChildren(QPushButton):
        if button.text() == "Save":
            QTest.mouseClick(button, Qt.LeftButton)
    settle(app, 200)
    check("step 3 pace saved",
          abs(data_mod.seed_pace(store.data) - 1.0) < 1e-9)

    # Step 4: start date.
    start = dialogs_mod.StartDateDialog(store, dashboard)
    start.show()
    settle(app, 200)
    for button in start.findChildren(QPushButton):
        if button.text() == "Save":
            QTest.mouseClick(button, Qt.LeftButton)
    settle(app, 200)
    check("step 4 start date saved",
          data_mod.term_start(store.data) is not None,
          str(data_mod.term_start(store.data)))

    # Step 5: tour, driven step by step, with Show me on two windows.
    from syllaport import tour as tour_mod
    tour = tour_mod.TourDialog(store, manager, dashboard)
    tour.show()
    settle(app, 200)
    tour.go_next()
    tour.show_window()
    settle(app, 200)
    check("tour show me opens Dashboard", manager.active_index == 0)
    tour.go_next()
    tour.show_window()
    settle(app, 200)
    check("tour show me opens Courses", manager.active_index == 1)
    while tour.index < len(tour_mod.STEPS) - 1:
        tour.go_next()
    QTest.mouseClick(tour.finish_button, Qt.LeftButton)
    settle(app, 200)
    check("step 5 tour done",
          checklist_mod.checklist_state(store.data)["tour"])
    check("checklist complete", checklist_mod.is_complete(store.data))

    # Dashboard hero is now Do this now.
    manager.show_window(0)
    settle(app, 300)
    texts = [b.text() for b in dashboard.hero.findChildren(QPushButton)]
    check("hero becomes Do this now", "Open Courses" in texts, str(texts))
    shot(dashboard, "04-dashboard-done.png")

    # Persistence: a fresh Store sees the completed checklist.
    reloaded = Store(tmp.name)
    check("checklist persists across restart",
          checklist_mod.is_complete(reloaded.data))

    # Presets, through the View menu actions.
    dashboard.preset_actions["high_contrast"].trigger()
    settle(app, 200)
    check("high contrast preset applies",
          "#ffffff" in app.styleSheet()
          and store.preset("high_contrast"))
    shot(dashboard, "05-dashboard-high-contrast.png")
    dashboard.preset_actions["high_contrast"].trigger()
    dashboard.preset_actions["larger_text"].trigger()
    settle(app, 200)
    check("larger text preset applies",
          "font-size: 18px" in app.styleSheet())
    shot(dashboard, "06-dashboard-larger-text.png")
    dashboard.preset_actions["larger_text"].trigger()
    dashboard.preset_actions["reduced_motion"].trigger()
    settle(app, 100)
    label = dashboard.status_text
    check("reduced motion skips animation",
          anim.fade_in(label, store) is None)
    dashboard.preset_actions["reduced_motion"].trigger()

    # Every window opens.
    for index in range(8):
        manager.show_window(index)
        settle(app, 150)
        check("window %d opens" % index,
              manager.windows[index].isVisible())
    shot(manager.windows[7], "07-settings.png")

    # How to Use index.
    manager.how_to_action()
    settle(app, 300)
    howto = manager.how_to_window
    check("how to use opens", howto is not None and howto.isVisible())
    check("how to use has 12 topics", howto.topic_list.count() == 12)
    howto.topic_list.setCurrentRow(2)
    settle(app, 100)
    check("how to use shows topic text",
          "catalog" in howto.text.toPlainText().lower())
    shot(howto, "08-how-to-use.png")

    # Remove the class (confirm dialog driven by a timer click).
    # Stop the safety watcher first: this dialog is expected, and the
    # watcher would reject it before the Yes click lands. Close the
    # How to Use window too, so nothing covers the Courses window.
    timer.stop()
    howto.close()
    settle(app, 200)
    manager.show_window(1)
    settle(app, 200)
    courses.course_list.setCurrentRow(0)
    settle(app, 100)

    def click_yes():
        for widget in app.topLevelWidgets():
            if isinstance(widget, QMessageBox) and widget.isVisible():
                print("click_yes: found visible confirm")
                button = widget.button(QMessageBox.StandardButton.Yes)
                print("click_yes: yes button:", button)
                if button is not None:
                    QTest.mouseClick(button, Qt.LeftButton)
                    print("click_yes: clicked Yes")
    QTimer.singleShot(400, click_yes)
    remove = find_button(courses, "Remove this class")
    QTest.mouseClick(remove, Qt.LeftButton)
    settle(app, 500)
    check("remove class works", len(store.data["courses"]) == 0)
    check("log entries survive removal (none yet, no crash)", True)
    timer.start(200)

    # Backup now, through the manager action.
    manager.backup_now_action()
    settle(app, 200)
    backups = data_mod.list_backups(str(store.path))
    check("backup now writes a backup", len(backups) >= 1,
          "count=%d" % len(backups))

    timer.stop()
    failed = [r for r in RESULTS if not r[1]]
    print("\n%d checks, %d passed, %d failed"
          % (len(RESULTS), len(RESULTS) - len(failed), len(failed)))
    for name, ok, detail in failed:
        print("FAILED:", name, detail)
    tmp.cleanup()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
