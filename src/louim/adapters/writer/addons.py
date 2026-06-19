# LibreOffice UI Manager — Writer addon-menu adapter.
#
# Extension-contributed menus (e.g. Dmaths, and LOUIM's own menu) are NOT part
# of the built-in menu bar managed by menubar.py. They are merged in separately
# by LibreOffice's addon merger, driven by the configuration node
#
#     org.openoffice.Office.Addons / AddonUI / OfficeMenuBar
#
# Each addon menu has a ``Context`` property: a comma-separated list of document
# service names where the menu appears. An empty Context means "all modules".
# To hide an addon menu from Writer we remove the Writer services from its
# Context (a user-level config override); to restore it we write the saved
# original Context back. The change takes effect for newly opened Writer windows.

import json
import os

import uno

ADDONS_NODE = "/org.openoffice.Office.Addons/AddonUI/OfficeMenuBar"

# Document services that mean "this menu shows in Writer".
WRITER_CONTEXTS = (
    "com.sun.star.text.TextDocument",
    "com.sun.star.text.WebDocument",
    "com.sun.star.text.GlobalDocument",
)

# When an addon is Writer-only and we remove Writer, an empty Context would mean
# "all modules" (the opposite of hiding). So fall back to the non-Writer modules,
# keeping the addon available everywhere except Writer.
NON_WRITER_CONTEXTS = (
    "com.sun.star.sheet.SpreadsheetDocument",
    "com.sun.star.presentation.PresentationDocument",
    "com.sun.star.drawing.DrawingDocument",
    "com.sun.star.formula.FormulaProperties",
)

# LOUIM's own menu — never hide it, it is the user's control surface.
LOUIM_OWN_NODE = "org.louim.libreoffice-ui-manager.menu"

STATE_FILENAME = "louim-addon-state.json"


def _config_provider(ctx):
    return ctx.getServiceManager().createInstanceWithContext(
        "com.sun.star.configuration.ConfigurationProvider", ctx
    )


def _make_nodepath_arg(node):
    arg = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
    arg.Name = "nodepath"
    arg.Value = node
    return arg


def _read_access(provider, node):
    return provider.createInstanceWithArguments(
        "com.sun.star.configuration.ConfigurationAccess", (_make_nodepath_arg(node),)
    )


def _update_access(provider, node):
    return provider.createInstanceWithArguments(
        "com.sun.star.configuration.ConfigurationUpdateAccess",
        (_make_nodepath_arg(node),),
    )


def _addon_path(node):
    """Full configuration path of a single addon menu node."""
    return ADDONS_NODE + "/" + node


def _split(context):
    return [c.strip() for c in context.split(",") if c.strip()]


def _shows_in_writer(context):
    """True if an addon with this Context appears in Writer."""
    if not context or not context.strip():
        return True  # empty Context = all modules
    parts = _split(context)
    return any(w in parts for w in WRITER_CONTEXTS)


def state_path(ctx):
    """Absolute path of the LOUIM addon-state file in the user profile."""
    ps = ctx.getServiceManager().createInstanceWithContext(
        "com.sun.star.util.PathSubstitution", ctx
    )
    user_dir = uno.fileUrlToSystemPath(ps.getSubstituteVariableValue("$(user)"))
    return os.path.join(user_dir, STATE_FILENAME)


def _load_state(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (FileNotFoundError, ValueError):
        return {}


def _save_state(path, state):
    if state:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2)
    elif os.path.exists(path):
        os.remove(path)


def discover_addon_menus(ctx):
    """Discover extension-contributed top-level menus visible in Writer.

    Returns a list of dicts in config order, each:
        {"node": "org.openoffice.Office.addon.aide", "title": "Dmaths"}

    LOUIM's own menu is excluded. ``node`` is the stable, language-independent
    identifier used in a .louim template's "addons" section; ``title`` is for
    display only.
    """
    provider = _config_provider(ctx)
    access = _read_access(provider, ADDONS_NODE)

    menus = []
    for node in access.getElementNames():
        if node == LOUIM_OWN_NODE:
            continue
        entry = access.getByName(node)
        try:
            context = entry.getByName("Context")
        except Exception:
            context = ""
        if not _shows_in_writer(context or ""):
            continue
        try:
            title = entry.getByName("Title")
        except Exception:
            title = node
        menus.append({"node": node, "title": title})
    return menus


def _context_of(provider, node):
    return _read_access(provider, _addon_path(node)).getByName("Context") or ""


def _set_context(provider, node, value):
    upd = _update_access(provider, _addon_path(node))
    upd.setPropertyValue("Context", value)
    upd.commitChanges()


def apply_addon_profile(ctx, addons, path=None):
    """Hide/show extension menus in Writer per an "addons" profile.

    ``addons`` maps addon node names to booleans (True = visible, False =
    hidden). Nodes not mentioned are left untouched. Returns the list of node
    names that were hidden.

    Original Context values are saved to the state file before the first change
    so the exact pre-LOUIM state can be restored later, even across restarts.
    """
    path = path or state_path(ctx)
    provider = _config_provider(ctx)
    state = _load_state(path)

    hidden = []
    for node, visible in addons.items():
        if node == LOUIM_OWN_NODE:
            continue
        try:
            current = _context_of(provider, node)
        except Exception:
            continue  # unknown node, skip

        if visible is False:
            if _shows_in_writer(current):
                if node not in state:
                    state[node] = current  # remember the original
                remaining = [c for c in _split(current) if c not in WRITER_CONTEXTS]
                new = ",".join(remaining) if remaining else ",".join(NON_WRITER_CONTEXTS)
                _set_context(provider, node, new)
            hidden.append(node)
        else:
            # Explicitly visible: restore original if we had hidden it.
            if node in state:
                _set_context(provider, node, state.pop(node))

    _save_state(path, state)
    return hidden


def restore_addon_menus(ctx, path=None):
    """Restore every addon menu LOUIM hid to its original Context.

    Returns the list of node names restored.
    """
    path = path or state_path(ctx)
    provider = _config_provider(ctx)
    state = _load_state(path)

    restored = []
    for node, original in list(state.items()):
        try:
            _set_context(provider, node, original)
            restored.append(node)
        except Exception:
            pass
    _save_state(path, {})
    return restored
