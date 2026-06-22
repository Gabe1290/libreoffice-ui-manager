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


def _command_labels(ctx):
    """Return an XNameAccess mapping command URL -> label info for Writer.

    The menu-bar UI config stores command IDs but usually leaves ``Label`` empty
    (LibreOffice resolves the visible text from the command at display time, and
    more so when no document frame is open). The ``UICommandDescription`` service
    is the language-aware source of those labels. Returns None if unavailable, so
    callers fall back to whatever ``Label`` the entry carried.
    """
    try:
        desc = ctx.getServiceManager().createInstanceWithContext(
            "com.sun.star.frame.UICommandDescription", ctx
        )
        return desc.getByName(WRITER_MODULE)
    except Exception:  # noqa: BLE001
        return None


def _label_for(command, entry_label, command_labels):
    """Best display label for a command: its entry label, else the resolved one.

    Mnemonic markers (``~``) are stripped for clean display. Labels are for
    humans only and are never written into a template.
    """
    label = entry_label or ""
    if not label and command_labels is not None and command:
        try:
            if command_labels.hasByName(command):
                info = _props_to_dict(command_labels.getByName(command))
                label = info.get("Label") or info.get("Name") or ""
        except Exception:  # noqa: BLE001
            label = ""
    return label.replace("~", "")


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
    command_labels = _command_labels(ctx)

    menus = []
    for i in range(menubar.getCount()):
        entry = _props_to_dict(menubar.getByIndex(i))
        command = entry.get("CommandURL")
        if not command:
            # Separators and other non-command entries have no CommandURL.
            continue
        menus.append({
            "command": command,
            "label": _label_for(command, entry.get("Label", ""), command_labels),
        })
    return menus


def _walk_items(container, path, items, command_labels):
    """Append every command entry under ``container`` (depth-first) to ``items``."""
    for i in range(container.getCount()):
        entry = _props_to_dict(container.getByIndex(i))
        command = entry.get("CommandURL")
        if command:
            items.append({
                "command": command,
                "label": _label_for(command, entry.get("Label", ""), command_labels),
                "path": list(path),
                "depth": len(path),
            })
        sub = entry.get("ItemDescriptorContainer")
        if sub is not None:
            _walk_items(sub, path + [command] if command else list(path), items,
                        command_labels)
    return items


def discover_menu_items(ctx):
    """Discover every Writer menu entry, including nested submenu items.

    Returns a flat list in menu order, each:
        {"command": ".uno:InsertPagebreak", "label": "...",
         "path": [".uno:InsertMenu"], "depth": 1}

    ``path`` is the chain of parent menu commands, so a teacher can see where a
    command lives. Separators are skipped. The list is read from the factory
    default, so it shows the full menu tree regardless of any current
    customization — useful for finding the UNO IDs of individual items to hide in
    a template's "menus" section.
    """
    default = _module_ui_config(ctx).getDefaultSettings(MENUBAR_RESOURCE)
    return _walk_items(default, [], [], _command_labels(ctx))


def _collect_command_set(container, out):
    """Add every CommandURL under ``container`` (depth-first) to the set ``out``."""
    for i in range(container.getCount()):
        entry = _props_to_dict(container.getByIndex(i))
        command = entry.get("CommandURL")
        if command:
            out.add(command)
        sub = entry.get("ItemDescriptorContainer")
        if sub is not None:
            _collect_command_set(sub, out)
    return out


def _export_walk(container, current_cmds, parent_visible, is_top, snapshot):
    """Record the visibility of menu commands for an exported template.

    Walks the factory-default tree and compares against ``current_cmds`` (the
    commands present in the live menu bar). Top-level menus are always recorded
    (True/False); a nested item is recorded only when it is hidden *and* its
    parent menu is still shown — so the export captures items a teacher removed
    via Tools ▸ Customize without listing every child of an already-hidden menu.
    """
    for i in range(container.getCount()):
        entry = _props_to_dict(container.getByIndex(i))
        command = entry.get("CommandURL")
        visible = command in current_cmds if command else True
        if command:
            if is_top:
                snapshot[command] = visible
            elif parent_visible and not visible:
                snapshot[command] = False
        sub = entry.get("ItemDescriptorContainer")
        if sub is not None:
            _export_walk(sub, current_cmds, parent_visible and visible, False,
                         snapshot)
    return snapshot


