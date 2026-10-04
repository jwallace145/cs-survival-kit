"""The timing harness: define cases, time them, and fit their growth."""

import gc
import math
import platform
import statistics
import time
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

from cs_survival_kit import __version__

OK = "ok"
NOT_IMPLEMENTED = "not implemented"

MIN_MEASUREMENT_NS = 100_000_000
"""A measurement loops its case until the timed calls add up to this long."""

_timer = time.perf_counter_ns


@dataclass(frozen=True)
class Fit:
    """The empirical growth of one case.

    Attributes:
        slope: Least-squares slope of `log(seconds)` against `log(n)`, or
            `None` when there are too few sizes to fit.
        growth: A rough human-readable reading of the slope.
    """

    slope: float | None
    growth: str


@dataclass(frozen=True)
class CaseResult:
    """The measurements for one case of a benchmark.

    Attributes:
        label: The case's label.
        status: `"ok"`, or `"not implemented"` if the case raised
            `NotImplementedError`.
        sizes: The input sizes that were measured.
        seconds: Per-call time for each entry of `sizes`.
        slope: Log-log slope of `seconds` against `sizes`, or `None`.
    """

    label: str
    status: str
    sizes: list[int]
    seconds: list[float]
    slope: float | None


@dataclass(frozen=True)
class Results:
    """The outcome of one [`Benchmark.run`][cs_survival_kit.bench.core.Benchmark.run].

    Attributes:
        name: The benchmark's name.
        run_at: When the run started, as an ISO 8601 UTC timestamp.
        package_version: The `cs-survival-kit` version that was measured.
        environment: The interpreter and machine the run happened on.
        cases: One result per case, in the order the cases were added.
    """

    name: str
    run_at: str
    package_version: str
    environment: dict[str, str]
    cases: list[CaseResult]

    def fit(self) -> dict[str, Fit]:
        """Estimate each case's growth from its measurements.

        The slope of time against size on a log-log scale approximates the
        exponent `k` in `O(n^k)`: about 0 is constant, about 1 is linear,
        about 2 is quadratic. `O(n log n)` has no exponent of its own and
        reads as slightly above 1.

        This is an empirical sanity check, not a proof. Constant factors,
        caches and small sizes all bend the line.

        Returns:
            A mapping from case label to its fit.
        """
        fits: dict[str, Fit] = {}
        for case in self.cases:
            if case.status != OK:
                growth = case.status
            elif case.slope is None:
                growth = "-"
            else:
                growth = describe_slope(case.slope)
            fits[case.label] = Fit(case.slope, growth)
        return fits

    def format(self) -> str:
        """Render the results as a plain-text table.

        Returns:
            One row per size and one column per case, followed by each
            case's slope and growth.
        """
        fits = self.fit()
        sizes = sorted({n for case in self.cases for n in case.sizes})
        columns: list[list[str]] = [
            ["n", *(f"{n:,}" for n in sizes), "slope", "growth"]
        ]
        for case in self.cases:
            times = dict(zip(case.sizes, case.seconds, strict=True))
            fit = fits[case.label]
            columns.append(
                [
                    case.label,
                    *(_format_seconds(times[n]) if n in times else "-" for n in sizes),
                    "-" if fit.slope is None else f"{fit.slope:.2f}",
                    fit.growth,
                ]
            )
        widths = [max(len(cell) for cell in column) for column in columns]
        lines = [self.name]
        for row in zip(*columns, strict=True):
            first, *rest = (
                cell.ljust(width) for cell, width in zip(row, widths, strict=True)
            )
            lines.append("  ".join([first.strip().rjust(widths[0]), *rest]).rstrip())
        return "\n".join(lines)

    def table(self) -> None:
        """Print the results as a plain-text table."""
        print(self.format())

    def to_dict(self) -> dict[str, Any]:
        """Convert the results to a JSON-serializable dictionary.

        Returns:
            The benchmark entry stored in `benchmarks.json`.
        """
        return asdict(self)


@dataclass(frozen=True)
class _Case:
    label: str
    setup: Callable[[int], Any]
    run: Callable[[Any], object]
    sizes: tuple[int, ...]


