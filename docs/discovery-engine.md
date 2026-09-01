# Discovery Engine

Principle 4 of the [project constitution](project-constitution.md) requires
LOUIM to discover the current LibreOffice interface rather than work from a
hardcoded list. A hardcoded menu tree drifts out of date across LibreOffice
versions and locales, and it can't see what an extension or a teacher's own
customization added. There's no single `DiscoveryEngine` class for this.
"Discovery" is a `discover_*` function in each adapter, and they all follow
the same shape. This document maps them out, and doubles as the reference for
`tools/discover-menus.py`.

## The pattern

Every `discover_*` function reads live LibreOffice configuration, never a
bundled table. It returns language-independent identifiers, UNO command IDs,
toolbar resource URLs, deck Ids, or addon node names, as the primary key, and
attaches a human-readable label resolved separately for display only. Labels
never get persisted into a `.louim` template; see
[ui-element-model.md](ui-element-model.md). Each function takes a UNO
component context (`ctx`) and an optional `module`, default `WRITER`, so the
same function works from inside the extension
(`XSCRIPTCONTEXT.getComponentContext()`) or from an external socket connection
used by the dev tools and tests.

## What each adapter discovers

`discover_top_level_menus(ctx, module)`, in `menubar.py`, returns the module's
top-level menus in menu-bar order.

`discover_menu_items(ctx, module)`, also in `menubar.py`, returns the full
nested tree: every menu item at every depth, with a `path` giving the parent
chain and a `depth`. It reads from the factory default, so it shows the
complete tree regardless of current customization. This is how you find the
UNO ID of an item you want to hide.

`discover_toolbars(ctx, module)`, in `toolbars.py`, returns the module's
toolbars via `getUIElementsInfo(TOOLBAR)`.

`discover_sidebar_decks(ctx, module)`, in `sidebar.py`, returns sidebar decks
whose `ContextList` shows them in this module.

`discover_addon_menus(ctx, module)`, in `addons.py`, returns
extension-contributed top-level menus visible in this module, with LOUIM's own
menu excluded.

There's no `discover_toolbar_items` function. Toolbar-item hiding
(`toolbaritems.py`) reuses `discover_toolbars` to figure out which toolbars to
inspect, then walks each one's settings container directly
(`_collect_commands`) when it needs the full command list.

## Label resolution

The menu-bar UI configuration usually leaves an entry's `Label` empty.
LibreOffice resolves display text at render time, and does so more
aggressively when no document frame is open, which is exactly the situation
the headless dev tools run in. `menubar._command_labels` queries the
`UICommandDescription` service directly, keyed by the module's document
service, to get real, language-correct labels even with nothing open.
`_label_for` prefers an entry's own `Label` when present and falls back to
this lookup, stripping mnemonic markers like `~`. This was verified against a
running instance with no document open: 11 out of 11 top-level menus and 553
out of 553 menu items resolved real names.

## Export is discovery plus a visibility comparison

A `*_visibility` function in each adapter builds on its discovery function to
answer a different question: what does the current, possibly hand-customized
interface look like as a template? It compares live state against the
factory default and returns the same identifier-to-bool shape a `.louim` file
uses. `saver.build_current_template` calls all five `*_visibility` functions
and assembles the result. This is what runs when a teacher clicks "Save
Current Layout as Template...".

## Dev tool

`tools/discover-menus.py [--tree]` connects to a throwaway headless instance
(see the safety rules in [CLAUDE.md](../CLAUDE.md)) and prints menus, toolbars,
and extension menus with their UNO IDs. With `--tree` it prints the full
nested menu tree too. This is the practical way to find an identifier to put
in a template.
