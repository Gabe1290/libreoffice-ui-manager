# Workspace

The [project constitution](project-constitution.md), Principle 5, lists
`Workspace` as one of three Model objects, alongside `Profile` and
`UIElement`. None of the three exist as classes in the shipped code (see
[ADR 0004](adr/0004-workspace-concept.md) for the full reasoning). This
document explains what plays the Workspace's role instead, since the question
it was meant to answer, which application and which document LOUIM is
currently acting on, is real and still needs answering.

## What a Workspace would have needed to answer

A Workspace object would have had to know which LibreOffice application is
active right now, where that application's UI configuration lives (which
config nodes, which window-state node), and where this application's LOUIM
state files should be read from and written to.

## What answers those questions instead

Which application is active gets answered per call, not held as session
state. `module_for_document(doc)`, in
[`src/louim/adapters/modules.py`](../src/louim/adapters/modules.py), inspects
the document LibreOffice currently has open through `doc.supportsService(...)`
and returns the matching `Module`. `extension.py` calls this at the start of
every apply, restore, and export entry point. There's nothing to keep in sync
if the user switches documents between calls, because nothing gets cached.

Where the config lives gets answered by the `Module` descriptor itself. Its
`doc_service`, `windowstate_node`, and sidebar and addon context-group
fields are exactly the per-application identifiers a Workspace object would
otherwise have had to look up. See
[architecture.md](architecture.md#srclouimadaptersmodulespy--the-module-descriptor).

Where state files live gets answered by each adapter's own
`state_path(ctx, module)` helper. It asks LibreOffice's `PathSubstitution`
service for the user profile directory and appends a module-keyed filename,
such as `louim-toolbar-state-writer.json` or
`louim-sidebar-state-calc.json`. There's no shared "workspace directory"
concept. Each surface's state is independent, which matches how each surface
gets applied and restored independently.

## Why this is enough

A `Workspace` object would have needed to be created, held somewhere, and kept
current as the user switched between open Writer, Calc, Impress, and Draw
windows. That's extra state that could get stale or leak. Deriving the module
fresh from the active document on every call removes that whole class of bug,
at the cost of one cheap `supportsService` check per entry point. It's the
same trade-off `architecture.md` describes for `Profile` and `UIElement`: the
constitution's Model layer turned into stateless lookups against LibreOffice's
own live configuration, with only the template itself, a plain dict,
persisted as data.

## Multi-document caveat

Because "workspace" is derived per call rather than tracked, LOUIM has no
notion of "the Writer workspace" as something you could inspect independent of
a currently-open Writer document. If no Writer, Calc, Impress, or Draw
document is the active component when an entry point runs,
`module_for_document` returns `None` and there's nothing for the entry point
to act on. That matches how the extension actually gets used, through menu
commands invoked from within the app they affect, and it hasn't needed to
change since v1.0.
