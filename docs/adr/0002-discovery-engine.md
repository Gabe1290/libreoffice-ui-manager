# ADR 0002 — Discover the live interface; never hardcode it

## Status

Accepted. In force since v1.0.

## Context

An alternative to reading LibreOffice's own configuration would be to ship a
bundled table of known menus, toolbars, and commands per LibreOffice version.
That table would need updating for every LibreOffice release, it would miss
anything an extension like Dmaths or a teacher's own Tools ▸ Customize
contributed, and it would silently drift out of sync with reality over time.

## Decision

Every `discover_*` and `*_visibility` function reads live LibreOffice
configuration at call time: the module UI configuration manager for menus and
toolbars, the window-state config for toolbar visibility, the Sidebar config
for decks, the Addons config for extension menus. Nothing about the interface
LOUIM can see is bundled as a static table. See
[discovery-engine.md](../discovery-engine.md) for the full function map.

## Consequences

LOUIM automatically sees whatever menus, toolbars, decks, and addons the
running LibreOffice actually has, including third-party extension menus and
anything a teacher removed by hand before exporting. The "Save Current Layout
as Template..." feature depends on this directly. There's no maintenance
burden tracking LibreOffice's menu structure across versions; a discovery
call against a newer LibreOffice just returns whatever that version actually
has. The tradeoff is that every discovery or export call needs a live UNO
context. There's no offline fallback for "what does Writer's menu bar look
like right now." That's why the dev tools exist: finding an identifier to put
in a template means actually asking a running instance, per the safety rules
in [CLAUDE.md](../../CLAUDE.md), a throwaway headless instance, never the
user's own.

## Where this lives in code

Principle 4 in `docs/project-constitution.md` — "Hardcoded interface
definitions should only be used as compatibility fallbacks," and in practice
none exist. Every `discover_*` and `*_visibility` function across
`src/louim/adapters/writer/*.py`.
