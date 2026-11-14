"""Tests for the first-run checklist model (entry 020)."""

import unittest

from syllaport import checklist as c
from syllaport import data as d


class ChecklistTests(unittest.TestCase):
    def test_five_steps_in_order(self):
        self.assertEqual(c.STEP_ORDER,
                         ["profile", "first_class", "pace", "start_date",
                          "tour"])
        for step in c.STEP_ORDER:
            self.assertIn(step, c.STEPS)
            self.assertTrue(c.STEPS[step]["title"])
            self.assertTrue(c.STEPS[step]["detail"])
            self.assertTrue(c.STEPS[step]["button"])

    def test_fresh_data_shows_checklist(self):
        data = d.default_data()
        self.assertTrue(c.show_checklist(data))
        self.assertEqual(c.done_count(data), 0)
        self.assertFalse(c.is_complete(data))

    def test_mark_done_counts_and_completes(self):
        data = d.default_data()
        self.assertTrue(c.mark_done(data, "profile"))
        self.assertFalse(c.mark_done(data, "profile"))  # already done
        self.assertEqual(c.done_count(data), 1)
        for step in ("first_class", "pace", "start_date", "tour"):
            c.mark_done(data, step)
        self.assertTrue(c.is_complete(data))
        self.assertFalse(c.show_checklist(data))

    def test_unknown_step_is_ignored(self):
        data = d.default_data()
        self.assertFalse(c.mark_done(data, "not-a-step"))
        self.assertEqual(c.done_count(data), 0)

    def test_dismissed_checklist_hides(self):
        data = d.default_data()
        data["checklist_dismissed"] = True
        self.assertFalse(c.show_checklist(data))
        self.assertFalse(c.is_complete(data))

    def test_partial_checklist_state_fills_in(self):
        data = d.default_data()
        data["checklist"] = {"profile": True}
        state = c.checklist_state(data)
        self.assertTrue(state["profile"])
        self.assertFalse(state["tour"])


if __name__ == "__main__":
    unittest.main()
