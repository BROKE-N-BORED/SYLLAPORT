"""Tests for the data model, storage, and pace engine (stdlib only)."""

import json
import os
import tempfile
import unittest
from datetime import date, timedelta

from syllaport import data as d


class DefaultDataTests(unittest.TestCase):
    def test_fresh_data_has_no_person(self):
        data = d.default_data()
        self.assertEqual(data["profile"]["name"], "")
        self.assertEqual(data["profile"]["start_date"], "")

    def test_fresh_data_has_no_courses_or_dates(self):
        data = d.default_data()
        self.assertEqual(data["courses"], [])
        self.assertEqual(data["settings"]["term_start"], "")
        self.assertIsNone(d.term_start(data))

    def test_fresh_data_checklist_all_undone(self):
        data = d.default_data()
        self.assertFalse(any(data["checklist"].values()))
        self.assertFalse(data["checklist_dismissed"])

    def test_seed_pace_default(self):
        self.assertEqual(d.seed_pace(d.default_data()), 1.0)


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "data.json")

    def tearDown(self):
        self.tmp.cleanup()

    def test_save_load_roundtrip(self):
        data = d.default_data()
        data["profile"]["name"] = "Test User"
        d.save_data(data, self.path)
        loaded = d.load_data(self.path)
        self.assertEqual(loaded["profile"]["name"], "Test User")

    def test_missing_file_gives_defaults(self):
        self.assertEqual(d.load_data(self.path)["profile"]["name"], "")

    def test_corrupt_file_gives_defaults(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("{not json")
        self.assertEqual(d.load_data(self.path)["profile"]["name"], "")

    def test_partial_file_fills_missing_keys(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"version": 1, "profile": {"name": "A"}}, f)
        loaded = d.load_data(self.path)
        self.assertEqual(loaded["profile"]["name"], "A")
        self.assertEqual(loaded["courses"], [])
        self.assertEqual(loaded["settings"]["seed_pace"], 1.0)
        self.assertFalse(loaded["checklist"]["tour"])

    def test_backups_rotate(self):
        data = d.default_data()
        for i in range(3):
            data["profile"]["name"] = "v%d" % i
            d.save_data(data, self.path)
        backups = d.list_backups(self.path)
        self.assertEqual(len(backups), 2)  # first save has nothing to back up
        self.assertEqual(backups[0][0], "data.json.bak1")

    def test_backup_now_writes_timestamped_copy(self):
        data = d.default_data()
        data["profile"]["name"] = "Keep Me"
        d.save_data(data, self.path)
        dest = d.backup_now(data, self.path)
        self.assertIsNotNone(dest)
        self.assertTrue(os.path.exists(dest))
        self.assertEqual(d.load_data(dest)["profile"]["name"], "Keep Me")

    def test_validate_backup(self):
        ok, _reason = d.validate_backup(d.default_data())
        self.assertTrue(ok)
        ok, _reason = d.validate_backup({"version": 1})
        self.assertFalse(ok)
        ok, _reason = d.validate_backup("nope")
        self.assertFalse(ok)
        ok, _reason = d.validate_backup({"version": 99, "courses": [],
                                         "completions": [], "notes": {}})
        self.assertFalse(ok)


class CourseTests(unittest.TestCase):
    def test_add_course_gets_unique_ids(self):
        data = d.default_data()
        a = d.add_course(data, "A", "mit-ocw", "MIT OCW")
        b = d.add_course(data, "B", "mit-ocw", "MIT OCW")
        self.assertNotEqual(a["id"], b["id"])
        self.assertEqual(len(data["courses"]), 2)

    def test_remove_course_keeps_log_entries(self):
        data = d.default_data()
        course = d.add_course(data, "A", "mit-ocw", "MIT OCW")
        data["completions"].append({"course_id": course["id"], "date": "2026-11-13",
                                    "minutes": 30, "note": "worked"})
        d.remove_course(data, course["id"])
        self.assertEqual(data["courses"], [])
        self.assertEqual(len(data["completions"]), 1)


