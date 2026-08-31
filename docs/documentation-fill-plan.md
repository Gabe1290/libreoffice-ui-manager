# Documentation Fill Plan

Tracks the plan to fill the currently-empty docs/guide files and correct a few
stale ones. Written 2026-08-31. Update the checkboxes as tiers land; delete
this file once Tier 3 is done and its content is absorbed into `docs/README.md`
history (or just leave it as a record — no strong opinion).

## Context / decisions made

- `docs/workspace.md`, `docs/ui-element-model.md`, and ADRs 0003/0004 were
  named for a "Workspace -> Application -> UI Elements -> Profile" model
  (see `docs/project-constitution.md` Principle 5, `docs/architecture.md`
  "Internal Model") that was **never actually built that way**. The real code
  uses a simpler `Module` descriptor (`src/louim/adapters/modules.py`): a
  plain data object per app (doc service, window-state node, sidebar/addon
  context names) that every adapter takes as a parameter. There is no
  `Workspace` or `UIElement` class anywhere in `src/`.
  **Decision: document the as-built `Module` pattern**, not the original
  aspirational object model. Note the supersession explicitly in ADR 0004 so
  nobody goes looking for a `Workspace` class.
- Also correcting three already-filled docs that now contradict PROJECT.md's
  actual status (v4.0.0, all four apps shipped): `architecture.md`,
  `project-definition.md`, `roadmap.md`. Small targeted edits, not rewrites.
- Sequencing: tiered, review after each tier rather than all 14 files at once.

## Tier 1 — Technical docs (contributors) — not started

- [ ] `docs/adr/0001-use-uno-command-ids.md` — decision record for
      design-principles.md #4 / constitution Principle 3: templates key on
      UNO command IDs / resource URLs / node names, never localized labels.
- [ ] `docs/adr/0002-discovery-engine.md` — decision to discover the live
      interface rather than hardcode per-version menu trees; references the
      real `discover_*` functions (`discover_top_level_menus`,
      `discover_menu_items`, `discover_toolbars`, `discover_sidebar_decks`).
- [ ] `docs/adr/0003-ui-element-model.md` — as-built: "UI element" in practice
      is a command/resource/node id + bool in a template map, no runtime
      object model.
- [ ] `docs/adr/0004-workspace-concept.md` — as-built: "Workspace" collapsed
      into the `Module` descriptor; explicitly supersedes the earlier planned
      Workspace/UIElement/Profile hierarchy.
- [ ] `docs/discovery-engine.md` — reference expanding ADR 0002: what each
      `discover_*` returns, label resolution via `UICommandDescription`,
      `tools/discover-menus.py --tree`, module-parameterization.
- [ ] `docs/ui-element-model.md` — reference expanding ADR 0003: the element
      kinds LOUIM tracks (menu commands, toolbars, toolbar items, sidebar
      decks, addon menus) and their template shape (cross-reference
      `docs/template-format.md`, don't duplicate it).
- [ ] `docs/workspace.md` — reference expanding ADR 0004: `Module` fields, the
      four instances (WRITER/CALC/IMPRESS/DRAW), `module_for_document`, why
      adding an app is "a new Module + templates."
- [ ] `docs/coding-standards.md` — from CLAUDE.md's Conventions section plus
      observed patterns: why-not-what docstrings, `except Exception` only at
      the extension.py glue boundary, pure-Python logic vs. lazy `uno`
      imports, non-cumulative apply/restore with a state file, i18n rules.
- [ ] `docs/developer-guide.md` — onboarding: repo layout, `pytest`, dev
      tools, the throwaway-headless-instance safety rule (link CLAUDE.md,
      don't repeat it), how to add a new adapter or Module.
- [ ] Stale-doc fixes bundled here:
  - [ ] `docs/architecture.md` — replace the Workspace/UIElements diagram
        with the actual Module-parameterized flow; Calc/Impress/Draw are
        done, not "future."
  - [ ] `docs/project-definition.md` — "Version 1 supports only Writer" ->
        reflect v4.0.0 (all four apps shipped).
  - [ ] `docs/roadmap.md` — mark Milestones 0.1-0.7 and Versions 1.0-4.0 done
        (per PROJECT.md); add what's actually next (PROJECT.md's "Next
        Session Tasks").

## Tier 2 — User-facing guides — not started

- [ ] `docs/glossary.md` — Template, Profile, Module, Apply/Restore,
      non-cumulative, UNO command ID, Discovery, Addon, Sidebar deck,
      `.louim`.
- [ ] `docs/teacher-guide.md` — task-oriented: apply a starter template,
      customize via Tools > Customize + "Save Current Layout as
      Template...", share a `.louim` file, restore full menus. No internals.

## Tier 3 — Education essays (`docs/education/`) — not started

- [ ] `why-progressive-interfaces-matter.md` — pedagogical case for
      progressive disclosure.
- [ ] `reducing-cognitive-load.md` — mechanism (fewer visible tools -> less
      decision fatigue), tied to the level-1/level-2/full template pattern.
- [ ] `designing-progressive-writer-courses.md` — sequencing level-1 ->
      level-2 -> full across a course.
- [ ] `using-louim-in-primary-schools.md` — classroom-specific (young
      learners, simple vocabulary).
- [ ] `using-louim-in-adult-education.md` — adult-learner angle (digital
      literacy programs, self-paced).

## How to resume

Say "continue the documentation fill plan" (or reference this file). Work
through the next unchecked tier, show the drafts for review before moving to
the next tier, then update the checkboxes here and in `HANDOFF.md`.
