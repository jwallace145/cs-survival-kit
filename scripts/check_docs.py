"""Docs-completeness check for the study modules.

Enforces two rules over ``data_structures/`` and ``algorithms/``:

1. Every public class has a ``Complexity:`` section in its docstring.
2. An implemented function or method (its body is no longer just
   ``raise NotImplementedError``) must not have ``TODO`` in its own docstring,
   its class docstring, or its module docstring.

Stubs may keep their placeholders; nothing ships implemented and undocumented.

Usage:
    python scripts/check_docs.py [PATH ...]
"""

import ast
import sys
from collections.abc import Iterator, Sequence
from pathlib import Path

DEFAULT_PATHS = (
    "src/cs_survival_kit/data_structures",
    "src/cs_survival_kit/algorithms",
)
PLACEHOLDER = "TODO"
COMPLEXITY_HEADER = "Complexity:"

type FunctionNode = ast.FunctionDef | ast.AsyncFunctionDef


def _has_placeholder(node: ast.Module | ast.ClassDef | FunctionNode) -> bool:
    return PLACEHOLDER in (ast.get_docstring(node) or "")


def _is_stub(function: FunctionNode) -> bool:
    """Return whether the body is only ``raise NotImplementedError``."""
    body = function.body
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        body = body[1:]
    if len(body) != 1 or not isinstance(body[0], ast.Raise):
        return False
    raised = body[0].exc
    if isinstance(raised, ast.Call):
        raised = raised.func
    return isinstance(raised, ast.Name) and raised.id == "NotImplementedError"


def _walk(
    body: Sequence[ast.stmt], classes: tuple[ast.ClassDef, ...] = ()
) -> Iterator[tuple[ast.ClassDef | FunctionNode, tuple[ast.ClassDef, ...]]]:
    """Yield each class, function and method with its enclosing classes.

    Functions nested inside other functions are implementation details and
    are not visited.
    """
    for node in body:
        if isinstance(node, ast.ClassDef):
            yield node, classes
            yield from _walk(node.body, (*classes, node))
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            yield node, classes


def check_source(source: str, filename: str) -> list[str]:
    """Check one module's source and return its violations.

    Args:
        source: The module's source code.
        filename: Name used to prefix each violation.

    Returns:
        One ``file:line: message`` string per violation, in source order.
    """
    module = ast.parse(source, filename=filename)
    errors: list[str] = []

    def report(node: ast.ClassDef | FunctionNode, message: str) -> None:
        errors.append(f"{filename}:{node.lineno}: {message}")

    for node, classes in _walk(module.body):
        name = ".".join([*(cls.name for cls in classes), node.name])
        if isinstance(node, ast.ClassDef):
            public = not any(part.startswith("_") for part in name.split("."))
            if public and COMPLEXITY_HEADER not in (ast.get_docstring(node) or ""):
                report(node, f"class {name} has no '{COMPLEXITY_HEADER}' section")
            continue
        if _is_stub(node):
            continue
        scopes = [("its", node), ("its module", module)]
        if classes:
            scopes.insert(1, ("its class", classes[-1]))
        for owner, scope in scopes:
            if _has_placeholder(scope):
                report(
                    node,
                    f"{name} is implemented but {owner} docstring "
                    f"contains {PLACEHOLDER}",
                )
    return errors


def main(argv: Sequence[str] | None = None) -> int:
    """Run the check over the given paths (default: the study modules).

    Returns:
        0 if clean, 1 if there are violations, 2 if a path does not exist.
    """
    args = sys.argv[1:] if argv is None else argv
    roots = [Path(arg) for arg in (args or DEFAULT_PATHS)]

    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
        elif root.is_dir():
            files.extend(sorted(root.rglob("*.py")))
        else:
            print(f"check_docs: path does not exist: {root}", file=sys.stderr)
            return 2

    errors: list[str] = []
    for file in files:
        errors.extend(check_source(file.read_text(encoding="utf-8"), str(file)))

    for error in errors:
        print(error)
    if errors:
        print(f"\ncheck_docs: {len(errors)} problem(s) in {len(files)} file(s)")
        return 1
    print(f"check_docs: {len(files)} file(s) OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
