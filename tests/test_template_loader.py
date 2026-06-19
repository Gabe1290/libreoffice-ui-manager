"""Tests for the .louim template loader.

Pure Python — no LibreOffice/UNO required, so these run in CI.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from louim.template.loader import load_template, TemplateError  # noqa: E402


def _write(tmpdir, data):
    path = Path(tmpdir) / "t.louim"
    path.write_text(data if isinstance(data, str) else json.dumps(data))
    return str(path)


class LoadTemplateTest(unittest.TestCase):
    def test_loads_bundled_templates(self):
        for name in ("writer-level-1", "writer-level-2", "writer-full"):
            template = load_template(str(ROOT / "templates" / (name + ".louim")))
            self.assertEqual(template["application"], "writer")
            self.assertIn("menus", template)

    def test_missing_file(self):
        with self.assertRaises(TemplateError):
            load_template(str(ROOT / "templates" / "does-not-exist.louim"))

    def test_invalid_json(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(TemplateError):
                load_template(_write(d, "{not json"))

    def test_wrong_application(self):
        with tempfile.TemporaryDirectory() as d:
            path = _write(d, {"application": "calc", "menus": {}})
            with self.assertRaises(TemplateError):
                load_template(path)

    def test_non_boolean_menu_value(self):
        with tempfile.TemporaryDirectory() as d:
            path = _write(d, {"application": "writer",
                              "menus": {".uno:EditMenu": "yes"}})
            with self.assertRaises(TemplateError):
                load_template(path)

    def test_menus_must_be_object(self):
        with tempfile.TemporaryDirectory() as d:
            path = _write(d, {"application": "writer", "menus": []})
            with self.assertRaises(TemplateError):
                load_template(path)


if __name__ == "__main__":
    unittest.main()
