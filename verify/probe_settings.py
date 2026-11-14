"""Probe: Settings study-card overlap + checkbox indicator rendering."""

import os
import sys
import tempfile

sys.path.insert(0, os.path.expanduser("~/workspace/syllaport"))

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import QApplication, QCheckBox, QLabel, QPushButton  # noqa: E402

from syllaport import style as style_mod  # noqa: E402
from syllaport.store import Store  # noqa: E402
from syllaport.windows import WindowManager  # noqa: E402


def main():
    app = QApplication(sys.argv[:1])
    tmp = tempfile.TemporaryDirectory()
    store = Store(tmp.name)
    store.data["pace_seed"] = 1.0
    store.data["term_start"] = "2026-11-16"
    store.data["checklist"] = {"profile": True, "first_class": True,
                               "pace": True, "start_date": True,
                               "tour": True}
    store.save()
    style_mod.apply_presets(app, store.data.get("presets", {}))
    manager = WindowManager(store, app)
    manager.show_window(7)
    QTest.qWait(500)
    settings = manager.windows[7]
    card = settings.pace_label.parent()
    labels = card.findChildren(QLabel)
    buttons = card.findChildren(QPushButton)
    print("study card labels:", len(labels), "buttons:", len(buttons))
    for label in labels:
        print("  label %r at y=%d h=%d visible=%s" % (
            label.text()[:40], label.y(), label.height(), label.isVisible()))
    for button in buttons:
        print("  button %r at y=%d h=%d visible=%s" % (
            button.text(), button.y(), button.height(), button.isVisible()))
    print("card height:", card.height(),
          "layout total height:", card.layout().totalSizeHint().height())
    # Checkbox indicator: geometry of the first preset checkbox.
    boxes = settings.findChildren(QCheckBox)
    print("checkboxes:", len(boxes))
    for box in boxes:
        print("  box %r at y=%d h=%d" % (box.text(), box.y(), box.height()))
    # Zoomed grab of the presets card for the indicator pixels.
    presets = settings.preset_boxes["larger_text"].parent()
    pix = presets.grab()
    out = os.path.expanduser(
        "~/workspace/universal-portal/verify-r2/probe-presets.png")
    pix.save(out)
    print("saved", out)
    pix2 = card.grab()
    out2 = os.path.expanduser(
        "~/workspace/universal-portal/verify-r2/probe-study.png")
    pix2.save(out2)
    print("saved", out2)
    tmp.cleanup()
    return 0


if __name__ == "__main__":
    sys.exit(main())
