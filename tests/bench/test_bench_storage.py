import json
from pathlib import Path

import pytest

from cs_survival_kit.bench import storage


def entry(name: str, marker: str = "") -> dict[str, object]:
    return {"name": name, "run_at": marker, "cases": []}


def test_merge_creates_the_file(tmp_path: Path):
    path = tmp_path / "nested" / "benchmarks.json"
    storage.merge(path, [entry("b"), entry("a")])

    data = json.loads(path.read_text())
    assert data["schema_version"] == storage.SCHEMA_VERSION
    assert [b["name"] for b in data["benchmarks"]] == ["a", "b"]
    assert path.read_text().endswith("\n")


def test_merge_replaces_by_name_and_keeps_other_entries(tmp_path: Path):
    path = tmp_path / "benchmarks.json"
    storage.merge(path, [entry("a", "old"), entry("b", "old")])
    storage.merge(path, [entry("b", "new"), entry("c", "new")])

    benchmarks = {b["name"]: b["run_at"] for b in storage.load(path)["benchmarks"]}
    assert benchmarks == {"a": "old", "b": "new", "c": "new"}


def test_load_of_a_missing_file_is_an_empty_document(tmp_path: Path):
    assert storage.load(tmp_path / "missing.json") == {
        "schema_version": storage.SCHEMA_VERSION,
        "benchmarks": [],
    }


def test_load_rejects_an_unknown_schema(tmp_path: Path):
    path = tmp_path / "benchmarks.json"
    path.write_text('{"schema_version": 999, "benchmarks": []}')

    with pytest.raises(ValueError, match="schema_version"):
        storage.load(path)


def test_the_shipped_results_file_is_valid():
    shipped = Path(storage.__file__).parents[1] / "_data" / "benchmarks.json"
    assert storage.load(shipped)["schema_version"] == storage.SCHEMA_VERSION
