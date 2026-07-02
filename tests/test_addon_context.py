"""Tests for the addon Context logic (module-parameterized).

Pure Python — no LibreOffice/UNO. addons.py imports ``uno`` lazily, so the
Context parsing/merging functions import and run without LibreOffice.

The Context is one value shared by every application while LOUIM keeps state
per module, so these tests walk the cross-module scenarios end to end: hide the
same addon in two applications, then restore in both orders, asserting neither
order disturbs the other module's hide.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from louim.adapters.writer.addons import (  # noqa: E402
    _merge_context, _shows_in_module, _split,
)
from louim.adapters.modules import WRITER, CALC  # noqa: E402


def _hide(current, module):
    """The Context ``apply_addon_profile`` writes when hiding in ``module``."""
    remaining = [c for c in _split(current) if c not in module.addon_contexts]
    return ",".join(remaining) if remaining \
        else ",".join(module.other_addon_contexts)


def _restore(current, record, module):
    """The Context restore writes: exact undo, or compositional re-add."""
    if current == record["result"]:
        return record["original"]
    return _merge_context(current, record["original"], module)


class MergeContextTest(unittest.TestCase):
    def test_empty_original_grants_all_module_contexts(self):
        merged = _merge_context("com.sun.star.sheet.SpreadsheetDocument", "",
                                WRITER)
        self.assertTrue(_shows_in_module(merged, WRITER))
        # The other module's context is untouched.
        self.assertIn("com.sun.star.sheet.SpreadsheetDocument", _split(merged))

    def test_original_grants_only_its_own_contexts(self):
        original = ("com.sun.star.text.TextDocument,"
                    "com.sun.star.sheet.SpreadsheetDocument")
        merged = _merge_context("", original, WRITER)
        # Writer's service comes back; Calc's is NOT re-added by a Writer
        # restore, even though the original had it.
        self.assertIn("com.sun.star.text.TextDocument", _split(merged))
        self.assertNotIn("com.sun.star.sheet.SpreadsheetDocument",
                         _split(merged))

    def test_no_duplicates(self):
        current = "com.sun.star.text.TextDocument"
        merged = _merge_context(current, "", WRITER)
        parts = _split(merged)
        self.assertEqual(len(parts), len(set(parts)))


class CrossModuleScenarioTest(unittest.TestCase):
    """Hide in Writer and Calc, restore in both orders (original shows in all)."""

    def _hide_both(self):
        original = ""  # empty Context = every module
        result_w = _hide(original, WRITER)
        record_w = {"original": original, "result": result_w}
        result_c = _hide(result_w, CALC)
        record_c = {"original": result_w, "result": result_c}
        return record_w, record_c, result_c

    def test_restore_in_hide_order_keeps_calc_hidden(self):
        record_w, record_c, current = self._hide_both()
        # Restore Writer first: Writer comes back, Calc's hide must survive.
        current = _restore(current, record_w, WRITER)
        self.assertTrue(_shows_in_module(current, WRITER))
        self.assertFalse(_shows_in_module(current, CALC))
        # Then restore Calc: everything is visible again.
        current = _restore(current, record_c, CALC)
        self.assertTrue(_shows_in_module(current, WRITER))
        self.assertTrue(_shows_in_module(current, CALC))

    def test_restore_in_reverse_order_is_exact(self):
        record_w, record_c, current = self._hide_both()
        # Restore Calc first: nothing else touched the value, exact undo.
        current = _restore(current, record_c, CALC)
        self.assertTrue(_shows_in_module(current, CALC))
        self.assertFalse(_shows_in_module(current, WRITER))
        # Then restore Writer: back to the pristine empty Context.
        current = _restore(current, record_w, WRITER)
        self.assertEqual(current, "")

    def test_single_module_round_trip_is_exact(self):
        original = "com.sun.star.text.TextDocument"
        result = _hide(original, WRITER)
        self.assertFalse(_shows_in_module(result, WRITER))
        record = {"original": original, "result": result}
        self.assertEqual(_restore(result, record, WRITER), original)


if __name__ == "__main__":
    unittest.main()
