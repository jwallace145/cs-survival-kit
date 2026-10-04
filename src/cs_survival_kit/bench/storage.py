"""Reading and writing the benchmark results file, `benchmarks.json`."""

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

SCHEMA_VERSION = 1


def load(path: Path) -> dict[str, Any]:
    """Load a results file.

    Args:
        path: The results file. It does not have to exist.

    Returns:
        The stored document, or an empty one if the file does not exist.

    Raises:
        ValueError: If the file was written with a different schema version.
    """
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "benchmarks": []}
    document = cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))
    if document.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(
            f"{path}: expected schema_version {SCHEMA_VERSION}, "
            f"found {document.get('schema_version')!r}"
        )
    return document


def merge(path: Path, results: Sequence[dict[str, Any]]) -> None:
    """Merge benchmark entries into a results file, by benchmark name.

    An entry replaces the stored entry with the same name. Every other stored
    entry is kept, so re-running one benchmark updates only that benchmark.

    Args:
        path: The results file. Created, along with its parent directories,
            if it does not exist.
        results: Benchmark entries, as produced by
            [`Results.to_dict`][cs_survival_kit.bench.core.Results.to_dict].

    Raises:
        ValueError: If the existing file has a different schema version.
    """
    document = load(path)
    stored = cast(list[dict[str, Any]], document["benchmarks"])
    by_name = {entry["name"]: entry for entry in stored}
    by_name.update({entry["name"]: entry for entry in results})
    document["benchmarks"] = [by_name[name] for name in sorted(by_name)]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
