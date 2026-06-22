"""Tests for toolbar-button (icon) hiding logic.

Pure Python — toolbaritems.py imports only uno-free helpers at module load
(uno is imported lazily inside the config helpers), so hidden_commands_for and
_collect_commands run without LibreOffice.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from louim.adapters.writer.toolbaritems import (  # noqa: E402
    hidden_commands_for, _collect_commands, _visible_commands,
)


class HiddenCommandsForTest(unittest.TestCase):
    def test_explicit_toolbaritems_only(self):
        tpl = {"toolbaritems": {".uno:InsertTable": False, ".uno:Bold": True}}
        self.assertEqual(hidden_commands_for(tpl), {".uno:InsertTable"})

    def test_flag_merges_hidden_menu_commands(self):
        tpl = {
            "menus": {".uno:InsertObjectChart": False, ".uno:EditMenu": True},
            "toolbaritems": {".uno:InsertTable": False},
            "hide_toolbar_buttons_with_menus": True,
        }
        self.assertEqual(hidden_commands_for(tpl),
                         {".uno:InsertTable", ".uno:InsertObjectChart"})

    def test_flag_off_ignores_menus(self):
        tpl = {
            "menus": {".uno:InsertObjectChart": False},
            "toolbaritems": {".uno:InsertTable": False},
        }
        self.assertEqual(hidden_commands_for(tpl), {".uno:InsertTable"})

    def test_flag_on_without_toolbaritems(self):
        tpl = {"menus": {".uno:ToolsMenu": False},
               "hide_toolbar_buttons_with_menus": True}
        self.assertEqual(hidden_commands_for(tpl), {".uno:ToolsMenu"})

    def test_empty_template(self):
        self.assertEqual(hidden_commands_for({}), set())


# --- fake settings container, mirroring the UNO toolbar-settings API ---

class _Prop:
    def __init__(self, name, value):
        self.Name = name
        self.Value = value


class FakeContainer:
    def __init__(self, entries):
        self._entries = entries  # list of {command, sub, visible}

    def getCount(self):
        return len(self._entries)

    def getByIndex(self, i):
        e = self._entries[i]
        props = [_Prop("CommandURL", e.get("command"))]
        if "visible" in e:
            props.append(_Prop("IsVisible", e["visible"]))
        if e.get("sub") is not None:
            props.append(_Prop("ItemDescriptorContainer", e["sub"]))
        return props


class CollectCommandsTest(unittest.TestCase):
    def test_collects_flat_and_nested(self):
        nested = FakeContainer([{"command": ".uno:SubA"},
                                {"command": ".uno:SubB"}])
        root = FakeContainer([
            {"command": ".uno:Save"},
            {"command": None},                       # separator
            {"command": ".uno:InsertTable", "sub": nested},
        ])
        out = _collect_commands(root, [])
        self.assertEqual(out, [".uno:Save", ".uno:InsertTable",
                               ".uno:SubA", ".uno:SubB"])


class VisibleCommandsTest(unittest.TestCase):
    def test_excludes_isvisible_false(self):
        root = FakeContainer([
            {"command": ".uno:Save"},                       # no IsVisible -> shown
            {"command": ".uno:OpenUrl", "visible": False},  # Customize-hidden
            {"command": ".uno:Print", "visible": True},
        ])
        self.assertEqual(_visible_commands(root, set()),
                         {".uno:Save", ".uno:Print"})

    def test_recurses(self):
        sub = FakeContainer([{"command": ".uno:Sub", "visible": False}])
        root = FakeContainer([{"command": ".uno:Menu", "sub": sub}])
        self.assertEqual(_visible_commands(root, set()), {".uno:Menu"})


if __name__ == "__main__":
    unittest.main()
