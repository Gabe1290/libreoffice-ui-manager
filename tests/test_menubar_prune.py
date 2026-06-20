"""Tests for the recursive menu-pruning logic.

Pure Python — no LibreOffice/UNO. The menu adapter no longer imports ``uno`` at
module load, so ``_prune_hidden`` can be exercised directly with fake index
containers that mimic the UNO menu-settings API (getCount / getByIndex /
removeByIndex, entries as sequences of objects with .Name / .Value).
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from louim.adapters.writer.menubar import _prune_hidden  # noqa: E402


class _Prop:
    def __init__(self, name, value):
        self.Name = name
        self.Value = value


class FakeContainer:
    """Stand-in for a UNO menu-settings XIndexContainer."""

    def __init__(self, entries):
        # entries: list of dicts {command, sub(FakeContainer or None)}.
        self._entries = entries

    def getCount(self):
        return len(self._entries)

    def getByIndex(self, i):
        e = self._entries[i]
        props = []
        if e.get("command") is not None:
            props.append(_Prop("CommandURL", e["command"]))
        else:
            props.append(_Prop("CommandURL", None))  # separator
        if e.get("sub") is not None:
            props.append(_Prop("ItemDescriptorContainer", e["sub"]))
        return props

    def removeByIndex(self, i):
        del self._entries[i]

    def commands(self):
        return [e.get("command") for e in self._entries]


def menu(command, *children):
    return {"command": command, "sub": FakeContainer(list(children))}


def item(command):
    return {"command": command, "sub": None}


def sep():
    return {"command": None, "sub": None}


class PruneHiddenTest(unittest.TestCase):
    def test_hides_top_level_menu(self):
        root = FakeContainer([item(".uno:FileMenu"), menu(".uno:InsertMenu")])
        hidden = []
        _prune_hidden(root, {".uno:InsertMenu": False}, hidden)
        self.assertEqual(hidden, [".uno:InsertMenu"])
        self.assertEqual(root.commands(), [".uno:FileMenu"])

    def test_hides_nested_item_keeps_parent(self):
        insert = menu(".uno:InsertMenu",
                      item(".uno:InsertPagebreak"), item(".uno:InsertGraphic"))
        root = FakeContainer([insert])
        hidden = []
        _prune_hidden(root, {".uno:InsertPagebreak": False}, hidden)
        self.assertEqual(hidden, [".uno:InsertPagebreak"])
        self.assertEqual(root.commands(), [".uno:InsertMenu"])
        self.assertEqual(insert["sub"].commands(), [".uno:InsertGraphic"])

    def test_hides_deeply_nested_item(self):
        shapes = menu(".uno:ShapesMenu", item(".uno:BasicShapes"),
                      item(".uno:StarShapes"))
        insert = menu(".uno:InsertMenu", item(".uno:InsertPagebreak"), shapes)
        root = FakeContainer([insert])
        hidden = []
        _prune_hidden(root, {".uno:StarShapes": False}, hidden)
        self.assertEqual(hidden, [".uno:StarShapes"])
        self.assertEqual(shapes["sub"].commands(), [".uno:BasicShapes"])

    def test_hidden_parent_swallows_children_without_listing_them(self):
        insert = menu(".uno:InsertMenu", item(".uno:InsertPagebreak"))
        root = FakeContainer([insert])
        hidden = []
        # Both the menu and a child are marked false; only the menu is reported.
        _prune_hidden(root, {".uno:InsertMenu": False,
                             ".uno:InsertPagebreak": False}, hidden)
        self.assertEqual(hidden, [".uno:InsertMenu"])
        self.assertEqual(root.commands(), [])

    def test_unlisted_default_visible_and_separators_untouched(self):
        root = FakeContainer([item(".uno:FileMenu"), sep(),
                              item(".uno:HelpMenu")])
        hidden = []
        _prune_hidden(root, {}, hidden)  # nothing marked false
        self.assertEqual(hidden, [])
        self.assertEqual(root.commands(), [".uno:FileMenu", None, ".uno:HelpMenu"])

    def test_removes_multiple_siblings_by_correct_index(self):
        root = FakeContainer([item(".uno:A"), item(".uno:B"),
                              item(".uno:C"), item(".uno:D")])
        hidden = []
        _prune_hidden(root, {".uno:A": False, ".uno:C": False}, hidden)
        self.assertEqual(set(hidden), {".uno:A", ".uno:C"})
        self.assertEqual(root.commands(), [".uno:B", ".uno:D"])


if __name__ == "__main__":
    unittest.main()
