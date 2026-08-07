# Contributing to LOUIM

Thanks for helping make LibreOffice friendlier for learners!

## Getting started

```sh
python -m pytest -q          # offline unit tests (no LibreOffice needed)
python tools/build.py        # build dist/louim.oxt
```

The engine logic (menu pruning, template loading/saving, context editing) is
pure Python and must stay testable without LibreOffice. Code that talks to
LibreOffice lives in `src/louim/adapters/` and imports `uno` lazily.

## Ground rules

- **Never test against a LibreOffice instance someone is actually using.**
  Use a throwaway headless instance with its own `-env:UserInstallation`
  profile — see the safety rules in [CLAUDE.md](CLAUDE.md).
- Templates store UNO command IDs / resource URLs, never localized labels
  (see [docs/template-format.md](docs/template-format.md)).
- Every hide must have a clean restore path back to the user's original
  interface.
- New user-facing strings go into `src/louim/i18n.py` in all four languages
  (en/fr/de/it); new menu items in `extension/Addons.xcu` need `xml:lang`
  titles for the same four.
- Add or extend the offline tests in `tests/` for any logic change.

## Submitting changes

Open a pull request against `main`. CI byte-compiles the sources, runs the
test suite, and builds the `.oxt`; all three must pass.
