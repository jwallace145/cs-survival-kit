import textwrap
from pathlib import Path

import check_docs


def check(source: str) -> list[str]:
    return check_docs.check_source(textwrap.dedent(source), "mod.py")


STUB = '''
    """TODO: One-line summary."""


    def helper(n: int) -> int:
        """TODO: One-line summary.

        Args:
            n: TODO
        """
        raise NotImplementedError


    class Stack[T]:
        """TODO: One-line summary.

        Complexity:
            | Operation | Time | Space |
            | --------- | ---- | ----- |
            | `push`    | TODO | TODO  |
        """

        def __init__(self) -> None:
            raise NotImplementedError

        def push(self, item: T) -> None:
            """TODO: One-line summary."""
            raise NotImplementedError()
'''

DOCUMENTED = '''
    """A stack."""


    class Stack[T]:
        """A LIFO stack.

        Complexity:
            | Operation | Time | Space |
            | --------- | ---- | ----- |
            | `push`    | O(1) | O(1)  |
        """

        def __init__(self) -> None:
            self._items: list[T] = []

        def push(self, item: T) -> None:
            """Push an item."""
            self._items.append(item)
'''


def test_stub_with_todos_passes():
    assert check(STUB) == []


def test_implemented_and_documented_passes():
    assert check(DOCUMENTED) == []


def test_implemented_method_with_todo_docstring_fails():
    source = DOCUMENTED.replace('"""Push an item."""', '"""TODO: One-line summary."""')
    errors = check(source)
    assert len(errors) == 1
    assert "Stack.push" in errors[0]
    assert "its docstring" in errors[0]


def test_implemented_method_under_todo_class_docstring_fails():
    source = DOCUMENTED.replace("A LIFO stack.", "TODO: One-line summary.")
    errors = check(source)
    # __init__ and push are both implemented under the placeholder class docstring.
    assert len(errors) == 2
    assert all("class docstring" in error for error in errors)


def test_implemented_function_under_todo_module_docstring_fails():
    source = DOCUMENTED.replace('"""A stack."""', '"""TODO: One-line summary."""')
    errors = check(source)
    assert errors
    assert all("module docstring" in error for error in errors)


def test_implemented_module_level_function_with_todo_fails():
    errors = check('''
        """Helpers."""


        def double(n: int) -> int:
            """TODO: One-line summary."""
            return n * 2
    ''')
    assert len(errors) == 1
    assert "double" in errors[0]


def test_class_without_complexity_section_fails():
    source = STUB.replace("Complexity:", "Notes:")
    errors = check(source)
    assert len(errors) == 1
    assert "Stack" in errors[0]
    assert "Complexity:" in errors[0]


def test_class_without_docstring_fails_complexity_rule():
    errors = check('''
        """Helpers."""


        class Bare:
            pass
    ''')
    assert len(errors) == 1
    assert "Complexity:" in errors[0]


def test_private_class_is_exempt_from_complexity_rule():
    errors = check('''
        """Helpers."""


        class _Node:
            """A node."""
    ''')
    assert errors == []


def test_nested_helper_functions_are_not_checked():
    errors = check('''
        """Policies."""


        def geometric(factor: float):
            """Return a growth policy."""

            def policy(capacity: int) -> int:
                return int(capacity * factor) + 1

            return policy
    ''')
    assert errors == []


def test_errors_carry_file_and_line():
    errors = check(DOCUMENTED.replace('"""Push an item."""', '"""TODO"""'))
    assert errors[0].startswith("mod.py:")


def test_main_exit_codes(tmp_path: Path, capsys):
    good = tmp_path / "good"
    good.mkdir()
    (good / "stack.py").write_text(textwrap.dedent(DOCUMENTED))
    assert check_docs.main([str(good)]) == 0

    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "stack.py").write_text(
        textwrap.dedent(STUB.replace("Complexity:", "Notes:"))
    )
    assert check_docs.main([str(bad)]) == 1
    assert "Complexity:" in capsys.readouterr().out


def test_main_fails_on_missing_path(tmp_path: Path):
    assert check_docs.main([str(tmp_path / "nope")]) == 2
