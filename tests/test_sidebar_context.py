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
    shows_in_module, strip_module, merge_context_list,
)
from louim.adapters.modules import WRITER, CALC, IMPRESS, DRAW  # noqa: E402


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


def _restore(current, record, module):
    """The ContextList restore writes: exact undo, or compositional re-add."""
    if current == record["result"]:
        return record["original"]
    return merge_context_list(current, record["original"], module)


class MergeContextListTest(unittest.TestCase):
    def test_any_original_readds_only_module_apps(self):
        merged = merge_context_list(["Chart, any, visible"],
                                    ["any, any, visible"], WRITER)
        self.assertTrue(shows_in_module(merged, WRITER))
        # "any" itself is never re-added — Calc's hide would be undone.
        self.assertFalse(shows_in_module(merged, CALC))
        self.assertIn("Chart, any, visible", merged)

    def test_group_original_readds_plain_app_only(self):
        # Restoring Impress from a shared DrawImpress entry must not
        # resurrect the deck in Draw (which may still hide it).
        merged = merge_context_list([], ["DrawImpress, any, visible"], IMPRESS)
        self.assertEqual(merged, ["Impress, any, visible"])
        self.assertTrue(shows_in_module(merged, IMPRESS))
        self.assertFalse(shows_in_module(merged, DRAW))

    def test_no_duplicates(self):
        merged = merge_context_list(["Calc, any, visible"],
                                    ["Calc, any, visible"], CALC)
        self.assertEqual(merged, ["Calc, any, visible"])

    def test_unrelated_original_adds_nothing(self):
        merged = merge_context_list(["Chart, any, visible"],
                                    ["Math, any, visible"], WRITER)
        self.assertEqual(merged, ["Chart, any, visible"])


class CrossModuleRestoreScenarioTest(unittest.TestCase):
    """Hide the same deck in Writer and Calc, restore in both orders."""

    def _hide_both(self):
        original = ["any, any, visible"]
        result_w = strip_module(original, WRITER)
        record_w = {"original": original, "result": result_w}
        result_c = strip_module(result_w, CALC)
        record_c = {"original": result_w, "result": result_c}
        return record_w, record_c, result_c

    def test_restore_in_hide_order_keeps_calc_hidden(self):
        record_w, record_c, current = self._hide_both()
        current = _restore(current, record_w, WRITER)
        self.assertTrue(shows_in_module(current, WRITER))
        self.assertFalse(shows_in_module(current, CALC))
        current = _restore(current, record_c, CALC)
        self.assertTrue(shows_in_module(current, WRITER))
        self.assertTrue(shows_in_module(current, CALC))

    def test_restore_in_reverse_order_is_exact(self):
        record_w, record_c, current = self._hide_both()
        current = _restore(current, record_c, CALC)
        self.assertTrue(shows_in_module(current, CALC))
        self.assertFalse(shows_in_module(current, WRITER))
        # Writer's turn finds the list exactly as it left it: pristine undo.
        current = _restore(current, record_w, WRITER)
        self.assertEqual(current, ["any, any, visible"])


if __name__ == "__main__":
    unittest.main()
