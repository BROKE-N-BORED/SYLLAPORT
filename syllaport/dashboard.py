"""Dashboard window: the home window (Design Spec section 2, 6.2).

Bento grid: one hero tile plus five supporting tiles, all showing real
numbers from the store. While first run is unfinished, the hero tile IS
the setup checklist (Spec section 6.2: the checklist appears as the
Dashboard hero tile state, not as a ninth window). When setup is done,
the hero becomes "Do this now". R4 rebuilds this dashboard with the
full bento breakpoints; R2 sets the structure and the real numbers.
"""

from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, \
    QVBoxLayout, QWidget

from syllaport import anim
from syllaport import checklist as checklist_mod
from syllaport import data as data_mod
from syllaport import dialogs as dialogs_mod
from syllaport import tour as tour_mod
from syllaport.windows import Card, SyllaportWindow, make_label


class DashboardWindow(SyllaportWindow):
    key = "dashboard"

    def build_content(self):
        self.content_layout.addWidget(make_label("Dashboard", "title"))
        holder = QWidget()
        self.grid = QGridLayout(holder)
        self.grid.setContentsMargins(4, 4, 8, 8)
        self.grid.setSpacing(20)
        self.content_layout.addWidget(holder, 1)

        self.hero = Card(self.store, radius=20)
        self.grid.addWidget(self.hero, 0, 0, 2, 4)
        self._tile_labels = {}
        self.tile_pace = self._tile("Your pace")
        self.tile_classes = self._tile("My classes")
        self.tile_streak = self._tile("Streak")
        self.tile_time = self._tile("Time in")
        self.grid.addWidget(self.tile_pace, 2, 0)
        self.grid.addWidget(self.tile_classes, 2, 1)
        self.grid.addWidget(self.tile_streak, 2, 2)
        self.grid.addWidget(self.tile_time, 2, 3)
        self.tile_next = Card(self.store, radius=16)
        self.grid.addWidget(self.tile_next, 3, 0, 1, 4)
        self._done_before = set()
        self._hero_signature = None
        self._tour_dialog = None
        self.refresh()

    def _tile(self, title):
        card = Card(self.store, radius=16)
        card.layout().addWidget(make_label(title, "cardtitle"))
        big = make_label("", "bignum")
        sub = make_label("", "muted", wrap=True)
        card.layout().addWidget(big)
        card.layout().addWidget(sub)
        card.layout().addStretch(1)
        self._tile_labels[title] = (big, sub)
        return card

    # -- hero -----------------------------------------------------------
    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _refresh_hero(self):
        self._clear_layout(self.hero.layout())
        if checklist_mod.show_checklist(self.store.data):
            self._build_checklist_hero()
        elif checklist_mod.is_complete(self.store.data):
            self._build_do_now_hero()
        else:
            self._build_resume_hero()

    def _build_checklist_hero(self):
        self.hero.layout().addWidget(make_label("Set up Syllaport",
                                                "cardtitle"))
        done = checklist_mod.done_count(self.store.data)
        self.hero.layout().addWidget(make_label(
            "%d of 5 steps done. Each step takes under a minute." % done,
            "muted"))
        state = checklist_mod.checklist_state(self.store.data)
        newly_done = {s for s in checklist_mod.STEP_ORDER
                      if state.get(s)} - self._done_before
        self._done_before = {s for s in checklist_mod.STEP_ORDER
                             if state.get(s)}
        for step in checklist_mod.STEP_ORDER:
            info = checklist_mod.STEPS[step]
            row = QWidget()
            row_layout = QVBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(2)
            head = QWidget()
            head_layout = QVBoxLayout(head)
            head_layout.setContentsMargins(0, 0, 0, 0)
            head_layout.setSpacing(0)
            mark = QLabel("Done" if state.get(step) else "To do")
            mark.setProperty("role", "tag")
            title = make_label(info["title"], "section")
            head_layout.addWidget(mark)
            head_layout.addWidget(title)
            row_layout.addWidget(head)
            row_layout.addWidget(make_label(info["detail"], "muted",
                                            wrap=True))
            button = QPushButton("Change" if state.get(step)
                                 else info["button"])
            if not state.get(step):
                button.clicked.connect(
                    lambda _c=False, s=step: self._open_step(s))
            else:
                button.setProperty("role", "quiet")
                button.clicked.connect(
                    lambda _c=False, s=step: self._open_step(s))
            row_layout.addWidget(button)
            self.hero.layout().addWidget(row)
            if step in newly_done:
                anim.fade_in(mark, self.store)
        skip = QPushButton("Skip setup for now")
        skip.setProperty("role", "link")
        skip.clicked.connect(self._skip_setup)
        self.hero.layout().addWidget(skip)

    def _build_resume_hero(self):
        self.hero.layout().addWidget(make_label("Finish setup",
                                                "cardtitle"))
        done = checklist_mod.done_count(self.store.data)
        self.hero.layout().addWidget(make_label(
            "Setup is %d of 5 steps done. Pick up where you left off."
            % done, wrap=True))
        resume = QPushButton("Resume setup")
        resume.clicked.connect(self._resume_setup)
        self.hero.layout().addWidget(resume)

    def _build_do_now_hero(self):
        self.hero.layout().addWidget(make_label("Do this now", "cardtitle"))
        courses = self.store.data.get("courses", [])
        start = data_mod.term_start(self.store.data)
        if not courses:
            self.hero.layout().addWidget(make_label(
                "You have no classes yet. Pick your first class from "
                "the verified free catalog.", wrap=True))
            button = QPushButton("Pick your first class")
            button.clicked.connect(
                lambda: self._open_step("first_class"))
            self.hero.layout().addWidget(button)
        else:
            first = courses[0]
            self.hero.layout().addWidget(make_label(
                "Your first class is %s, from %s."
                % (first["title"], first["source_name"]), wrap=True))
            if start is not None:
                self.hero.layout().addWidget(make_label(
                    "Your plan starts %s." % start.isoformat(), "muted"))
            button = QPushButton("Open Courses")
            button.clicked.connect(lambda: self.manager.show_window(1))
            self.hero.layout().addWidget(button)

    def _open_step(self, step):
        if step == "profile":
            dialogs_mod.ProfileDialog(self.store, self).exec()
        elif step == "first_class":
            dialogs_mod.CatalogPickerDialog(self.store, self).exec()
        elif step == "pace":
            dialogs_mod.PaceDialog(self.store, self).exec()
        elif step == "start_date":
            dialogs_mod.StartDateDialog(self.store, self).exec()
        elif step == "tour":
            self._tour_dialog = tour_mod.TourDialog(
                self.store, self.manager, self)
            self._tour_dialog.show()
        self.refresh()

    def _skip_setup(self):
        self.store.dismiss_checklist()
        self.set_status("Setup skipped. Resume any time from Settings.")
        self.refresh()

    def _resume_setup(self):
        self.store.reopen_checklist()
        self.refresh()

    # -- tiles ----------------------------------------------------------
    def _refresh_tiles(self):
        data = self.store.data
        pace = data_mod.compute_pace(data)
        big, sub = self._tile_labels["Your pace"]
        big.setText("%.1f" % pace["effective"])
        if pace["measured"] is None:
            sub.setText("units a week (your setting). No units logged yet.")
        else:
            sub.setText("units a week, measured over %.1f weeks."
                        % pace["elapsed_weeks"])
        big, sub = self._tile_labels["My classes"]
        courses = data.get("courses", [])
        big.setText("%d" % len(courses))
        if courses:
            sub.setText("classes picked. First: %s." % courses[0]["title"])
        else:
            sub.setText("classes picked. Pick your first class to begin.")
        big, sub = self._tile_labels["Streak"]
        days = data_mod.streak(data)
        big.setText("%d" % days)
        if days == 0:
            sub.setText("No streak yet. Log a study day to start one.")
        else:
            sub.setText("day streak.")
        big, sub = self._tile_labels["Time in"]
        big.setText(data_mod.fmt_minutes(data_mod.minutes_total(data)))
        sub.setText("time in. This week: %s."
                    % data_mod.fmt_minutes(data_mod.minutes_this_week(data)))
        self._clear_layout(self.tile_next.layout())
        self.tile_next.layout().addWidget(
            make_label("Next milestone", "cardtitle"))
        if not courses:
            self.tile_next.layout().addWidget(make_label(
                "Pick your first class. That is the next milestone.",
                wrap=True))
        else:
            self.tile_next.layout().addWidget(make_label(
                "Start %s. Your first class is the next milestone."
                % courses[0]["title"], wrap=True))
        start = data_mod.term_start(data)
        if start is not None:
            self.tile_next.layout().addWidget(make_label(
                "Your plan starts %s." % start.isoformat(), "muted"))
        else:
            self.tile_next.layout().addWidget(make_label(
                "Start date not set.", "muted"))

    def refresh(self):
        super().refresh()
        if not hasattr(self, "hero"):
            return
        # Rebuild the hero only when the checklist state changed; the
        # rebuild deletes and recreates ~30 widgets, and most saves do
        # not touch the checklist at all.
        state = checklist_mod.checklist_state(self.store.data)
        signature = (tuple(sorted(s for s in checklist_mod.STEP_ORDER
                                  if state.get(s))),
                     checklist_mod.is_dismissed(self.store.data),
                     len(self.store.data.get("courses", [])),
                     data_mod.term_start(self.store.data))
        if signature != self._hero_signature:
            self._hero_signature = signature
            self._refresh_hero()
        self._refresh_tiles()
        self.hero.update()
        self.tile_next.update()
