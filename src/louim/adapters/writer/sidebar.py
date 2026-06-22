# LibreOffice UI Manager — Writer sidebar adapter.
#
# The sidebar shows "decks" (Properties, Styles, Gallery, Navigator, ...) chosen
# by the configuration node
#
#     org.openoffice.Office.UI.Sidebar / Content / DeckList
#
# Each deck has a ``ContextList``: a list of strings, one per context descriptor,
# each "Application, Context, InitialState" (e.g. "WriterVariants, any, visible").
# A deck appears in Writer when its ContextList has an entry for a Writer
# application group (or the catch-all "any"). To hide a deck from Writer we drop
# its Writer entries — exactly the approach addons.py uses for extension menus —
# saving the original list to a state file so it can be restored. Changes take
# effect for newly opened Writer windows.
#
# The ContextList parsing/editing is pure Python (no ``uno``) so it is unit
# tested in CI; only the configuration read/write needs LibreOffice.

import json
import os

SIDEBAR_DECKS_NODE = "/org.openoffice.Office.UI.Sidebar/Content/DeckList"

# Application-group names that mean a deck shows in Writer. "WriterVariants"
# covers the plain/web/global Writer documents; the others appear in some deck
# definitions. "any" (handled separately) matches every application.
WRITER_DECK_APPS = (
    "WriterVariants", "Writer", "WriterWeb", "WriterGlobal",
    "WriterXForm", "WriterReport", "WriterForm",
)

# When a deck is contextually "any" (all apps) and we remove Writer, we rewrite
# the entry to the non-Writer applications so the deck stays everywhere except
# Writer — mirroring addons.py's NON_WRITER_CONTEXTS fallback.
NON_WRITER_DECK_APPS = ("Calc", "DrawImpress", "Chart", "Math")

STATE_FILENAME = "louim-sidebar-state.json"


# --- pure ContextList helpers (no uno) ---------------------------------------

def _app_of(entry):
    """Application-group name from a single ContextList entry string."""
    return entry.split(",", 1)[0].strip()


def _rest_of(entry):
    """The "Context, State" remainder of an entry, or '' if absent."""
    return entry.split(",", 1)[1].strip() if "," in entry else ""


def shows_in_writer(context_list):
    """True if a deck with this ContextList appears in Writer."""
    for entry in context_list:
        app = _app_of(entry)
        if app == "any" or app in WRITER_DECK_APPS:
            return True
    return False


def strip_writer(context_list):
    """Return a ContextList with Writer removed (kept elsewhere).

    Writer-specific entries are dropped. A catch-all "any" entry is rewritten to
    the non-Writer applications so the deck still appears in Calc/Draw/etc.
    """
    out = []
    for entry in context_list:
        app = _app_of(entry)
        if app == "any":
            rest = _rest_of(entry)
            for other in NON_WRITER_DECK_APPS:
                out.append("%s, %s" % (other, rest) if rest else other)
        elif app in WRITER_DECK_APPS:
            continue  # drop the Writer entry
        else:
            out.append(entry)
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
    # tuple ("inappropriate property value"). Hand it an explicitly typed Any via
    # uno.invoke, the same way the menu-bar adapter passes typed sequences.
    value = uno.Any("[]string", tuple(entries))
    uno.invoke(upd, "setPropertyValue", ("ContextList", value))
    upd.commitChanges()


def state_path(ctx):
    """Absolute path of the LOUIM sidebar-state file in the user profile."""
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
        return {}


def _save_state(path, state):
    if state:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2)
    elif os.path.exists(path):
        os.remove(path)


# --- public API --------------------------------------------------------------

def discover_sidebar_decks(ctx):
    """Discover sidebar decks that appear in Writer.

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
        if not shows_in_writer(context_list):
            continue
        try:
            title = entry.getByName("Title")
        except Exception:  # noqa: BLE001
            title = deck_id
        decks.append({"deck": deck_id, "title": title})
    return decks


def sidebar_visibility(ctx):
    """Snapshot whether each sidebar deck currently shows in Writer.

    Returns a dict mapping deck Id to a bool, for exporting the current interface
    as a template.
    """
    provider = _config_provider(ctx)
    access = _read_access(provider, SIDEBAR_DECKS_NODE)

    snapshot = {}
    for deck_id in access.getElementNames():
        try:
            context_list = list(access.getByName(deck_id).getByName("ContextList") or [])
        except Exception:  # noqa: BLE001
            continue
        snapshot[deck_id] = shows_in_writer(context_list)
    return snapshot


def apply_sidebar_profile(ctx, sidebar, path=None):
    """Hide/show Writer sidebar decks per a "sidebar" profile.

    ``sidebar`` maps deck Ids to booleans (True = visible, False = hidden). Decks
    not mentioned are left untouched. Returns the list of deck Ids that were
    hidden.

    Original ContextList values are saved to the state file before the first
    change so the exact pre-LOUIM state can be restored, even across restarts.
    """
    path = path or state_path(ctx)
    provider = _config_provider(ctx)
    state = _load_state(path)

    hidden = []
    for deck_id, visible in sidebar.items():
        try:
            current = _context_list(provider, deck_id)
        except Exception:  # noqa: BLE001
            continue  # unknown deck, skip

        if visible is False:
            if shows_in_writer(current):
                if deck_id not in state:
                    state[deck_id] = current  # remember the original
                _set_context_list(provider, deck_id, strip_writer(current))
            hidden.append(deck_id)
        else:
            # Explicitly visible: restore original if we had hidden it.
            if deck_id in state:
                _set_context_list(provider, deck_id, state.pop(deck_id))

    _save_state(path, state)
    return hidden


def restore_sidebar_decks(ctx, path=None):
    """Restore every sidebar deck LOUIM hid to its original ContextList.

    Returns the list of deck Ids restored.
    """
    path = path or state_path(ctx)
    provider = _config_provider(ctx)
    state = _load_state(path)

    restored = []
    for deck_id, original in list(state.items()):
        try:
            _set_context_list(provider, deck_id, original)
            restored.append(deck_id)
        except Exception:  # noqa: BLE001
            pass
    _save_state(path, {})
    return restored
