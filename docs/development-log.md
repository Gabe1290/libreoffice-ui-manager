# Development Log

**Status note (2026-09-01):** this log stopped after its first session, back
when the extension's Python entry point didn't yet execute (milestone 0.3).
Everything below is historical, kept for the record of where the project
started rather than as a live document. LOUIM has since shipped v1.0.0
through v4.3.0, with Writer, Calc, Impress, and Draw support, and is
mature/stable per [HANDOFF.md](../HANDOFF.md). For current status, use
[HANDOFF.md](../HANDOFF.md) for running status updated every session,
[CHANGELOG.md](../CHANGELOG.md) for the per-release history this log never
grew into, and [PROJECT.md](../PROJECT.md) for the current milestone and
open tasks.

## Session 1

### Project Vision

LOUIM is an educational LibreOffice extension.

Its purpose is to progressively simplify the LibreOffice interface to reduce cognitive overload while learning.

It is **not** primarily a lockdown or administration tool.

Teachers can create and share interface templates that students can import.

---

## Supported Platforms

* Linux
* Windows
* macOS

---

## Version 1 Scope

* LibreOffice Writer only
* Python
* LibreOffice Extension (.oxt)

---

## Architecture Decisions

* Use UNO command IDs internally.
* Keep LibreOffice-specific code isolated.
* `.louim` templates remain language-independent.
* The extension should eventually import and export LibreOffice interface configurations.

---

## Current Repository Status

Completed:

* Documentation
* Project structure
* Build system
* Initial extension packaging
* Architecture documents
* Roadmap

Current milestone:

Milestone 0.3 — First working extension.

Goal:

```
Tools
    LibreOffice UI Manager...

↓

Hello LOUIM
```

No UI customization yet.

---

## Current Issue

The extension packages correctly, but the Python entry point does not execute.

Most likely causes:

* Python registration inside the extension
* Incorrect script location
* Use of `XSCRIPTCONTEXT` inside an extension

---

## Decision

Rather than debugging packaging immediately, first create a working Python macro.

Development sequence:

1. Working Python macro
2. Hello World dialog
3. Package as an extension
4. Add Tools menu
5. Continue with Discovery Engine

---

## Next Session

1. Make a minimal Python macro work.
2. Verify UNO Python execution.
3. Convert it into an installable extension.
4. Build a development workflow for rapid testing without rebuilding the .oxt every time.

---

## Long-Term Vision

LOUIM should become the reference educational interface manager for LibreOffice.

Teachers should be able to create and share progressive Writer interfaces that students can load with a single click.
