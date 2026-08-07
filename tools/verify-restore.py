#!/usr/bin/env python3
"""Live check of the cross-application restore and export curation (4.1.0).

Exercises the shared-config state machinery end to end against a running
LibreOffice: hides the same sidebar deck (and, when one exists, the same addon
menu) in Writer AND Calc, then restores in both orders, verifying that
restoring one application never disturbs the other's hide — the scenario that
corrupted state before 4.1.0. Also snapshots the current interface and checks
that no contextual toolbar is exported as visible.

⚠ Point this ONLY at a throwaway instance with its own profile, never at a
LibreOffice someone is using (see the safety rules in CLAUDE.md):

    soffice --headless --norestore \\
        -env:UserInstallation=file:///tmp/louim-test-profile \\
        --accept="socket,host=localhost,port=2002;urp;"

Then:

    python3 tools/verify-restore.py [--port 2002]

Uses temp state files and writes the original ContextList/Context values back
when it finishes, so even the throwaway profile ends where it started.
"""

import argparse
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import uno  # noqa: E402

from louim.adapters.modules import WRITER, CALC, MODULES  # noqa: E402
from louim.adapters.writer.sidebar import (  # noqa: E402
    SIDEBAR_DECKS_NODE, _config_provider, _context_list, _read_access,
    _set_context_list, apply_sidebar_profile, restore_sidebar_decks,
    shows_in_module,
)
from louim.adapters.writer.addons import (  # noqa: E402
    ADDONS_NODE, LOUIM_OWN_NODE, _context_of, _set_context, _shows_in_module,
    _read_access as _addons_read_access,
    apply_addon_profile, restore_addon_menus,
)
from louim.template.saver import build_current_template, save_template  # noqa: E402
from louim.template.loader import load_template  # noqa: E402

CONTEXTUAL_TOOLBARS = ("tableobjectbar", "frameobjectbar", "graphicobjectbar")


def connect(host, port):
    local_ctx = uno.getComponentContext()
    resolver = local_ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local_ctx
    )
    return resolver.resolve(
        "uno:socket,host=%s,port=%d;urp;StarOffice.ComponentContext" % (host, port)
    )


class Checker:
    def __init__(self):
        self.failures = []

    def check(self, label, ok):
        print("  %-58s %s" % (label, "OK" if ok else "FAIL"))
        if not ok:
            self.failures.append(label)


def pick_shared_deck(provider):
    """A deck visible in both Writer and Calc (preferring an "any" entry)."""
    access = _read_access(provider, SIDEBAR_DECKS_NODE)
    fallback = None
    for deck_id in access.getElementNames():
        try:
            cl = _context_list(provider, deck_id)
        except Exception:  # noqa: BLE001
            continue
        if shows_in_module(cl, WRITER) and shows_in_module(cl, CALC):
            if any(e.split(",", 1)[0].strip() == "any" for e in cl):
                return deck_id
            fallback = fallback or deck_id
    return fallback


def pick_shared_addon(provider):
    """A third-party addon menu visible in both Writer and Calc, or None."""
    access = _addons_read_access(provider, ADDONS_NODE)
    for node in access.getElementNames():
        if node == LOUIM_OWN_NODE:
            continue
        try:
            context = _context_of(provider, node)
        except Exception:  # noqa: BLE001
            continue
        if _shows_in_module(context, WRITER) and _shows_in_module(context, CALC):
            return node
    return None


def verify_sidebar(ctx, provider, deck, c, tmp):
    original = _context_list(provider, deck)
    shows = lambda m: shows_in_module(_context_list(provider, deck), m)  # noqa: E731

    print("\nSidebar deck %r — restore in REVERSE order (exact undo):" % deck)
    pw, pc = str(tmp / "a-writer.json"), str(tmp / "a-calc.json")
    apply_sidebar_profile(ctx, {deck: False}, WRITER, path=pw)
    c.check("hidden in Writer, still in Calc", not shows(WRITER) and shows(CALC))
    apply_sidebar_profile(ctx, {deck: False}, CALC, path=pc)
    c.check("hidden in both", not shows(WRITER) and not shows(CALC))
    restore_sidebar_decks(ctx, CALC, path=pc)
    c.check("Calc restored, Writer hide intact", shows(CALC) and not shows(WRITER))
    restore_sidebar_decks(ctx, WRITER, path=pw)
    c.check("ContextList back to the exact original",
            _context_list(provider, deck) == original)

    print("Sidebar deck %r — restore in HIDE order (compositional):" % deck)
    pw, pc = str(tmp / "b-writer.json"), str(tmp / "b-calc.json")
    apply_sidebar_profile(ctx, {deck: False}, WRITER, path=pw)
    apply_sidebar_profile(ctx, {deck: False}, CALC, path=pc)
    restore_sidebar_decks(ctx, WRITER, path=pw)
    c.check("Writer restored, Calc hide intact (pre-4.1.0 bug)",
            shows(WRITER) and not shows(CALC))
    restore_sidebar_decks(ctx, CALC, path=pc)
    c.check("both restored", shows(WRITER) and shows(CALC))
    final = _context_list(provider, deck)
    c.check("functionally equal to original in every app",
            all(shows_in_module(final, m) == shows_in_module(original, m)
                for m in MODULES.values()))
    return original


