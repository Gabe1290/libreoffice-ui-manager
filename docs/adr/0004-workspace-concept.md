# ADR 0004 — Drop the `Workspace` object; derive the active module per call

## Status

Accepted, superseding the `Workspace` model object in
`docs/project-constitution.md`, Principle 5. In force since Calc support in
v2.0, which forced the question of "which application is this operation for"
to get answered concretely for the first time.

## Context

The constitution's Model layer names `Workspace` alongside `Profile` and
`UIElement`. Implicitly, this meant an object tracking which LibreOffice
application and document LOUIM is currently working with, presumably created
once and consulted, and kept in sync, as the user moved between windows.

When Calc support was added, the question that actually needed answering was
narrower: given the document that is the active component right now, which
`Module` applies? That's a pure function of the document itself, and it can
be answered fresh every time rather than tracked.

## Decision

No `Workspace` object. `module_for_document(doc)` in
`src/louim/adapters/modules.py` inspects the active document through
`doc.supportsService(module.doc_service)` and returns the matching `Module`
on every call. `extension.py`'s entry points call it at the start of each
apply, restore, or export, rather than reading it from any held state. See
[workspace.md](../workspace.md) for the full mapping from what a `Workspace`
would have answered to what answers it instead.

## Consequences

There's no session state to keep in sync if the user switches between an
open Writer document and an open Calc document between two LOUIM menu
clicks. Each click re-derives the module from scratch. This costs one extra
`supportsService` check per entry point call, which is negligible, paid to
avoid a whole class of stale-workspace bugs. If no supported document is the
active component, `module_for_document` returns `None` and the entry point
has nothing to act on. There's no separate "no workspace selected" state
machine to maintain, just a `None` check. Per-module state files, like
`louim-toolbar-state-writer.json`, already give each application-scoped
operation its own persistent identity without needing a `Workspace` object to
own them. See [architecture.md](../architecture.md).

## Where this lives in code

`module_for_document` in `src/louim/adapters/modules.py`, called from every
entry point in `src/louim/extension.py`.
