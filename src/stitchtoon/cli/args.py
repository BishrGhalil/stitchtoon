# This file is part of stitchtoon.
# License: MIT, see the file "LICENSE" for details.
"""CLI argument parsing."""

import argparse
from typing import Optional, Sequence

from ..const import FORMATS
from ..core.slices_detectors.slices_detector import DetectionMethod
from .. import VERSION


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stitchtoon",
        description="Stitch and slice webtoon/manhwa/manhua raws.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--version", action="version", version=VERSION)

    # Positional arguments
    parser.add_argument("input", metavar="INPUT", help="Input directory path")
    parser.add_argument("output", metavar="OUTPUT", help="Output directory path")

    # I/O options
    io = parser.add_argument_group("I/O Options")
    io.add_argument(
        "-f", "--format",
        default="jpg",
        metavar="FORMAT",
        help=f"Output image format. Supported: {', '.join(sorted(FORMATS))}",
    )
    io.add_argument(
        "-r", "--recursive",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Recursively scan subdirectories",
    )
    io.add_argument(
        "--archive",
        action="store_true",
        default=False,
        help="Pack each output directory into a zip archive",
    )
    io.add_argument(
        "--width",
        type=int,
        default=None,
        metavar="PX",
        help="Normalize all images to this width before processing. "
             "If omitted, auto-resize to the minimum width found",
    )

    parser.add_argument(
        "--progress",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Show a progress bar while processing",
    )

    # Detection options
    det = parser.add_argument_group("Detection Options")
    det.add_argument(
        "-m", "--method",
        choices=[m.value for m in DetectionMethod if m != DetectionMethod.AUTO],
        default=DetectionMethod.PIXEL.value,
        help="Slice detection method",
    )
    det.add_argument(
        "-H", "--height",
        type=int,
        default=None,
        metavar="PX",
        help="Target slice height in pixels. Required for 'pixel' and 'direct' methods",
    )

    # Pixel-detection tuning
    px = parser.add_argument_group(
        "Pixel Detection Options",
        description="Fine-tuning options only used when --method=pixel",
    )
    px.add_argument(
        "--step",
        type=int,
        default=3,
        metavar="N",
        help="Search step size when scanning for valid slice rows",
    )
    px.add_argument(
        "--x-margins",
        type=int,
        default=0,
        metavar="PX",
        help="Pixels to ignore on the left and right edges during detection",
    )
    px.add_argument(
        "--sensitivity",
        type=int,
        default=100,
        metavar="PCT",
        help="Detection accuracy (1-100 percent; lower = more permissive)",
    )
    px.add_argument(
        "--max-height",
        type=float,
        default=-1,
        metavar="VALUE",
        help="Maximum slice height. -1 means no limit. "
             "A float < height is treated as a fraction of --height; an int is treated as pixels",
    )
    px.add_argument(
        "--min-height",
        type=float,
        default=-1,
        metavar="VALUE",
        help="Minimum slice height. -1 means no limit. "
             "A float < height is treated as a fraction of --height; an int is treated as pixels",
    )
    px.add_argument(
        "--division-factor",
        type=int,
        default=1,
        metavar="N",
        help="Downscale factor applied before detection (1-5). "
             "Higher values are faster but less accurate",
    )

    return parser


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Validate format
    args.format = args.format.strip(".").upper()
    if args.format not in FORMATS:
        parser.error(
            f"Unsupported format '{args.format}'. "
            f"Choose from: {', '.join(sorted(FORMATS))}"
        )

    # Height is required for non-auto methods
    needs_height = {DetectionMethod.PIXEL.value, DetectionMethod.DIRECT.value}
    if args.method in needs_height and args.height is None:
        parser.error(f"--height is required when using --method={args.method}")

    # Coerce whole-number floats to int for max/min height
    for attr in ("max_height", "min_height"):
        val = getattr(args, attr)
        if val != -1 and val == int(val):
            setattr(args, attr, int(val))

    return args
