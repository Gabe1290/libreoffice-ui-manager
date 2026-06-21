# LibreOffice UI Manager — Writer toolbar adapter.
#
# Toolbars are not part of the menu bar resource managed by menubar.py. Their
# persistent visibility lives in the module window-state configuration
#
#     org.openoffice.Office.UI.WriterWindowState / UIElements / States
#
# which is a configuration *set* keyed by toolbar resource URL (for example
# ``private:resource/toolbar/standardbar``). Each element carries a ``Visible``
# boolean (plus docking/position state). Toggling a toolbar via View > Toolbars
# writes here, which is why the change survives a restart.
#
# To hide a toolbar we set ``Visible = false`` on its state element, creating the
# element if Writer has never persisted one. To restore we put back exactly what
# was there before — including *removing* an element we had to create — using a
# state file in the user profile, mirroring addons.py. Changes take effect for
# newly opened Writer windows.

import json
import os

# ``uno`` is imported lazily inside the few helpers that need it, so this module
# (and its pure helpers like ``curate_toolbars``) imports without LibreOffice and
# is unit-tested in CI.

# The window-state set for Writer toolbars.
WINDOWSTATE_NODE = "/org.openoffice.Office.UI.WriterWindowState/UIElements/States"

# Resource-URL prefix that identifies a toolbar (as opposed to a statusbar,
# menubar, etc.) in the window-state set.
TOOLBAR_PREFIX = "private:resource/toolbar/"

STATE_FILENAME = "louim-toolbar-state.json"

# The common, teacher-relevant Writer toolbars. A profile snapshot would
# otherwise list every toolbar that has a window-state entry (~58), most of them
# contextual noise; exporting only these (plus anything explicitly hidden) keeps
# a saved template readable. All are real Writer toolbar resource URLs.
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

    Keeps the common, teacher-relevant toolbars (``CURATED_TOOLBARS``) plus any
    toolbar the snapshot marks hidden (``False``) — an explicit hide is an
    intentional choice worth preserving even if the toolbar is not in the curated
    set. Everything else (the dozens of contextual toolbars that merely happen to
    have a window-state entry) is dropped. Pure function, unit-tested.
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


def _module_ui_config(ctx):
    """Return the module-level UI configuration manager for Writer."""
    smgr = ctx.getServiceManager()
    supplier = smgr.createInstanceWithContext(
        "com.sun.star.ui.ModuleUIConfigurationManagerSupplier", ctx
    )
    return supplier.getUIConfigurationManager("com.sun.star.text.TextDocument")


def _props_to_dict(props):
    return {p.Name: p.Value for p in props}


def state_path(ctx):
    """Absolute path of the LOUIM toolbar-state file in the user profile."""
    ps = ctx.getServiceManager().createInstanceWithContext(
        "com.sun.star.util.PathSubstitution", ctx
    )
    import uno
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


def discover_toolbars(ctx):
    """Discover Writer's toolbars.

    Returns a list of dicts in configuration order, each:
        {"resource": "private:resource/toolbar/standardbar", "label": "Standard"}

    ``resource`` is the language-independent toolbar resource URL used as the key
    in a .louim template's "toolbars" section; ``label`` (the toolbar's UIName)
    is for display only and is never stored in a template.
    """
    from com.sun.star.ui.UIElementType import TOOLBAR

    ui_cfg = _module_ui_config(ctx)
    toolbars = []
    for info in ui_cfg.getUIElementsInfo(TOOLBAR):
        entry = _props_to_dict(info)
        resource = entry.get("ResourceURL")
        if not resource:
            continue
        toolbars.append({"resource": resource, "label": entry.get("UIName", "")})
    return toolbars


def toolbar_visibility(ctx):
    """Snapshot the persisted visibility of Writer toolbars.

    Returns a dict mapping toolbar resource URL to a bool (its current
    window-state ``Visible`` value). Only toolbars that carry an explicit
    window-state entry are included — those are exactly the ones the user (or
    LOUIM) has turned on or off, which is what makes a meaningful exported
    template. Toolbars left at their built-in default are omitted.
    """
    states = _read_access(_config_provider(ctx), WINDOWSTATE_NODE)
    snapshot = {}
    for resource in states.getElementNames():
        if not resource.startswith(TOOLBAR_PREFIX):
            continue
        try:
            snapshot[resource] = bool(states.getByName(resource).getByName("Visible"))
        except Exception:  # noqa: BLE001 — entry without a Visible prop; skip
            continue
    return snapshot


