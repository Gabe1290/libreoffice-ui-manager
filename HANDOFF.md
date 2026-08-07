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

- **GitLab (origin):** `gitlab.com/gthullen-group/libreoffice-ui-manager` — the
  **source of truth**. Development, issues, and automated releases live here.
- **GitHub (`github` remote):** `github.com/Gabe1290/libreoffice-ui-manager` —
  a **plain public mirror**. No CI there; do not develop on it directly.
- CI: `.gitlab-ci.yml` (compile → unittest → build `.oxt`; on tags, publish the
  Release with the `.oxt` attached). **Green.**

### Mirroring (do this every release)

Push `main` **and** tags to **both** remotes:

```sh
git push origin main && git push github main
git push origin vX.Y.Z && git push github vX.Y.Z
```

Only GitLab CI reacts to the tag (builds + publishes the Release); GitHub just
stores the mirrored commits/tags. **Never commit directly on GitHub** — it
caused a real divergence once: work pushed straight to the GitHub mirror never
reached GitLab, so the two `4.1.0`s differed and had to be reconciled by merge
in **v4.2.0** (2026-08). Keep them in lockstep to avoid a repeat.

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

## Releasing

Fully automated by `.gitlab-ci.yml` (build -> release stages). To cut a release:

1. Bump `<version>` in `extension/description.xml` and add a `## [X.Y.Z]` section
   to `CHANGELOG.md` (with a matching `[X.Y.Z]: .../tags/vX.Y.Z` link at the
   bottom).
2. Commit, push, then tag and push the tag: `git tag -a vX.Y.Z -m "..." &&
   git push origin vX.Y.Z`.

The tag pipeline then builds the `.oxt`, uploads it to the generic Package
Registry, extracts that version's CHANGELOG section as the notes, and creates
the GitLab Release with the `.oxt` attached — no manual UI step. Proven
end-to-end on v4.1.1 (2026-08-03). One release per tag: don't also create the
release by hand (release-cli errors if it already exists).

## Install / where things live

- Installer: `dist/louim.oxt` → **Tools ▸ Extension Manager ▸ Add…**.
- User templates: **`Documents/LOUIM templates`** (persist across reinstall).
- Safety: never run live tests against your working LibreOffice — use a throwaway
  isolated profile (see LONBM `HANDOFF.md` for the rig).
