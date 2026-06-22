"""Tests for the module descriptors (Writer/Calc routing)."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from louim.adapters.modules import (  # noqa: E402
    WRITER, CALC, IMPRESS, MODULES, get_module, module_for_document,
)


class _FakeDoc:
    def __init__(self, *services):
        self._services = set(services)

    def supportsService(self, name):
        return name in self._services


class ModuleTest(unittest.TestCase):
    def test_keys(self):
        self.assertEqual(WRITER.key, "writer")
        self.assertEqual(CALC.key, "calc")
        self.assertEqual(IMPRESS.key, "impress")
        self.assertEqual(set(MODULES), {"writer", "calc", "impress"})

    def test_get_module(self):
        self.assertIs(get_module("writer"), WRITER)
        self.assertIs(get_module("calc"), CALC)
        self.assertIs(get_module("impress"), IMPRESS)
        self.assertIsNone(get_module("draw"))

    def test_impress_shares_drawimpress_group_with_draw(self):
        self.assertIn("DrawImpress", IMPRESS.deck_apps)
        self.assertEqual(IMPRESS.deck_group_subs["DrawImpress"], ("Draw",))

    def test_distinct_windowstate_nodes(self):
        self.assertIn("WriterWindowState", WRITER.windowstate_node)
        self.assertIn("CalcWindowState", CALC.windowstate_node)
        self.assertNotEqual(WRITER.windowstate_node, CALC.windowstate_node)

    def test_module_for_document(self):
        self.assertIs(module_for_document(_FakeDoc(WRITER.doc_service)), WRITER)
        self.assertIs(module_for_document(_FakeDoc(CALC.doc_service)), CALC)
        self.assertIsNone(module_for_document(_FakeDoc("com.sun.star.other")))

    def test_calc_contexts_are_spreadsheet(self):
        self.assertIn("com.sun.star.sheet.SpreadsheetDocument", CALC.addon_contexts)
        self.assertNotIn("com.sun.star.sheet.SpreadsheetDocument",
                         WRITER.addon_contexts)


if __name__ == "__main__":
    unittest.main()
