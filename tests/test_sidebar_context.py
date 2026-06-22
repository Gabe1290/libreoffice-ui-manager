"""Tests for the sidebar ContextList logic (module-parameterized).

Pure Python — no LibreOffice/UNO. sidebar.py imports ``uno`` lazily, so the
ContextList parsing/editing functions import and run without LibreOffice.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from louim.adapters.writer.sidebar import (  # noqa: E402
    shows_in_module, strip_module,
)
from louim.adapters.modules import WRITER, CALC, IMPRESS  # noqa: E402


class ShowsInModuleTest(unittest.TestCase):
    def test_writer_variants_shows_in_writer(self):
        self.assertTrue(shows_in_module(["WriterVariants, any, visible"], WRITER))

    def test_any_shows_in_any_module(self):
        self.assertTrue(shows_in_module(["any, any, visible"], WRITER))
        self.assertTrue(shows_in_module(["any, any, visible"], CALC))

    def test_calc_shows_in_calc_not_writer(self):
        self.assertTrue(shows_in_module(["Calc, any, visible"], CALC))
        self.assertFalse(shows_in_module(["Calc, any, visible"], WRITER))

    def test_writer_does_not_show_in_calc(self):
        self.assertFalse(shows_in_module(["WriterVariants, any, visible"], CALC))

    def test_empty_does_not_show(self):
        self.assertFalse(shows_in_module([], WRITER))


class StripModuleTest(unittest.TestCase):
    def test_writer_drops_writer_keeps_others(self):
        out = strip_module(["WriterVariants, any, visible", "Calc, any, visible"],
                           WRITER)
        self.assertEqual(out, ["Calc, any, visible"])
        self.assertFalse(shows_in_module(out, WRITER))

    def test_calc_drops_calc_keeps_writer(self):
        out = strip_module(["WriterVariants, any, visible", "Calc, any, visible"],
                           CALC)
        self.assertEqual(out, ["WriterVariants, any, visible"])
        self.assertFalse(shows_in_module(out, CALC))

    def test_any_expands_to_other_apps(self):
        out = strip_module(["any, any, visible"], WRITER)
        self.assertEqual(out,
                         ["%s, any, visible" % a for a in WRITER.other_deck_apps])
        self.assertFalse(shows_in_module(out, WRITER))

    def test_module_only_deck_becomes_empty(self):
        self.assertEqual(strip_module(["Writer, SomeContext, hidden"], WRITER), [])
        self.assertEqual(strip_module(["Calc, SomeContext, hidden"], CALC), [])

    def test_non_module_entries_untouched(self):
        entries = ["Calc, any, visible", "DrawImpress, any, hidden"]
        self.assertEqual(strip_module(entries, WRITER), entries)

    def test_round_trip_idempotent_after_strip(self):
        once = strip_module(["WriterVariants, any, visible", "Calc, any, visible"],
                            WRITER)
        self.assertEqual(strip_module(once, WRITER), once)


class ImpressGroupTest(unittest.TestCase):
    """DrawImpress is shared with Draw — hiding from Impress must keep Draw."""

    def test_drawimpress_shows_in_impress(self):
        self.assertTrue(shows_in_module(["DrawImpress, any, visible"], IMPRESS))

    def test_strip_impress_replaces_group_with_draw(self):
        out = strip_module(["DrawImpress, any, visible"], IMPRESS)
        self.assertEqual(out, ["Draw, any, visible"])
        self.assertFalse(shows_in_module(out, IMPRESS))
        # Crucially, the deck still shows in Draw.
        from louim.adapters.modules import Module
        draw = Module("draw", "s", "n", ("Draw", "DrawImpress"),
                      ("Impress",), ("c",), ("o",),
                      deck_group_subs={"DrawImpress": ("Impress",)})
        self.assertTrue(shows_in_module(out, draw))

    def test_plain_impress_entry_dropped(self):
        self.assertEqual(strip_module(["Impress, any, visible"], IMPRESS), [])


if __name__ == "__main__":
    unittest.main()
