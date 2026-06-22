"""Tests for the menu-state export walk (capturing submenu items).

Pure Python — menubar.py is uno-free, so _export_walk runs against fake settings
containers that mimic the UNO menu API.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from louim.adapters.writer.menubar import (  # noqa: E402
    _export_walk, _collect_command_set, _collect_descendants,
)


class _Prop:
    def __init__(self, name, value):
        self.Name = name
        self.Value = value


class FakeContainer:
    def __init__(self, entries):
        self._entries = entries  # list of {command, sub}

    def getCount(self):
        return len(self._entries)

    def getByIndex(self, i):
        e = self._entries[i]
        props = [_Prop("CommandURL", e.get("command"))]
        if e.get("sub") is not None:
            props.append(_Prop("ItemDescriptorContainer", e["sub"]))
        return props


def menu(command, *children):
    return {"command": command, "sub": FakeContainer(list(children))}


def item(command):
    return {"command": command, "sub": None}


def export(default, current_cmds):
    return _export_walk(default, set(current_cmds), True, True, {})


class ExportWalkTest(unittest.TestCase):
    def test_top_level_recorded_true_false(self):
        default = FakeContainer([item(".uno:FileMenu"), item(".uno:ToolsMenu")])
        # Tools removed from the live menu bar.
        out = export(default, {".uno:FileMenu"})
        self.assertEqual(out, {".uno:FileMenu": True, ".uno:ToolsMenu": False})

    def test_hidden_nested_item_recorded_false(self):
        insert = menu(".uno:InsertMenu",
                      item(".uno:InsertPagebreak"), item(".uno:InsertGraphic"))
        default = FakeContainer([insert])
        # Page break removed; menu and the other item still present.
        out = export(default, {".uno:InsertMenu", ".uno:InsertGraphic"})
        self.assertEqual(out, {".uno:InsertMenu": True,
                               ".uno:InsertPagebreak": False})

    def test_children_of_hidden_menu_not_listed(self):
        insert = menu(".uno:InsertMenu", item(".uno:InsertPagebreak"))
        default = FakeContainer([insert])
        # Whole Insert menu gone -> only the menu is recorded false, not its child.
        out = export(default, set())
        self.assertEqual(out, {".uno:InsertMenu": False})

    def test_all_visible_lists_only_top_level_true(self):
        insert = menu(".uno:InsertMenu", item(".uno:InsertPagebreak"))
        default = FakeContainer([item(".uno:FileMenu"), insert])
        out = export(default, {".uno:FileMenu", ".uno:InsertMenu",
                               ".uno:InsertPagebreak"})
        self.assertEqual(out, {".uno:FileMenu": True, ".uno:InsertMenu": True})

    def test_collect_command_set_is_recursive(self):
        insert = menu(".uno:InsertMenu", item(".uno:InsertPagebreak"))
        default = FakeContainer([item(".uno:FileMenu"), insert])
        self.assertEqual(
            _collect_command_set(default, set()),
            {".uno:FileMenu", ".uno:InsertMenu", ".uno:InsertPagebreak"},
        )


class CollectDescendantsTest(unittest.TestCase):
    def test_collects_commands_inside_targeted_menu_only(self):
        insert = menu(".uno:InsertMenu",
                      item(".uno:InsertTable"), item(".uno:InsertObjectChart"))
        tools = menu(".uno:ToolsMenu", item(".uno:Macro"))
        default = FakeContainer([item(".uno:FileMenu"), insert, tools])
        out = _collect_descendants(default, {".uno:InsertMenu"}, False, set())
        # Only Insert's children; the menu itself and other menus excluded.
        self.assertEqual(out, {".uno:InsertTable", ".uno:InsertObjectChart"})

    def test_recurses_into_nested_submenus(self):
        shapes = menu(".uno:ShapesMenu", item(".uno:BasicShapes"))
        insert = menu(".uno:InsertMenu", item(".uno:InsertTable"), shapes)
        default = FakeContainer([insert])
        out = _collect_descendants(default, {".uno:InsertMenu"}, False, set())
        self.assertEqual(out, {".uno:InsertTable", ".uno:ShapesMenu",
                               ".uno:BasicShapes"})

    def test_no_targets_collects_nothing(self):
        insert = menu(".uno:InsertMenu", item(".uno:InsertTable"))
        default = FakeContainer([insert])
        self.assertEqual(_collect_descendants(default, set(), False, set()), set())


if __name__ == "__main__":
    unittest.main()
