# UI Element Model

This is how LOUIM represents the pieces of interface it can hide and show.
There's no shared `UIElement` class (see [ADR 0003](adr/0003-ui-element-model.md)
for why), so instead of documenting one type, this is a map across the five
kinds of element.

Every kind shares three things: a language-independent identifier, a boolean
visibility, and a section name in the `.louim` template format (the full JSON
schema is in [template-format.md](template-format.md)). What differs is where
LibreOffice stores that visibility and how it gets edited.

## Menus (`menus`)

The identifier is a UNO command ID, like `.uno:InsertMenu` or
`.uno:InsertPagebreak`. It works the same way for a top-level menu or an item
nested at any depth.

Storage is the menu bar settings tree at
`private:resource/menubar/menubar`, inside the module UI configuration.
Nested items live in each entry's `ItemDescriptorContainer`.

Editing is non-cumulative and whole-tree. Applying a profile resets the menu
bar to LibreOffice's factory default, then recursively removes every entry
whose command is marked `false` (`menubar._prune_hidden`). Hiding a parent
removes everything inside it, so a template never has to list a hidden menu's
children individually. Three commands can never be hidden: File, Edit, and
Help, tracked in `PROTECTED_MENUS` and enforced in `apply_menu_profile`
regardless of what a template asks for.

Adapter: `src/louim/adapters/writer/menubar.py`.

## Toolbars (`toolbars`)

The identifier is a toolbar resource URL, like
`private:resource/toolbar/standardbar`.

Storage is a `Visible` boolean per resource in
`org.openoffice.Office.UI.<Module>WindowState/UIElements/States`. This is the
same config that View ▸ Toolbars writes to, which is why toggling a toolbar
there survives a restart.

Editing is non-cumulative across all toolbars. `true` genuinely forces a
toolbar visible, even one that's off by default like Drawing. `false` hides
it. A toolbar left out of the profile returns to whatever state it was in
before LOUIM touched it. Don't mark a contextual toolbar like `tableobjectbar`
as `true` — it will pin the toolbar open outside the context that would
normally show it.

Adapter: `src/louim/adapters/writer/toolbars.py`.

## Toolbar items (`toolbaritems`)

The identifier is a UNO command ID, the same namespace `menus` uses, since a
toolbar button and a menu entry for the same feature share a command.

Storage is each toolbar's own settings container, the same kind of tree the
menu bar uses. That's why toolbar-item pruning simply reuses
`menubar._prune_hidden` rather than reimplementing it.

Editing is non-cumulative across all toolbars: every apply first resets every
customized toolbar to its factory definition, undoing both LOUIM's own prior
changes and anything a teacher removed by hand through Tools ▸ Customize, then
removes the current profile's hidden commands.

A template-level flag, `hide_toolbar_buttons_with_menus`, unions this section
with whatever `menus` hides. Hiding a menu also drops the toolbar buttons for
every command nested inside it (`menubar.menu_command_descendants`), so a
reduced menu and a reduced toolbar stay in sync without listing every command
twice.

Adapter: `src/louim/adapters/writer/toolbaritems.py`.

## Sidebar decks (`sidebar`)

The identifier is a deck Id, like `GalleryDeck` or `PropertyDeck`.

Storage is each deck's `ContextList` under
`org.openoffice.Office.UI.Sidebar/Content/DeckList/<deckId>`, a list of
strings shaped `"Application, Context, InitialState"`. A deck shows in an
application if its `ContextList` has an entry for that app's group or the
catch-all `"any"`.

Editing works on a shared list. `DeckList` isn't per-application config, so
hiding a deck from Writer edits the same list Calc's entry lives in. Hiding a
deck drops this module's app-group entries, or rewrites `"any"` to cover the
other apps instead. Impress and Draw additionally share a `"DrawImpress"`
group, substituted for the sibling app on hide, so hiding a deck from Impress
leaves it visible in Draw. Because the list is shared, restore has to be
careful: if the list still matches exactly what LOUIM last wrote, restore
replays the original untouched; if another module changed it in the
meantime, restore re-adds only this module's own entries instead of
clobbering the other module's hide.

Adapter: `src/louim/adapters/writer/sidebar.py`.

## Addon menus (`addons`)

The identifier is an addon config node name, like
`org.openoffice.Office.addon.aide`. These are extension-contributed
top-level menus, such as Dmaths, not part of the built-in menu bar.

Storage is a `Context` property, comma-separated document-service names, on
each node under `org.openoffice.Office.Addons/AddonUI/OfficeMenuBar`. An
empty `Context` means the menu shows in every module.

Editing follows the same shared-config, compositional-restore shape as
sidebar decks, and for the same reason: `Context` is one value covering every
application. LOUIM removes only this module's services on hide, and on
restore either replays the original verbatim or re-adds just this module's
services if something else changed the value since. LOUIM's own menu node,
`org.louim.libreoffice-ui-manager.menu`, is always excluded — it can never
hide itself.

Adapter: `src/louim/adapters/writer/addons.py`.

## Common patterns across all five

Discovery is always live, never a hardcoded table. See
[discovery-engine.md](discovery-engine.md) and
[ADR 0002](adr/0002-discovery-engine.md). Labels come from
`UICommandDescription`, which is language-aware, while identifiers come
straight from LibreOffice's own configuration.

A state file per surface, per module, lives in the user profile
(`louim-<surface>-state-<app>.json`) and records enough to undo exactly what
LOUIM changed, independent of whichever template was last applied.

An identifier left out of a template defaults to visible on apply, so a
template only needs to name what it hides.

Labels are display-only. No adapter ever writes a localized label into a
`.louim` file, only the identifier gets persisted. See Principle 3 in
[project-constitution.md](project-constitution.md).
