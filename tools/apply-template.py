#!/usr/bin/env python3
"""Apply (or restore) a LOUIM Writer menu profile on a running LibreOffice.

Connects over a UNO socket and applies a .louim template's menu visibility to
Writer's menu bar, or restores the factory-default menu bar.

Start LibreOffice with a listening socket first, e.g.:

    soffice --norestore --accept="socket,host=localhost,port=2002;urp;"

Then:

    python3 tools/apply-template.py templates/writer-level-1.louim
    python3 tools/apply-template.py --restore

The change persists in the LibreOffice user profile and affects all Writer
documents until restored.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import uno  # noqa: E402

from louim.adapters.writer.menubar import (  # noqa: E402
    apply_menu_profile,
    restore_default_menus,
)
from louim.adapters.writer.addons import (  # noqa: E402
    apply_addon_profile,
    restore_addon_menus,
)
from louim.template.loader import load_template  # noqa: E402


def connect(host, port):
    local_ctx = uno.getComponentContext()
    resolver = local_ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local_ctx
    )
    return resolver.resolve(
        "uno:socket,host=%s,port=%d;urp;StarOffice.ComponentContext" % (host, port)
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("template", nargs="?", help="path to a .louim template")
    parser.add_argument("--restore", action="store_true",
                        help="restore the factory-default Writer menu bar")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=2002)
    args = parser.parse_args()

    if not args.restore and not args.template:
        parser.error("provide a template path or --restore")

    try:
        ctx = connect(args.host, args.port)
    except Exception as exc:
        print("Could not connect to LibreOffice on %s:%d" % (args.host, args.port))
        print("Error:", exc)
        return 1

    if args.restore:
        restored_menus = restore_default_menus(ctx)
        restored_addons = restore_addon_menus(ctx)
        print("Restored default menu bar." if restored_menus
              else "Menu bar already default.")
        print("Restored %d addon menu(s): %s"
              % (len(restored_addons), ", ".join(restored_addons) or "none"))
        return 0

    template = load_template(args.template)
    profile = template.get("profile", {})
    hidden = apply_menu_profile(ctx, template.get("menus", {}))
    hidden_addons = apply_addon_profile(ctx, template.get("addons", {}))
    print("Applied profile: %s" % profile.get("name", args.template))
    print("Hidden %d menu(s): %s" % (len(hidden), ", ".join(hidden) or "none"))
    print("Hidden %d addon menu(s): %s"
          % (len(hidden_addons), ", ".join(hidden_addons) or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
