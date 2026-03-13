# This file is part of stitchtoon.
# License: MIT, see the file "LICENSE" for details.
"""Benchmark primitives shared across all bench modules."""

from __future__ import annotations

import cProfile
import io
import pstats
import statistics
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class Benchmark:
    """Description of a single benchmarked operation."""

    name: str
    fn: Callable[[Any], Any]
    # Called once before timing to prepare shared state passed to fn.
    setup: Optional[Callable[[], Any]] = None
    iterations: int = 5
    description: str = ""
    # Declares the type of argument fn expects when --data is used.
    # "images"     -> list[PIL.Image.Image]
    # "file_paths" -> list[str]  (paths to image files on disk)
    # "zip_path"   -> str        (path to a zip archive)
    data_type: str = "images"


@dataclass
class BenchmarkResult:
    name: str
    description: str
    times: list[float]  # seconds per iteration

    @property
    def mean(self) -> float:
        return statistics.mean(self.times)

    @property
    def stdev(self) -> float:
        return statistics.stdev(self.times) if len(self.times) > 1 else 0.0

    @property
    def minimum(self) -> float:
        return min(self.times)

    @property
    def maximum(self) -> float:
        return max(self.times)


def run_benchmark(bench: Benchmark) -> BenchmarkResult:
    """Time *bench.fn* over *bench.iterations* iterations and return results."""
    arg = bench.setup() if bench.setup else None
    times: list[float] = []

    for _ in range(bench.iterations):
        t0 = time.perf_counter()
        bench.fn(arg)
        times.append(time.perf_counter() - t0)

    return BenchmarkResult(
        name=bench.name,
        description=bench.description,
        times=times,
    )


def profile_benchmark(bench: Benchmark, top_n: int = 20) -> str:
    """Profile a single call to *bench.fn* and return a formatted report string."""
    arg = bench.setup() if bench.setup else None

    profiler = cProfile.Profile()
    profiler.enable()
    bench.fn(arg)
    profiler.disable()

    buf = io.StringIO()
    stats = pstats.Stats(profiler, stream=buf)
    stats.sort_stats(pstats.SortKey.CUMULATIVE)
    stats.print_stats(top_n)
    return buf.getvalue()
