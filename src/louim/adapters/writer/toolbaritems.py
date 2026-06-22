# LibreOffice UI Manager — Writer toolbar-item adapter.
#
# Whole-toolbar visibility lives in toolbars.py (the WriterWindowState config).
# This module handles the finer grain: hiding individual *buttons* inside the
# toolbars, so a simplified profile can drop the icons for features it also
# removed from the menus.
#
# Toolbar button lists are stored in the same place as the menu bar — the module
# UI configuration — so we reuse the menu bar's recursive pruning: reset a
# toolbar to its factory definition, remove every item whose command is hidden
# (at any depth, e.g. dropdown sub-items), then write it back. Applying is
# non-cumulative and restorable: a state file records which toolbars LOUIM
# rewrote so restore can drop those customizations again. Changes take effect for
# newly opened Writer windows.

import json
import os

from louim.adapters.writer.menubar import (
    _module_ui_config, _props_to_dict, _prune_hidden,
)
from louim.adapters.writer.toolbars import discover_toolbars

STATE_FILENAME = "louim-toolbaritem-state.json"


def hidden_commands_for(template):
    """Compute the set of command IDs whose toolbar buttons should be hidden.

    Combines the template's explicit ``toolbaritems`` (commands mapped False)
    with, when ``hide_toolbar_buttons_with_menus`` is true, every command the
    ``menus`` section hides — so reducing the menus reduces the matching toolbar
    icons without listing them twice. Pure function (no LibreOffice).
    """
    hidden = {c for c, visible in template.get("toolbaritems", {}).items()
              if visible is False}
    if template.get("hide_toolbar_buttons_with_menus"):
        hidden |= {c for c, visible in template.get("menus", {}).items()
                   if visible is False}
    return hidden


def hidden_toolbar_commands(ctx, template):
    """The full set of commands whose toolbar buttons a template hides.

    Starts from ``hidden_commands_for`` (explicit ``toolbaritems`` plus, when the
    flag is set, the commands hidden in ``menus``) and — when
    ``hide_toolbar_buttons_with_menus`` is set — also expands every hidden *menu*
    to the commands nested inside it, so hiding e.g. the whole Insert menu also
    drops the Insert Table / Chart toolbar buttons. Needs ``ctx`` to read the
    menu tree; the pure ``hidden_commands_for`` remains for templates that only
    list individual commands.
    """
    hidden = hidden_commands_for(template)
    if template.get("hide_toolbar_buttons_with_menus"):
        from louim.adapters.writer.menubar import menu_command_descendants
        menus_hidden = {c for c, v in template.get("menus", {}).items()
                        if v is False}
        hidden |= menu_command_descendants(ctx, menus_hidden)
    return hidden


def _collect_commands(container, out):
    """Collect every CommandURL under a settings container (depth-first)."""
    for i in range(container.getCount()):
        entry = _props_to_dict(container.getByIndex(i))
        command = entry.get("CommandURL")
        if command:
            out.append(command)
        sub = entry.get("ItemDescriptorContainer")
        if sub is not None:
            _collect_commands(sub, out)
    return out


def _state_path(ctx):
    import uno
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
        return []


def _save_state(path, resources):
    if resources:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(resources, handle, indent=2)
    elif os.path.exists(path):
        os.remove(path)


def _toolbar_resources(ctx):
    return [t["resource"] for t in discover_toolbars(ctx)]


def _visible_commands(container, out):
    """Collect commands whose toolbar item is visible (IsVisible is not False).

    Tools ▸ Customize hides a button by setting its ``IsVisible`` to False while
    leaving it in the toolbar definition (``toolbar:visible="false"`` in the
    config), so a button can be "removed" yet still present. Comparing visibility
    rather than mere presence catches those.
    """
    for i in range(container.getCount()):
        entry = _props_to_dict(container.getByIndex(i))
        command = entry.get("CommandURL")
        if command and entry.get("IsVisible", True) is not False:
            out.add(command)
        sub = entry.get("ItemDescriptorContainer")
        if sub is not None:
            _visible_commands(sub, out)
    return out


def toolbar_item_visibility(ctx):
    """Snapshot toolbar buttons a teacher has hidden, as {command: False}.

    For every toolbar, records each command that is visible in the factory
    default but not visible now — whether it was removed outright or merely
    hidden via Tools ▸ Customize (``IsVisible`` False). This is the
    ``toolbaritems`` shape, so exporting then applying reproduces the current
    toolbar buttons. Buttons still shown are omitted (they default to visible on
    apply).
    """
    ui_cfg = _module_ui_config(ctx)
    hidden = {}
    for resource in _toolbar_resources(ctx):
        try:
            default = ui_cfg.getDefaultSettings(resource)
        except Exception:  # noqa: BLE001 — toolbar without a factory default
            continue
        default_visible = _visible_commands(default, set())
        if not default_visible:
            continue
        try:
            current = ui_cfg.getSettings(resource, False)
        except Exception:  # noqa: BLE001
            continue
        current_visible = _visible_commands(current, set())
        for command in default_visible:
            if command not in current_visible:
                hidden[command] = False
    return hidden


def apply_toolbar_items(ctx, hidden_commands, path=None):
    """Hide individual toolbar buttons for the given command IDs.

    ``hidden_commands`` is a set/iterable of UNO command IDs whose buttons should
    be removed from every toolbar that holds them. Returns the list of toolbar
    resource URLs that were rewritten.

    Non-cumulative across **all** toolbars: every customized toolbar is first
    reset to its factory definition — whether LOUIM pruned it before or the user
    removed buttons by hand via Tools ▸ Customize — then the current profile's
    hidden commands are removed. This mirrors how ``apply_menu_profile`` rebuilds
    the whole menu bar from the factory default, so applying any template (even
    one with no toolbar entries, like ``writer-full``) brings the toolbars back
    to a known state and restores removed icons.
    """
    hidden_commands = set(hidden_commands)
    path = path or _state_path(ctx)
    ui_cfg = _module_ui_config(ctx)
    resources = _toolbar_resources(ctx)

    # Reset EVERY customized toolbar to its factory definition first.
    for resource in resources:
        if ui_cfg.hasSettings(resource):
            ui_cfg.removeSettings(resource)

    modified = []
    if hidden_commands:
        hidden_map = {c: False for c in hidden_commands}
        for resource in resources:
            try:
                default = ui_cfg.getDefaultSettings(resource)
            except Exception:  # noqa: BLE001 — toolbar without a factory default
                continue
            if not hidden_commands.intersection(_collect_commands(default, [])):
                continue  # nothing to remove from this toolbar
            writable = ui_cfg.getSettings(resource, True)
            removed = []
            _prune_hidden(writable, hidden_map, removed)
            if removed:
                ui_cfg.replaceSettings(resource, writable)
                modified.append(resource)

    ui_cfg.store()
    _save_state(path, modified)
    return modified


def restore_toolbar_items(ctx, path=None):
    """Reset every customized toolbar to its factory definition.

    Returns the list of resource URLs restored. Like ``restore_default_menus``,
    this returns the toolbars to the full built-in set, undoing both LOUIM's
    pruning and any hand customization.
    """
    path = path or _state_path(ctx)
    ui_cfg = _module_ui_config(ctx)

    restored = []
    for resource in _toolbar_resources(ctx):
        if ui_cfg.hasSettings(resource):
            ui_cfg.removeSettings(resource)
            restored.append(resource)
    if restored:
        ui_cfg.store()
    _save_state(path, [])
    return restored
