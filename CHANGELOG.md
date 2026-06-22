# Changelog

All notable changes to LibreOffice UI Manager (LOUIM) are documented here.
This project adheres to [Semantic Versioning](https://semver.org/).

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
