#!/usr/bin/env python3
"""One-off live check of the toolbar apply/restore mechanism.

Connects to a running LibreOffice over a UNO socket and, for a couple of test
toolbars, records the original window-state, hides via apply_toolbar_profile,
verifies the persisted Visible flag flipped, then restores and verifies the
state matches the original exactly (including removing an entry we had to
create). Uses a temp state file so the real user profile is never touched.

    python tools/verify-toolbars.py [--port 2002]
"""

import argparse
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import uno  # noqa: E402

from louim.adapters.writer.toolbars import (  # noqa: E402
    apply_toolbar_profile,
    restore_toolbars,
    WINDOWSTATE_NODE,
    _config_provider,
    _read_access,
)


def connect(host, port):
    local_ctx = uno.getComponentContext()
    resolver = local_ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local_ctx
    )
    return resolver.resolve(
        "uno:socket,host=%s,port=%d;urp;StarOffice.ComponentContext" % (host, port)
    )


def state_of(ctx, resource):
    """Return (exists, visible) for a toolbar in the window-state config."""
    states = _read_access(_config_provider(ctx), WINDOWSTATE_NODE)
    if not states.hasByName(resource):
        return (False, None)
    try:
        visible = bool(states.getByName(resource).getByName("Visible"))
    except Exception:
        visible = None
    return (True, visible)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=2002)
    args = parser.parse_args()

    ctx = connect(args.host, args.port)
    targets = [
        "private:resource/toolbar/standardbar",
        "private:resource/toolbar/colorbar",
    ]

    ok = True
    with tempfile.TemporaryDirectory() as d:
        path = str(Path(d) / "state.json")

        before = {r: state_of(ctx, r) for r in targets}
        for r in targets:
            print("BEFORE  %-44s exists=%s visible=%s" % (r, *before[r]))

        hidden = apply_toolbar_profile(ctx, {r: False for r in targets}, path=path)
        print("\napply hid: %s" % ", ".join(hidden))
        for r in targets:
            exists, visible = state_of(ctx, r)
            hid_ok = exists and visible is False
            ok = ok and hid_ok
            print("HIDDEN  %-44s exists=%s visible=%s  %s"
                  % (r, exists, visible, "OK" if hid_ok else "FAIL"))

        restored = restore_toolbars(ctx, path=path)
        print("\nrestore put back: %s" % ", ".join(restored))
        for r in targets:
            after = state_of(ctx, r)
            match = after == before[r]
            ok = ok and match
            print("RESTORED %-43s exists=%s visible=%s  %s"
                  % (r, after[0], after[1], "OK (matches original)" if match
                     else "FAIL (was %s)" % (before[r],)))

    print("\n%s" % ("ALL CHECKS PASSED" if ok else "SOME CHECKS FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
