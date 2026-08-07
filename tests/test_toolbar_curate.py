"""Tests for the toolbar export curation.

Pure Python — toolbars.py now imports ``uno`` lazily, so ``curate_toolbars``
imports and runs without LibreOffice.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from louim.adapters.writer.toolbars import (  # noqa: E402
    curate_toolbars, CURATED_TOOLBARS, TOOLBAR_PREFIX,
)


class CurateToolbarsTest(unittest.TestCase):
    def test_keeps_curated_regardless_of_state(self):
        snap = {CURATED_TOOLBARS[0]: True, CURATED_TOOLBARS[1]: False}
        self.assertEqual(curate_toolbars(snap), snap)

    def test_drops_non_curated_visible(self):
        noise = TOOLBAR_PREFIX + "arrowshapes"
        out = curate_toolbars({noise: True, CURATED_TOOLBARS[0]: True})
        self.assertNotIn(noise, out)
        self.assertIn(CURATED_TOOLBARS[0], out)

    def test_keeps_non_curated_when_hidden(self):
        # An explicit hide is intentional and worth preserving.
        odd = TOOLBAR_PREFIX + "colorbar"
        out = curate_toolbars({odd: False})
        self.assertEqual(out, {odd: False})

    def test_empty(self):
        self.assertEqual(curate_toolbars({}), {})

    def test_curated_urls_are_well_formed(self):
        for url in CURATED_TOOLBARS:
            self.assertTrue(url.startswith(TOOLBAR_PREFIX))

    def test_contextual_toolbars_not_curated(self):
        # Exporting a contextual toolbar as ``true`` would pin it open outside
        # its context on apply, so curation must drop it when visible…
        for name in ("tableobjectbar", "frameobjectbar", "graphicobjectbar"):
            resource = TOOLBAR_PREFIX + name
            self.assertNotIn(resource, CURATED_TOOLBARS)
            self.assertEqual(curate_toolbars({resource: True}), {})
            # …but keep an explicit, intentional hide.
            self.assertEqual(curate_toolbars({resource: False}),
                             {resource: False})


if __name__ == "__main__":
    unittest.main()
