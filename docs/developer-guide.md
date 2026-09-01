# Developer Guide

A practical guide to working on LOUIM's code. For the reasoning behind the
design, read [architecture.md](architecture.md). For style conventions, read
[coding-standards.md](coding-standards.md). And before running anything
against a real LibreOffice instance, read the safety rules in
[CLAUDE.md](../CLAUDE.md).

## Setup

```sh
git clone <repo>
cd libreoffice-ui-manager
pip install pytest
```

There's no other dependency. The codebase only needs the Python standard
library plus `uno`/`unohelper`, which come from the LibreOffice installation
itself and are only imported lazily where they're actually needed (see
coding-standards.md's section on lazy imports).

## Running the test suite

```sh
python -m pytest -q
```

All ~110 tests run offline, no LibreOffice required. They cover template
loading, saving, and validation; the pure list and string-editing helpers in
each adapter, like menu pruning, `ContextList` editing, `Context` editing, and
toolbar curation; i18n key and placeholder parity across the four languages;
and a static guard, `tests/test_uno_imports.py`, that catches a `uno` name
used without an import in scope in the same function. That last one is the
exact class of bug that only ever surfaces live, never in an offline test
otherwise.

## Building the extension

```sh
python tools/build.py
```

This produces `dist/louim.oxt` with a stable filename that never has a version
in it. PROJECT.md's "Resolved" section explains why that matters for the
script URL. The build excludes `__pycache__` and `*.pyc`; a stale compiled
file left in the bundled `python/` folder can break extension startup.

Install it through LibreOffice's Extension Manager, Tools ▸ Extension Manager
▸ Add, against `dist/louim.oxt`. Close LibreOffice first if you're
reinstalling. PROJECT.md describes the `KeyError` a half-committed reinstall
can cause otherwise.

## Live verification

Never test against your own running LibreOffice. See the safety rules in
CLAUDE.md. Use the dev tools in `tools/` against a throwaway headless instance
with its own `UserInstallation` profile:

```sh
soffice --headless --norestore \
  -env:UserInstallation=file:///tmp/louim-test-profile \
  --accept="socket,host=localhost,port=2002;urp;"
```

`tools/discover-menus.py [--tree]` lists menus, toolbars, and addon menus with
their UNO IDs; `--tree` shows the full nested menu tree.
`tools/apply-template.py <file.louim>` applies a profile, or use `--restore`
to undo it. `tools/export-template.py <out.louim>` snapshots the current
interface.

## Adding a new UI surface

Say you're adding a sixth kind of hideable element, following the pattern in
[ui-element-model.md](ui-element-model.md) and
[ADR 0003](adr/0003-ui-element-model.md).

Start with a new module under `src/louim/adapters/writer/` — the folder name
is historical, it isn't Writer-specific. Import `uno` lazily, inside function
bodies rather than at module level. Write a `discover_<surface>(ctx,
module=WRITER)` function that reads live config, and a
`<surface>_visibility(ctx, module=WRITER)` snapshot function for export. Then
write `apply_<surface>_profile(ctx, <surface>, module=WRITER, path=None)`,
non-cumulative like every existing adapter, writing a state file through a
`state_path(ctx, module)` helper, and `restore_<surface>s(ctx, module=WRITER,
path=None)` to revert from that state file.

From there, add the new section to `loader._validate_bool_map` calls in
`template/loader.py`, and to `saver.assemble_template` and
`build_current_template`. Wire it into `extension.py`'s apply, restore, and
export entry points. Document the section in
[template-format.md](template-format.md) and add a row to
ui-element-model.md. Unit-test the pure logic with fake containers, the
pattern in `tests/test_menubar_prune.py`, rather than against a live instance.

## Adding a new LibreOffice application

This should need no changes to the adapter logic itself, per
[ADR 0004](adr/0004-workspace-concept.md). Add a new `Module` instance to
`src/louim/adapters/modules.py` with the app-specific identifiers:
`doc_service`, `windowstate_node`, `deck_apps`/`other_deck_apps`,
`addon_contexts`/`other_addon_contexts`, and `deck_group_subs` if the app
shares a sidebar context group with another app, the way Impress and Draw
share `"DrawImpress"`. Add it to `MODULES` and to
`loader.SUPPORTED_APPLICATIONS`, then add starter templates under
`templates/<app>/`. `module_for_document` picks the new app up automatically
through `supportsService`; nothing in `extension.py` needs to change.

## Internationalization workflow

Any new user-facing string in `extension.py` or `ui/menu_picker.py` needs a
key added to all four language tables in `src/louim/i18n.py` (English, French,
German, Italian), with matching `%`-placeholders — a test enforces
placeholder-count parity, so a mismatch fails CI rather than shipping a
runtime `%` error. Fetch the string through the translator
(`office_language(ctx)` then `translator(lang)`); never hard-code English. A
new menu item, as opposed to a dialog string, also needs `xml:lang` titles
for all four languages in `extension/Addons.xcu`.

`.louim` templates themselves never need translation. They store UNO IDs, not
labels; see [ADR 0001](adr/0001-use-uno-command-ids.md).

## Releasing

See [HANDOFF.md](../HANDOFF.md). GitLab is the source of truth, with an
automated tag-driven release pipeline; this checkout's `origin` remote is
just a plain GitHub mirror with no CI. Bump `extension/description.xml`, add a
CHANGELOG.md section, commit, tag `vX.Y.Z`, and push the tag. GitLab CI builds
and publishes the `.oxt` as a Release automatically.
