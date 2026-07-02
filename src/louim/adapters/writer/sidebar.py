# LibreOffice UI Manager — sidebar deck adapter (module-parameterized).
#
# The sidebar shows "decks" (Properties, Styles, Gallery, Navigator, ...) chosen
# by the configuration node
#
#     org.openoffice.Office.UI.Sidebar / Content / DeckList
#
# Each deck has a ``ContextList``: a list of strings, one per context descriptor,
# each "Application, Context, InitialState" (e.g. "WriterVariants, any, visible").
# A deck appears in an application when its ContextList has an entry for that
# application group (or the catch-all "any"). To hide a deck we drop the module's
# entries — exactly the approach addons.py uses for extension menus — saving the
# original list to a per-module state file so it can be restored. Changes take
# effect for newly opened windows.
#
# The DeckList is shared across applications (it is not per-module config), so a
# deck managed in two applications at once shares one ContextList; LOUIM tracks
# each module's change in its own state file. Each state record stores the
# pre-hide ``original`` list and the ``result`` LOUIM wrote: if the live
# ContextList still equals ``result``, restore writes ``original`` back
# verbatim; otherwise another module changed the shared list since, and restore
# re-adds only this module's own app entries, leaving the other module's hide
# intact. Legacy records (a bare original list) are written back verbatim.
#
# The ContextList parsing/editing is pure Python (no ``uno``) and unit-tested.

import json
import os

from louim.adapters.modules import WRITER

SIDEBAR_DECKS_NODE = "/org.openoffice.Office.UI.Sidebar/Content/DeckList"

_STATE_FILENAME = "louim-sidebar-state-%s.json"


# --- pure ContextList helpers (no uno) ---------------------------------------

def _app_of(entry):
    """Application-group name from a single ContextList entry string."""
    return entry.split(",", 1)[0].strip()


def _rest_of(entry):
    """The "Context, State" remainder of an entry, or '' if absent."""
    return entry.split(",", 1)[1].strip() if "," in entry else ""


def shows_in_module(context_list, module=WRITER):
    """True if a deck with this ContextList appears in ``module``."""
    for entry in context_list:
        app = _app_of(entry)
        if app == "any" or app in module.deck_apps:
            return True
    return False


def strip_module(context_list, module=WRITER):
    """Return a ContextList with ``module`` removed (kept elsewhere).

    The module's own entries are dropped. A catch-all "any" entry is rewritten to
    the other applications so the deck still appears outside this module. A shared
    context *group* (e.g. "DrawImpress", which covers Draw + Impress) is replaced
    with the apps to keep — so hiding a deck from Impress leaves it in Draw.
    """
    out = []
    for entry in context_list:
        app = _app_of(entry)
        rest = _rest_of(entry)
        if app == "any":
            for other in module.other_deck_apps:
                out.append("%s, %s" % (other, rest) if rest else other)
        elif app in module.deck_group_subs:
            for keep in module.deck_group_subs[app]:
                out.append("%s, %s" % (keep, rest) if rest else keep)
        elif app in module.deck_apps:
            continue  # drop the module's own entry
        else:
            out.append(entry)
    return out


def merge_context_list(current, original, module=WRITER):
    """A ContextList showing the deck in ``module`` again, keeping other hides.

    Used when the live list no longer matches what LOUIM wrote (another module
    hid or restored the same deck since). For every ``original`` entry that made
    the deck visible in this module ("any", one of the module's app groups, or a
    shared group), appends entries for the module's own plain app groups with
    the same "Context, State" remainder — never "any" or a shared group, so
    another module's hide is not undone. Entries already present are not
    duplicated.
    """
    plain_apps = [a for a in module.deck_apps if a not in module.deck_group_subs]
    out = list(current)
    for entry in original:
        app = _app_of(entry)
        if app == "any" or app in module.deck_apps:
            rest = _rest_of(entry)
            for keep in plain_apps:
                candidate = "%s, %s" % (keep, rest) if rest else keep
                if candidate not in out:
                    out.append(candidate)
    return out


# --- configuration access (uno) ----------------------------------------------

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


def _deck_path(deck_id):
    return SIDEBAR_DECKS_NODE + "/" + deck_id


def _context_list(provider, deck_id):
    """Return a deck's ContextList as a list of strings."""
    value = _read_access(provider, _deck_path(deck_id)).getByName("ContextList")
    return list(value) if value else []


def _set_context_list(provider, deck_id, entries):
    import uno
    upd = _update_access(provider, _deck_path(deck_id))
    # ContextList is a string sequence; the config manager rejects a bare Python
    # tuple ("inappropriate property value"). Hand it an explicitly typed Any.
    value = uno.Any("[]string", tuple(entries))
    uno.invoke(upd, "setPropertyValue", ("ContextList", value))
    upd.commitChanges()


