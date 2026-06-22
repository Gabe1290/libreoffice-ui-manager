# LibreOffice UI Manager — toolbar visibility adapter (module-parameterized).
#
# Toolbars are not part of the menu bar resource managed by menubar.py. Their
# persistent visibility lives in each application's window-state configuration
# (``org.openoffice.Office.UI.<Module>WindowState / UIElements / States``), a
# configuration *set* keyed by toolbar resource URL (e.g.
# ``private:resource/toolbar/standardbar``). Each element carries a ``Visible``
# boolean (plus docking/position state); toggling a toolbar via View ▸ Toolbars
# writes here, which is why the change survives a restart.
#
# To hide a toolbar we set ``Visible = false`` on its state element, creating the
# element if none was persisted. To restore we put back exactly what was there
# before — including *removing* an element we had to create — using a per-module
# state file in the user profile, mirroring addons.py. Changes take effect for
# newly opened windows.

import json
import os

from louim.adapters.modules import WRITER
from louim.adapters.writer.menubar import _module_ui_config, _props_to_dict

# ``uno`` is imported lazily inside the few helpers that need it, so this module
# (and pure helpers like ``curate_toolbars``) imports without LibreOffice.

# Resource-URL prefix that identifies a toolbar (vs a statusbar, menubar, …).
TOOLBAR_PREFIX = "private:resource/toolbar/"

_STATE_FILENAME = "louim-toolbar-state-%s.json"

# The common, teacher-relevant toolbars. A profile snapshot would otherwise list
# every toolbar that has a window-state entry (~58), most of them contextual
# noise; exporting only these (plus anything explicitly hidden) keeps a saved
# template readable. Tuned for Writer; harmless elsewhere (non-matching names are
# simply absent from another module's snapshot).
CURATED_TOOLBARS = (
    TOOLBAR_PREFIX + "standardbar",
    TOOLBAR_PREFIX + "textobjectbar",
    TOOLBAR_PREFIX + "findbar",
    TOOLBAR_PREFIX + "insertbar",
    TOOLBAR_PREFIX + "drawbar",
    TOOLBAR_PREFIX + "tableobjectbar",
    TOOLBAR_PREFIX + "frameobjectbar",
    TOOLBAR_PREFIX + "graphicobjectbar",
    TOOLBAR_PREFIX + "formcontrols",
    TOOLBAR_PREFIX + "mailmerge",
)


def curate_toolbars(snapshot):
    """Trim a toolbar visibility map for a readable exported template.

    Keeps the common toolbars (``CURATED_TOOLBARS``) plus any toolbar the
    snapshot marks hidden (``False``) — an explicit hide is intentional and worth
    keeping even if not curated. Everything else is dropped. Pure, unit-tested.
    """
    return {
        resource: visible
        for resource, visible in snapshot.items()
        if resource in CURATED_TOOLBARS or visible is False
    }


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


def state_path(ctx, module=WRITER):
    """Absolute path of the LOUIM toolbar-state file for ``module``."""
    ps = ctx.getServiceManager().createInstanceWithContext(
        "com.sun.star.util.PathSubstitution", ctx
    )
    import uno
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


def discover_toolbars(ctx, module=WRITER):
    """Discover the module's toolbars.

    Returns a list of dicts in configuration order, each:
        {"resource": "private:resource/toolbar/standardbar", "label": "Standard"}

    ``resource`` is the language-independent toolbar resource URL; ``label`` is
    for display only.
    """
    from com.sun.star.ui.UIElementType import TOOLBAR

    ui_cfg = _module_ui_config(ctx, module)
    toolbars = []
    for info in ui_cfg.getUIElementsInfo(TOOLBAR):
        entry = _props_to_dict(info)
        resource = entry.get("ResourceURL")
        if not resource:
            continue
        toolbars.append({"resource": resource, "label": entry.get("UIName", "")})
    return toolbars


