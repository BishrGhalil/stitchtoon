# This file is part of stitchtoon.
# License: MIT, see the file "LICENSE" for details.
"""Synthetic image fixtures for benchmarks.

Images are generated with PIL and kept entirely in memory — no disk I/O needed
to set up a benchmark run.
"""

from __future__ import annotations

import random
from typing import Optional

from PIL import Image


def make_image(
    width: int = 800,
    height: int = 3_000,
    mode: str = "RGB",
    seed: Optional[int] = None,
) -> Image.Image:
    """Return a synthetic PIL image filled with deterministic noise."""
    rng = random.Random(seed)
    # Generate a flat byte buffer – fast and avoids numpy dependency in fixtures.
    n_channels = len(mode)
    data = bytes(rng.getrandbits(8) for _ in range(width * height * n_channels))
    return Image.frombytes(mode, (width, height), data)


def make_images(
    count: int = 5,
    width: int = 800,
    height: int = 3_000,
    mode: str = "RGB",
    seed: int = 42,
) -> list[Image.Image]:
    """Return *count* synthetic images with reproducible content."""
    return [make_image(width, height, mode, seed=seed + i) for i in range(count)]


def make_striped_images(
    count: int = 5,
    width: int = 800,
    height: int = 3_000,
    stripe_height: int = 10,
    mode: str = "RGB",
) -> list[Image.Image]:
    """Return images with alternating solid-colour horizontal stripes.

    These produce predictable pixel-detect slice points, making detection
    benchmarks representative of real-world webtoon content.
    """
    images = []
    for _ in range(count):
        img = Image.new(mode, (width, height), (255, 255, 255))
        y = 0
        toggle = False
        while y < height:
            colour = (200, 200, 200) if toggle else (255, 255, 255)
            band = Image.new(mode, (width, min(stripe_height, height - y)), colour)
            img.paste(band, (0, y))
            y += stripe_height
            toggle = not toggle
        images.append(img)
    return images
