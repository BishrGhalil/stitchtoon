# This file is part of stitchtoon.
# License: MIT, see the file "LICENSE" for details.
"""End-to-end pipeline benchmarks."""

from __future__ import annotations

import tempfile
from typing import Any

from stitchtoon.core.image_io import ImageIO
from stitchtoon.core.image_manipulator import ImageManipulator
from stitchtoon.core.slices_detectors.slices_detector import DetectionMethod, SlicesDetector
from stitchtoon.core.stitcher import Stitcher

from .core import Benchmark
from .fixtures import make_striped_images


def _setup_small() -> list:
    return make_striped_images(count=5, width=800, height=3_000)


def _setup_large() -> list:
    return make_striped_images(count=10, width=1_200, height=6_000)


def _run_pipeline(images: Any, method: DetectionMethod, height: int, fmt: str) -> None:
    images = ImageManipulator.resize_all_width(images)
    slices = SlicesDetector.slice_points(images, method=method, height=height)
    stitched = Stitcher.stitch(images, slices)
    with tempfile.TemporaryDirectory() as tmp:
        ImageIO.save_all(out=tmp, images=stitched, format=fmt)


def _pipeline_pixel_jpeg_small(images: Any) -> None:
    _run_pipeline(images, DetectionMethod.PIXEL, height=1_000, fmt="jpeg")


def _pipeline_direct_jpeg_small(images: Any) -> None:
    _run_pipeline(images, DetectionMethod.DIRECT, height=1_000, fmt="jpeg")


def _pipeline_pixel_jpeg_large(images: Any) -> None:
    _run_pipeline(images, DetectionMethod.PIXEL, height=1_000, fmt="jpeg")


def _pipeline_pixel_png_small(images: Any) -> None:
    _run_pipeline(images, DetectionMethod.PIXEL, height=1_000, fmt="png")


BENCHMARKS: list[Benchmark] = [
    Benchmark(
        name="pipeline/pixel+jpeg/small",
        fn=_pipeline_pixel_jpeg_small,
        setup=_setup_small,
        iterations=3,
        description="full pipeline – pixel detect + jpeg out – 5×(800×3000)",
    ),
    Benchmark(
        name="pipeline/direct+jpeg/small",
        fn=_pipeline_direct_jpeg_small,
        setup=_setup_small,
        iterations=3,
        description="full pipeline – direct detect + jpeg out – 5×(800×3000)",
    ),
    Benchmark(
        name="pipeline/pixel+png/small",
        fn=_pipeline_pixel_png_small,
        setup=_setup_small,
        iterations=3,
        description="full pipeline – pixel detect + png out – 5×(800×3000)",
    ),
    Benchmark(
        name="pipeline/pixel+jpeg/large",
        fn=_pipeline_pixel_jpeg_large,
        setup=_setup_large,
        iterations=2,
        description="full pipeline – pixel detect + jpeg out – 10×(1200×6000)",
    ),
]
