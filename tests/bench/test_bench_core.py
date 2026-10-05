import gc
import math

import pytest

from cs_survival_kit import __version__
from cs_survival_kit.bench import Benchmark, CaseResult, Results, core


class FakeClock:
    """A clock that only moves when a fake workload advances it."""

    def __init__(self) -> None:
        self.now = 0

    def __call__(self) -> int:
        return self.now

    def advance(self, ns: int) -> None:
        self.now += ns


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> FakeClock:
    fake = FakeClock()
    monkeypatch.setattr(core, "_timer", fake)
    return fake


def results_for(*cases: CaseResult) -> Results:
    return Results(
        name="synthetic",
        run_at="2026-01-01T00:00:00+00:00",
        package_version="0.0.0",
        environment={},
        cases=list(cases),
    )


def synthetic_case(label: str, exponent: float, scale: float = 1e-9) -> CaseResult:
    sizes = [10**k for k in range(2, 7)]
    seconds = [scale * n**exponent for n in sizes]
    return CaseResult(
        label=label,
        status=core.OK,
        sizes=sizes,
        seconds=seconds,
        slope=core.fit_slope(sizes, seconds),
    )


# --- timing harness ---------------------------------------------------------


def test_reports_per_call_seconds_for_each_size(clock: FakeClock):
    # One second per element: far above the autorange threshold, so one call each.
    bench = Benchmark("fake", sizes=[1, 2, 4])
    bench.case("linear", setup=lambda n: n, run=lambda n: clock.advance(n * 10**9))

    (case,) = bench.run(repeat=1).cases

    assert case.status == core.OK
    assert case.sizes == [1, 2, 4]
    assert case.seconds == [1.0, 2.0, 4.0]
    assert case.slope == pytest.approx(1.0)


def test_setup_is_not_timed(clock: FakeClock):
    def setup(n: int) -> int:
        clock.advance(500 * 10**9)
        return n

    bench = Benchmark("fake", sizes=[3])
    bench.case("case", setup=setup, run=lambda n: clock.advance(n * 10**9))

    assert bench.run(repeat=2).cases[0].seconds == [3.0]


def test_setup_runs_before_every_timed_call(clock: FakeClock):
    seen: list[list[int]] = []

    def run(inputs: list[int]) -> None:
        seen.append(inputs)
        inputs.append(0)  # mutating the inputs must not leak into the next call
        clock.advance(10**9)

    bench = Benchmark("fake", sizes=[5])
    bench.case("case", setup=lambda n: [n], run=run)
    bench.run(repeat=3)

    assert len(seen) == 3
    assert all(inputs == [5, 0] for inputs in seen)
    assert len({id(inputs) for inputs in seen}) == 3


def test_takes_the_minimum_of_repeats(clock: FakeClock):
    durations = iter([5, 2, 9])
    bench = Benchmark("fake", sizes=[1])
    bench.case(
        "case", setup=lambda n: n, run=lambda n: clock.advance(next(durations) * 10**9)
    )

    assert bench.run(repeat=3).cases[0].seconds == [2.0]


def test_fast_calls_are_looped_until_the_measurement_is_long_enough(clock: FakeClock):
    calls_in_final_measurement = 0
    calls = 0

    def run(n: int) -> None:
        nonlocal calls
        calls += 1
        clock.advance(1_000_000)  # 1 ms per call

    bench = Benchmark("fake", sizes=[1])
    bench.case("case", setup=lambda n: n, run=run)
    (case,) = bench.run(repeat=1).cases

    # Loop counts grow 1, 2, 5, 10, 20, 50, 100; 100 calls of 1 ms reach 0.1 s.
    calls_in_final_measurement = 100
    assert calls == 1 + 2 + 5 + 10 + 20 + 50 + calls_in_final_measurement
    assert case.seconds == [pytest.approx(0.001)]


def test_gc_is_disabled_during_the_timed_call_and_restored(clock: FakeClock):
    states: list[bool] = []

    def run(n: int) -> None:
        states.append(gc.isenabled())
        clock.advance(10**9)

    bench = Benchmark("fake", sizes=[1])
    bench.case("case", setup=lambda n: n, run=run)

    assert gc.isenabled()
    bench.run(repeat=2)
    assert states == [False, False]
    assert gc.isenabled()


def test_gc_stays_disabled_if_it_was_disabled_before_the_run(clock: FakeClock):
    bench = Benchmark("fake", sizes=[1])
    bench.case("case", setup=lambda n: n, run=lambda n: clock.advance(10**9))

    gc.disable()
    try:
        bench.run(repeat=1)
        assert not gc.isenabled()
    finally:
        gc.enable()


def test_gc_is_restored_when_a_case_raises(clock: FakeClock):
    def run(n: int) -> None:
        raise RuntimeError("boom")

    bench = Benchmark("fake", sizes=[1])
    bench.case("case", setup=lambda n: n, run=run)

    with pytest.raises(RuntimeError, match="boom"):
        bench.run()
    assert gc.isenabled()


def test_per_case_sizes_override_the_benchmark_sizes(clock: FakeClock):
    bench = Benchmark("fake", sizes=[1, 2, 3])
    bench.case("default", setup=lambda n: n, run=lambda n: clock.advance(10**9))
    bench.case(
        "small", setup=lambda n: n, run=lambda n: clock.advance(10**9), sizes=[1, 2]
    )

    default, small = bench.run(repeat=1).cases
    assert default.sizes == [1, 2, 3]
    assert small.sizes == [1, 2]


