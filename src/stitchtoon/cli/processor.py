# This file is part of stitchtoon.
# License: MIT, see the file "LICENSE" for details.
"""Core processing logic for the CLI."""

import os.path as osp
import sys
import zipfile
from argparse import Namespace
from typing import List, Tuple

from PIL.Image import Image

from ..core.image_io import ImageIO
from ..core.image_manipulator import ImageManipulator
from ..core.scanner import scan
from ..core.slices_detectors.slices_detector import DetectionMethod, SlicesDetector
from ..core.stitcher import Stitcher
from ..progressbar import DefaultCliProgress, ProgressHandler

# Progress increments per stage (must sum to 100)
_STAGE_LOAD = 30
_STAGE_RESIZE = 10
_STAGE_DETECT = 20
_STAGE_STITCH = 20
_STAGE_SAVE = 20


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_progress(show: bool) -> ProgressHandler:
    return DefaultCliProgress() if show else ProgressHandler()


def _is_zip(path: str) -> bool:
    return osp.isfile(path) and zipfile.is_zipfile(path)


def _output_path(dir_path: str, input_base: str, output_base: str, archive: bool) -> str:
    """Derive the output path for a scanned directory."""
    rel = osp.relpath(dir_path, input_base)
    out = osp.join(output_base, rel) if rel != "." else output_base
    if archive:
        out = out.rstrip(osp.sep) + ".zip"
    return out


def _pixel_detect_kwargs(args: Namespace) -> dict:
    return {
        "x_margins": args.x_margins,
        "sensitivity": args.sensitivity,
        "max_height": args.max_height,
        "min_height": args.min_height,
        "division_factor": args.division_factor,
        "window": args.window,
    }


# ---------------------------------------------------------------------------
# Shared processing pipeline
# ---------------------------------------------------------------------------

def _pipeline(
    images: List[Image],
    out: str,
    args: Namespace,
    progress: ProgressHandler,
) -> None:
    """Run resize → detect → stitch → save on a list of already-loaded images."""
    progress.update(_STAGE_RESIZE, "Resizing")
    images = ImageManipulator.resize_all_width(images, value=args.width)

    progress.update(_STAGE_DETECT, "Detecting slices")
    method = DetectionMethod(args.method)
    extra = _pixel_detect_kwargs(args) if method == DetectionMethod.PIXEL else {}
    slices = SlicesDetector.slice_points(images, method=method, height=args.height, **extra)

    progress.update(_STAGE_STITCH, "Stitching")
    stitched = Stitcher.stitch(images, slices)

    progress.update(_STAGE_SAVE, "Saving")
    ImageIO.save_all(
        out=out,
        images=stitched,
        format=args.format,
        archive=args.archive,
        make_dirs=True,
    )


# ---------------------------------------------------------------------------
# Per-input-type entry points
# ---------------------------------------------------------------------------

def _process_directory(
    image_dir: Tuple[str, List[str]],
    args: Namespace,
    progress: ProgressHandler,
) -> None:
    dir_path, image_files = image_dir
    out = _output_path(dir_path, args.input, args.output, args.archive)

    progress.update(_STAGE_LOAD, "Loading")
    images = ImageIO.load_all(files=tuple(image_files))

    _pipeline(images, out, args, progress)


def _process_zip(zip_path: str, args: Namespace, progress: ProgressHandler) -> None:
    out = args.output
    if args.archive:
        out = osp.join(out, osp.splitext(osp.basename(zip_path))[0] + ".zip")

    progress.update(_STAGE_LOAD, "Loading archive")
    images = ImageIO.load_archive(path=zip_path)
    if not images:
        raise ValueError(f"No supported images found in '{zip_path}'")

    _pipeline(images, out, args, progress)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run(args: Namespace) -> int:
    if _is_zip(args.input):
        return _run_zip(args)
    return _run_directory(args)


def _run_zip(args: Namespace) -> int:
    if not args.recursive:
        # --recursive is meaningless for a zip, but don't silently ignore it
        print("Note: --no-recursive has no effect when INPUT is a zip archive.", file=sys.stderr)

    label = osp.basename(args.input)
    print(f"[1/1] {label}")

    progress = _make_progress(args.progress)
    progress.start()
    try:
        _process_zip(args.input, args, progress)
    except Exception as exc:
        progress.finish()
        print(f"  Error: {exc}", file=sys.stderr)
        return 1

    progress.finish()
    return 0


def _run_directory(args: Namespace) -> int:
    dirs = scan(args.input, recursive=args.recursive)

    if not dirs:
        print(f"No supported images found in '{args.input}'", file=sys.stderr)
        return 1

    total = len(dirs)
    errors = 0

    for i, image_dir in enumerate(dirs, 1):
        dir_path = image_dir[0]
        label = osp.relpath(dir_path, args.input)
        print(f"[{i}/{total}] {label}")

        progress = _make_progress(args.progress)
        progress.start()
        try:
            _process_directory(image_dir, args, progress)
        except Exception as exc:
            progress.finish()
            print(f"  Error: {exc}", file=sys.stderr)
            errors += 1
            continue

        progress.finish()

    return 0 if errors == 0 else 1