def verify_addon(ctx, provider, node, c, tmp):
    original = _context_of(provider, node)
    shows = lambda m: _shows_in_module(_context_of(provider, node), m)  # noqa: E731

    print("\nAddon menu %r — restore in both orders:" % node)
    pw, pc = str(tmp / "aa-writer.json"), str(tmp / "aa-calc.json")
    apply_addon_profile(ctx, {node: False}, WRITER, path=pw)
    apply_addon_profile(ctx, {node: False}, CALC, path=pc)
    restore_addon_menus(ctx, CALC, path=pc)
    c.check("Calc restored, Writer hide intact", shows(CALC) and not shows(WRITER))
    restore_addon_menus(ctx, WRITER, path=pw)
    c.check("Context back to the exact original",
            _context_of(provider, node) == original)

    pw, pc = str(tmp / "ab-writer.json"), str(tmp / "ab-calc.json")
    apply_addon_profile(ctx, {node: False}, WRITER, path=pw)
    apply_addon_profile(ctx, {node: False}, CALC, path=pc)
    restore_addon_menus(ctx, WRITER, path=pw)
    c.check("Writer restored, Calc hide intact (pre-4.1.0 bug)",
            shows(WRITER) and not shows(CALC))
    restore_addon_menus(ctx, CALC, path=pc)
    c.check("both restored (functionally)", shows(WRITER) and shows(CALC))
    return original


def verify_export(ctx, c, tmp):
    print("\nExport curation (Writer snapshot):")
    template = build_current_template(ctx, name="verify-restore", module=WRITER)
    toolbars = template.get("toolbars", {})
    pinned = [r for r, v in toolbars.items()
              if v is True and r.rsplit("/", 1)[-1] in CONTEXTUAL_TOOLBARS]
    c.check("no contextual toolbar exported as true (was: %s)"
            % (", ".join(pinned) or "none"), not pinned)
    path = str(tmp / "export.louim")
    try:
        save_template(path, template)
        load_template(path)
        ok = True
    except Exception as exc:  # noqa: BLE001 — report as a failed check
        print("    round-trip error: %s" % exc)
        ok = False
    c.check("exported template round-trips through the loader", ok)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=2002)
    args = parser.parse_args()

    try:
        ctx = connect(args.host, args.port)
    except Exception as exc:
        print("Could not connect to LibreOffice on %s:%d" % (args.host, args.port))
        print("Error:", exc)
        return 1

    provider = _config_provider(ctx)
    c = Checker()
    deck = pick_shared_deck(provider)
    addon = pick_shared_addon(provider)
    deck_original = addon_original = None

    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        try:
            if deck:
                deck_original = verify_sidebar(ctx, provider, deck, c, tmp)
            else:
                print("No deck shared by Writer and Calc found — SKIPPED")
            if addon:
                addon_original = verify_addon(ctx, provider, addon, c, tmp)
            else:
                print("\nNo third-party addon menu in Writer+Calc — addon "
                      "check SKIPPED (same code path as the sidebar check)")
            verify_export(ctx, c, tmp)
        finally:
            # Belt and braces: leave the throwaway profile exactly as found.
            if deck and deck_original is not None:
                _set_context_list(provider, deck, deck_original)
            if addon and addon_original is not None:
                _set_context(provider, addon, addon_original)

    print("\n%s" % ("ALL CHECKS PASSED" if not c.failures
                    else "FAILED: %d check(s)" % len(c.failures)))
    return 0 if not c.failures else 1


if __name__ == "__main__":
    sys.exit(main())
