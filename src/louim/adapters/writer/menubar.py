# LibreOffice UI Manager — Writer menu bar adapter.
#
# This is part of the Writer provider: the only place (besides the future
# Apply Engine) that talks to LibreOffice directly. It implements dynamic
# discovery (design principle #5) by reading the live Writer menu bar from
# LibreOffice's UI configuration, identifying every menu by its UNO command
# ID rather than its localized label.
#
# The functions take a UNO component context so they work both inside the
# extension (pass XSCRIPTCONTEXT.getComponentContext()) and from an external
# socket connection (used by the headless discovery tool / tests).

import uno

WRITER_MODULE = "com.sun.star.text.TextDocument"
MENUBAR_RESOURCE = "private:resource/menubar/menubar"

# A menu-bar entry is a UNO Sequence<PropertyValue>; index containers need it
# passed as an explicitly typed Any rather than a bare Python tuple.
_MENU_ENTRY_TYPE = "[]com.sun.star.beans.PropertyValue"


def _module_ui_config(ctx):
    """Return the module-level UI configuration manager for Writer."""
    smgr = ctx.getServiceManager()
    supplier = smgr.createInstanceWithContext(
        "com.sun.star.ui.ModuleUIConfigurationManagerSupplier", ctx
    )
    return supplier.getUIConfigurationManager(WRITER_MODULE)


def _props_to_dict(props):
    """Turn a UNO sequence of PropertyValue into a plain dict."""
    return {p.Name: p.Value for p in props}


def discover_top_level_menus(ctx):
    """Discover Writer's top-level menus.

    Returns a list of dicts in menu-bar order, each:
        {"command": ".uno:FileMenu", "label": "~File"}

    The command is the language-independent UNO ID; the label is whatever the
    current LibreOffice locale produced (kept only for display, never stored
    in a .louim template).
    """
    ui_cfg = _module_ui_config(ctx)
    menubar = ui_cfg.getSettings(MENUBAR_RESOURCE, False)

    menus = []
    for i in range(menubar.getCount()):
        entry = _props_to_dict(menubar.getByIndex(i))
        command = entry.get("CommandURL")
        if not command:
            # Separators and other non-command entries have no CommandURL.
            continue
        menus.append({"command": command, "label": entry.get("Label", "")})
    return menus


def apply_menu_profile(ctx, menus):
    """Apply a menu visibility profile to Writer's top-level menu bar.

    ``menus`` maps UNO command IDs to booleans (True = visible, False = hidden),
    as produced by a .louim template. Top-level menus marked False are removed
    from the menu bar; everything else is kept. Commands not mentioned in the
    profile default to visible.

    The new menu bar is always derived from LibreOffice's factory-default menu
    bar, so applying is idempotent and never cumulative: applying level-1 then
    level-2 yields exactly level-2, not the intersection of both.

    Returns the list of command IDs that were hidden. The change is persisted
    to the user's LibreOffice profile and affects all Writer documents until
    restored with ``restore_default_menus``.
    """
    ui_cfg = _module_ui_config(ctx)
    default = ui_cfg.getDefaultSettings(MENUBAR_RESOURCE)

    kept = ui_cfg.createSettings()
    hidden = []
    next_index = 0
    for i in range(default.getCount()):
        entry = default.getByIndex(i)
        command = _props_to_dict(entry).get("CommandURL")
        if command is not None and menus.get(command, True) is False:
            hidden.append(command)
            continue
        # insertByIndex needs the entry as an explicitly typed Any; passing a
        # bare tuple loses the Sequence<PropertyValue> type. A typed Any can
        # only be handed to a UNO method via uno.invoke.
        uno.invoke(kept, "insertByIndex",
                   (next_index, uno.Any(_MENU_ENTRY_TYPE, entry)))
        next_index += 1

    if hidden:
        if ui_cfg.hasSettings(MENUBAR_RESOURCE):
            ui_cfg.replaceSettings(MENUBAR_RESOURCE, kept)
        else:
            ui_cfg.insertSettings(MENUBAR_RESOURCE, kept)
    else:
        # Nothing to hide: drop any customization and fall back to the default.
        restore_default_menus(ctx, _ui_cfg=ui_cfg)
        return hidden

    ui_cfg.store()
    return hidden


def restore_default_menus(ctx, _ui_cfg=None):
    """Restore Writer's factory-default menu bar.

    Removes any LOUIM (or other) menu-bar customization from the user profile,
    so Writer falls back to its built-in full menu bar. Returns True if a
    customization was removed, False if there was nothing to restore.
    """
    ui_cfg = _ui_cfg or _module_ui_config(ctx)
    if not ui_cfg.hasSettings(MENUBAR_RESOURCE):
        return False
    ui_cfg.removeSettings(MENUBAR_RESOURCE)
    ui_cfg.store()
    return True
