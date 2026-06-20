# LibreOffice UI Manager — PROJECT

## Mission

LOUIM is an educational LibreOffice extension designed to progressively simplify the LibreOffice Writer interface.

It helps teachers reduce cognitive overload by showing only the tools needed for the current learning step.

LOUIM is not primarily a lockdown tool. It is a learning tool.

## Current Milestone

Milestone 0.3 — First working extension.

Goal:

- Installable `.oxt`
- Entry in LibreOffice Writer
- Simple "Hello LOUIM" dialog

No menu hiding yet.

## Current Problem

RESOLVED — the bundled Python entry point now resolves and executes.

Root causes that were fixed:

- The extension manifest did not register the Python scripts. Added a
  `framework-script` file-entry for the `python/` folder in
  `extension/META-INF/manifest.xml`.
- The menu script URL was malformed. The correct form for a bundled script is
  `vnd.sun.star.script:<oxt-folder>/python/louim/extension.py$hello?language=Python&location=user:uno_packages`
  (first path segment is the deployed `.oxt` folder name; `$` before the
  function name).
- The build now produces a stable filename `dist/louim.oxt` (no version), so the
  deployed folder name in the script URL stays constant across version bumps.
  The version still lives in `extension/description.xml`.

Operational gotcha discovered: a half-committed registration (e.g. installing
via the GUI and `unopkg add` while LibreOffice is running) leaves the user
extension repository inconsistent, and a later full startup *purges* the
package during synchronization — which presents as `KeyError: '<oxt>'` from
`pythonscript.py`. Fix: close LibreOffice, then `unopkg add dist/louim.oxt`
once, cleanly.

Verified headlessly via the script provider: the menu URI both resolves and
invokes successfully.

## Current Decision

The bundled extension works, so continue with proper `.oxt` packaging. The
standalone dev macro (`tools/dev-macro/louim_hello.py` +
`tools/install-dev-macro.sh`) remains as a quick way to test UNO snippets
outside the package.

## Next Session Tasks

1. GUI-verify toolbar hide/restore: run `tools/discover-menus.py` against a
   running Writer to get the real toolbar resource URLs, add a couple to a
   template's `toolbars` section (e.g. `private:resource/toolbar/tablebar`:
   false), Apply Template..., and confirm those toolbars disappear for newly
   opened Writer windows and come back with "Restore Full Menus".
2. Populate the bundled level-1/level-2 templates with sensible `toolbars`
   entries once the real resource URLs are confirmed (kept empty for now to
   avoid shipping unverified IDs).
3. Extend discovery/apply to submenu items (individual entries inside a menu)
   and the sidebar per the architecture.

## Done — Toolbar hide/restore (Apply Engine v2)

`src/louim/adapters/writer/toolbars.py` extends the engine beyond the menu bar
to whole toolbars, following the addons.py pattern (config node + user-profile
state file, restorable across restarts):

- `discover_toolbars(ctx)` — lists Writer toolbars as
  `{"resource": "private:resource/toolbar/standardbar", "label": "Standard"}`
  via the module UI config's `getUIElementsInfo(TOOLBAR)`.
- `apply_toolbar_profile(ctx, toolbars)` — for each resource URL marked `false`,
  sets `Visible=false` in `org.openoffice.Office.UI.WriterWindowState /
  UIElements/States`, creating the state element if Writer never persisted one.
  Saves the pre-LOUIM state (original `Visible`, or "did not exist") to
  `louim-toolbar-state.json`.
- `restore_toolbars(ctx)` — replays the saved state exactly, including removing
  an element LOUIM had to create.

Wired into `extension.py` (apply_template / restore_menus) and both dev tools
(`discover-menus.py`, `apply-template.py`). Template `toolbars` section is now
validated by the loader and documented in `docs/template-format.md`. Tests:
10 pass (added toolbar-section validation). Build packages the adapter into
`dist/louim.oxt`. **Not yet GUI-verified** — see task 1 (need real resource URLs
from a running Writer; the mechanism is untested against a live instance).

## Done — Apply Engine wired into the extension UI

The "LibreOffice UI Manager" menu now drives the engine directly (no socket /
dev tool needed):

- `apply_template` (`src/louim/extension.py`) — opens a file picker for a
  `.louim`, loads+validates it via the Template Manager, then calls
  `apply_menu_profile` + `apply_addon_profile`. Reports what was hidden.
- `restore_menus` — calls `restore_default_menus` + `restore_addon_menus`.
- Menu entries added to `extension/Addons.xcu`: "Apply Template...",
  "Restore Full Menus", a separator, and the existing "Hello LOUIM".
- `extension.py` adds `python/` to `sys.path` so the bundled `louim` package
  imports the same way it does for the dev tools / tests.

Built and packaged clean (`python tools/build.py` → `dist/louim.oxt` contains
the entry points and the three starter templates); loader tests still pass.
Not yet GUI-verified (no display in this environment) — see task 1.

The file picker now defaults to the deployed `templates/` folder, located via
the `PackageInformationProvider` (refactored into `_package_url`, shared with
`_ensure_package_path`). Best-effort: falls back to the picker's last location
if the folder can't be resolved.

## Engine Status (verified headlessly)

- **Discovery Engine v0** — `src/louim/adapters/writer/menubar.py`
  `discover_top_level_menus(ctx)` reads Writer's live top-level menus as UNO
  command IDs. Dev tool: `tools/discover-menus.py`.
- **Template Manager (load)** — `src/louim/template/loader.py`
  `load_template(path)` parses and validates `.louim` files. Unit-tested in CI.
- **Apply Engine v0** — same adapter: `apply_menu_profile(ctx, menus)` hides the
  top-level menus a template marks `false` (always derived from the factory
  default, so it is idempotent), and `restore_default_menus(ctx)` reverts to the
  built-in full menu bar. Dev tool: `tools/apply-template.py`.

  Verified: applying `writer-level-1.louim` reduces the Writer menu bar to
  exactly File/Edit/Format/Help, and restore returns all 11 menus, leaving the
  profile clean.

- **Apply Engine v1 (extension menus)** — `src/louim/adapters/writer/addons.py`
  handles menus contributed by *other* extensions (e.g. Dmaths), which are
  merged separately from the built-in menu bar and keyed by config node name in
  a template's `addons` section. `apply_addon_profile` hides them by removing
  Writer from each addon's `Context` (saving the original to a state file in the
  user profile); `restore_addon_menus` writes the originals back. Takes effect
  for newly opened Writer windows. Verified in the GUI: Dmaths hides and
  restores. LOUIM's own menu is always excluded.

  Note: addon-menu changes persist via config `commitChanges()`; a normally
  running LibreOffice flushes them. (Abruptly killing a headless instance right
  after a commit can lose the last write — relevant only to test harnesses.)

## Known fix

The extension's own menu did not render because its `Addons.xcu` entry had no
`Context`. Recent LibreOffice requires one for top-level addon menus. Fixed by
binding the LOUIM menu to the Writer document modules. Confirmed in the GUI: the
"LibreOffice UI Manager" menu shows and "Hello LOUIM" opens the dialog.

## Resume Prompt

Continue LOUIM from PROJECT.md
