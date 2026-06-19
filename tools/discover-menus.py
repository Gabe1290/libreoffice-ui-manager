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

from louim.adapters.writer.menubar import discover_top_level_menus  # noqa: E402


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
    args = parser.parse_args()

    try:
        ctx = connect(args.host, args.port)
    except Exception as exc:
        print("Could not connect to LibreOffice on %s:%d" % (args.host, args.port))
        print("Start it with: soffice --headless --norestore "
              '--accept="socket,host=localhost,port=%d;urp;"' % args.port)
        print("Error:", exc)
        return 1

    menus = discover_top_level_menus(ctx)
    print("Discovered %d top-level Writer menus:" % len(menus))
    for menu in menus:
        print("  %-24s %s" % (menu["command"], menu["label"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
