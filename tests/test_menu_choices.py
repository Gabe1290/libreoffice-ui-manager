"""Tests for the Configure Menus dialog's data layer.

Pure Python — menubar.py is uno-free, so the choice list and the merge run
against fake settings containers that mimic the UNO menu API. The dialog itself
(louim.ui.menu_picker) is toolkit code and is not exercised here.

The point of these tests: LibreOffice's Tools > Customize cannot remove a whole
built-in menu, only its items. LOUIM can, and these cover the path that carries
a "remove the Table menu" tick from the dialog to the pruner.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from louim.adapters.writer.menubar import (  # noqa: E402
    _prune_hidden, _top_level_choices, merge_top_level_choices,
    PROTECTED_MENUS,
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


class TopLevelChoicesTest(unittest.TestCase):
    def test_lists_every_factory_menu_with_its_current_state(self):
        default = FakeContainer([menu(".uno:PickList"), menu(".uno:TableMenu"),
                                 menu(".uno:HelpMenu")])
        # Table is currently removed from the live menu bar.
        choices = _top_level_choices(
            default, {".uno:PickList", ".uno:HelpMenu"}, None)
        self.assertEqual([(c["command"], c["visible"]) for c in choices],
                         [(".uno:PickList", True), (".uno:TableMenu", False),
                          (".uno:HelpMenu", True)])

    def test_hidden_menu_still_offered_so_it_can_be_brought_back(self):
        # Read from the factory default, not the live bar: otherwise the dialog
        # that removed a menu could never restore it.
        default = FakeContainer([menu(".uno:TableMenu")])
        choices = _top_level_choices(default, set(), None)
        self.assertEqual(len(choices), 1)
        self.assertFalse(choices[0]["visible"])

    def test_skips_separators(self):
        default = FakeContainer([menu(".uno:PickList"), sep()])
        choices = _top_level_choices(default, {".uno:PickList"}, None)
        self.assertEqual([c["command"] for c in choices], [".uno:PickList"])

    def test_does_not_descend_into_submenus(self):
        default = FakeContainer([menu(".uno:PickList", item(".uno:Save"))])
        choices = _top_level_choices(default, {".uno:PickList"}, None)
        self.assertEqual([c["command"] for c in choices], [".uno:PickList"])


class MergeTopLevelChoicesTest(unittest.TestCase):
    def test_top_level_ticks_win(self):
        current = {".uno:TableMenu": True, ".uno:HelpMenu": True}
        merged = merge_top_level_choices(
            current, {".uno:TableMenu": False, ".uno:HelpMenu": True})
        self.assertEqual(merged[".uno:TableMenu"], False)
        self.assertEqual(merged[".uno:HelpMenu"], True)

    def test_keeps_individually_hidden_items(self):
        # The teacher already removed Insert > Page Break via Tools > Customize;
        # removing the Table menu in the dialog must not bring it back.
        current = {".uno:InsertMenu": True, ".uno:InsertPagebreak": False,
                   ".uno:TableMenu": True}
        merged = merge_top_level_choices(
            current, {".uno:InsertMenu": True, ".uno:TableMenu": False})
        self.assertEqual(merged[".uno:InsertPagebreak"], False)
        self.assertEqual(merged[".uno:TableMenu"], False)

    def test_does_not_mutate_the_snapshot(self):
        current = {".uno:TableMenu": True}
        merge_top_level_choices(current, {".uno:TableMenu": False})
        self.assertEqual(current, {".uno:TableMenu": True})


class DialogToMenuBarTest(unittest.TestCase):
    """End-to-end over the pure pieces: a ticked-off menu really disappears."""

    def test_unticking_a_menu_removes_it_whole(self):
        table = menu(".uno:TableMenu", item(".uno:InsertTable"))
        bar = FakeContainer([menu(".uno:PickList"), table,
                             menu(".uno:FormatFormMenu")])
        profile = merge_top_level_choices(
            {".uno:PickList": True, ".uno:TableMenu": True,
             ".uno:FormatFormMenu": True},
            {".uno:PickList": True, ".uno:TableMenu": False,
             ".uno:FormatFormMenu": False},
        )
        hidden = []
        _prune_hidden(bar, profile, hidden)
        # The menus are gone from the bar, not merely emptied — which is the
        # thing Tools > Customize cannot do.
        self.assertEqual(bar.commands(), [".uno:PickList"])
        self.assertEqual(sorted(hidden),
                         [".uno:FormatFormMenu", ".uno:TableMenu"])

    def test_retick_restores_the_menu_on_the_next_apply(self):
        # Apply is non-cumulative (rebuilt from the factory default), so
        # re-ticking a menu simply means it is not pruned this time.
        bar = FakeContainer([menu(".uno:TableMenu")])
        hidden = []
        _prune_hidden(bar, {".uno:TableMenu": True}, hidden)
        self.assertEqual(bar.commands(), [".uno:TableMenu"])
        self.assertEqual(hidden, [])


if __name__ == "__main__":
    unittest.main()


class ProtectedMenusTest(unittest.TestCase):
    """File, Edit and Help are never removable.

    They are a universal desktop convention, and keeping Help in particular
    guarantees LOUIM stays reachable: its own menu is merged into the menu bar
    anchored after Help, so an all-menus-hidden profile used to hide the only
    route to "Restore Full Menus".
    """

    def test_protected_set_is_file_edit_help(self):
        self.assertEqual(set(PROTECTED_MENUS),
                         {".uno:PickList", ".uno:EditMenu", ".uno:HelpMenu"})

    def test_marked_protected_in_the_choice_list(self):
        default = FakeContainer([menu(".uno:PickList"), menu(".uno:TableMenu"),
                                 menu(".uno:HelpMenu")])
        choices = _top_level_choices(default, {".uno:PickList", ".uno:TableMenu",
                                               ".uno:HelpMenu"}, None)
        flags = {c["command"]: c["protected"] for c in choices}
        self.assertTrue(flags[".uno:PickList"])
        self.assertTrue(flags[".uno:HelpMenu"])
        self.assertFalse(flags[".uno:TableMenu"])

    def test_pruning_a_profile_that_hides_everything_keeps_them(self):
        # The lockout case: every menu unticked. File/Edit/Help must survive, so
        # the LOUIM menu anchored after Help survives with them.
        bar = FakeContainer([menu(".uno:PickList"), menu(".uno:EditMenu"),
                             menu(".uno:TableMenu"), menu(".uno:HelpMenu")])
        profile = {c: False for c in (".uno:PickList", ".uno:EditMenu",
                                      ".uno:TableMenu", ".uno:HelpMenu")}
        # apply_menu_profile forces the protected menus visible before pruning.
        for command in PROTECTED_MENUS:
            profile[command] = True
        hidden = []
        _prune_hidden(bar, profile, hidden)
        self.assertEqual(bar.commands(),
                         [".uno:PickList", ".uno:EditMenu", ".uno:HelpMenu"])
        self.assertEqual(hidden, [".uno:TableMenu"])
