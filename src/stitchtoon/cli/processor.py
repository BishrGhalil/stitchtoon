# This file is part of stitchtoon.
# License: MIT, see the file "LICENSE" for details.
"""Core processing logic for the CLI."""

import os.path as osp
import sys
from argparse import Namespace
from typing import Tuple, List

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


def _make_progress(show: bool) -> ProgressHandler:
    return DefaultCliProgress() if show else ProgressHandler()


def _output_path(dir_path: str, input_base: str, output_base: str, archive: bool) -> str:
    """Derive the output path for a scanned directory."""
    rel = osp.relpath(dir_path, input_base)
    out = osp.join(output_base, rel) if rel != "." else output_base
    if archive:
        out = out.rstrip(osp.sep) + ".zip"
    return out


def _pixel_detect_kwargs(args: Namespace) -> dict:
    return {
        "step": args.step,
        "x_margins": args.x_margins,
        "sensitivity": args.sensitivity,
        "max_height": args.max_height,
        "min_height": args.min_height,
        "division_factor": args.division_factor,
    }


def _process_directory(
    image_dir: Tuple[str, List[str]],
    args: Namespace,
    progress: ProgressHandler,
) -> None:
    dir_path, image_files = image_dir

    out = _output_path(dir_path, args.input, args.output, args.archive)

    progress.update(_STAGE_LOAD, "Loading")
    images = ImageIO.load_all(files=tuple(image_files))

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


def run(args: Namespace) -> int:
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
