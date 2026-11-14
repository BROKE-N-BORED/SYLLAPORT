"""Probe: does _clear_layout actually remove Card children?"""

import os
import sys
import time

sys.path.insert(0, os.path.expanduser("~/workspace/syllaport"))

from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import QApplication, QLabel, QPushButton  # noqa: E402

from syllaport.windows import Card  # noqa: E402


def main():
    app = QApplication(sys.argv[:1])
    card = Card(None, radius=16)
    card.resize(400, 300)
    for i in range(3):
        card.layout().addWidget(QLabel("label %d" % i))
    btn = QPushButton("Test button")
    card.layout().addWidget(btn)
    card.show()
    app.processEvents()
    time.sleep(0.2)
    app.processEvents()
    print("children before clear:",
          len(card.findChildren(QLabel)) + len(card.findChildren(QPushButton)))

    # Replicate Dashboard._clear_layout exactly.
    layout = card.layout()
    print("layout count before:", layout.count())
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
    print("layout count after takeAt:", layout.count())
    QTest.qWait(200)
    print("children after clear + qWait:",
          len(card.findChildren(QLabel)) + len(card.findChildren(QPushButton)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
