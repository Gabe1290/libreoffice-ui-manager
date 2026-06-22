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
            path = _write(d, {"application": "math", "menus": {}})
            with self.assertRaises(TemplateError):
                load_template(path)

    def test_calc_application_supported(self):
        with tempfile.TemporaryDirectory() as d:
            path = _write(d, {"application": "calc",
                              "menus": {".uno:ToolsMenu": False}})
            self.assertEqual(load_template(path)["application"], "calc")

    def test_loads_bundled_calc_templates(self):
        for name in ("calc-level-1", "calc-level-2", "calc-full"):
            template = load_template(str(ROOT / "templates" / (name + ".louim")))
            self.assertEqual(template["application"], "calc")
            self.assertIn("menus", template)

    def test_loads_bundled_impress_templates(self):
        for name in ("impress-level-1", "impress-level-2", "impress-full"):
            template = load_template(str(ROOT / "templates" / (name + ".louim")))
            self.assertEqual(template["application"], "impress")
            self.assertIn("menus", template)

    def test_loads_bundled_draw_templates(self):
        for name in ("draw-level-1", "draw-level-2", "draw-full"):
            template = load_template(str(ROOT / "templates" / (name + ".louim")))
            self.assertEqual(template["application"], "draw")
            self.assertIn("menus", template)

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

    def test_addons_optional_and_validated(self):
        with tempfile.TemporaryDirectory() as d:
            # Valid addons section.
            path = _write(d, {"application": "writer", "menus": {},
                              "addons": {"org.example.addon": False}})
            self.assertEqual(load_template(path)["addons"]["org.example.addon"], False)
            # Non-boolean addon value is rejected.
            bad = _write(d, {"application": "writer", "menus": {},
                             "addons": {"org.example.addon": "no"}})
            with self.assertRaises(TemplateError):
                load_template(bad)

    def test_bundled_templates_have_addons_section(self):
        for name in ("writer-level-1", "writer-level-2", "writer-full"):
            template = load_template(str(ROOT / "templates" / (name + ".louim")))
            self.assertIsInstance(template["addons"], dict)

    def test_toolbars_optional_and_validated(self):
        with tempfile.TemporaryDirectory() as d:
            # Valid toolbars section.
            path = _write(d, {"application": "writer", "menus": {},
                              "toolbars": {"private:resource/toolbar/tableobjectbar": False}})
            loaded = load_template(path)
            self.assertEqual(
                loaded["toolbars"]["private:resource/toolbar/tableobjectbar"], False
            )
            # Non-boolean toolbar value is rejected.
            bad = _write(d, {"application": "writer", "menus": {},
                             "toolbars": {"private:resource/toolbar/tableobjectbar": "no"}})
            with self.assertRaises(TemplateError):
                load_template(bad)
            # A non-object toolbars section is rejected.
            worse = _write(d, {"application": "writer", "menus": {},
                               "toolbars": []})
            with self.assertRaises(TemplateError):
                load_template(worse)

    def test_bundled_templates_have_toolbars_section(self):
        for name in ("writer-level-1", "writer-level-2", "writer-full"):
            template = load_template(str(ROOT / "templates" / (name + ".louim")))
            self.assertIsInstance(template["toolbars"], dict)

    def test_sidebar_optional_and_validated(self):
        with tempfile.TemporaryDirectory() as d:
            path = _write(d, {"application": "writer", "menus": {},
                              "sidebar": {"GalleryDeck": False}})
            self.assertEqual(load_template(path)["sidebar"]["GalleryDeck"], False)
            bad = _write(d, {"application": "writer", "menus": {},
                             "sidebar": {"GalleryDeck": "no"}})
            with self.assertRaises(TemplateError):
                load_template(bad)


if __name__ == "__main__":
    unittest.main()
