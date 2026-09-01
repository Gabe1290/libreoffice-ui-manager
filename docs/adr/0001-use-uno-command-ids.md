# ADR 0001 — Identify UI elements by UNO command ID, never by localized label

## Status

Accepted. In force since the first Discovery Engine in v1.0, unchanged
through v4.3.0.

## Context

LibreOffice ships in many languages, and a teacher and a student might run
different UI languages on the same `.louim` template. Every menu, toolbar
button, and extension menu LOUIM manages has both a stable internal
identifier, a UNO command URL like `.uno:InsertPagebreak`, a toolbar resource
URL, or a config node name, and a display label that LibreOffice localizes at
render time.

## Decision

Every template and every internal comparison uses the stable identifier.
Labels get resolved separately, through `UICommandDescription` (see
discovery-engine.md), purely for display, and they're never written into a
`.louim` file or used to decide what gets hidden.

## Consequences

A `.louim` template built in an English LibreOffice applies identically in a
French, German, or Italian one, with no translation step and no per-language
template variants. Discovery, export, and apply all key on the identifier;
label lookups can fail, if `UICommandDescription` is unavailable or no
document frame is open, without breaking the actual hide/show logic. They
only degrade what gets shown to the human. Tooling exists specifically
because identifiers aren't visible anywhere in the LibreOffice UI itself. A
teacher can't get `.uno:InsertPagebreak` by looking at a menu, so
`tools/discover-menus.py` was necessary from day one.

## Where this lives in code

Principle 3 in `docs/project-constitution.md`; enforced throughout
`src/louim/adapters/writer/*.py`, where every discovery, apply, and restore
function keys on `command`, `resource`, `deck`, or `node`, never `label`. The
i18n tests assert placeholder parity but never touch template content.
