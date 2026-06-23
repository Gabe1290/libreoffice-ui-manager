#!/usr/bin/env python3
"""Apply (or restore) a LOUIM Writer menu profile on a running LibreOffice.

Connects over a UNO socket and applies a .louim template's menu visibility to
Writer's menu bar, or restores the factory-default menu bar.

Start LibreOffice with a listening socket first, e.g.:

    soffice --norestore --accept="socket,host=localhost,port=2002;urp;"

Then:

    python3 tools/apply-template.py templates/writer/writer-level-1.louim
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
from louim.adapters.writer.toolbars import (  # noqa: E402
    apply_toolbar_profile,
    restore_toolbars,
)
from louim.adapters.writer.sidebar import (  # noqa: E402
    apply_sidebar_profile,
    restore_sidebar_decks,
)
from louim.adapters.writer.toolbaritems import (  # noqa: E402
    apply_toolbar_items,
    restore_toolbar_items,
    hidden_toolbar_commands,
)
from louim.template.loader import load_template  # noqa: E402
from louim.adapters.modules import get_module  # noqa: E402


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
                        help="restore the factory-default interface")
    parser.add_argument("--module", default="writer", choices=("writer", "calc", "impress", "draw"),
                        help="application to restore (apply uses the template's "
                             "own application); default: writer")
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
        module = get_module(args.module)
        restored_menus = restore_default_menus(ctx, module)
        restored_addons = restore_addon_menus(ctx, module)
        restored_toolbars = restore_toolbars(ctx, module)
        restored_items = restore_toolbar_items(ctx, module)
        restored_decks = restore_sidebar_decks(ctx, module)
        print("Restored default menu bar." if restored_menus
              else "Menu bar already default.")
        print("Restored %d addon menu(s): %s"
              % (len(restored_addons), ", ".join(restored_addons) or "none"))
        print("Restored %d toolbar(s): %s"
              % (len(restored_toolbars), ", ".join(restored_toolbars) or "none"))
        print("Restored toolbar buttons in %d toolbar(s): %s"
              % (len(restored_items), ", ".join(restored_items) or "none"))
        print("Restored %d sidebar deck(s): %s"
              % (len(restored_decks), ", ".join(restored_decks) or "none"))
        return 0

    template = load_template(args.template)
    module = get_module(template["application"])
    profile = template.get("profile", {})
    hidden = apply_menu_profile(ctx, template.get("menus", {}), module)
    hidden_addons = apply_addon_profile(ctx, template.get("addons", {}), module)
    hidden_toolbars = apply_toolbar_profile(ctx, template.get("toolbars", {}), module)
    modified_item_bars = apply_toolbar_items(
        ctx, hidden_toolbar_commands(ctx, template, module), module)
    hidden_decks = apply_sidebar_profile(ctx, template.get("sidebar", {}), module)
    print("Applied profile: %s" % profile.get("name", args.template))
    print("Hidden %d menu(s): %s" % (len(hidden), ", ".join(hidden) or "none"))
    print("Hidden %d addon menu(s): %s"
          % (len(hidden_addons), ", ".join(hidden_addons) or "none"))
    print("Hidden %d toolbar(s): %s"
          % (len(hidden_toolbars), ", ".join(hidden_toolbars) or "none"))
    print("Pruned buttons in %d toolbar(s): %s"
          % (len(modified_item_bars), ", ".join(modified_item_bars) or "none"))
    print("Hidden %d sidebar deck(s): %s"
          % (len(hidden_decks), ", ".join(hidden_decks) or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
