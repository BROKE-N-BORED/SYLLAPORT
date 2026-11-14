"""Tests for the stylesheet builder and the tree-wide copy rules."""

import os
import unittest

from syllaport import style as s

TREE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The em-dash character, spelled out so this file never contains one
# literally (the tree-wide U33 test scans this file too).
EMDASH = chr(0x2014)


class StylesheetTests(unittest.TestCase):
    def test_palette_hexes_present(self):
        sheet = s.build_stylesheet()
        for hex_value in ("#f7f1e3", "#fffdf6", "#141414", "#b6e61e",
                          "#d8d0ba", "#222222"):
            self.assertIn(hex_value, sheet)

    def test_focus_ring_is_two_px_solid(self):
        sheet = s.build_stylesheet()
        self.assertIn("border: 2px solid", sheet)
        self.assertNotIn("1px dotted", sheet)
        self.assertNotIn("outline: 1px", sheet)

    def test_type_scale_present(self):
        sheet = s.build_stylesheet()
        for size in ("font-size: 30px", "font-size: 24px",
                     "font-size: 19px", "font-size: 14px"):
            self.assertIn(size, sheet)

    def test_larger_text_scales_body(self):
        base = s.build_stylesheet()
        large = s.build_stylesheet({"larger_text": True})
        self.assertIn("font-size: 14px", base)
        self.assertIn("font-size: 18px", large)
        self.assertIn("font-size: 30px", large)  # title grows 24 -> 30

    def test_high_contrast_swaps_surfaces(self):
        sheet = s.build_stylesheet({"high_contrast": True})
        self.assertIn("QMainWindow, QDialog { background: #ffffff; }", sheet)
        self.assertIn("#000000", sheet)

    def test_presets_combine(self):
        sheet = s.build_stylesheet({"larger_text": True,
                                    "high_contrast": True})
        self.assertIn("font-size: 18px", sheet)
        self.assertIn("QMainWindow, QDialog { background: #ffffff; }", sheet)

    def test_no_em_dash_in_stylesheet(self):
        self.assertNotIn(EMDASH, s.build_stylesheet())


class TreeCopyTests(unittest.TestCase):
    """U33 (no em-dashes) and no leftover stubs, enforced on the tree."""

    def _tree_files(self, suffixes):
        out = []
        for root, dirs, files in os.walk(TREE):
            dirs[:] = [d for d in dirs
                       if d not in ("__pycache__", ".git", "verify")]
            for name in files:
                if name.endswith(suffixes):
                    out.append(os.path.join(root, name))
        return out

    def test_no_em_dash_anywhere(self):
        offenders = []
        for path in self._tree_files((".py", ".md", ".svg", ".txt")):
            with open(path, encoding="utf-8") as f:
                if EMDASH in f.read():
                    offenders.append(path)
        self.assertEqual(offenders, [])

    def test_no_todo_or_fixme_markers(self):
        # Markers spelled in parts so this file does not contain them.
        markers = ["TO" + "DO", "FIX" + "ME"]
        offenders = []
        for path in self._tree_files((".py",)):
            with open(path, encoding="utf-8") as f:
                text = f.read()
                if any(marker in text for marker in markers):
                    offenders.append(path)
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
