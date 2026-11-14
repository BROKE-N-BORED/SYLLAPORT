"""Tests for the verified $0 catalog: integrity, not invention."""

import unittest

from syllaport import catalog as c

# The em-dash character, spelled out so this file never contains one
# literally (the tree-wide U33 test scans this file too).
EMDASH = chr(0x2014)


class SourceTests(unittest.TestCase):
    def test_nineteen_sources(self):
        self.assertEqual(len(c.SOURCES), 19)

    def test_source_ids_unique(self):
        ids = [s["id"] for s in c.SOURCES]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_source_has_url_signup_certificate(self):
        for source in c.SOURCES:
            self.assertTrue(source["url"].startswith("http"),
                            source["id"])
            self.assertTrue(source["signup"], source["id"])
            self.assertTrue(source["certificate"], source["id"])
            self.assertTrue(source["subjects"], source["id"])

    def test_no_coursera_source(self):
        # Coursera fails the $0 filter (preview only since 2026-08-08).
        names = " ".join(s["name"] for s in c.SOURCES).lower()
        self.assertNotIn("coursera", names)


class CourseTests(unittest.TestCase):
    def test_course_ids_unique(self):
        ids = [course["id"] for course in c.COURSES]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_course_names_a_real_source(self):
        for course in c.COURSES:
            self.assertIn(course["source_id"], c.SOURCE_BY_ID, course["id"])

    def test_every_course_has_subject_url_blurb(self):
        for course in c.COURSES:
            self.assertIn(course["subject"], c.SUBJECTS, course["id"])
            self.assertTrue(course["url"].startswith("http"), course["id"])
            self.assertTrue(course["blurb"], course["id"])
            self.assertTrue(course["certificate"], course["id"])

    def test_every_subject_has_courses(self):
        for subject in c.SUBJECTS:
            self.assertTrue(c.courses_for_subject(subject), subject)

    def test_cs50x_is_the_coding_anchor(self):
        course = c.COURSE_BY_ID["cs50x"]
        self.assertEqual(course["subject"], "Coding")
        self.assertIn("Free CS50 Certificate", course["certificate"])

    def test_managing_my_money_has_its_hours(self):
        course = c.COURSE_BY_ID["ou-money"]
        self.assertEqual(course["length"], "24 hours")

    def test_search_finds_by_school_and_word(self):
        self.assertTrue(any(x["id"] == "cs50x"
                            for x in c.search_courses("harvard")))
        self.assertTrue(any(x["id"] == "ou-money"
                            for x in c.search_courses("money")))
        self.assertEqual(len(c.search_courses("")), len(c.COURSES))
        self.assertEqual(c.search_courses("zzz-no-such-word-zzz"), [])


class GuidedPickTests(unittest.TestCase):
    def test_every_subject_has_a_pick(self):
        for subject in c.SUBJECTS:
            pick_id, _runner = c.SUBJECT_PICKS[subject]
            self.assertIn(pick_id, c.COURSE_BY_ID, subject)

    def test_picks_match_their_subject(self):
        for subject, (pick_id, runner_id) in c.SUBJECT_PICKS.items():
            self.assertEqual(c.COURSE_BY_ID[pick_id]["subject"], subject)
            if runner_id is not None:
                self.assertEqual(c.COURSE_BY_ID[runner_id]["subject"],
                                 subject)

    def test_music_has_no_runner_up(self):
        # The report verifies no second fully free music anchor.
        _pick, runner = c.SUBJECT_PICKS["Music"]
        self.assertIsNone(runner)


class NoEmDashTests(unittest.TestCase):
    def test_no_em_dashes_in_catalog_strings(self):
        # U33: no em-dashes in visible UI text. The catalog is UI text.
        for source in c.SOURCES:
            for value in source.values():
                if isinstance(value, str):
                    self.assertNotIn(EMDASH, value, source["id"])
                elif isinstance(value, list):
                    for item in value:
                        self.assertNotIn(EMDASH, item, source["id"])
        for course in c.COURSES:
            for value in course.values():
                if isinstance(value, str):
                    self.assertNotIn(EMDASH, value, course["id"])

    def test_no_ampersand_in_catalog_titles(self):
        # U11: visible labels use "and", never bare "&".
        for course in c.COURSES:
            self.assertNotIn("&", course["title"], course["id"])
        for source in c.SOURCES:
            self.assertNotIn("&", source["name"], source["id"])


if __name__ == "__main__":
    unittest.main()
