# This file is part of stitchtoon.
# License: MIT, see the file "LICENSE" for details.
"""Benchmarks for image I/O (load / save)."""

from __future__ import annotations

import io as _io
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from PIL import Image

from stitchtoon.core.image_io import ImageIO
from stitchtoon.core.image_manipulator import ImageManipulator

from .core import Benchmark
from .fixtures import make_images

def _write_temp_images(count: int, fmt: str) -> list[str]:
    """Save synthetic images to a temp directory and return their paths."""
    tmpdir = Path(tempfile.mkdtemp())
    images = make_images(count=count, width=800, height=3_000)
    paths = []
    for i, img in enumerate(images):
        p = tmpdir / f"{i:03}.{fmt}"
        img.save(p, format=fmt)
        paths.append(str(p))
    return paths


def _write_temp_zip(count: int, fmt: str) -> str:
    """Save synthetic images into a zip archive and return its path."""
    tmpdir = Path(tempfile.mkdtemp())
    images = make_images(count=count, width=800, height=3_000)
    zip_path = str(tmpdir / "images.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
        for i, img in enumerate(images):
            buf = _io.BytesIO()
            img.save(buf, format=fmt)
            zf.writestr(f"{i:03}.{fmt}", buf.getvalue())
    return zip_path


def _setup_load_jpeg() -> list[str]:
    return _write_temp_images(5, "jpeg")


def _setup_load_png() -> list[str]:
    return _write_temp_images(5, "png")


def _setup_load_zip() -> str:
    return _write_temp_zip(5, "jpeg")


def _setup_save() -> list[Image.Image]:
    return make_images(count=5, width=800, height=3_000)


def _load_all_jpeg(paths: Any) -> None:
    ImageIO.load_all(files=tuple(paths))


def _load_all_png(paths: Any) -> None:
    ImageIO.load_all(files=tuple(paths))


def _load_archive(zip_path: Any) -> None:
    ImageIO.load_archive(path=zip_path)


def _save_all_jpeg(images: Any) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        ImageIO.save_all(out=tmp, images=images, format="JPEG", quality=85)


def _save_all_png(images: Any) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        ImageIO.save_all(out=tmp, images=images, format="PNG")


def _save_archive(images: Any) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        ImageIO.save_all(
            out=str(Path(tmp) / "out.zip"),
            images=images,
            format="JPEG",
            archive=True,
            quality=85,
        )


BENCHMARKS: list[Benchmark] = [
    Benchmark(
        name="io/load/jpeg/5-images",
        fn=_load_all_jpeg,
        setup=_setup_load_jpeg,
        iterations=5,
        description="load_all – 5 JPEG files (800×3000)",
    ),
    Benchmark(
        name="io/load/png/5-images",
        fn=_load_all_png,
        setup=_setup_load_png,
        iterations=5,
        description="load_all – 5 PNG files (800×3000)",
    ),
    Benchmark(
        name="io/load/zip/5-images",
        fn=_load_archive,
        setup=_setup_load_zip,
        iterations=5,
        description="load_archive – 5 JPEG files in zip (800×3000)",
    ),
    Benchmark(
        name="io/save/jpeg/5-images",
        fn=_save_all_jpeg,
        setup=_setup_save,
        iterations=5,
        description="save_all – 5 JPEG files (800×3000)",
    ),
    Benchmark(
        name="io/save/png/5-images",
        fn=_save_all_png,
        setup=_setup_save,
        iterations=5,
        description="save_all – 5 PNG files (800×3000)",
    ),
    Benchmark(
        name="io/save/zip/5-images",
        fn=_save_archive,
        setup=_setup_save,
        iterations=5,
        description="save_all (archive) – 5 JPEG files in zip (800×3000)",
    ),
]
