# This file is part of stitchtoon.
# License: MIT, see the file "LICENSE" for details.
"""Benchmarks for slice-detection methods."""

from __future__ import annotations

from typing import Any

from stitchtoon.core.slices_detectors.slices_detector import (
    DetectionMethod,
    SlicesDetector,
)

from .core import Benchmark
from .fixtures import make_images, make_striped_images


def _images_small() -> list:
    return make_striped_images(count=5, width=800, height=3_000)


def _images_large() -> list:
    return make_striped_images(count=10, width=1_200, height=6_000)


def _images_noisy() -> list:
    """Random-noise images -- window filtering is most impactful here."""
    return make_images(count=5, width=800, height=3_000, seed=99)


def _direct_detect(images: Any) -> None:
    SlicesDetector.slice_points(images, method=DetectionMethod.DIRECT, height=1_000)


def _pixel_detect_default(images: Any) -> None:
    SlicesDetector.slice_points(images, method=DetectionMethod.PIXEL, height=1_000)


def _pixel_detect_div2(images: Any) -> None:
    SlicesDetector.slice_points(
        images, method=DetectionMethod.PIXEL, height=1_000, division_factor=2
    )


def _pixel_detect_div4(images: Any) -> None:
    SlicesDetector.slice_points(
        images, method=DetectionMethod.PIXEL, height=1_000, division_factor=4
    )


def _pixel_detect_large(images: Any) -> None:
    SlicesDetector.slice_points(images, method=DetectionMethod.PIXEL, height=1_000)


def _pixel_detect_window5(images: Any) -> None:
    SlicesDetector.slice_points(
        images, method=DetectionMethod.PIXEL, height=1_000, window=5
    )


def _pixel_detect_window20(images: Any) -> None:
    SlicesDetector.slice_points(
        images, method=DetectionMethod.PIXEL, height=1_000, window=20
    )


def _pixel_detect_div2_window5(images: Any) -> None:
    SlicesDetector.slice_points(
        images, method=DetectionMethod.PIXEL, height=1_000, division_factor=2, window=5
    )


def _pixel_detect_window5_noisy(images: Any) -> None:
    SlicesDetector.slice_points(
        images, method=DetectionMethod.PIXEL, height=1_000, window=5
    )


BENCHMARKS: list[Benchmark] = [
    Benchmark(
        name="detection/direct/small",
        fn=_direct_detect,
        setup=_images_small,
        iterations=10,
        description="direct_detect - 5x(800x3000)",
    ),
    Benchmark(
        name="detection/pixel/window=1/small",
        fn=_pixel_detect_default,
        setup=_images_small,
        iterations=5,
        description="pixel_detect window=1 (baseline) - 5x(800x3000)",
    ),
    Benchmark(
        name="detection/pixel/window=5/small",
        fn=_pixel_detect_window5,
        setup=_images_small,
        iterations=5,
        description="pixel_detect window=5 - 5x(800x3000)",
    ),
    Benchmark(
        name="detection/pixel/window=20/small",
        fn=_pixel_detect_window20,
        setup=_images_small,
        iterations=5,
        description="pixel_detect window=20 - 5x(800x3000)",
    ),
    Benchmark(
        name="detection/pixel/div=2/small",
        fn=_pixel_detect_div2,
        setup=_images_small,
        iterations=5,
        description="pixel_detect division_factor=2 - 5x(800x3000)",
    ),
    Benchmark(
        name="detection/pixel/div=4/small",
        fn=_pixel_detect_div4,
        setup=_images_small,
        iterations=5,
        description="pixel_detect division_factor=4 - 5x(800x3000)",
    ),
    Benchmark(
        name="detection/pixel/div=2+window=5/small",
        fn=_pixel_detect_div2_window5,
        setup=_images_small,
        iterations=5,
        description="pixel_detect division_factor=2 window=5 - 5x(800x3000)",
    ),
    Benchmark(
        name="detection/pixel/window=1/large",
        fn=_pixel_detect_default,
        setup=_images_large,
        iterations=3,
        description="pixel_detect window=1 - 10x(1200x6000)",
    ),
    Benchmark(
        name="detection/pixel/window=5/noisy",
        fn=_pixel_detect_window5_noisy,
        setup=_images_noisy,
        iterations=5,
        description="pixel_detect window=5 on noisy images - 5x(800x3000)",
    ),
]
