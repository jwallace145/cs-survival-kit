import json
import textwrap
from pathlib import Path

import pytest

from cs_survival_kit.bench import cli, core

BENCH_MODULE = """
    from cs_survival_kit.bench import Benchmark


    def stub(n):
        raise NotImplementedError


    bench = Benchmark("{name}", sizes=[10, 20])
    bench.case("real", setup=lambda n: n, run=lambda n: sum(range(n)))
    bench.case("stub", setup=lambda n: n, run=stub)

    BENCHMARKS = [bench]
"""


@pytest.fixture(autouse=True)
def fast(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(core, "MIN_MEASUREMENT_NS", 1_000)


def write_bench(directory: Path, stem: str, name: str) -> Path:
    directory.mkdir(exist_ok=True)
    path = directory / f"{stem}.py"
    path.write_text(textwrap.dedent(BENCH_MODULE.format(name=name)))
    return path


def test_full_run_writes_results(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    bench_file = write_bench(tmp_path, "bench_demo", "demo")
    output = tmp_path / "out.json"

    assert cli.main([str(bench_file), "--output", str(output)]) == 0

    (benchmark,) = json.loads(output.read_text())["benchmarks"]
    assert benchmark["name"] == "demo"
    real, stub = benchmark["cases"]
    assert real["status"] == "ok" and real["sizes"] == [10, 20]
    assert stub["status"] == "not implemented"
    assert "demo" in capsys.readouterr().out


def test_smoke_writes_nothing(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    bench_file = write_bench(tmp_path, "bench_demo", "demo")
    output = tmp_path / "out.json"

    assert cli.main([str(bench_file), "--output", str(output), "--smoke"]) == 0

    assert not output.exists()
    out = capsys.readouterr().out
    assert "not implemented" in out
    assert "not written" in out


def test_rerunning_one_file_updates_only_its_entries(tmp_path: Path):
    first = write_bench(tmp_path, "bench_first", "first")
    second = write_bench(tmp_path, "bench_second", "second")
    output = tmp_path / "out.json"

    assert cli.main([str(tmp_path), "--output", str(output)]) == 0
    before = {b["name"]: b for b in json.loads(output.read_text())["benchmarks"]}
    assert set(before) == {"first", "second"}

    assert cli.main([str(second), "--output", str(output)]) == 0
    after = {b["name"]: b for b in json.loads(output.read_text())["benchmarks"]}
    assert after["first"] == before["first"]
    assert first.exists()


def test_directories_are_searched_for_bench_files_only(tmp_path: Path):
    write_bench(tmp_path, "bench_demo", "demo")
    (tmp_path / "helper.py").write_text("raise RuntimeError('must not be imported')")

    assert [p.name for p in cli.discover([tmp_path])] == ["bench_demo.py"]


def test_default_paths_are_relative_to_the_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    write_bench(tmp_path / "benchmarks", "bench_demo", "demo")
    monkeypatch.chdir(tmp_path)

    assert cli.main(["--smoke"]) == 0
    assert not (tmp_path / "src").exists()


def test_errors_exit_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    assert cli.main([str(tmp_path / "missing.py")]) == 2
    assert "does not exist" in capsys.readouterr().err

    assert cli.main([str(tmp_path)]) == 2
    assert "no benchmark files" in capsys.readouterr().err

    bad = tmp_path / "bench_bad.py"
    bad.write_text("BENCHMARKS = 'nope'")
    assert cli.main([str(bad), "--smoke"]) == 2
    assert "BENCHMARKS" in capsys.readouterr().err
