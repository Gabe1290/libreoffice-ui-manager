# LOUIM — Development Handoff

**Purpose.** Running status/handoff so work can be picked up on any computer.
**Practice for every machine on this project:** at the end of a session, update
this file, then `git commit` + `git push`; on start, `git pull` and read it first.

_Last updated: 2026-06-24._

## Status: **mature / stable.**

LOUIM (LibreOffice UI Manager) is the working product — it simplifies the
**classic menus/toolbars** from a `.louim` template. It is actively usable and
installed. Day-to-day state lives in git history, `CHANGELOG.md`, and `docs/`.

## Hosting

- **GitLab (origin):** `gitlab.com/gthullen-group/libreoffice-ui-manager` — migrated from GitHub.
- GitHub kept as a secondary `github` remote (fallback; not the canonical home).
- CI: `.gitlab-ci.yml` (compile → unittest → build `.oxt`). **Green.**

## Recent work (2026-06)

- Save dialog defaults teacher templates to **`Documents/LOUIM templates`** (persists across reinstalls).
- Migrated GitHub → GitLab; repointed all project URLs; added `.gitlab-ci.yml`.
- Gotcha: **keep `.gitlab-ci.yml` pure ASCII** (an em-dash in a comment = "yaml invalid" on GitLab).

## Companion project

The **tabbed (Notebookbar) UI** is handled by a **separate** extension,
**LONBM** (`gitlab.com/gthullen-group/libreoffice-notebookbar-manager`) — that's
where the active development (and an open blocker) currently is; see its
`HANDOFF.md`. LONBM owns the `ToolbarMode` (active-variant) setting; LOUIM stays
out of it.

## Build / test

```sh
python -m pytest -q          # (or: python -m unittest discover -s tests)
python tools/build.py        # -> dist/louim.oxt
```

## Install / where things live

- Installer: `dist/louim.oxt` → **Tools ▸ Extension Manager ▸ Add…**.
- User templates: **`Documents/LOUIM templates`** (persist across reinstall).
- Safety: never run live tests against your working LibreOffice — use a throwaway
  isolated profile (see LONBM `HANDOFF.md` for the rig).
