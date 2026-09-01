# Development Roadmap

## Milestone 0.1

Project creation

- Git repository
- Documentation
- GitHub
- Initial templates

---

## Milestone 0.2

Documentation Complete

- Vision
- Architecture
- Design principles
- Template format
- Discovery Engine
- Workspace
- Coding standards
- Developer guide

---

## Milestone 0.3

First Extension

- Installable OXT
- Tools menu
- "Hello LOUIM" dialog

---

## Milestone 0.4

Discovery Engine

- Discover Writer menus
- Discover toolbars
- Discover sidebars
- Discover commands

---

## Milestone 0.5

Profile Manager

- Internal data model
- Save profile
- Load profile

---

## Milestone 0.6

Template Manager

- Import template
- Export template
- Export current interface

---

## Milestone 0.7

Apply Engine

- Hide menus
- Restore menus
- Apply profile

---

## Version 1.0

Stable Writer Release

---

## Version 2.0

Calc

---

## Version 3.0

Impress

---

## Version 4.0

Draw

---

## Version 4.1 – 4.2

Stabilization

- Fix cross-application audit findings: wrong-app messaging, localized
  restore confirmation, addon/sidebar state composing across modules
- Move source of truth from GitHub to GitLab, with automated tag-driven
  releases
- Reconcile a history divergence caused during the move (4.2.0)
- Fix the release asset filename (4.2.1) and a `NameError` regression in the
  addon adapter (4.2.2); the latter got a permanent static guard test

---

## Version 4.3

Configure Menus

- In-app dialog to remove a whole built-in top-level menu, something
  Tools ▸ Customize can't do
- Protect File, Edit, and Help from ever being hidden, closing a menu-bar
  lockout

---

## Current phase — Maintenance

As of v4.3.0 (2026-08-30) the project considers itself mature and stable
(see [HANDOFF.md](../HANDOFF.md)). All four milestone-0.3-through-4.0 goals
are delivered, and day-to-day status now lives in `CHANGELOG.md` and
`HANDOFF.md` rather than new numbered milestones here. Open items are
tracked as a punch list in PROJECT.md's "Next Session Tasks," not as
roadmap milestones. The Notebookbar/tabbed UI is deliberately out of scope
for LOUIM; it belongs to the separate LONBM project.

