"""Tests for the .louim template saver / exporter.

Pure Python — no LibreOffice/UNO required, so these run in CI. The live snapshot
(`build_current_template`) needs a running Writer and is exercised by
tools/export-template.py, not here.
"""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from louim.template.saver import assemble_template, save_template  # noqa: E402
from louim.template.loader import load_template  # noqa: E402


class AssembleTemplateTest(unittest.TestCase):
    def test_shape_and_defaults(self):
        t = assemble_template("My Layout", "desc",
                              menus={".uno:ToolsMenu": False})
        self.assertEqual(t["application"], "writer")
        self.assertEqual(t["version"], 1)
        self.assertEqual(t["profile"]["name"], "My Layout")
        self.assertEqual(t["menus"], {".uno:ToolsMenu": False})
        # Optional maps default to empty objects, not None.
        self.assertEqual(t["addons"], {})
        self.assertEqual(t["toolbars"], {})

    def test_blank_name_falls_back(self):
        self.assertEqual(assemble_template("", "", menus={})["profile"]["name"],
                         "Untitled")

    def test_copies_inputs(self):
        # The assembled dict must not alias the caller's maps.
        menus = {".uno:EditMenu": True}
        t = assemble_template("n", "d", menus=menus)
        menus[".uno:EditMenu"] = False
        self.assertTrue(t["menus"][".uno:EditMenu"])


class SaveTemplateTest(unittest.TestCase):
    def test_round_trips_through_loader(self):
        t = assemble_template(
            "Exported", "from a running Writer",
            menus={".uno:ViewMenu": False, ".uno:HelpMenu": True},
            addons={"org.example.addon": False},
            toolbars={"private:resource/toolbar/drawbar": True},
        )
        with tempfile.TemporaryDirectory() as d:
            path = str(Path(d) / "exported.louim")
            self.assertEqual(save_template(path, t), path)
            reloaded = load_template(path)
        self.assertEqual(reloaded, t)
        self.assertFalse(reloaded["menus"][".uno:ViewMenu"])
        self.assertTrue(reloaded["toolbars"]["private:resource/toolbar/drawbar"])

    def test_written_file_is_human_editable_json(self):
        t = assemble_template("n", "d", menus={})
        with tempfile.TemporaryDirectory() as d:
            path = str(Path(d) / "t.louim")
            save_template(path, t)
            text = Path(path).read_text(encoding="utf-8")
        # Pretty-printed (indented) and newline-terminated for hand editing.
        self.assertIn("\n  ", text)
        self.assertTrue(text.endswith("\n"))


if __name__ == "__main__":
    unittest.main()
