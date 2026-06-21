"""Tests for the sidebar ContextList logic.

Pure Python — no LibreOffice/UNO. sidebar.py imports ``uno`` lazily (only inside
the config-access helpers), so the ContextList parsing/editing functions import
and run without LibreOffice. The live apply/restore is verified separately
against a throwaway instance / in the GUI.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from louim.adapters.writer.sidebar import (  # noqa: E402
    shows_in_writer, strip_writer, NON_WRITER_DECK_APPS,
)


class ShowsInWriterTest(unittest.TestCase):
    def test_writer_variants_shows(self):
        self.assertTrue(shows_in_writer(["WriterVariants, any, visible"]))

    def test_plain_writer_shows(self):
        self.assertTrue(shows_in_writer(["Writer, AnyContext, hidden"]))

    def test_any_shows(self):
        self.assertTrue(shows_in_writer(["any, any, visible"]))

    def test_non_writer_does_not_show(self):
        self.assertFalse(shows_in_writer(["Calc, any, visible",
                                          "DrawImpress, any, visible"]))

    def test_empty_does_not_show(self):
        self.assertFalse(shows_in_writer([]))


class StripWriterTest(unittest.TestCase):
    def test_drops_writer_keeps_others(self):
        out = strip_writer(["WriterVariants, any, visible",
                            "Calc, any, visible"])
        self.assertEqual(out, ["Calc, any, visible"])
        self.assertFalse(shows_in_writer(out))

    def test_any_expands_to_non_writer_apps(self):
        out = strip_writer(["any, any, visible"])
        self.assertEqual(out, ["%s, any, visible" % a for a in NON_WRITER_DECK_APPS])
        self.assertFalse(shows_in_writer(out))

    def test_writer_only_deck_becomes_empty(self):
        out = strip_writer(["Writer, SomeContext, hidden"])
        self.assertEqual(out, [])
        self.assertFalse(shows_in_writer(out))

    def test_non_writer_entries_untouched(self):
        entries = ["Calc, any, visible", "DrawImpress, any, hidden"]
        self.assertEqual(strip_writer(entries), entries)

    def test_mixed_writer_groups_all_dropped(self):
        out = strip_writer([
            "WriterVariants, any, visible",
            "WriterGlobal, any, visible",
            "Calc, any, visible",
        ])
        self.assertEqual(out, ["Calc, any, visible"])

    def test_round_trip_idempotent_after_strip(self):
        # Stripping an already-stripped list changes nothing further.
        once = strip_writer(["WriterVariants, any, visible", "Calc, any, visible"])
        twice = strip_writer(once)
        self.assertEqual(once, twice)


if __name__ == "__main__":
    unittest.main()
