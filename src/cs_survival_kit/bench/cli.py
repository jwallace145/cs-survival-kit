"""Command-line runner: `python -m cs_survival_kit.bench`."""

import argparse
import importlib.util
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import cast

from cs_survival_kit.bench import storage
from cs_survival_kit.bench.core import Benchmark

DEFAULT_PATH = Path("benchmarks")
DEFAULT_OUTPUT = Path("src/cs_survival_kit/_data/benchmarks.json")


class BenchmarkError(Exception):
    """A benchmark file could not be found or loaded."""


def discover(paths: Sequence[Path]) -> list[Path]:
    """Find the benchmark files that the given paths refer to.

    Args:
        paths: Files, which are used as given, and directories, which
            contribute their `bench_*.py` files.

    Returns:
        The benchmark files, in the order given and sorted within a directory.

    Raises:
        BenchmarkError: If a path does not exist, or nothing was found.
    """
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.glob("bench_*.py")))
        elif path.is_file():
            files.append(path)
        else:
            raise BenchmarkError(f"path does not exist: {path}")
    if not files:
        raise BenchmarkError(
            f"no benchmark files found in: {', '.join(map(str, paths))}"
        )
    return files


def load_benchmarks(path: Path) -> list[Benchmark]:
    """Import a benchmark file and return its `BENCHMARKS` list.

    Args:
        path: A Python file that defines `BENCHMARKS: list[Benchmark]`.

    Returns:
        The benchmarks the file defines.

    Raises:
        BenchmarkError: If the file cannot be imported, or does not define
            `BENCHMARKS` as a list of `Benchmark` objects.
    """
    spec = importlib.util.spec_from_file_location(
        f"_cs_survival_kit_bench_{path.stem}", path
    )
    if spec is None or spec.loader is None:
        raise BenchmarkError(f"{path}: cannot be imported")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    found: object = getattr(module, "BENCHMARKS", None)
    if not isinstance(found, list):
        raise BenchmarkError(
            f"{path}: must define BENCHMARKS as a list of Benchmark objects"
        )
    benchmarks: list[Benchmark] = []
    for item in cast(list[object], found):
        if not isinstance(item, Benchmark):
            raise BenchmarkError(
                f"{path}: BENCHMARKS must contain only Benchmark objects"
            )
        benchmarks.append(item)
    return benchmarks


def main(argv: Sequence[str] | None = None) -> int:
    """Run benchmark files and store their results.

    Args:
        argv: Command-line arguments. Defaults to `sys.argv[1:]`.

    Returns:
        The process exit code: 0 on success, 2 if a benchmark file could not
        be found or loaded.
    """
    parser = argparse.ArgumentParser(
        prog="python -m cs_survival_kit.bench",
        description="Run benchmark files and merge their results into a JSON file.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        metavar="PATH",
        help=f"benchmark files, or directories of them (default: {DEFAULT_PATH}/)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        metavar="FILE",
        help=f"results file to merge into (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="check that benchmarks execute: smallest size, one call, nothing written",
    )
    args = parser.parse_args(argv)
    paths: list[Path] = args.paths or [DEFAULT_PATH]
    output: Path = args.output
    smoke: bool = args.smoke

    try:
        benchmarks = [b for file in discover(paths) for b in load_benchmarks(file)]
    except BenchmarkError as error:
        print(f"bench: {error}", file=sys.stderr)
        return 2

    entries: list[dict[str, object]] = []
    for benchmark in benchmarks:
        results = benchmark.run(smoke=smoke)
        results.table()
        print()
        entries.append(results.to_dict())

    if smoke:
        print("bench: smoke mode, results not written")
    else:
        storage.merge(output, entries)
        print(f"bench: wrote {len(entries)} benchmark(s) to {output}")
    return 0
