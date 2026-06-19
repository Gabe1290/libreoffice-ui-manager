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

WRITER_MODULE = "com.sun.star.text.TextDocument"
MENUBAR_RESOURCE = "private:resource/menubar/menubar"


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
