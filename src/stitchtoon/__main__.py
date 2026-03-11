# This file is part of stitchtoon.
# License: MIT, see the file "LICENSE" for details.
"""Entry point for `python -m stitchtoon` and the `stitchtoon` console script."""

import sys

from .cli.args import parse_args
from .cli.processor import run


def main() -> None:
    args = parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
