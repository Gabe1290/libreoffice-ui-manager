# Changelog

All notable changes to LibreOffice UI Manager (LOUIM) are documented here.
This project adheres to [Semantic Versioning](https://semver.org/).

## [4.1.0] — 2026-07-02

### Fixed

- The "wrong application" message now tells you to open a document of the
  **template's** application ("Open a Calc document…") instead of the one you
  are already in.
- The restore confirmation names the **active application** ("Restored the full
  Calc interface.") instead of always saying Writer, in all four languages.
- Restoring an addon menu or sidebar deck hidden in **two applications** no
  longer disturbs the other application's hide: the state files now record both
  the pre-hide value and what LOUIM wrote, so restore undoes exactly when it
  can and re-adds only its own application's entries when the other app still
  hides the item. Old state files are still understood.
- **Save Current Layout** no longer exports contextual toolbars
  (`tableobjectbar`, `frameobjectbar`, `graphicobjectbar`) as visible —
  applying such a template would have pinned them open outside their context.
  An explicit hide of one is still captured.
- Templates from a **newer LOUIM** (`version` above 1) are now refused with a
  clear message instead of being applied partially; a malformed `profile`
  section is reported as an invalid template instead of a raw error.
- `tools/verify-toolbars.py` works again (it referenced a symbol removed in the
  2.0.0 module refactor) and takes `--module` like the other dev tools.

### Changed

- The template picker filters by **folder**: it opens in the active
  application's bundled `templates/<app>/` subfolder (replacing the 4.0.2
  filename-pattern filter, which the native dialog ignored on some platforms).
  Navigating up one folder shows every application's templates.
- **Save Current Layout** defaults to `Documents/LOUIM templates/`, so
  teacher-made templates survive extension reinstalls and updates.
- The project is now formally licensed under the **Mozilla Public License 2.0**.

### Removed

- `tools/create-project-md.sh`, a stale scaffold that overwrote PROJECT.md with
  obsolete content.

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

[1.0.0]: https://github.com/Gabe1290/libreoffice-ui-manager/releases/tag/v1.0.0