def _restore_context_list(provider, deck_id, record, module):
    """Restore a deck's ContextList from a state record.

    Exact undo (write ``original`` back) when the live list is still what LOUIM
    wrote; compositional (re-add this module's app entries) when another module
    changed the shared list since. Legacy records — a bare original list from
    older LOUIM — are written back verbatim.
    """
    if not isinstance(record, dict):
        _set_context_list(provider, deck_id, record)
        return
    original = list(record.get("original") or [])
    current = _context_list(provider, deck_id)
    if current == list(record.get("result") or []):
        _set_context_list(provider, deck_id, original)
    else:
        _set_context_list(provider, deck_id,
                          merge_context_list(current, original, module))


def state_path(ctx, module=WRITER):
    """Absolute path of the LOUIM sidebar-state file for ``module``."""
    import uno
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


# --- public API --------------------------------------------------------------

def discover_sidebar_decks(ctx, module=WRITER):
    """Discover sidebar decks that appear in ``module``.

    Returns a list of dicts in configuration order, each:
        {"deck": "GalleryDeck", "title": "Gallery"}

    ``deck`` is the stable, language-independent deck Id used in a .louim
    template's "sidebar" section; ``title`` is for display only.
    """
    provider = _config_provider(ctx)
    access = _read_access(provider, SIDEBAR_DECKS_NODE)

    decks = []
    for deck_id in access.getElementNames():
        entry = access.getByName(deck_id)
        try:
            context_list = list(entry.getByName("ContextList") or [])
        except Exception:  # noqa: BLE001
            context_list = []
        if not shows_in_module(context_list, module):
            continue
        try:
            title = entry.getByName("Title")
        except Exception:  # noqa: BLE001
            title = deck_id
        decks.append({"deck": deck_id, "title": title})
    return decks


def sidebar_visibility(ctx, module=WRITER):
    """Snapshot whether each sidebar deck currently shows in ``module``.

    Returns a dict mapping deck Id to a bool, for exporting the current interface.
    """
    provider = _config_provider(ctx)
    access = _read_access(provider, SIDEBAR_DECKS_NODE)

    snapshot = {}
    for deck_id in access.getElementNames():
        try:
            context_list = list(access.getByName(deck_id).getByName("ContextList") or [])
        except Exception:  # noqa: BLE001
            continue
        snapshot[deck_id] = shows_in_module(context_list, module)
    return snapshot


def apply_sidebar_profile(ctx, sidebar, module=WRITER, path=None):
    """Hide/show ``module`` sidebar decks per a "sidebar" profile.

    ``sidebar`` maps deck Ids to booleans (True = visible, False = hidden). Decks
    not mentioned are left untouched. Returns the list of deck Ids hidden.

    The pre-hide ContextList and the value LOUIM wrote are both saved to the
    state file before the first change, so restore can undo exactly — or compose
    with another module's hide of the same deck (see ``_restore_context_list``).
    """
    path = path or state_path(ctx, module)
    provider = _config_provider(ctx)
    state = _load_state(path)

    hidden = []
    for deck_id, visible in sidebar.items():
        try:
            current = _context_list(provider, deck_id)
        except Exception:  # noqa: BLE001
            continue  # unknown deck, skip

        if visible is False:
            if shows_in_module(current, module):
                record = state.get(deck_id)
                if not isinstance(record, dict):
                    # First hide, or a legacy bare-list record to upgrade.
                    record = {"original": record if record is not None
                              else current}
                stripped = strip_module(current, module)
                _set_context_list(provider, deck_id, stripped)
                record["result"] = stripped
                state[deck_id] = record
            hidden.append(deck_id)
        else:
            # Explicitly visible: restore original if we had hidden it.
            if deck_id in state:
                _restore_context_list(provider, deck_id, state.pop(deck_id),
                                      module)

    _save_state(path, state)
    return hidden


def restore_sidebar_decks(ctx, module=WRITER, path=None):
    """Restore every sidebar deck LOUIM hid in ``module``.

    Exact where possible, compositional where another module still hides the
    same deck (see ``_restore_context_list``). Returns the list of deck Ids
    restored.
    """
    path = path or state_path(ctx, module)
    provider = _config_provider(ctx)
    state = _load_state(path)

    restored = []
    for deck_id, record in list(state.items()):
        try:
            _restore_context_list(provider, deck_id, record, module)
            restored.append(deck_id)
        except Exception:  # noqa: BLE001
            pass
    _save_state(path, {})
    return restored