def _collect_descendants(container, targets, inside, out):
    """Collect commands nested under any menu whose command is in ``targets``."""
    for i in range(container.getCount()):
        entry = _props_to_dict(container.getByIndex(i))
        command = entry.get("CommandURL")
        if inside and command:
            out.add(command)
        sub = entry.get("ItemDescriptorContainer")
        if sub is not None:
            _collect_descendants(sub, targets, inside or command in targets, out)
    return out


def menu_command_descendants(ctx, menu_commands):
    """Return every command nested inside the given menus (factory default tree).

    For each command in ``menu_commands`` that is a menu (has a submenu), returns
    the command IDs of all items inside it, recursively (the menus themselves are
    not included). Hiding a top-level menu can then also hide the *toolbar*
    buttons for the features that lived in that menu.
    """
    default = _module_ui_config(ctx).getDefaultSettings(MENUBAR_RESOURCE)
    return _collect_descendants(default, set(menu_commands), False, set())


def menu_visibility(ctx):
    """Snapshot the current menu state for export, including submenu items.

    Returns a dict mapping UNO command IDs to booleans in the shape a .louim
    template's "menus" section uses:

    - every top-level menu → True (shown) or False (hidden);
    - every nested item a teacher has removed (present in the factory default but
      not in the live menu bar) → False.

    Unlisted commands stay visible on apply, so the result reproduces the current
    (possibly hand-customized) menus exactly, item by item.
    """
    ui_cfg = _module_ui_config(ctx)
    default = ui_cfg.getDefaultSettings(MENUBAR_RESOURCE)
    current_cmds = _collect_command_set(
        ui_cfg.getSettings(MENUBAR_RESOURCE, False), set()
    )
    return _export_walk(default, current_cmds, True, True, {})


def _prune_hidden(container, menus, hidden):
    """Recursively remove entries whose command is marked False, at any depth.

    Walks ``container`` depth-first: recurses into the submenu of every entry
    that survives, then removes the hidden entries at this level (in descending
    index order, so earlier removals do not shift the indices still to remove).
    A hidden parent is removed whole — its children are not visited or listed.
    """
    to_remove = []
    for i in range(container.getCount()):
        entry = _props_to_dict(container.getByIndex(i))
        command = entry.get("CommandURL")
        if command is not None and menus.get(command, True) is False:
            to_remove.append(i)
            hidden.append(command)
            continue
        sub = entry.get("ItemDescriptorContainer")
        if sub is not None:
            _prune_hidden(sub, menus, hidden)
    for i in reversed(to_remove):
        container.removeByIndex(i)


def apply_menu_profile(ctx, menus):
    """Apply a menu visibility profile to Writer's menus.

    ``menus`` maps UNO command IDs to booleans (True = visible, False = hidden),
    as produced by a .louim template. Any command marked False is removed —
    whether it is a top-level menu (``.uno:InsertMenu``) or an individual item
    inside a menu or submenu (``.uno:InsertPagebreak``). Commands not mentioned
    default to visible. Hiding a menu also removes everything inside it.

    The menu bar is always rebuilt from LibreOffice's factory default, so
    applying is non-cumulative: applying level-1 then level-2 yields exactly
    level-2. Returns the list of command IDs that were hidden. The change
    persists in the user's profile until ``restore_default_menus``.
    """
    ui_cfg = _module_ui_config(ctx)

    # Non-cumulative: drop any prior customization so we start from the factory
    # default. getSettings(..., True) then yields a writable clone of the full
    # default tree (whereas it would return only the customization layer if one
    # were left in place).
    if ui_cfg.hasSettings(MENUBAR_RESOURCE):
        ui_cfg.removeSettings(MENUBAR_RESOURCE)
        ui_cfg.store()

    # Fast path: nothing to hide — leave the factory default menu bar in place.
    if not any(visible is False for visible in menus.values()):
        return []

    writable = ui_cfg.getSettings(MENUBAR_RESOURCE, True)
    hidden = []
    _prune_hidden(writable, menus, hidden)

    if hidden:
        ui_cfg.replaceSettings(MENUBAR_RESOURCE, writable)
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
