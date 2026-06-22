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

1. End-to-end GUI smoke test in a real Writer window (all surfaces verified via
   the engine/headless, but not yet eyeballed together): install `dist/louim.oxt`,
   Apply "Getting Started", confirm Drawing toolbar shows / Find+Insert gone;
   add a `sidebar` entry hiding `GalleryDeck` and confirm it leaves the sidebar;
   "Save Current Layout as Template..." round-trips; Restore returns everything.
2. Verify the fr/de/it UI in a non-English LibreOffice (string + format parity
   already unit-tested; this is the on-screen confirmation).
3. Decide whether the in-app export should also capture **nested menu items**
   (currently top-level menus only; full-tree capture would be large/verbose).
4. Add a localized `description.xml` / `description.txt` for the Extension
   Manager (currently English only) if desired.

## Done (verified on isolated instance) — Toolbar-button hiding (Apply Engine v5)

Templates can now thin the icons *inside* toolbars, not just hide whole toolbars,
so a simplified profile drops the buttons for features it removed.
`src/louim/adapters/writer/toolbaritems.py`:

- `toolbaritems` (template) — a command → bool map; buttons for commands marked
  `false` are removed from every toolbar that holds them.
- `hide_toolbar_buttons_with_menus` (template, bool) — when true, every command
  hidden in `menus` also loses its toolbar button (the requested "reduce menus →
  reduce icons" behaviour). `hidden_commands_for(template)` is the pure helper
  that unions the two sources.
- Reuses the menu bar's recursive `_prune_hidden`: each affected toolbar is reset
  to its factory definition and pruned, recorded in `louim-toolbaritem-state.json`
  so restore reverts exactly. Only toolbars that actually contain a hidden command
  are touched (cheap `getDefaultSettings` membership pre-check).

Wired into the extension apply/restore, the `apply-template.py` dev tool, the
loader, and `docs/template-format.md`. Pure logic unit-tested (54 tests pass).
**Verified** on a throwaway headless instance: hiding a Standard-toolbar command
dropped it (53 → 52 buttons) and restore brought it back (→ 53); the
auto-match-menus path was exercised.

## Done — Localization: English, French, German, Italian

LOUIM's own UI is now translated. The engine was already language-independent
(it keys on UNO command IDs / resource URLs, never localized labels), so only
LOUIM's own surfaces needed work:

- `src/louim/i18n.py` — string tables for en/fr/de/it, a pure `translator(lang)`
  (English fallback for missing key/language), `normalize_lang` ("fr-FR" → "fr",
  unsupported → "en"), and `office_language(ctx)` reading `ooLocale` from the
  Office L10N config (lazy `uno` import).
- `extension.py` — every dialog title, message-box body, and file-picker
  string now comes from the translator, chosen by the live Office language.
- `extension/Addons.xcu` — each menu item Title carries `xml:lang` values for
  en-US/fr/de/it (Apply Template, Save Current Layout, Restore Full Menus,
  Hello). The top menu name stays the "LibreOffice UI Manager" brand.
- Tests: 48 pass (10 new) — key/lang parity, **placeholder-count parity** across
  languages (so `%` formatting can't fail), fallback behaviour, locale
  normalization. Verified the fr/de/it strings render with correct accents and
  quotes.

Not localized (deliberate, low value): the Extension Manager `description.xml`
display name (a brand) and the `description.txt` blurb.

## Done — Discovery labels (verified) + leaner export

- **Menu labels** now resolve via the `UICommandDescription` service
  (`menubar.py` `_command_labels` / `_label_for`), so `discover-menus.py` shows
  real names even with no document frame open (the menu-bar config leaves
  `Label` empty). **Verified** on the isolated instance: 11/11 top-level menus
  and 553/553 menu items resolved real names.
- **Leaner export**: `curate_toolbars` (in `toolbars.py`) trims the exported
  `toolbars` map to the common Writer toolbars plus anything explicitly hidden,
  instead of all ~58 window-state toolbars, so saved templates stay readable.
  Pure function, unit-tested.
- Refactored `toolbars.py` to import `uno` lazily (like `menubar.py`/`sidebar.py`)
  so `curate_toolbars` is testable offline. Suite: 38 tests pass (5 new).

## Done (verified on isolated instance) — Sidebar deck hiding (Apply Engine v4)

Verified 2026-06-20 on a **throwaway headless LibreOffice** (its own
`UserInstallation` profile + port 2003, terminated via its own socket — the
user's session never touched, per the safety rules). Hiding `GalleryDeck`
removed the `WriterVariants` entry from its `ContextList`
(`shows_in_writer` → False) and restore returned the list byte-for-byte. Menu
**labels** were verified in the same run: 11/11 top-level menus and 553/553
menu items resolve real names via `UICommandDescription`.

The run also **caught a bug**: `setPropertyValue("ContextList", tuple(...))`
threw "inappropriate property value" — the config manager needs an explicitly
typed string sequence. Fixed `_set_context_list` to pass
`uno.Any("[]string", ...)` via `uno.invoke` (same idiom as the menu-bar
adapter). This is exactly the kind of defect headless verification is for.

Design details:

`src/louim/adapters/writer/sidebar.py` hides/shows whole sidebar decks
(Properties, Styles, Gallery, Navigator, …), mirroring addons.py: a deck appears
in Writer when its `ContextList` (under
`org.openoffice.Office.UI.Sidebar/Content/DeckList/<deckId>`) has a Writer entry;
LOUIM drops the Writer entries (saving the original to
`louim-sidebar-state.json`) to hide it, and writes them back to restore. A
template's new `sidebar` section maps deck Id → bool.

- `discover_sidebar_decks` / `sidebar_visibility` read the live decks; wired into
  the extension apply/restore, both dev tools, the exporter, the loader, and
  `docs/template-format.md`.
- The `ContextList` parse/edit logic (`shows_in_writer`, `strip_writer`, with an
  "any" → non-Writer-apps fallback) is **pure Python** (sidebar.py imports `uno`
  lazily), so it is unit-tested in CI: 33 tests pass (12 new).

Design was derived **offline** by reading the installed deck definitions in
`share/registry/main.xcd` (deck Ids + the `ContextList` format) — no live
LibreOffice was touched, per the safety rules. **Not yet GUI-verified**; apply
needs confirmation on a real/throwaway Writer (see task 2).

## Done — Submenu-item hiding (Apply Engine v3)

`apply_menu_profile` now hides commands at **any depth**, not just top-level
menus. A template's `menus` map can list an individual item
(`.uno:InsertPagebreak`) or a deep submenu entry and it is removed; a hidden
menu still removes everything inside it. The `menus` map shape is unchanged
(command → bool), so the loader and existing templates need no change.

Mechanism (validated live before coding, then end-to-end):

- Reset to the factory menu bar (`removeSettings`), then take a **writable
  clone** via `getSettings(MENUBAR, True)` — which yields the full default tree
  with writable nested `ItemDescriptorContainer`s only because we reset first
  (otherwise it returns just the customization layer).
- `_prune_hidden` walks the tree depth-first and `removeByIndex`-es every entry
  whose command is marked `False` (removing in descending index order so indices
  don't shift), recursing into survivors' submenus.
- `replaceSettings` + `store`. Non-cumulative, like the top-level behaviour it
  replaces — the old build-from-default-into-createSettings path is gone, and
  `menubar.py` no longer imports `uno` (so the prune logic is unit-tested in CI).

Discovery: new `discover_menu_items(ctx)` returns the full menu tree as a flat
list with `command`/`label`/`path`/`depth` (553 commands in Writer); surfaced via
`tools/discover-menus.py --tree` so teachers can find the UNO ID of any item.
Docs updated. Tests: 21 pass (6 new fake-container prune tests).

**Live-verified** against a running Writer: hiding `.uno:InsertPagebreak` drops
Insert 34→33 with the menu and the other 10 top-level menus intact; an empty
profile resets (pagebreak returns); hiding a top-level menu + a nested item
together works; restore returns the full 11 menus.

## Done — Template export + Drawing-in-level-1 (Apply Engine v2.1)

Three changes driven by classroom feedback:

- **Drawing toolbar shows in level-1.** Toolbar apply is now **non-cumulative**
  (rolls back prior LOUIM toolbar changes first, like the menu bar) with honest
  force semantics: `true` shows a toolbar (even one off by default, e.g.
  Drawing), `false` hides it, empty `toolbars` (writer-full) resets to the
  user's defaults. Replaces the earlier "true never forces" rule, which couldn't
  satisfy "show Drawing for beginners". Bundled templates only manage ordinary
  toggleable toolbars; listing a *contextual* bar (`tableobjectbar`) as `true`
  would pin it open — documented in `docs/template-format.md`.
- **Export / create-your-own templates.** New `src/louim/template/saver.py`
  (`assemble_template`, `save_template`, `build_current_template`) snapshots the
  live interface into a `.louim`. Visibility snapshots added to each adapter
  (`menu_visibility`, `toolbar_visibility`, `addon_visibility`). New extension
  entry point `export_template` + menu "Save Current Layout as Template..."
  (`extension/Addons.xcu`), plus `tools/export-template.py`. Templates are plain
  JSON, editable in any text editor (docs section added).
- Tests: 15 pass (added saver round-trip suite).

**Live-verified** against a running Writer (`tools/_verify_tmp.py`, throwaway):
menu apply hides 7 / keeps 4 and restore returns all 11; level-1 toolbars force
Drawing **on** (was off) and hide Find, and writer-full + restore is net-zero;
export snapshots 11 menus + 58 toolbars, saves, and reloads through the loader
cleanly. So the menu apply/restore path is now live-verified too (previously only
headless via the script provider).

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
`dist/louim.oxt`.

**Live-verified** against a running Writer (`tools/verify-toolbars.py`): hiding
`standardbar`/`colorbar` flips the persisted `Visible` flag and restore
reproduces the exact original state for both. Caveat: both test toolbars already
had a window-state entry, so only the *update* path is live-verified; the
*create-then-remove* path (no prior entry) is covered in code but not yet
exercised against a live instance.

Real Writer toolbar resource URLs confirmed via discovery (labels come back
empty when discovering without an open document frame — a display-only gap, IDs
are correct). Common ones for profiles: `standardbar` (Standard),
`textobjectbar` (Formatting), `findbar` (Find), `tableobjectbar` (Table),
`insertbar` (Insert), `drawbar` (Drawing).

### Starter templates now carry toolbar entries

All three bundled templates share the same six toolbar keys with level-appropriate
values: level-1 hides Find/Insert/Table/Drawing (keeps Standard + Formatting),
level-2 re-shows Insert/Table/Find (still hides Drawing), writer-full shows all.
Sharing the key set means moving to a lighter profile un-hides what a heavier one
hid, since toolbar applies are cumulative through the state file (unlike menus,
which rebuild from the factory default each apply).

Semantics fix this required: a `true` toolbar entry now only *un-hides* a toolbar
LOUIM previously hid — it no longer forces `Visible=true`, which would have pinned
a contextual bar (Table, Drawing) open outside its context. This matches addons.py.

Live end-to-end verified against a running Writer: applying level-1 then
writer-full returns every toolbar to its exact original state (net-zero), and a
toolbar that was hidden *before* LOUIM ran stays hidden through a `true` entry
(no force-show).

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
