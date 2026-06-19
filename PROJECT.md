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

1. Confirm the Tools-menu "Hello LOUIM" entry works in the GUI (install
   `dist/louim.oxt` via Extension Manager, restart, click the menu item).
2. Begin the Discovery Engine: enumerate available Writer `.uno:` commands.
3. Wire a first `.louim` template to actually show/hide a menu.

## Resume Prompt

Continue LOUIM from PROJECT.md
