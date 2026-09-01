# ADR 0003 — No unified `UIElement` class; a flat identifier-to-bool map per surface

## Status

Accepted, superseding the unified `UIElement` model in
`docs/project-constitution.md`, Principle 5. In force since the toolbar
adapter was added in Apply Engine v2, which established the pattern later
surfaces (toolbar items, sidebar, addons) all followed.

## Context

The constitution's Model layer names a single `UIElement` type meant to
represent, generically, a piece of interface LOUIM can show or hide: menus,
toolbars, and whatever else got added later. As toolbars, individual toolbar
buttons, sidebar decks, and extension menus actually got built, each turned
out to need a genuinely different storage mechanism. Menus need a settings
tree to reset and prune, keyed by UNO command ID. Toolbars need a flat
`Visible` flag per resource URL in the window-state config. Toolbar items
need the same kind of settings tree as menus, but per toolbar. Sidebar decks
need a shared string list (`ContextList`) per deck, edited compositionally
because it's shared across applications. Addon menus need a shared
comma-separated string (`Context`) per node, edited the same compositional
way as sidebar decks, for the same reason.

A single `UIElement` class covering all five would need either a large
optional-field union, where most fields are meaningless for most instances,
or a subclass per surface that ends up doing all the real work anyway, at
which point the base class doesn't contribute much beyond a name.

## Decision

No `UIElement` class. Each surface keeps its own identifier namespace, UNO
command ID, toolbar resource URL, deck Id, or addon node name, and its own
flat `{identifier: bool}` map, both in memory and in the `.louim` file format
(`menus`, `toolbars`, `toolbaritems`, `sidebar`, `addons` — five independent
top-level keys; see [template-format.md](../template-format.md)). What's
actually shared across all five isn't a base class, it's behavioral: the
discovery, apply, and restore function shape documented in
[ui-element-model.md](../ui-element-model.md) and
[discovery-engine.md](../discovery-engine.md).

## Consequences

Adding a sixth surface means adding a sixth adapter module and a sixth
template section, not modifying a shared class. That's held for four
surfaces added after menus, toolbars, toolbar items, sidebar, and addons,
each shipped in its own release. Two surfaces, menus and toolbar items,
share code directly through `menubar._prune_hidden`, because their storage
genuinely is the same shape. Reuse follows structural similarity here, it
isn't forced through a common interface. The `.louim` format stays easy to
hand-edit, a goal since v1, because each section is a plain flat map with no
nested element-type discriminators to get right. A generic UI tool that
wanted to render "all UI elements" in one list would need to merge five
differently-keyed maps itself. LOUIM's own dialogs, like Configure Menus,
only ever operate on one surface at a time, so this hasn't been a real cost
in practice.

## Where this lives in code

`src/louim/adapters/writer/menubar.py`, `toolbars.py`, `toolbaritems.py`,
`sidebar.py`, and `addons.py` — five independent modules, no shared base
class and no import between them except `toolbaritems.py` reusing
`menubar._prune_hidden`.