class Benchmark:
    """A named set of cases, each timed across a range of input sizes.

    Each case pairs a `setup` function, which builds the inputs for a size
    and is not timed, with a `run` function, which is. Cases in the same
    benchmark are alternatives to compare, such as two implementations of one
    operation.

    Args:
        name: A unique name for the benchmark, such as
            `"dynamic_array.append"`. Stored results are keyed by it.
        sizes: The input sizes to measure. Cases use these unless they bring
            their own.

    Raises:
        ValueError: If `sizes` is empty or contains a non-positive size.

    Examples:
        >>> b = Benchmark("sum", sizes=[1_000, 10_000])
        >>> b.case("builtin", setup=lambda n: list(range(n)), run=sum)
        >>> results = b.run(smoke=True)
        >>> [case.sizes for case in results.cases]
        [[1000]]
    """

    def __init__(self, name: str, sizes: Sequence[int]) -> None:
        self.name = name
        self.sizes = _validate_sizes(sizes)
        self._cases: list[_Case] = []

    def case[T](
        self,
        label: str,
        *,
        setup: Callable[[int], T],
        run: Callable[[T], object],
        sizes: Sequence[int] | None = None,
    ) -> None:
        """Add a case to the benchmark.

        Args:
            label: A name for the case, unique within the benchmark.
            setup: Builds the inputs for a size `n`. Not timed. It is called
                again before every timed call, so `run` is free to mutate
                what it is given.
            run: The code to time. It receives whatever `setup` returned.
            sizes: Sizes for this case only, overriding the benchmark's. Use
                it to cap a slow case at smaller inputs.

        Raises:
            ValueError: If `label` is already taken, or `sizes` is invalid.
        """
        if any(case.label == label for case in self._cases):
            raise ValueError(f"duplicate case label: {label!r}")
        case_sizes = self.sizes if sizes is None else _validate_sizes(sizes)
        self._cases.append(_Case(label, setup, run, case_sizes))

    def run(self, repeat: int = 5, *, smoke: bool = False) -> Results:
        """Time every case at every size.

        Each measurement calls `run` in a loop until the timed calls add up
        to about 0.1 seconds, so that fast calls are not lost in timer noise.
        The reported time is per call, and is the minimum over `repeat`
        measurements: the minimum is the run least disturbed by the rest of
        the machine. Garbage collection is disabled while timing.

        A case that raises `NotImplementedError` is reported as
        `"not implemented"` and skipped, so benchmarks can be written before
        the code they measure.

        Args:
            repeat: How many measurements to take per size.
            smoke: Only check that the cases execute: time the smallest size
                once, with a single call. The numbers are meaningless.

        Returns:
            The measurements for every case.

        Raises:
            ValueError: If `repeat` is less than 1.
        """
        if repeat < 1:
            raise ValueError("repeat must be at least 1")
        run_at = datetime.now(UTC).isoformat(timespec="seconds")
        cases = [_run_case(case, repeat, smoke) for case in self._cases]
        return Results(self.name, run_at, __version__, _environment(), cases)


def fit_slope(sizes: Sequence[int], seconds: Sequence[float]) -> float | None:
    """Fit the log-log slope of time against size.

    Args:
        sizes: The input sizes.
        seconds: The time measured at each size.

    Returns:
        The least-squares slope of `log(seconds)` against `log(sizes)`, or
        `None` if there are fewer than two distinct sizes to fit.
    """
    points = [
        (math.log(n), math.log(s)) for n, s in zip(sizes, seconds, strict=True) if s > 0
    ]
    if len({x for x, _ in points}) < 2:
        return None
    xs, ys = zip(*points, strict=True)
    return statistics.linear_regression(xs, ys).slope


def describe_slope(slope: float) -> str:
    """Give a rough human-readable reading of a log-log slope.

    Args:
        slope: A slope from [`fit_slope`][cs_survival_kit.bench.core.fit_slope].

    Returns:
        `"~ constant"`, `"~ linear"` or `"~ quadratic"` when the slope is
        within 0.25 of 0, 1 or 2, and a looser description otherwise. Note
        that `O(n log n)` lands slightly above 1 and reads as `"~ linear"`.
    """
    if slope < 0.25:
        return "~ constant"
    if slope < 0.75:
        return "sublinear"
    if slope < 1.25:
        return "~ linear"
    if slope < 1.75:
        return "superlinear"
    if slope < 2.25:
        return "~ quadratic"
    return f"~ n^{slope:.1f}"


def _validate_sizes(sizes: Sequence[int]) -> tuple[int, ...]:
    if not sizes:
        raise ValueError("a benchmark needs at least one size")
    if any(n <= 0 for n in sizes):
        raise ValueError("sizes must be positive")
    return tuple(sizes)


def _run_case(case: _Case, repeat: int, smoke: bool) -> CaseResult:
    sizes = [min(case.sizes)] if smoke else list(case.sizes)
    seconds: list[float] = []
    try:
        for n in sizes:
            if smoke:
                seconds.append(_measure(case, n, 1) / 1e9)
            else:
                seconds.append(_time_size(case, n, repeat))
    except NotImplementedError:
        return CaseResult(case.label, NOT_IMPLEMENTED, [], [], None)
    return CaseResult(case.label, OK, sizes, seconds, fit_slope(sizes, seconds))


def _time_size(case: _Case, n: int, repeat: int) -> float:
    """Return the best per-call time, in seconds, over `repeat` measurements."""
    number = 1
    total = _measure(case, n, number)
    while total < MIN_MEASUREMENT_NS:
        number = _next_number(number)
        total = _measure(case, n, number)
    best = total / number
    for _ in range(repeat - 1):
        best = min(best, _measure(case, n, number) / number)
    return best / 1e9


def _next_number(number: int) -> int:
    """Step through 1, 2, 5, 10, 20, 50, ... like `timeit.Timer.autorange`."""
    magnitude = 10 ** (len(str(number)) - 1)
    leading = number // magnitude
    return {1: 2, 2: 5, 5: 10}[leading] * magnitude


def _measure(case: _Case, n: int, number: int) -> int:
    """Return the total nanoseconds spent in `number` timed calls."""
    total = 0
    for _ in range(number):
        inputs = case.setup(n)
        gc_was_enabled = gc.isenabled()
        gc.disable()
        try:
            start = _timer()
            case.run(inputs)
            total += _timer() - start
        finally:
            if gc_was_enabled:
                gc.enable()
    return total


def _environment() -> dict[str, str]:
    return {
        "python_version": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }


def _format_seconds(seconds: float) -> str:
    for unit, scale in (("s", 1.0), ("ms", 1e-3), ("µs", 1e-6)):
        if seconds >= scale:
            return f"{seconds / scale:.3g} {unit}"
    return f"{seconds / 1e-9:.3g} ns"