def _set_visible(provider, resource, visible):
    """Set a toolbar's persistent Visible flag, creating its state if needed.

    Returns the record needed to undo this change later: the original Visible
    value if the element already existed, or None if we had to create it (so
    restore knows to remove it again).
    """
    states = _update_access(provider, WINDOWSTATE_NODE)
    if states.hasByName(resource):
        element = states.getByName(resource)
        try:
            original = bool(element.getByName("Visible"))
        except Exception:  # noqa: BLE001 — property may be absent; assume visible
            original = True
        element.setPropertyValue("Visible", visible)
        states.commitChanges()
        return {"existed": True, "visible": original}

    # No persisted state yet: create one carrying just the Visible flag.
    element = states.createInstance()
    element.setPropertyValue("Visible", visible)
    states.insertByName(resource, element)
    states.commitChanges()
    return {"existed": False}


def _restore_one(provider, resource, record):
    states = _update_access(provider, WINDOWSTATE_NODE)
    if record.get("existed"):
        if states.hasByName(resource):
            states.getByName(resource).setPropertyValue(
                "Visible", record.get("visible", True)
            )
    elif states.hasByName(resource):
        states.removeByName(resource)
    states.commitChanges()


def apply_toolbar_profile(ctx, toolbars, path=None):
    """Show/hide whole toolbars in Writer per a "toolbars" profile.

    ``toolbars`` maps toolbar resource URLs to booleans: ``True`` shows the
    toolbar, ``False`` hides it (by setting its persistent ``Visible`` state in
    Writer's window-state configuration). Resources not mentioned are left at
    their pre-LOUIM state. Returns the list of resource URLs that were hidden.

    Applying is **non-cumulative**, exactly like the menu bar: every call first
    rolls back any toolbar LOUIM changed on a previous apply, so the profile is
    always interpreted against the user's own original toolbar layout. Applying
    level-1 then writer-full therefore yields writer-full, not a leftover blend,
    and an empty profile restores the user's defaults.

    The pre-LOUIM Visible state of each affected toolbar is saved to the state
    file so ``restore_toolbars`` (and the rollback above) can reproduce it
    exactly — even across restarts, and even for a toolbar LOUIM had to create a
    window-state entry for.

    Note: ``True`` genuinely forces a toolbar visible. That is what makes
    "show the Drawing toolbar for beginners" work, but it means listing a
    *contextual* toolbar (e.g. ``tableobjectbar``, shown only inside a table) as
    ``True`` will pin it open. The bundled templates only manage ordinary
    toggleable toolbars; hand-authored templates should do the same.
    """
    path = path or state_path(ctx)
    provider = _config_provider(ctx)
    state = _load_state(path)

    # Roll back any previous LOUIM toolbar change so this profile is applied
    # against the user's original layout (non-cumulative, like the menu bar).
    for resource, record in list(state.items()):
        try:
            _restore_one(provider, resource, record)
        except Exception:  # noqa: BLE001
            pass
    state = {}

    hidden = []
    for resource, visible in toolbars.items():
        if not resource.startswith(TOOLBAR_PREFIX):
            continue  # only manage genuine toolbar resources
        try:
            record = _set_visible(provider, resource, bool(visible))
            if resource not in state:
                state[resource] = record  # remember the original for restore
            if visible is False:
                hidden.append(resource)
        except Exception:  # noqa: BLE001 — unknown/locked resource, skip it
            continue

    _save_state(path, state)
    return hidden


def restore_toolbars(ctx, path=None):
    """Restore every toolbar LOUIM hid to its original window state.

    Returns the list of resource URLs restored.
    """
    path = path or state_path(ctx)
    provider = _config_provider(ctx)
    state = _load_state(path)

    restored = []
    for resource, record in list(state.items()):
        try:
            _restore_one(provider, resource, record)
            restored.append(resource)
        except Exception:  # noqa: BLE001
            pass
    _save_state(path, {})
    return restored
