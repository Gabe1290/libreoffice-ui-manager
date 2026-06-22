# LOUIM Template Format

LOUIM templates use the `.louim` file extension.

A `.louim` file is a JSON file that describes a simplified LibreOffice interface profile.

## Design rule

Templates must use LibreOffice UNO command IDs, not visible menu labels.

This makes templates independent of the LibreOffice language.

## Minimal example

```json
{
  "version": 1,
  "application": "writer",
  "profile": {
    "name": "Getting Started",
    "description": "Very simple Writer interface for beginners."
  },
  "menus": {
    ".uno:PickList": true,
    ".uno:EditMenu": true,
    ".uno:ViewMenu": false,
    ".uno:InsertMenu": false,
    ".uno:FormatMenu": true,
    ".uno:FormatStylesMenu": false,
    ".uno:TableMenu": false,
    ".uno:FormatFormMenu": false,
    ".uno:ToolsMenu": false,
    ".uno:WindowList": false,
    ".uno:HelpMenu": true
  },
  "addons": {},
  "toolbars": {}
}
```

Note: `.uno:PickList` is the File menu, `.uno:FormatStylesMenu` is Styles, and
`.uno:FormatFormMenu` is Form. Use `tools/discover-menus.py` against a running
LibreOffice to list the exact IDs for your version.

## Canonical Identifiers

All templates must use LibreOffice UNO command IDs.

Localized names must never be stored.

The user interface will display localized names, but the template file always stores UNO IDs.

## Built-in menus

The `menus` object maps a UNO command ID to a boolean (`true` = visible,
`false` = hidden). Commands not listed default to visible.

This works at **any depth**, not just the top-level menu bar. A command can be:

- a top-level menu — `.uno:InsertMenu` hides the whole Insert menu;
- an item inside a menu — `.uno:InsertPagebreak` hides just that entry;
- an item inside a submenu — e.g. an entry under Insert ▸ Shapes.

Hiding a menu also removes everything inside it. The menu bar is rebuilt from
LibreOffice's factory default on every Apply, so the result never depends on
what was applied before.

To find the UNO ID of an individual item, run `tools/discover-menus.py --tree`
against a running Writer — it prints the full menu tree, indented, with every
command ID.

## Extension menus

The optional `addons` object hides or shows menus contributed by **other
LibreOffice extensions** (for example, a maths add-on). These are not part of
the built-in menu bar, so they are keyed by the extension's stable
configuration node name rather than a `.uno:` command:

```json
"addons": {
  "org.openoffice.Office.addon.aide": false
}
```

Run `tools/discover-menus.py` to list the extension menus available in Writer
and their node names. LOUIM never hides its own menu.

## Toolbars

The optional `toolbars` object hides or shows whole Writer toolbars. It maps a
toolbar's **resource URL** to a boolean (`true` = visible, `false` = hidden):

```json
"toolbars": {
  "private:resource/toolbar/standardbar": true,
  "private:resource/toolbar/tableobjectbar": false
}
```

Resource URLs all start with `private:resource/toolbar/` and are
language-independent. `true` shows the toolbar, `false` hides it (by setting its
persistent `Visible` state in Writer's window-state configuration, so the change
survives a restart and applies to newly opened Writer windows). Toolbars not
listed are left at the user's own state.

Applying a template's toolbars is **non-cumulative**, like the menu bar: each
Apply first rolls back any toolbar LOUIM changed previously, then applies the new
profile against the user's original layout. So an empty `toolbars` section
(see `writer-full`) restores the user's default toolbars, and switching profiles
never leaves a leftover blend.

Because `true` genuinely forces a toolbar visible, it can turn an
optional-but-off toolbar on — that is how the bundled `writer-level-1` shows the
Drawing toolbar. Do not list a **contextual** toolbar (one shown only in a
context, e.g. `tableobjectbar` inside a table) as `true`, or it will be pinned
open everywhere. The bundled templates only manage ordinary toggleable toolbars.

"Restore Full Menus" returns every toolbar LOUIM hid to exactly the state it
had before (including removing a window-state entry LOUIM had to create).

Run `tools/discover-menus.py` to list the exact toolbar resource URLs and their
display names for your LibreOffice version.

## Toolbar buttons (icons)

The `toolbars` section above shows/hides *whole* toolbars. To thin out the icons
*inside* the toolbars — so a simplified profile doesn't show buttons for features
it removed — there are two fields:

- `toolbaritems` — a map of UNO command ID → boolean. Any command marked `false`
  has its button removed from every toolbar that holds it (at any depth,
  including dropdown sub-items). These are the same `.uno:` IDs used in `menus`.
- `hide_toolbar_buttons_with_menus` — a boolean. When `true`, every command you
  hide in `menus` also has its toolbar button removed, so reducing the menus
  reduces the matching icons without listing them twice.

```json
"menus": { ".uno:InsertObjectChart": false },
"toolbaritems": { ".uno:InsertTable": false },
"hide_toolbar_buttons_with_menus": true
```

The example removes both the Insert Chart button (because its menu entry is
hidden and the flag is on) and the Insert Table button (listed explicitly).
Pruning is non-cumulative and rebuilt from each toolbar's factory definition, so
"Restore Full Menus" returns every pruned toolbar to its original buttons.

Use `tools/discover-menus.py --tree` to find the command ID of any button (the
same IDs appear on toolbars and in menus).

## Sidebar

The optional `sidebar` object hides or shows whole sidebar **decks** (Properties,
Styles, Gallery, Navigator, …). It maps a deck's stable **Id** to a boolean
(`true` = visible, `false` = hidden):

```json
"sidebar": {
  "GalleryDeck": false,
  "PropertyDeck": true
}
```

Deck Ids are language-independent (e.g. `GalleryDeck`, `StyleListDeck`,
`NavigatorDeck`, `PropertyDeck`). Decks not listed keep their current state.

Hiding works like the `addons` section: LOUIM removes Writer from the deck's
`ContextList` (saving the original first), so the deck stops appearing in
Writer's sidebar but stays available in Calc/Draw/etc. "Restore Full Menus"
returns every deck LOUIM hid to its original context. Changes take effect for
newly opened Writer windows.

Run `tools/discover-menus.py` to list the sidebar decks available in Writer and
their Ids.

## Creating and editing your own templates

A `.louim` file is plain JSON — copy one of the bundled templates (or export your
current setup, below) and edit it in any text editor. Use `true`/`false` to show
or hide each menu, extension menu, and toolbar; keep the UNO command IDs and
resource URLs exactly as discovered (they are language-independent — never put a
localized label in the file).

To start from what you already have, use **LibreOffice UI Manager > Save Current
Layout as Template...**. LOUIM snapshots the current interface into a new
`.louim` file you can trim and rename. The snapshot captures, **item by item**:

- **menus** — every top-level menu (true/false) and every individual menu item
  you have removed (via Tools ▸ Customize) as `false`;
- **toolbaritems** — every toolbar button you have removed as `false`;
- **toolbars** — the common Writer toolbars' visibility (plus any you hid);
- **sidebar** — each deck's visibility; **addons** — extension menus.

This means a teacher can build a real "beginner" profile by hand: use
**Tools ▸ Customize** to strip the menus and toolbars down to just what learners
need, then **Save Current Layout as Template…** to capture that exact reduced
interface. Only what differs from the default is written, so the file stays
readable. The command-line equivalent is `tools/export-template.py` (run against
a Writer started with a UNO socket).