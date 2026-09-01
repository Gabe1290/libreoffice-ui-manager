# Coding Standards

These conventions describe what `src/louim/` actually does. They aren't an
aspirational style guide. If you find code that doesn't match one of these,
that's probably a bug worth fixing rather than a license to ignore the rule.

## Lazy `uno` imports

Adapter modules don't import `uno` or `unohelper` at module level. Each
function that actually needs a UNO struct or invocation imports it locally:

```python
def _make_nodepath_arg(node):
    import uno
    arg = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
    ...
```

This keeps the pure logic in the same file, parsing, list and string editing,
tree pruning, importable and unit-testable without a LibreOffice installation
present. `tests/test_uno_imports.py` enforces this statically. It walks every
function in `src/` and fails if `uno` or `unohelper` is referenced without an
import reachable in that function's scope, whether module-level or local.

This test exists because of a real bug. In v4.2.2, `addons.state_path` used
`uno.fileUrlToSystemPath` after a lazy-import refactor had dropped the
top-level import elsewhere in the file. The offline test suite passed
anyway, since nothing exercised that code path without a live instance, and
the code raised `NameError` the moment it actually ran.

## Exception handling: broad only at the glue boundary

`except Exception` shows up in two places, deliberately. One is individual
UNO property or config reads inside adapters, where a missing property or an
unknown resource should skip that one item rather than aborting a whole
discovery or apply pass over many elements. The other is `extension.py`, the
outermost layer, where an uncaught exception would otherwise surface as a
cryptic LibreOffice error dialog instead of LOUIM's own message.

Everywhere else, `template/loader.py`, `template/saver.py`, and the pure
helper functions inside adapters, exceptions propagate. Tests assert on them
directly, for example `TemplateError` from `load_template`. Swallowing
exceptions there would just hide real bugs behind silent no-ops.

## Module-level docstrings explain the reasoning, not the mechanics

Every adapter module opens with a comment block that gives the reasoning a
reader needs before the code makes sense: which config node is being edited
and why, what's shared versus per-application, why a particular UNO idiom is
required. Look at the top of `sidebar.py` or `addons.py` for the pattern.
Function docstrings follow the same rule at a smaller scale. They explain
non-obvious behavior, like why a return value composes instead of
overwriting, or why an operation has to be non-cumulative, rather than
paraphrasing the function signature. A function whose docstring would only
restate its name and arguments probably doesn't need one.

## Non-cumulative apply, always

Every `apply_*` function resets to a known baseline before applying the
current profile. For menus, toolbars, and toolbar items that baseline is the
factory default; for sidebar and addons it's the pre-LOUIM state (see
ui-element-model.md for which applies where). Applying template A then
template B always yields exactly B. It never leaves A's leftovers merged
into B. This is a hard invariant. A new adapter that stacks changes instead
of resetting first is a bug, however it gets tested.

## State files: one per surface, per module

Every adapter's `restore_*` function reverts using a private JSON state file
in the user profile, `louim-<surface>-state-<app>.json`, rather than
inferring the undo from the current template. That's what makes Restore work
regardless of which template, if any, was last applied, and it's what lets
sidebar and addons compose correctly when two different `Module`s have both
touched the same shared config value. See `sidebar._restore_context_list` and
`addons._restore_context` for the pattern: an exact undo when nothing else
changed the value since, and a compositional re-add otherwise.

## Pure logic gets unit-tested with fake containers

Recursive tree-walking logic, like `menubar._prune_hidden`,
`_collect_command_set`, and `_export_walk`, gets tested against small
hand-built fake objects that mimic the relevant slice of the UNO container
interface: `getCount`, `getByIndex`, `removeByIndex`. A live LibreOffice
instance is never involved. `tests/test_menubar_prune.py` shows the pattern.
This is why the whole test suite runs in well under a second with no
LibreOffice installed anywhere near it.

## Identifiers carry the logic; labels are just for display

Every comparison, every dict key, every template field uses a UNO command ID,
a toolbar resource URL, a deck Id, or an addon node name. Labels exist purely
for the dev tools and the Configure Menus dialog, to show a human something
readable. See [ADR 0001](adr/0001-use-uno-command-ids.md).

## `module=WRITER` as the default

Every adapter function signature takes `module`, defaulting to `WRITER`. This
isn't because Writer is architecturally special. It's because Writer was the
first application supported, and existing call sites, including the dev
tools, predate multi-app support. New code should still accept `module`
explicitly rather than assuming Writer. The `WRITER` default exists for
backward compatibility with pre-v2.0 call sites, not as a template to copy.
