"""GUI tests: windows open, checklist completes, presets work.

Run under Xvfb (see run_tests.sh) or plain offscreen; the module falls
back to the offscreen platform when no display is present. Dialogs are
driven by calling their save methods directly, never exec(), so no test
can hang on a modal loop.
"""

import os
import sys
import tempfile
import unittest

if not os.environ.get("DISPLAY"):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog,
                               QDialogButtonBox, QGroupBox, QLabel,
                               QPushButton, QRadioButton, QWidget)

from syllaport import anim
from syllaport import catalog as catalog_mod
from syllaport import checklist as checklist_mod
from syllaport import data as data_mod
from syllaport import dialogs as dialogs_mod
from syllaport import tour as tour_mod
from syllaport.store import Store
from syllaport.windows import WindowManager

APP = None
SETTINGS_DIR = None


def setUpModule():
    global APP, SETTINGS_DIR
    SETTINGS_DIR = tempfile.TemporaryDirectory()
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope,
                      SETTINGS_DIR.name)
    APP = QApplication.instance() or QApplication(sys.argv[:1])


def tearDownModule():
    global SETTINGS_DIR
    if SETTINGS_DIR is not None:
        SETTINGS_DIR.cleanup()


class GuiTestCase(unittest.TestCase):
    """One WindowManager per test class (8 windows are expensive to
    build under load); every test gets fresh data via replace_data."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.store = Store(cls.tmp.name)
        cls.manager = WindowManager(cls.store, APP)

    @classmethod
    def tearDownClass(cls):
        for window in cls.manager.windows:
            window.close()
        if cls.manager.how_to_window is not None:
            cls.manager.how_to_window.close()
        cls.tmp.cleanup()

    def setUp(self):
        if self.manager.how_to_window is not None:
            self.manager.how_to_window.close()
            self.manager.how_to_window = None
        self.store.replace_data(data_mod.default_data())
        # Per-window transient state that replace_data does not reset.
        self.manager.windows[0]._done_before = set()
        self.manager.windows[0]._tour_dialog = None
        self.manager.windows[1]._selected_id = None
        self.manager.show_window(0)


class WindowTests(GuiTestCase):
    def test_all_eight_windows_open(self):
        titles = ["Dashboard", "Courses", "Schedule", "Notebook",
                  "Work Log", "Account", "Backup", "Settings"]
        for index, title in enumerate(titles):
            self.manager.show_window(index)
            window = self.manager.windows[index]
            self.assertTrue(window.isVisible(), title)
            self.assertIn(title, window.windowTitle())

    def test_every_window_has_the_full_menu_bar(self):
        for window in self.manager.windows:
            menus = [a.text() for a in window.menuBar().actions()]
            self.assertIn("&File", menus)
            self.assertIn("&View", menus)
            self.assertIn("&Tools", menus)
            self.assertIn("&Help", menus)

    def test_view_menu_checkmark_follows_active_window(self):
        self.manager.show_window(3)
        for window in self.manager.windows:
            self.assertTrue(window.view_actions[3].isChecked())
            self.assertFalse(window.view_actions[0].isChecked())

    def test_rail_has_eight_entries_and_collapses(self):
        window = self.manager.windows[0]
        self.assertEqual(len(window.rail_buttons), 8)
        self.assertEqual(window.rail.width(), 200)
        self.manager.toggle_rail()
        self.assertEqual(window.rail.width(), 56)
        self.assertEqual(window.rail_buttons[0].text(), "DA")
        self.manager.toggle_rail()
        self.assertEqual(window.rail.width(), 200)
        self.assertEqual(window.rail_buttons[0].text(), "Dashboard")

    def test_status_bar_shows_ready(self):
        window = self.manager.windows[0]
        window.set_status("Ready")
        self.assertEqual(window.status_text.text(), "Ready")
        window.set_status("Saved")
        self.assertEqual(window.status_text.text(), "Saved")


class NoAmpersandTests(GuiTestCase):
    def test_no_bare_ampersand_in_visible_labels(self):
        # U11: Qt eats & as a mnemonic marker. Menu mnemonics are the
        # mechanism; visible label text must never contain one.
        # QDialogButtonBox standard buttons are Qt's own text, skipped.
        for window in self.manager.windows:
            self.manager.show_window(self.manager.windows.index(window))
            for widget in window.findChildren(QWidget):
                if not isinstance(widget, (QLabel, QPushButton, QCheckBox,
                                           QRadioButton, QGroupBox)):
                    continue
                parent = widget.parent()
                inside_box = False
                while parent is not None:
                    if isinstance(parent, QDialogButtonBox):
                        inside_box = True
                        break
                    parent = parent.parent()
                if inside_box:
                    continue
                self.assertNotIn("&", widget.text(),
                                 "%s in %s" % (widget.text(),
                                               window.windowTitle()))


class ChecklistFlowTests(GuiTestCase):
    def _complete_profile(self):
        dialog = dialogs_mod.ProfileDialog(self.store)
        dialog.name_edit.setText("Test User")
        dialog.save()
        self.assertEqual(dialog.result(), QDialog.Accepted)
        self.assertEqual(self.store.data["profile"]["name"], "Test User")

    def _complete_first_class(self):
        dialog = dialogs_mod.CatalogPickerDialog(self.store)
        dialog.course_list.setCurrentRow(0)
        self.assertIsNotNone(dialog.selected_course())
        dialog.add_selected()
        self.assertEqual(dialog.result(), QDialog.Accepted)
        self.assertEqual(len(self.store.data["courses"]), 1)

    def _complete_pace(self):
        dialog = dialogs_mod.PaceDialog(self.store)
        dialog.radios[1].setChecked(True)  # 1.0 units a week
        dialog.save()
        self.assertEqual(dialog.result(), QDialog.Accepted)
        self.assertEqual(data_mod.seed_pace(self.store.data), 1.0)

    def _complete_start_date(self):
        dialog = dialogs_mod.StartDateDialog(self.store)
        dialog.save()
        self.assertEqual(dialog.result(), QDialog.Accepted)
        self.assertIsNotNone(data_mod.term_start(self.store.data))

    def _complete_tour(self):
        dialog = tour_mod.TourDialog(self.store, self.manager)
        while dialog.index < len(tour_mod.STEPS) - 1:
            dialog.go_next()
        dialog.finish()
        self.assertEqual(dialog.result(), QDialog.Accepted)

    def test_checklist_completes_end_to_end_and_persists(self):
        self.assertTrue(checklist_mod.show_checklist(self.store.data))
        self._complete_profile()
        self._complete_first_class()
        self._complete_pace()
        self._complete_start_date()
        self._complete_tour()
        self.assertTrue(checklist_mod.is_complete(self.store.data))
        self.assertFalse(checklist_mod.show_checklist(self.store.data))
        reloaded = Store(self.tmp.name)
        self.assertTrue(checklist_mod.is_complete(reloaded.data))
        self.assertEqual(reloaded.data["profile"]["name"], "Test User")
        self.assertEqual(len(reloaded.data["courses"]), 1)

    def test_dashboard_hero_shows_checklist_then_do_now(self):
        dashboard = self.manager.windows[0]
        self.manager.show_window(0)
        texts = [b.text() for b in
                 dashboard.hero.findChildren(QPushButton)]
        self.assertIn("Create profile", texts)
        self.assertIn("Skip setup for now", texts)
        self._complete_profile()
        self._complete_first_class()
        self._complete_pace()
        self._complete_start_date()
        self._complete_tour()
        dashboard.refresh()
        texts = [b.text() for b in
                 dashboard.hero.findChildren(QPushButton)]
        self.assertIn("Open Courses", texts)

    def test_skip_and_resume_checklist(self):
        dashboard = self.manager.windows[0]
        dashboard._skip_setup()
        self.assertTrue(self.store.data["checklist_dismissed"])
        texts = [b.text() for b in
                 dashboard.hero.findChildren(QPushButton)]
        self.assertIn("Resume setup", texts)
        settings = self.manager.windows[7]
        settings._reopen_checklist()
        self.assertFalse(self.store.data["checklist_dismissed"])
        self.assertTrue(checklist_mod.show_checklist(self.store.data))

    def test_profile_requires_a_name(self):
        dialog = dialogs_mod.ProfileDialog(self.store)
        dialog.show()
        APP.processEvents()
        dialog.save()
        self.assertNotEqual(dialog.result(), QDialog.Accepted)
        self.assertTrue(dialog.message.isVisible())
        self.assertEqual(self.store.data["profile"]["name"], "")
        dialog.close()

    def test_pace_requires_a_choice(self):
        dialog = dialogs_mod.PaceDialog(self.store)
        dialog.show()
        APP.processEvents()
        dialog.save()
        self.assertNotEqual(dialog.result(), QDialog.Accepted)
        self.assertTrue(dialog.message.isVisible())
        dialog.close()

    def test_tour_skip_leaves_step_undone(self):
        dialog = tour_mod.TourDialog(self.store, self.manager)
        dialog.reject()
        state = checklist_mod.checklist_state(self.store.data)
        self.assertFalse(state["tour"])

    def test_tour_show_me_opens_windows(self):
        dialog = tour_mod.TourDialog(self.store, self.manager)
        dialog.go_next()  # Dashboard step
        dialog.show_window()
        self.assertEqual(self.manager.active_index, 0)
        dialog.go_next()  # Courses step
        dialog.show_window()
        self.assertEqual(self.manager.active_index, 1)


class NoDefaultSelectionTests(GuiTestCase):
    def test_picker_starts_unselected(self):
        dialog = dialogs_mod.CatalogPickerDialog(self.store)
        self.assertEqual(dialog.subject_combo.currentIndex(), -1)
        self.assertEqual(dialog.course_list.currentRow(), -1)
        self.assertFalse(dialog.add_button.isEnabled())

    def test_guided_pick_starts_unselected(self):
        dialog = dialogs_mod.GuidedPickDialog(self.store)
        self.assertEqual(dialog.subject_list.currentRow(), -1)
        self.assertFalse(dialog.pick_button.isEnabled())

    def test_add_known_class_starts_unselected(self):
        dialog = dialogs_mod.AddKnownClassDialog(self.store)
        self.assertEqual(dialog.source_combo.currentIndex(), -1)

    def test_pace_starts_unselected(self):
        dialog = dialogs_mod.PaceDialog(self.store)
        self.assertIsNone(dialog.chosen_pace())
        self.assertFalse(any(r.isChecked() for r in dialog.radios))


class CoursesTests(GuiTestCase):
    def test_empty_state_offers_three_teaching_choices(self):
        window = self.manager.windows[1]
        self.manager.show_window(1)
        texts = [b.text() for b in window.findChildren(QPushButton)]
        self.assertIn("Browse the catalog", texts)
        self.assertIn("Add a class you already know", texts)
        self.assertIn("Start with a guided pick", texts)

    def test_guided_pick_adds_the_top_pick(self):
        dialog = dialogs_mod.GuidedPickDialog(self.store)
        dialog.subject_list.setCurrentRow(4)  # Coding
        self.assertEqual(dialog._pick["id"], "cs50x")
        dialog.add_pick()
        self.assertEqual(len(self.store.data["courses"]), 1)
        self.assertEqual(self.store.data["courses"][0]["title"],
                         catalog_mod.COURSE_BY_ID["cs50x"]["title"])

    def test_guided_pick_music_has_no_runner_up(self):
        dialog = dialogs_mod.GuidedPickDialog(self.store)
        dialog.subject_list.setCurrentRow(6)  # Music
        self.assertEqual(dialog._pick["id"], "mit-21m385")
        self.assertTrue(dialog.runner_box.isHidden())

    def test_add_known_class_validates(self):
        dialog = dialogs_mod.AddKnownClassDialog(self.store)
        dialog.save()
        self.assertNotEqual(dialog.result(), QDialog.Accepted)
        dialog.name_edit.setText("My Class")
        dialog.save()
        self.assertNotEqual(dialog.result(), QDialog.Accepted)
        dialog.source_combo.setCurrentIndex(0)
        dialog.save()
        self.assertEqual(dialog.result(), QDialog.Accepted)
        self.assertEqual(self.store.data["courses"][0]["title"], "My Class")
        self.assertEqual(self.store.data["courses"][0]["source_id"],
                         catalog_mod.SOURCES[0]["id"])

    def test_courses_list_shows_added_class(self):
        data_mod.add_course(self.store.data, "CS50x", "harvard-cs50",
                            "Harvard CS50")
        self.store.save()
        window = self.manager.windows[1]
        self.manager.show_window(1)
        self.assertEqual(window.course_list.count(), 1)
        window.course_list.setCurrentRow(0)
        self.assertIn("CS50x", window.details.text())


class PresetTests(GuiTestCase):
    def test_larger_text_changes_the_stylesheet(self):
        self.manager.set_preset("larger_text", True)
        self.assertIn("font-size: 18px", APP.styleSheet())
        self.assertTrue(self.store.preset("larger_text"))

    def test_high_contrast_changes_the_stylesheet(self):
        self.manager.set_preset("high_contrast", True)
        self.assertIn("QMainWindow, QDialog { background: #ffffff; }",
                      APP.styleSheet())
        self.assertTrue(self.store.preset("high_contrast"))

    def test_reduced_motion_skips_animation(self):
        label = QLabel("tick")
        self.manager.set_preset("reduced_motion", True)
        self.assertIsNone(anim.fade_in(label, self.store))
        self.assertTrue(label.isVisible())
        self.manager.set_preset("reduced_motion", False)
        self.assertIsNotNone(anim.fade_in(label, self.store))

    def test_preset_menu_and_settings_stay_in_sync(self):
        self.manager.set_preset("larger_text", True)
        window = self.manager.windows[0]
        self.assertTrue(window.preset_actions["larger_text"].isChecked())
        settings = self.manager.windows[7]
        settings.refresh()
        self.assertTrue(settings.preset_boxes["larger_text"].isChecked())

    def test_settings_checkbox_toggles_preset(self):
        settings = self.manager.windows[7]
        box = settings.preset_boxes["high_contrast"]
        box.setChecked(True)
        self.assertTrue(self.store.preset("high_contrast"))
        box.setChecked(False)
        self.assertFalse(self.store.preset("high_contrast"))


class DashboardTileTests(GuiTestCase):
    def test_tiles_show_real_numbers(self):
        window = self.manager.windows[0]
        self.manager.show_window(0)
        big, _sub = window._tile_labels["Your pace"]
        self.assertEqual(big.text(), "1.0")
        big, _sub = window._tile_labels["My classes"]
        self.assertEqual(big.text(), "0")
        big, _sub = window._tile_labels["Streak"]
        self.assertEqual(big.text(), "0")
        big, _sub = window._tile_labels["Time in"]
        self.assertEqual(big.text(), "0 min")

    def test_tiles_update_when_a_class_is_added(self):
        data_mod.add_course(self.store.data, "CS50x", "harvard-cs50",
                            "Harvard CS50")
        self.store.save()
        window = self.manager.windows[0]
        big, _sub = window._tile_labels["My classes"]
        self.assertEqual(big.text(), "1")


class HelpAndBackupTests(GuiTestCase):
    def test_how_to_use_index_opens_with_topics(self):
        self.manager.how_to_action()
        howto = self.manager.how_to_window
        self.assertIsNotNone(howto)
        self.assertTrue(howto.isVisible())
        self.assertEqual(howto.topic_list.count(), 12)
        howto.topic_list.setCurrentRow(0)
        self.assertIn("setup checklist", howto.text.toPlainText())

    def test_debug_report_builds(self):
        from syllaport import debuglog
        report = debuglog.build_report(str(self.store.path),
                                       str(self.store.log_path))
        self.assertIn("Syllaport debug report", report)
        self.assertIn("Version:", report)

    def test_backup_window_lists_backups_after_saves(self):
        self.store.save()
        self.store.save()
        window = self.manager.windows[6]
        self.manager.show_window(6)
        self.assertGreaterEqual(window.backup_list.count(), 1)
        self.assertIn("data.json.bak1",
                      window.backup_list.item(0).text())


if __name__ == "__main__":
    unittest.main()
