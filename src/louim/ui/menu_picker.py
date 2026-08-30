# LibreOffice UI Manager — the "Configure Menus" dialog.
#
# Why this exists: LibreOffice's own Tools > Customize can remove individual
# menu *items*, but it cannot remove a whole top-level menu. Built-in menus have
# no visibility checkbox there, and Delete is reserved for menus you created
# yourself — so you can empty the Table menu but the empty menu stays on the
# menu bar. LOUIM's engine removes the menu entry outright (see
# ``menubar.apply_menu_profile``); this dialog is the in-app way to ask for it,
# without hand-editing a .louim file.
#
# The dialog is built programmatically from ``UnoControlDialogModel`` rather
# than a static .xdl resource because the menu list is generated at run time
# from whatever the active application actually has, with labels resolved from
# LibreOffice's own localized command descriptions. Only UNO command IDs are
# ever returned to the caller — labels are for the eyes only.

# UnoControlButtonModel.PushButtonType is a `short` in the IDL, so the plain
# numeric values are what the property accepts.
_BUTTON_STANDARD = 0
_BUTTON_OK = 1
_BUTTON_CANCEL = 2

# Layout, in AppFont map units (the dialog model's native unit).
_MARGIN = 8
_WIDTH = 200
# Tall enough for four wrapped lines: the hint runs noticeably longer in
# French and German than in English, and a fixed two-line box clipped it.
_HINT_HEIGHT = 40
_ROW_HEIGHT = 11
_GAP = 7
_BUTTON_WIDTH = 52
_BUTTON_HEIGHT = 14

# Executing a dialog returns 1 for OK, 0 for Cancel / closed.
_EXECUTE_OK = 1


def _add(model, name, service, **props):
    """Create a control model, set its properties, and insert it by name."""
    control = model.createInstance("com.sun.star.awt.UnoControl%sModel" % service)
    for key, value in props.items():
        setattr(control, key, value)
    model.insertByName(name, control)
    return control


def show_menu_picker(ctx, choices, t, app_name):
    """Show a checkbox per top-level menu; return the user's decisions.

    ``choices`` is ``menubar.top_level_choices`` output — one dict per menu with
    ``command``, ``label``, and current ``visible`` state. Returns a
    ``(visibility, save_as_template)`` tuple, where ``visibility`` maps each menu's
    UNO command ID to the ticked state, or ``None`` if the user cancelled.

    Unticking a menu here means "remove this menu entirely", which is exactly
    what the caller then feeds to ``apply_menu_profile``.
    """
    smgr = ctx.getServiceManager()
    model = smgr.createInstanceWithContext(
        "com.sun.star.awt.UnoControlDialogModel", ctx)

    inner = _WIDTH - 2 * _MARGIN
    y = _MARGIN

    model.Title = t("configure_title")
    model.Width = _WIDTH

    _add(model, "hint", "FixedText", PositionX=_MARGIN, PositionY=y,
         Width=inner, Height=_HINT_HEIGHT, MultiLine=True,
         Label=t("configure_hint", app_name))
    y += _HINT_HEIGHT + _GAP

    # One checkbox per menu, in menu-bar order, ticked if the menu is shown now.
    names = []
    for index, choice in enumerate(choices):
        name = "menu%d" % index
        # Protected menus (File, Edit, Help) are shown ticked but disabled, so
        # the rule is visible in the UI rather than a silent override on apply.
        protected = choice.get("protected", False)
        _add(model, name, "CheckBox", PositionX=_MARGIN + 2, PositionY=y,
             Width=inner - 2, Height=_ROW_HEIGHT,
             Label=choice["label"] or choice["command"],
             State=1 if (choice["visible"] or protected) else 0,
             Enabled=not protected)
        names.append((name, choice["command"]))
        y += _ROW_HEIGHT
    y += _GAP

    _add(model, "save_tpl", "CheckBox", PositionX=_MARGIN + 2, PositionY=y,
         Width=inner - 2, Height=_ROW_HEIGHT, State=0,
         Label=t("configure_save_label"))
    y += _ROW_HEIGHT + _GAP

    _add(model, "ok", "Button", PositionX=_WIDTH - _MARGIN - 2 * _BUTTON_WIDTH - 4,
         PositionY=y, Width=_BUTTON_WIDTH, Height=_BUTTON_HEIGHT,
         Label=t("configure_apply"), PushButtonType=_BUTTON_OK, DefaultButton=True)
    _add(model, "cancel", "Button", PositionX=_WIDTH - _MARGIN - _BUTTON_WIDTH,
         PositionY=y, Width=_BUTTON_WIDTH, Height=_BUTTON_HEIGHT,
         Label=t("configure_cancel"), PushButtonType=_BUTTON_CANCEL)
    model.Height = y + _BUTTON_HEIGHT + _MARGIN

    dialog = smgr.createInstanceWithContext(
        "com.sun.star.awt.UnoControlDialog", ctx)
    dialog.setModel(model)
    dialog.setVisible(False)
    toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)
    dialog.createPeer(toolkit, None)
    try:
        if dialog.execute() != _EXECUTE_OK:
            return None
        visibility = {
            command: bool(dialog.getControl(name).getModel().State)
            for name, command in names
        }
        save = bool(dialog.getControl("save_tpl").getModel().State)
        return visibility, save
    finally:
        # Dispose whether we applied or cancelled: an undisposed dialog peer
        # leaks a window that can outlive the document frame.
        dialog.dispose()