class PaceTests(unittest.TestCase):
    def _data_with_units(self, total, first, today):
        data = d.default_data()
        course = d.add_course(data, "A", "mit-ocw", "MIT OCW")
        course["units"] = 10
        for i in range(1, total + 1):
            data["completions"].append({
                "course_id": course["id"],
                "unit_key": d.unit_key(course["id"], i),
                "date": first.isoformat(), "minutes": 50})
        return data, today

    def test_no_units_uses_seed(self):
        pace = d.compute_pace(d.default_data(), date(2026, 11, 13))
        self.assertIsNone(pace["measured"])
        self.assertEqual(pace["effective"], 1.0)
        self.assertEqual(pace["total_units"], 0)

    def test_one_unit_still_uses_seed(self):
        data, today = self._data_with_units(1, date(2026, 11, 6),
                                            date(2026, 11, 13))
        pace = d.compute_pace(data, today)
        self.assertEqual(pace["total_units"], 1)
        self.assertEqual(pace["effective"], 1.0)  # measured needs 2+ units

    def test_two_units_switch_to_measured(self):
        data, today = self._data_with_units(2, date(2026, 10, 30),
                                            date(2026, 11, 13))
        pace = d.compute_pace(data, today)
        self.assertEqual(pace["total_units"], 2)
        self.assertAlmostEqual(pace["measured"], 1.0)  # 2 units / 2 weeks
        self.assertAlmostEqual(pace["effective"], 1.0)

    def test_elapsed_weeks_floored_at_one(self):
        data, today = self._data_with_units(2, date(2026, 11, 13),
                                            date(2026, 11, 13))
        pace = d.compute_pace(data, today)
        self.assertEqual(pace["elapsed_weeks"], 1.0)
        self.assertAlmostEqual(pace["measured"], 2.0)

    def test_unknown_units_never_count(self):
        data = d.default_data()
        course = d.add_course(data, "A", "mit-ocw", "MIT OCW")
        # units is None: the key names no real unit, so it must not count.
        data["completions"].append({
            "course_id": course["id"],
            "unit_key": d.unit_key(course["id"], 1),
            "date": "2026-11-13", "minutes": 50})
        self.assertEqual(d.count_completed_units(data), 0)

    def test_unchecked_entries_do_not_count(self):
        data, today = self._data_with_units(2, date(2026, 10, 30),
                                            date(2026, 11, 13))
        data["completions"][0]["active"] = False
        self.assertEqual(d.count_completed_units(data), 1)

    def test_projected_finish(self):
        today = date(2026, 11, 13)
        self.assertEqual(d.projected_finish(0, 1.0, today), today)
        self.assertEqual(d.projected_finish(4, 1.0, today),
                         today + timedelta(weeks=4))
        self.assertEqual(d.projected_finish(5, 2.0, today),
                         today + timedelta(weeks=3))  # ceil(2.5)

    def test_snapshot_pace_records_once_per_week(self):
        data = d.default_data()
        today = date(2026, 11, 13)
        self.assertTrue(d.snapshot_pace(data, today))
        self.assertFalse(d.snapshot_pace(data, today))
        self.assertEqual(len(data["pace_history"]), 1)


class TimeTests(unittest.TestCase):
    def test_fmt_minutes(self):
        self.assertEqual(d.fmt_minutes(0), "0 min")
        self.assertEqual(d.fmt_minutes(45), "45 min")
        self.assertEqual(d.fmt_minutes(120), "2h")
        self.assertEqual(d.fmt_minutes(95), "1h 35m")

    def test_minutes_total_and_week(self):
        data = d.default_data()
        data["completions"].append({"date": "2026-11-13", "minutes": 50})
        data["completions"].append({"date": "2026-11-02", "minutes": 30})
        data["sessions"].append({"date": "2026-11-12", "minutes": 90})
        self.assertEqual(d.minutes_total(data), 170)
        # Week of 2026-11-13 starts Mon 2026-11-09: 50 + 90.
        self.assertEqual(d.minutes_this_week(data, date(2026, 11, 13)), 140)

    def test_streak(self):
        data = d.default_data()
        self.assertEqual(d.streak(data, date(2026, 11, 13)), 0)
        for day in ("2026-11-13", "2026-11-12", "2026-11-11"):
            data["completions"].append({"date": day, "minutes": 10})
        self.assertEqual(d.streak(data, date(2026, 11, 13)), 3)
        # Not logged today yet: streak counts back from yesterday.
        self.assertEqual(d.streak(data, date(2026, 11, 14)), 3)
        # A gap breaks it.
        data["completions"].append({"date": "2026-11-09", "minutes": 10})
        self.assertEqual(d.streak(data, date(2026, 11, 13)), 3)


class ExportTests(unittest.TestCase):
    def test_notes_markdown_empty_is_honest(self):
        text = d.notes_markdown(d.default_data())
        self.assertIn("No notes yet.", text)

    def test_notes_markdown_names_courses(self):
        data = d.default_data()
        course = d.add_course(data, "CS50x", "harvard-cs50", "Harvard CS50")
        data["notes"][course["id"]] = "Week 1 notes."
        data["notes"]["_general"] = "General note."
        text = d.notes_markdown(data)
        self.assertIn("## CS50x", text)
        self.assertIn("Week 1 notes.", text)
        self.assertIn("## General", text)

    def test_log_csv_header_and_rows(self):
        data = d.default_data()
        course = d.add_course(data, "CS50x", "harvard-cs50", "Harvard CS50")
        data["completions"].append({"date": "2026-11-13",
                                    "course_id": course["id"],
                                    "unit_label": "Week 1", "minutes": 50,
                                    "note": "did it"})
        text = d.log_csv(data)
        lines = text.strip().splitlines()
        self.assertEqual(lines[0], "date,course,unit,minutes,note")
        self.assertIn("CS50x", lines[1])
        self.assertIn("Week 1", lines[1])


if __name__ == "__main__":
    unittest.main()
