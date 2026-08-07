# LibreOffice UI Manager — addon-menu adapter (module-parameterized).
#
# Extension-contributed menus (e.g. Dmaths, and LOUIM's own menu) are NOT part
# of the built-in menu bar managed by menubar.py. They are merged in separately
# by LibreOffice's addon merger, driven by the configuration node
#
#     org.openoffice.Office.Addons / AddonUI / OfficeMenuBar
#
# Each addon menu has a ``Context`` property: a comma-separated list of document
# service names where the menu appears. An empty Context means "all modules".
# To hide an addon menu from a module we remove that module's services from its
# Context (a user-level config override).
#
# The Context is ONE value shared by every application, but LOUIM tracks state
# per module, so restore must compose with hides other modules still hold. Each
# state record stores the pre-hide ``original`` and the ``result`` LOUIM wrote:
# if the live Context still equals ``result`` (nothing else changed it), restore
# writes ``original`` back verbatim; otherwise it re-adds only this module's
# services, leaving the other modules' hides intact. Legacy state files (a bare
# original string) are written back verbatim, as older LOUIM did. Changes take
# effect for newly opened windows.

import json
import os

from louim.adapters.modules import WRITER

# ``uno`` is imported lazily inside the helpers that need it, so this module
# (and pure helpers like ``_merge_context``) imports without LibreOffice.

ADDONS_NODE = "/org.openoffice.Office.Addons/AddonUI/OfficeMenuBar"

# LOUIM's own menu — never hide it, it is the user's control surface.
LOUIM_OWN_NODE = "org.louim.libreoffice-ui-manager.menu"

_STATE_FILENAME = "louim-addon-state-%s.json"


def _config_provider(ctx):
    return ctx.getServiceManager().createInstanceWithContext(
        "com.sun.star.configuration.ConfigurationProvider", ctx
    )


def _make_nodepath_arg(node):
    import uno
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


def _shows_in_module(context, module):
    """True if an addon with this Context appears in ``module``."""
    if not context or not context.strip():
        return True  # empty Context = all modules
    parts = _split(context)
    return any(c in parts for c in module.addon_contexts)


def _merge_context(current, original, module):
    """A Context showing the addon in ``module`` again, keeping other hides.

    Used when the live Context no longer matches what LOUIM wrote (another
    module hid or restored the same addon since). Re-adds only the services
    ``original`` granted this module — everything another module removed stays
    removed. An empty ``original`` (= all modules) grants all of this module's
    services. Pure, unit-tested.
    """
    parts = _split(current)
    if original and original.strip():
        granted = [c for c in _split(original) if c in module.addon_contexts]
    else:
        granted = list(module.addon_contexts)
    for c in granted:
        if c not in parts:
            parts.append(c)
    return ",".join(parts)


def state_path(ctx, module=WRITER):
    """Absolute path of the LOUIM addon-state file for ``module``."""
    ps = ctx.getServiceManager().createInstanceWithContext(
        "com.sun.star.util.PathSubstitution", ctx
    )
    user_dir = uno.fileUrlToSystemPath(ps.getSubstituteVariableValue("$(user)"))
    return os.path.join(user_dir, _STATE_FILENAME % module.key)


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


def discover_addon_menus(ctx, module=WRITER):
    """Discover extension-contributed top-level menus visible in ``module``.

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
        except Exception:  # noqa: BLE001
            context = ""
        if not _shows_in_module(context or "", module):
            continue
        try:
            title = entry.getByName("Title")
        except Exception:  # noqa: BLE001
            title = node
        menus.append({"node": node, "title": title})
    return menus


def addon_visibility(ctx, module=WRITER):
    """Snapshot whether each extension menu currently shows in ``module``.

    Returns a dict mapping addon node name to a bool. Both shown and hidden
    addons are included, for exporting the current interface. LOUIM's own menu is
    excluded.
    """
    provider = _config_provider(ctx)
    access = _read_access(provider, ADDONS_NODE)

    snapshot = {}
    for node in access.getElementNames():
        if node == LOUIM_OWN_NODE:
            continue
        try:
            context = access.getByName(node).getByName("Context")
        except Exception:  # noqa: BLE001
            context = ""
        snapshot[node] = _shows_in_module(context or "", module)
    return snapshot


def _context_of(provider, node):
    return _read_access(provider, _addon_path(node)).getByName("Context") or ""


def _set_context(provider, node, value):
    upd = _update_access(provider, _addon_path(node))
    upd.setPropertyValue("Context", value)
    upd.commitChanges()


def _restore_context(provider, node, record, module):
    """Restore a node's Context from a state record.

    Exact undo (write ``original`` back) when the live value is still what LOUIM
    wrote; compositional (re-add this module's services) when another module
    changed the shared value since. Legacy records — a bare original string from
    older LOUIM — are written back verbatim.
    """
    if not isinstance(record, dict):
        _set_context(provider, node, record)
        return
    original = record.get("original", "")
    current = _context_of(provider, node)
    if current == record.get("result"):
        _set_context(provider, node, original)
    else:
        _set_context(provider, node, _merge_context(current, original, module))


def apply_addon_profile(ctx, addons, module=WRITER, path=None):
    """Hide/show extension menus in ``module`` per an "addons" profile.

    ``addons`` maps addon node names to booleans (True = visible, False =
    hidden). Nodes not mentioned are left untouched. Returns the list of node
    names that were hidden.

    The pre-hide Context and the value LOUIM wrote are both saved to the state
    file before the first change, so restore can undo exactly — or compose with
    another module's hide of the same addon (see ``_restore_context``).
    """
    path = path or state_path(ctx, module)
    provider = _config_provider(ctx)
    state = _load_state(path)

    hidden = []
    for node, visible in addons.items():
        if node == LOUIM_OWN_NODE:
            continue
        try:
            current = _context_of(provider, node)
        except Exception:  # noqa: BLE001
            continue  # unknown node, skip

        if visible is False:
            if _shows_in_module(current, module):
                record = state.get(node)
                if not isinstance(record, dict):
                    # First hide, or a legacy bare-string record to upgrade.
                    record = {"original": record if record is not None
                              else current}
                remaining = [c for c in _split(current)
                             if c not in module.addon_contexts]
                new = ",".join(remaining) if remaining \
                    else ",".join(module.other_addon_contexts)
                _set_context(provider, node, new)
                record["result"] = new
                state[node] = record
            hidden.append(node)
        else:
            # Explicitly visible: restore original if we had hidden it.
            if node in state:
                _restore_context(provider, node, state.pop(node), module)

    _save_state(path, state)
    return hidden


def restore_addon_menus(ctx, module=WRITER, path=None):
    """Restore every addon menu LOUIM hid in ``module``.

    Exact where possible, compositional where another module still hides the
    same addon (see ``_restore_context``). Returns the list of node names
    restored.
    """
    path = path or state_path(ctx, module)
    provider = _config_provider(ctx)
    state = _load_state(path)

    restored = []
    for node, record in list(state.items()):
        try:
            _restore_context(provider, node, record, module)
            restored.append(node)
        except Exception:  # noqa: BLE001
            pass
    _save_state(path, {})
    return restored
