# Working on LibreOffice UI Manager (LOUIM)

LOUIM is an educational LibreOffice **Writer** extension that progressively
simplifies the interface by hiding/showing menus, menu items, toolbars, and
extension menus from a `.louim` template. See [PROJECT.md](PROJECT.md) for
current status and [VISION.md](VISION.md) for the mission.

## ⚠️ Critical safety rules — testing against LibreOffice

These rules exist because ignoring them froze a contributor's LibreOffice and
made it impossible to type in Writer, Calc, and Impress (a single `soffice.bin`
process serves them all). Read before doing any live verification.

1. **Never run live UNO scripts against the user's primary / working LibreOffice
   instance.** Repeatedly writing config (`store()`, `commitChanges()`,
   `removeSettings`, `replaceSettings`) over a `--accept` socket — especially one
   that drops and is re-established — can hang the process and freeze every
   LibreOffice app. Do not attach to the instance the user is actually using.

2. **Prefer offline unit tests.** The menu prune logic and the template
   loader/saver are pure Python (no `uno` import) and run with `pytest` — no
   LibreOffice needed. Cover logic there first.

3. **If a live check is genuinely required, use a throwaway headless instance**
   with its **own** profile and socket, and tear it down afterward — never the
   user's profile:

   ```sh
   soffice --headless --norestore \
     -env:UserInstallation=file:///C:/temp/louim-test-profile \
     --accept="socket,host=localhost,port=2002;urp;"
   ```

   Connect, do the check, then close that instance. A separate
   `UserInstallation` means nothing you do can touch the user's real settings.

4. **Always back up the user profile before touching live config**, even
   indirectly. Profile path on Windows:
   `%APPDATA%\LibreOffice\4\user`.

5. **LOUIM must only ever change UI configuration** — menus, toolbar visibility,
   and extension-menu context. It must **never** touch rendering/graphics
   settings (Skia, OpenGL, hardware acceleration) or other unrelated options.
   Note for triage: if Writer shows a **blank/invisible document but still
   registers typing** (asks to save), that is a **Skia rendering** problem in
   LibreOffice itself, *not* LOUIM — fix via Tools ▸ Options ▸ LibreOffice ▸
   View ▸ uncheck "Use Skia for all rendering" (or set `UseSkia` to `false` in
   `registrymodifications.xcu` while LibreOffice is closed).

## Recovery, if a test breaks LibreOffice

1. Close all LibreOffice processes (`soffice`, `soffice.bin`).
2. Back up `%APPDATA%\LibreOffice\4\user`.
3. LOUIM's footprint to clear: the custom Writer UI config under
   `config/soffice.cfg/modules/swriter/`, toolbar `Visible` flags in
   `registrymodifications.xcu` (`WriterWindowState`), and LOUIM's own state files
   `louim-*.json` in the profile root.
4. Relaunch normally. If still broken, `soffice --safe-mode` offers a factory
   reset, or restore the backup.

## How the engine is structured

The only code that talks to LibreOffice lives in `src/louim/adapters/writer/`:

- `menubar.py` — top-level menus **and** nested menu items. Apply is
  non-cumulative: it resets to the factory menu bar, then recursively removes
  every command marked `false` at any depth.
- `toolbars.py` — whole-toolbar visibility via the `WriterWindowState` config.
  Non-cumulative; `true` shows, `false` hides; an empty section resets to the
  user's defaults. Do not list *contextual* toolbars (e.g. `tableobjectbar`) as
  `true` — it pins them open.
- `addons.py` — menus contributed by other extensions, keyed by config node.

`src/louim/template/` is pure Python (no `uno`): `loader.py` validates `.louim`
files, `saver.py` snapshots/serializes them. `extension.py` is the LibreOffice
entry-point glue (file pickers, message boxes) exposed via `g_exportedScripts`.

Templates are plain JSON. The `menus`/`addons`/`toolbars` maps use UNO command
IDs / resource URLs / node names — **never localized labels** (templates must be
language-independent). See [docs/template-format.md](docs/template-format.md).

## Build & test

```sh
python -m pytest -q          # offline unit tests (no LibreOffice)
python tools/build.py        # build dist/louim.oxt
```

Dev tools in `tools/` connect to a LibreOffice UNO socket — point them at a
throwaway headless instance per the safety rules, not the user's session:

- `discover-menus.py [--tree]` — list menus (and the full menu-item tree),
  toolbars, and extension menus with their UNO IDs.
- `apply-template.py <file.louim>` / `--restore` — apply or restore a profile.
- `export-template.py <out.louim>` — snapshot the current interface.

## Conventions

- Match the existing style: module-level docstrings explaining *why*, broad
  `except Exception` only at the LibreOffice glue boundary (entry points), and a
  state file in the user profile for anything that must be restorable.
- Keep changes non-cumulative and restorable — every hide must have a clean
  path back to the user's original interface.
- Build excludes bytecode (`__pycache__`, `*.pyc`) from the `.oxt`; stale `.pyc`
  in the bundled `python/` folder can break extension startup.
