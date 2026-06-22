#!/usr/bin/env python3
"""Discover Writer's top-level menus from a running LibreOffice.

Connects to a LibreOffice instance over a UNO socket and prints the Writer
menu bar's top-level menus as UNO command IDs. Useful for inspecting the real
interface while authoring .louim templates, and as a manual check of the
Writer menu-bar adapter.

Start LibreOffice with a listening socket first, e.g.:

    soffice --headless --norestore \\
        --accept="socket,host=localhost,port=2002;urp;"

Then run:

    python3 tools/discover-menus.py [--port 2002]
"""

import argparse
import sys
from pathlib import Path

# Make the in-repo louim package importable without installing it.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import uno  # noqa: E402  (provided by the LibreOffice Python/UNO bridge)

from louim.adapters.writer.menubar import (  # noqa: E402
    discover_top_level_menus,
    discover_menu_items,
)
from louim.adapters.writer.addons import discover_addon_menus  # noqa: E402
from louim.adapters.writer.toolbars import discover_toolbars  # noqa: E402
from louim.adapters.writer.sidebar import discover_sidebar_decks  # noqa: E402
from louim.adapters.modules import get_module  # noqa: E402


def connect(host, port):
    local_ctx = uno.getComponentContext()
    resolver = local_ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local_ctx
    )
    url = (
        "uno:socket,host=%s,port=%d;urp;StarOffice.ComponentContext"
        % (host, port)
    )
    return resolver.resolve(url)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=2002)
    parser.add_argument("--module", default="writer", choices=("writer", "calc", "impress", "draw"),
                        help="which application to discover (default: writer)")
    parser.add_argument("--tree", action="store_true",
                        help="also print every menu item, including submenu "
                             "items, with their UNO IDs (for hiding individual "
                             "entries in a template)")
    args = parser.parse_args()
    module = get_module(args.module)

    try:
        ctx = connect(args.host, args.port)
    except Exception as exc:
        print("Could not connect to LibreOffice on %s:%d" % (args.host, args.port))
        print("Start it with: soffice --headless --norestore "
              '--accept="socket,host=localhost,port=%d;urp;"' % args.port)
        print("Error:", exc)
        return 1

    menus = discover_top_level_menus(ctx, module)
    print("Discovered %d built-in %s menus:" % (len(menus), args.module))
    for menu in menus:
        print("  %-24s %s" % (menu["command"], menu["label"]))

    addons = discover_addon_menus(ctx, module)
    print("\nDiscovered %d extension menu(s) in %s:" % (len(addons), args.module))
    for addon in addons:
        print("  %-45s %s" % (addon["node"], addon["title"]))

    toolbars = discover_toolbars(ctx, module)
    print("\nDiscovered %d %s toolbar(s):" % (len(toolbars), args.module))
    for toolbar in toolbars:
        print("  %-45s %s" % (toolbar["resource"], toolbar["label"]))

    decks = discover_sidebar_decks(ctx, module)
    print("\nDiscovered %d %s sidebar deck(s):" % (len(decks), args.module))
    for deck in decks:
        print("  %-24s %s" % (deck["deck"], deck["title"]))

    if args.tree:
        items = discover_menu_items(ctx, module)
        print("\nFull menu tree (%d command items):" % len(items))
        for item in items:
            indent = "  " * (item["depth"] + 1)
            print("%s%-32s %s" % (indent, item["command"], item["label"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
