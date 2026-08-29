"""Guard: every use of `uno`/`unohelper` must have an import in scope.

The adapters import `uno` lazily (inside the functions that touch LibreOffice)
so the pure logic stays offline-testable. That makes it easy to write `uno.`
in a function and forget the local `import uno` -- which passes every offline
test but raises `NameError: name 'uno' is not defined` live, the moment that
code path runs in LibreOffice. This static check catches it offline.

It would have caught the addons.state_path regression fixed in 4.2.2 (the
top-level `import uno` was dropped when addons.py moved to lazy imports, but one
function still used `uno.fileUrlToSystemPath`).
"""

import ast
import pathlib
import unittest

SRC = pathlib.Path(__file__).resolve().parent.parent / "src"
WATCH = {"uno", "unohelper"}


def _imported_names(node):
    names = set()
    for n in ast.walk(node):
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            for alias in n.names:
                names.add(alias.asname or alias.name.split(".")[0])
    return names


def _module_level_imports(tree):
    names = set()
    for n in tree.body:
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            for alias in n.names:
                names.add(alias.asname or alias.name.split(".")[0])
    return names


class UnoImportScopeTest(unittest.TestCase):
    def test_every_uno_use_has_an_import_in_scope(self):
        problems = []
        for path in SRC.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            module_imports = _module_level_imports(tree)
            for fn in [n for n in ast.walk(tree)
                       if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
                used = {n.id for n in ast.walk(fn)
                        if isinstance(n, ast.Name)
                        and isinstance(n.ctx, ast.Load) and n.id in WATCH}
                available = module_imports | _imported_names(fn)
                missing = used - available
                if missing:
                    problems.append("%s:%d %s() uses %s with no import in scope"
                                    % (path.name, fn.lineno, fn.name,
                                       sorted(missing)))
        self.assertEqual(problems, [],
                         "uno/unohelper used without an import in scope:\n"
                         + "\n".join(problems))


if __name__ == "__main__":
    unittest.main()