def toolbar_visibility(ctx, module=WRITER):
    """Snapshot the persisted visibility of the module's toolbars.

    Returns a dict mapping toolbar resource URL to a bool (its window-state
    ``Visible`` value). Only toolbars with an explicit window-state entry are
    included — those the user (or LOUIM) has turned on or off.
    """
    states = _read_access(_config_provider(ctx), module.windowstate_node)
    snapshot = {}
    for resource in states.getElementNames():
        if not resource.startswith(TOOLBAR_PREFIX):
            continue
        try:
            snapshot[resource] = bool(states.getByName(resource).getByName("Visible"))
        except Exception:  # noqa: BLE001 — entry without a Visible prop; skip
            continue
    return snapshot


def _set_visible(provider, node, resource, visible):
    """Set a toolbar's persistent Visible flag, creating its state if needed.

    Returns the record needed to undo this change later: the original Visible
    value if the element already existed, or that it did not exist (so restore
    knows to remove it again).
    """
    states = _update_access(provider, node)
    if states.hasByName(resource):
        element = states.getByName(resource)
        try:
            original = bool(element.getByName("Visible"))
        except Exception:  # noqa: BLE001 — property may be absent; assume visible
            original = True
        element.setPropertyValue("Visible", visible)
        states.commitChanges()
        return {"existed": True, "visible": original}

    element = states.createInstance()
    element.setPropertyValue("Visible", visible)
    states.insertByName(resource, element)
    states.commitChanges()
    return {"existed": False}


def _restore_one(provider, node, resource, record):
    states = _update_access(provider, node)
    if record.get("existed"):
        if states.hasByName(resource):
            states.getByName(resource).setPropertyValue(
                "Visible", record.get("visible", True)
            )
    elif states.hasByName(resource):
        states.removeByName(resource)
    states.commitChanges()


def apply_toolbar_profile(ctx, toolbars, module=WRITER, path=None):
    """Show/hide whole toolbars per a "toolbars" profile.

    ``toolbars`` maps toolbar resource URLs to booleans: ``True`` shows, ``False``
    hides (via the persistent ``Visible`` state). Resources not mentioned are left
    at their pre-LOUIM state. Returns the list of resource URLs hidden.

    Non-cumulative, like the menu bar: every call first rolls back any toolbar
    LOUIM changed on a previous apply, so the profile is interpreted against the
    user's own layout and an empty profile restores the defaults.

    Note: ``True`` genuinely forces a toolbar visible, so do not list a contextual
    toolbar as ``True`` or it is pinned open. The bundled templates only manage
    ordinary toggleable toolbars.
    """
    node = module.windowstate_node
    path = path or state_path(ctx, module)
    provider = _config_provider(ctx)
    state = _load_state(path)

    for resource, record in list(state.items()):
        try:
            _restore_one(provider, node, resource, record)
        except Exception:  # noqa: BLE001
            pass
    state = {}

    hidden = []
    for resource, visible in toolbars.items():
        if not resource.startswith(TOOLBAR_PREFIX):
            continue  # only manage genuine toolbar resources
        try:
            record = _set_visible(provider, node, resource, bool(visible))
            if resource not in state:
                state[resource] = record
            if visible is False:
                hidden.append(resource)
        except Exception:  # noqa: BLE001 — unknown/locked resource, skip it
            continue

    _save_state(path, state)
    return hidden


def restore_toolbars(ctx, module=WRITER, path=None):
    """Restore every toolbar LOUIM hid to its original window state.

    Returns the list of resource URLs restored.
    """
    node = module.windowstate_node
    path = path or state_path(ctx, module)
    provider = _config_provider(ctx)
    state = _load_state(path)

    restored = []
    for resource, record in list(state.items()):
        try:
            _restore_one(provider, node, resource, record)
            restored.append(resource)
        except Exception:  # noqa: BLE001
            pass
    _save_state(path, {})
    return restored