def test_smoke_runs_the_smallest_size_exactly_once(clock: FakeClock):
    calls: list[int] = []

    def run(n: int) -> None:
        calls.append(n)
        clock.advance(1)  # far too fast; smoke must not loop to compensate

    bench = Benchmark("fake", sizes=[30, 10, 20])
    bench.case("case", setup=lambda n: n, run=run)
    (case,) = bench.run(repeat=5, smoke=True).cases

    assert calls == [10]
    assert case.sizes == [10]
    assert case.slope is None


def test_results_record_when_and_where_they_ran(clock: FakeClock):
    bench = Benchmark("fake", sizes=[1])
    bench.case("case", setup=lambda n: n, run=lambda n: clock.advance(10**9))
    results = bench.run(repeat=1)

    assert results.name == "fake"
    assert results.package_version == __version__
    assert results.run_at.endswith("+00:00")
    assert set(results.environment) == {
        "python_version",
        "implementation",
        "platform",
        "machine",
        "processor",
    }


# --- NotImplementedError handling -------------------------------------------


def test_case_raising_not_implemented_in_run_is_skipped(clock: FakeClock):
    def stub(n: int) -> None:
        raise NotImplementedError

    bench = Benchmark("fake", sizes=[1, 2])
    bench.case("stub", setup=lambda n: n, run=stub)
    bench.case("real", setup=lambda n: n, run=lambda n: clock.advance(n * 10**9))

    stub_case, real_case = bench.run(repeat=1).cases

    assert stub_case.status == core.NOT_IMPLEMENTED
    assert stub_case.sizes == []
    assert stub_case.seconds == []
    assert stub_case.slope is None
    assert real_case.status == core.OK
    assert real_case.seconds == [1.0, 2.0]


def test_case_raising_not_implemented_in_setup_is_skipped(clock: FakeClock):
    def setup(n: int) -> int:
        raise NotImplementedError

    bench = Benchmark("fake", sizes=[1])
    bench.case("stub", setup=setup, run=lambda n: clock.advance(10**9))

    assert bench.run().cases[0].status == core.NOT_IMPLEMENTED


# --- validation -------------------------------------------------------------


def test_rejects_bad_definitions():
    with pytest.raises(ValueError, match="at least one size"):
        Benchmark("fake", sizes=[])
    with pytest.raises(ValueError, match="positive"):
        Benchmark("fake", sizes=[0])

    bench = Benchmark("fake", sizes=[1])
    bench.case("case", setup=lambda n: n, run=lambda n: None)
    with pytest.raises(ValueError, match="duplicate"):
        bench.case("case", setup=lambda n: n, run=lambda n: None)
    with pytest.raises(ValueError, match="repeat"):
        bench.run(repeat=0)


# --- fit --------------------------------------------------------------------


@pytest.mark.parametrize(
    ("exponent", "growth"),
    [(0.0, "~ constant"), (1.0, "~ linear"), (2.0, "~ quadratic")],
)
def test_fit_recovers_known_slopes(exponent: float, growth: str):
    fit = results_for(synthetic_case("case", exponent)).fit()["case"]

    assert fit.slope == pytest.approx(exponent, abs=1e-9)
    assert fit.growth == growth


def test_n_log_n_reads_as_slightly_above_linear():
    sizes = [10**k for k in range(2, 7)]
    seconds = [1e-9 * n * math.log2(n) for n in sizes]
    slope = core.fit_slope(sizes, seconds)

    assert slope is not None
    assert 1.0 < slope < 1.25
    assert core.describe_slope(slope) == "~ linear"


def test_fit_labels_in_between_and_steeper_slopes():
    assert core.describe_slope(0.5) == "sublinear"
    assert core.describe_slope(1.5) == "superlinear"
    assert core.describe_slope(3.0) == "~ n^3.0"


def test_fit_needs_two_sizes():
    assert core.fit_slope([10], [1.0]) is None
    assert core.fit_slope([], []) is None


def test_fit_reports_unimplemented_cases():
    stub = CaseResult("stub", core.NOT_IMPLEMENTED, [], [], None)
    fit = results_for(stub).fit()["stub"]

    assert fit.slope is None
    assert fit.growth == core.NOT_IMPLEMENTED


# --- output -----------------------------------------------------------------


def test_to_dict_matches_the_results_schema():
    results = results_for(synthetic_case("case", 1.0))
    data = results.to_dict()

    assert set(data) == {"name", "run_at", "package_version", "environment", "cases"}
    assert set(data["cases"][0]) == {"label", "sizes", "seconds", "slope", "status"}
    assert data["cases"][0]["status"] == "ok"


def test_table_prints_every_case(capsys: pytest.CaptureFixture[str]):
    stub = CaseResult("stub", core.NOT_IMPLEMENTED, [], [], None)
    small = CaseResult("small", core.OK, [100], [2.5e-6], None)
    results_for(synthetic_case("linear", 1.0), small, stub).table()
    out = capsys.readouterr().out

    assert "synthetic" in out
    assert "linear" in out and "~ linear" in out
    assert "not implemented" in out
    assert "2.5 µs" in out
    assert "1,000,000" in out
