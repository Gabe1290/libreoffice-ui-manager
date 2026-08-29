# Changelog

All notable changes to LibreOffice UI Manager (LOUIM) are documented here.
This project adheres to [Semantic Versioning](https://semver.org/).

## [4.2.2] — 2026-08-16

### Fixed

- Applying a template that hides **addon menus** crashed with
  `NameError: name 'uno' is not defined`. `addons.py`'s `state_path` calls
  `uno.fileUrlToSystemPath` but lost its local `import uno` when the module moved
  to lazy imports (in 4.2.0); the other adapters kept theirs. Added the missing
  import, plus a static guard test (`test_uno_imports`) that fails offline if any
  function uses `uno`/`unohelper` without an import in scope.

## [4.2.1] — 2026-08-16

### Fixed

- Release assets are now published with the **stable filename `louim.oxt`**
  (previously `louim-<version>.oxt`). LibreOffice derives the extension's package
  name from the `.oxt` filename, and the menu commands reference `louim.oxt`, so
  installing a versioned-name file broke *Apply Template* / *Restore* with
  `KeyError: 'louim.oxt'`. Install `louim.oxt` and do not rename it.

## [4.2.0] - 2026-08-03

Reconciles the audit-fix work released on the GitHub mirror (tagged 4.1.0 there)
into the main history, and adds cross-application restore verification tooling.

### Fixed

- The "wrong application" message now names the *template's* application
  ("Open a Calc document...") instead of the one you are already in.
- The restore confirmation names the *active application* ("Restored the full
  Calc interface.") in all four languages, instead of always saying Writer.
- Restoring an addon menu or sidebar deck hidden in *two applications* no longer
  disturbs the other application's hide: state files now record both the
  pre-hide value and what LOUIM wrote. Old state files are still understood.
- **Save Current Layout** no longer exports contextual toolbars
  (`tableobjectbar`, `frameobjectbar`, `graphicobjectbar`) as visible.
- Templates from a newer LOUIM (`version` above 1) are refused with a clear
  message; a malformed `profile` section is reported as invalid.
- `tools/verify-toolbars.py` works again and takes `--module`.

### Added

- `tools/verify-restore.py` - live cross-application restore/export checker
  (throwaway instances only), plus `tests/test_addon_context.py` offline
  coverage.

### Changed

- The project is now formally licensed under the **Mozilla Public License 2.0**.

### Removed

- `tools/create-project-md.sh`, a stale scaffold that overwrote PROJECT.md.

## [4.1.1] — 2026-08-03

### Fixed

- README install note said the menu appears "in Writer"; it appears in every
  supported app (Writer, Calc, Impress, Draw). Also point the download at the
  versioned release asset (`louim-<version>.oxt`).

### Infrastructure

- CI now auto-publishes a GitLab Release with the built `.oxt` attached on every
  version tag.

## [4.1.0] — 2026-08-03

### Changed

- **Apply Template…** now filters templates **by folder** rather than by file
  name: starter templates are bundled in per-application subfolders
  (`templates/<app>/`) and the picker opens in the active app's subfolder, so
  Writer shows only Writer templates (go up one folder to see all). Uses the
  native FilePicker, which avoids a Skia list-paint glitch on locked-down Linux
  where filenames failed to render in the office picker.
- **Save Current Layout…** now defaults to **`Documents/LOUIM templates`**
  instead of the per-user extension cache (which is wiped on every
  reinstall/update, silently losing teacher-made templates).

### Infrastructure

- Project moved from GitHub to **GitLab** (`gthullen-group/libreoffice-ui-manager`):
  CI pipeline added, project URLs repointed, cross-machine `HANDOFF.md` added.

## [4.0.2] — 2026-06-20

### Changed

- **Apply Template…** now defaults its file filter to the active application
  (`<app>-*.louim`), so Writer shows only Writer templates, Calc only Calc, etc.
  — with an "All LOUIM templates" entry in the filter dropdown as the escape
  hatch.
- **Save Current Layout…** defaults the file name to `<app>-my-template.louim`,
  so saved templates follow the per-application naming convention and appear
  under that app's filter.

## [4.0.1] — 2026-06-20

### Changed

- The **LibreOffice UI Manager** menu is now placed as the **rightmost top-level
  menu, after Help**, with a separator before it (via `OfficeMenuBarMerging`),
  so it stands apart from the built-in menus instead of being mixed in.

## [4.0.0] — 2026-06-20

Adds **LibreOffice Draw** — LOUIM now supports all four core apps (Writer, Calc,
Impress, Draw).

### Added

- **Draw support** — the full Apply Engine works in Draw. The **LibreOffice UI
  Manager** menu appears in Draw, and Apply / Restore / Save Current Layout act
  on the active application.
- Three bundled Draw starter templates: *Getting Started (Draw)*,
  *Basic Drawing*, *Complete Draw*.
- Templates may target `"draw"`.

### Notes

- Draw and Impress are complementary halves of the `DrawImpress` sidebar context
  group: hiding a deck from Draw keeps it in Impress, and vice versa.
- Verified live on a throwaway, isolated Draw instance; 77 offline unit tests
  pass.

## [3.0.0] — 2026-06-20

Adds **LibreOffice Impress** support alongside Writer and Calc.

### Added

- **Impress support** — the full Apply Engine works in Impress. The
  **LibreOffice UI Manager** menu appears in Impress, and Apply / Restore / Save
  Current Layout act on the active application.
- Three bundled Impress starter templates: *Getting Started (Impress)*,
  *Basic Presentation*, *Complete Impress*.
- Templates may now target `"impress"`.

### Changed

- Sidebar context **groups** are handled: Impress and Draw share the
  `DrawImpress` deck context, so hiding a deck from Impress rewrites that group
  to `Draw` rather than dropping it — Draw's sidebar is left intact
  (`Module.deck_group_subs`).

### Notes

- Verified live on a throwaway, isolated Impress instance (including the
  DrawImpress group behavior); 76 offline unit tests pass.

## [2.0.0] — 2026-06-20

Adds **LibreOffice Calc** support alongside Writer.

### Added

- **Calc support** — the full Apply Engine (menus, menu items, toolbars, toolbar
  buttons, sidebar decks, extension menus, and export) now works in Calc. The
  **LibreOffice UI Manager** menu appears in Calc, and Apply / Restore / Save
  Current Layout act on whichever application you are in.
- Three bundled Calc starter templates: *Getting Started (Calc)*,
  *Basic Spreadsheet*, *Complete Calc*.
- A template's `application` field selects the target app (`writer` or `calc`);
  applying a template whose application does not match the active document is
  refused with a clear message.

### Changed

- The engine is now **module-parameterized** (`adapters/modules.py`): one code
  path drives every application, so Impress and Draw can follow the same pattern.
- LOUIM state files are now per-application (e.g. `louim-toolbar-state-writer.json`,
  `louim-toolbar-state-calc.json`), so Writer and Calc profiles never collide.
- Dev tools (`discover-menus.py`, `apply-template.py`, `export-template.py`) take
  a `--module writer|calc` option.

### Notes

- Verified live on throwaway, isolated Writer and Calc instances (never a user's
  working profile); 71 offline unit tests pass.

## [1.0.0] — 2026-06-20

First stable release. A complete, verified Apply Engine for **LibreOffice
Writer**, driven entirely from the **LibreOffice UI Manager** menu.

### Added

- **Apply Engine** — apply a `.louim` template to simplify the Writer interface,
  and restore the full interface, across every UI surface:
  - **Menus** — hide/show top-level menus.
  - **Menu items** — hide individual entries at any depth, including nested
    submenu items.
  - **Toolbars** — hide/show whole toolbars; show normally-off toolbars (e.g.
    Drawing).
  - **Toolbar buttons** — hide individual icons; `hide_toolbar_buttons_with_menus`
    drops the buttons for features whose menus you hid.
  - **Sidebar decks** — hide/show decks (Properties, Gallery, Navigator, …).
  - **Extension menus** — hide menus contributed by other add-ons.
  - Apply is **non-cumulative and restorable** — every change has a clean path
    back to the user's original interface.
- **Template authoring**
  - **Save Current Layout as Template…** snapshots the current interface
    item by item — including menu items and toolbar buttons removed by hand via
    Tools ▸ Customize — into an editable `.louim` (JSON) file.
  - Three bundled starter templates: *Getting Started*, *Basic Editing*,
    *Complete Writer*. The file picker opens in the bundled templates folder.
- **Localization** — the extension UI (menus, dialogs, messages) is available in
  **English, French, German, and Italian**, following the LibreOffice locale.
- **Developer tooling** — `tools/discover-menus.py` (with `--tree`),
  `apply-template.py`, and `export-template.py` for inspecting and scripting
  against a LibreOffice UNO socket.

### Notes

- Templates are language-independent: they store UNO command IDs / resource URLs,
  never localized labels, so a template made on one machine works on any locale.
- Tested offline with `pytest` (64 tests) and verified live on isolated,
  throwaway LibreOffice instances — never against a user's working profile.

[4.2.2]: https://gitlab.com/gthullen-group/libreoffice-ui-manager/-/tags/v4.2.2
[4.2.1]: https://gitlab.com/gthullen-group/libreoffice-ui-manager/-/tags/v4.2.1
[4.2.0]: https://gitlab.com/gthullen-group/libreoffice-ui-manager/-/tags/v4.2.0
[4.1.1]: https://gitlab.com/gthullen-group/libreoffice-ui-manager/-/tags/v4.1.1
[4.1.0]: https://gitlab.com/gthullen-group/libreoffice-ui-manager/-/tags/v4.1.0
[1.0.0]: https://gitlab.com/gthullen-group/libreoffice-ui-manager/-/tags/v1.0.0
