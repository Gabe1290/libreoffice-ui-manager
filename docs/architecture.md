# Architecture

This describes the architecture as shipped in v4.3.0, not the earlier plan in
[project-constitution.md](project-constitution.md). Building the real thing
simplified the original Model/Engine/UI layering. The [ADRs](adr/) explain why
each simplification happened.

## Overview

LOUIM has no central "Core Engine" object and no persisted internal model. A
small set of adapter modules, one per UI surface, talk to LibreOffice's own
configuration directly: the menu bar, toolbars, toolbar buttons, sidebar
decks, and addon menus. Every adapter function is parameterized by a `Module`
descriptor (`src/louim/adapters/modules.py`) instead of being duplicated per
application, so one code path drives Writer, Calc, Impress, and Draw.
Templates are the only persisted model. They're plain JSON dicts, validated on
load and assembled on save; there's no in-memory "Profile" class sitting
behind them. `extension.py` is the only place that talks to both LibreOffice's
script framework and the adapters, and it stays thin: entry-point glue, not a
business-logic layer.

## Main components

### `src/louim/adapters/modules.py` — the `Module` descriptor

A `Module` bundles the handful of identifiers that differ between LibreOffice
applications: the document service name, the window-state config node, the
sidebar `ContextList` app-group names, and the addon `Context` service names.
`WRITER`, `CALC`, `IMPRESS`, and `DRAW` are the four instances. `MODULES` maps
template `"application"` strings to them, and `module_for_document(doc)` picks
the right one for the active window using `supportsService`. This file is
pure data with no `uno` import, so it's importable and unit-tested without
LibreOffice.

### `src/louim/adapters/writer/` — the adapters

The package name is historical (Writer was the only app in v1). Every function
here takes a `module` argument, default `WRITER`, and works for any app.

`menubar.py` manages the menu bar itself:
`private:resource/menubar/menubar` in the module UI configuration. It
discovers top-level menus and the full nested item tree. Applying a
visibility profile resets to the factory default, then recursively removes
every command marked `false` at any depth (`_prune_hidden`). It also enforces
`PROTECTED_MENUS`, File, Edit, and Help, so a profile can never remove LOUIM's
own anchor menu. `toolbaritems.py` reuses this pruning logic, since toolbar
button lists live in the same kind of settings container.

`toolbars.py` handles whole-toolbar visibility through the
`org.openoffice.Office.UI.<Module>WindowState/UIElements/States` config. This
is a different mechanism from the menu bar: a `Visible` flag per toolbar
resource URL rather than a tree to prune.

`toolbaritems.py` hides individual buttons inside toolbars.

`sidebar.py` manages sidebar decks such as Properties, Styles, and Gallery,
through each deck's `ContextList` under
`org.openoffice.Office.UI.Sidebar/Content/DeckList`. The list-editing logic
(`shows_in_module`, `strip_module`, `merge_context_list`) is `uno`-free and
unit-tested. A deck's `ContextList` is shared config, so restoring composes
with whatever another `Module` may have changed in the meantime instead of
overwriting it outright.

`addons.py` manages menus contributed by other extensions, merged separately
from the built-in menu bar through
`org.openoffice.Office.Addons/AddonUI/OfficeMenuBar` and its `Context`
property. It follows the same compositional-restore approach as `sidebar.py`,
for the same reason: `Context` is shared config too.

Every adapter follows roughly the same shape. A pure discovery or snapshot
function needs no `uno` to test its logic. An apply function is
non-cumulative, always rebuilt from the factory default or the pre-LOUIM
state rather than stacked on top of the last apply. A restore function
reverts using a per-module JSON state file in the user profile
(`louim-<surface>-state-<app>.json`).

### `src/louim/template/` — the Template Manager

Pure Python, no `uno` import anywhere in this package. `loader.py` parses and
validates a `.louim` file: checks the JSON shape, checks `version` against
`TEMPLATE_VERSION` (rejecting anything newer than this LOUIM supports), checks
`application` against `SUPPORTED_APPLICATIONS`, and checks that every
visibility section is a plain string-to-bool map. `saver.py` is the mirror.
`assemble_template` builds the template dict from visibility maps,
`build_current_template` calls each adapter's snapshot function for a given
module and assembles the result, and `save_template` writes formatted JSON.

### `src/louim/extension.py` — the entry-point glue

This exposes `g_exportedScripts` for LibreOffice's script provider: file
pickers, message boxes, and the apply/restore/export commands wired to
`org.louim.libreoffice-ui-manager.menu` in `extension/Addons.xcu`. It routes
by `module_for_document(doc)`, so the same menu entries work in any of the
four apps. This is the only layer that catches broad `Exception`. Everything
below it lets errors propagate so tests can catch them.

### `src/louim/ui/menu_picker.py` — the Configure Menus dialog

Builds a tickbox-per-menu dialog at runtime from `UnoControlDialogModel`,
sourcing labels from `UICommandDescription` so they match the user's own
LibreOffice language. `menubar.top_level_choices()` supplies the list from the
factory default, so a menu LOUIM already hid still appears and can be brought
back. `menubar.merge_top_level_choices()` overlays the dialog's choices onto a
full `menu_visibility()` snapshot without resurrecting items that were hidden
individually.

### `src/louim/i18n.py`

A pure `translator(lang)` function over string tables for English, French,
German, and Italian, with an English fallback and test-enforced
`%`-placeholder parity across languages. `office_language(ctx)` reads the live
LibreOffice UI language to pick which table to use.

## How a template flows through the system

Discovery reads the live UI and returns language-independent identifiers.
Export snapshots current state as identifier-to-bool maps and assembles them
into a template dict, which `extension.export_template` writes through a file
picker. Loading parses and validates a `.louim` file into that same dict
shape. Applying calls each adapter's `apply_*` function with the matching
section of the template; every apply is non-cumulative, so applying two
templates in a row never stacks, the second one wins outright. Restoring
reverts each surface using its own state file, independent of whatever
template was last applied.

## What changed from the original design

The project constitution (Principle 5) envisioned three layers: Model
(Workspace, Profile, UIElement), Engine (Discovery Engine, Template Manager,
Apply Engine), and UI, with a Core Engine that never touches LibreOffice
directly. In practice there's no `Workspace` object (see
[ADR 0004](adr/0004-workspace-concept.md)) and no unified `UIElement` class
covering menus, toolbars, toolbar items, sidebar decks, and addons (see
[ADR 0003](adr/0003-ui-element-model.md)). There's no separate Core Engine
either; `extension.py` calls the adapters directly. The isolation the
constitution wanted is achieved a different way: every adapter keeps its
`uno` import lazy, so the pure logic (parsing, validation, list editing,
pruning) is unit-tested without LibreOffice, and only the thin function
bodies that call UNO APIs need a live instance.

The Discovery Engine and Apply Engine the constitution names do exist. They
just live as functions spread across the adapters, one discovery/apply pair
per surface, rather than as standalone classes. See
[discovery-engine.md](discovery-engine.md) and
[ui-element-model.md](ui-element-model.md).
