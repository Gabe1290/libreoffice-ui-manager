#!/usr/bin/env python3
"""Export a running Writer's current interface as a .louim template.

Connects over a UNO socket, snapshots the current menu / toolbar / extension-menu
visibility, and writes a .louim file a teacher can then edit by hand. The mirror
of apply-template.py.

Start LibreOffice with a listening socket first, e.g.:

    soffice --norestore --accept="socket,host=localhost,port=2002;urp;"

Then:

    python3 tools/export-template.py my-layout.louim --name "My Layout"
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import uno  # noqa: E402

from louim.template.saver import build_current_template, save_template  # noqa: E402
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
    parser.add_argument("output", help="path to write the .louim template to")
    parser.add_argument("--name", default=None,
                        help="profile name (defaults to the output file stem)")
    parser.add_argument("--description", default="")
    parser.add_argument("--module", default="writer", choices=("writer", "calc"),
                        help="application to snapshot (default: writer)")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=2002)
    args = parser.parse_args()

    try:
        ctx = connect(args.host, args.port)
    except Exception as exc:
        print("Could not connect to LibreOffice on %s:%d" % (args.host, args.port))
        print("Error:", exc)
        return 1

    name = args.name or Path(args.output).stem
    template = build_current_template(ctx, name=name, description=args.description,
                                      module=get_module(args.module))
    save_template(args.output, template)

    # Round-trip through the loader as a sanity check.
    load_template(args.output)

    print("Wrote %s" % args.output)
    print("  menus:    %d (%d hidden)"
          % (len(template["menus"]),
             sum(1 for v in template["menus"].values() if v is False)))
    print("  toolbars: %d (%d hidden)"
          % (len(template["toolbars"]),
             sum(1 for v in template["toolbars"].values() if v is False)))
    print("  addons:   %d (%d hidden)"
          % (len(template["addons"]),
             sum(1 for v in template["addons"].values() if v is False)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
