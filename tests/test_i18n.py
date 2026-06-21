"""Tests for LOUIM's UI localization (en/fr/de/it).

Pure Python — i18n.py imports ``uno`` lazily (only in ``office_language``), so
the string tables and translator are exercised without LibreOffice.
"""

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from louim import i18n  # noqa: E402
from louim.i18n import translator, normalize_lang, SUPPORTED_LANGS  # noqa: E402

_SPEC = re.compile(r"%[sd]")


class StringTableTest(unittest.TestCase):
    def test_every_key_has_every_language(self):
        for key, langs in i18n._STRINGS.items():
            for lang in SUPPORTED_LANGS:
                self.assertIn(lang, langs, "%s missing %s" % (key, lang))
                self.assertTrue(langs[lang], "%s/%s is empty" % (key, lang))

    def test_placeholders_match_across_languages(self):
        # Same printf specifiers, in the same order, so % formatting can never
        # fail for a translated string.
        for key, langs in i18n._STRINGS.items():
            ref = _SPEC.findall(langs["en"])
            for lang in SUPPORTED_LANGS:
                self.assertEqual(_SPEC.findall(langs[lang]), ref,
                                 "placeholder mismatch in %s/%s" % (key, lang))

    def test_apply_body_formats_in_all_languages(self):
        for lang in SUPPORTED_LANGS:
            t = translator(lang)
            out = t("apply_body", "MyProfile", 1, 2, 3, 4)
            self.assertIn("MyProfile", out)

    def test_export_body_formats_in_all_languages(self):
        for lang in SUPPORTED_LANGS:
            self.assertIn("layout.louim",
                          translator(lang)("export_body", "layout.louim"))


class TranslatorTest(unittest.TestCase):
    def test_unknown_language_falls_back_to_english(self):
        self.assertEqual(translator("es")("error_title"),
                         translator("en")("error_title"))

    def test_unknown_key_returns_key(self):
        self.assertEqual(translator("fr")("no_such_key"), "no_such_key")

    def test_french_differs_from_english(self):
        self.assertNotEqual(translator("fr")("error_title"),
                            translator("en")("error_title"))

    def test_each_language_translates_error_title(self):
        seen = {translator(l)("error_title") for l in ("fr", "de", "it")}
        self.assertEqual(len(seen), 3)  # all three are distinct translations


class NormalizeLangTest(unittest.TestCase):
    def test_region_stripped(self):
        self.assertEqual(normalize_lang("fr-FR"), "fr")
        self.assertEqual(normalize_lang("de_DE"), "de")
        self.assertEqual(normalize_lang("it-CH"), "it")

    def test_unsupported_and_empty_default_to_english(self):
        for v in ("es", "zh-CN", "", None):
            self.assertEqual(normalize_lang(v), "en")


if __name__ == "__main__":
    unittest.main()
