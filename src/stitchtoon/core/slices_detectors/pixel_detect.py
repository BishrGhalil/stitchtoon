from typing import List, Union

import numpy as np
import PIL.Image
from PIL.Image import Image

from ...logger import logged
from .slice import Slice


def _validate_margins(width: int, x_margins: int) -> None:
    if width - x_margins <= x_margins + 1:
        raise RuntimeError("Margins are too big")


def _compute_valid_rows(
    arr: np.ndarray,  # uint8, shape (H, W)
    x_margins: int,
    threshold: int,
) -> np.ndarray:  # bool, shape (H,)
    """Vectorized: returns True for rows that are valid slice candidates.

    A row is valid when:
      - No two neighboring pixels differ by more than *threshold* (absolute).
      - The row's pixel spread (max - min) is <= *threshold*.
    """
    if x_margins > 0:
        arr = arr[:, x_margins : arr.shape[1] - x_margins]

    # int16 only for the diff so subtraction does not wrap on uint8
    diff = np.abs(np.diff(arr.astype(np.int16), axis=1))   # (H, W-1)
    max_neighbor_diff = diff.max(axis=1)                    # (H,)

    col_min = arr.min(axis=1).astype(np.int16)
    col_max = arr.max(axis=1).astype(np.int16)
    spread = col_max - col_min                              # (H,)

    return (max_neighbor_diff <= threshold) & (spread <= threshold)


def _apply_window(valid_rows: np.ndarray, window: int) -> np.ndarray:
    """Return confirmed[i] = True iff rows [i, i+window) are ALL valid.

    Uses the cumulative-sum trick: O(H) with no Python loop.
    window=1 is a no-op (returns valid_rows unchanged).
    """
    if window <= 1:
        return valid_rows

    H = len(valid_rows)
    cum = np.concatenate([[0], np.cumsum(valid_rows.astype(np.int32))])
    window_sums = cum[window:] - cum[: H - window + 1]  # (H-window+1,)

    confirmed = np.zeros(H, dtype=bool)
    confirmed[: H - window + 1] = window_sums == window
    return confirmed


def _find_nearest_valid_row(
    confirmed: np.ndarray,  # bool, shape (H,)
    lo: int,                # inclusive lower bound
    hi: int,                # exclusive upper bound
    target: int,
) -> int | None:
    """Return the confirmed row closest to *target* within [lo, hi).

    No Python loop -- fully vectorized using np.where + np.argmin.
    """
    lo = max(lo, 0)
    hi = min(hi, len(confirmed))
    if lo >= hi:
        return None

    indices = np.where(confirmed[lo:hi])[0]
    if len(indices) == 0:
        return None

    abs_indices = indices + lo
    return int(abs_indices[np.argmin(np.abs(abs_indices - target))])


@logged
def pixel_detect(
    images: List[Image],
    height: int,
    x_margins: int = 0,
    sensitivity: int = 100,
    max_height: Union[int, float] = -1,
    min_height: Union[int, float] = -1,
    division_factor: int = 1,
    window: int = 1,
) -> List[Slice]:
    """Detect slice points using neighboring-pixel comparison.

    Args:
        images:          Input images (all must share the same width).
        height:          Target slice height in pixels (original space).
        x_margins:       Pixels to ignore on each side during row validation.
        sensitivity:     Percentage (1-100). 100 = strictest (threshold=0).
        max_height:      Hard ceiling on slice height. -1 = unlimited.
                         Float is treated as a fraction of *height*.
        min_height:      Hard floor on slice height. -1 = unlimited.
                         Float is treated as a fraction of *height*.
        division_factor: Downscale factor for detection (1-5).
                         Higher values are faster but less accurate.
                         Coordinates are always returned in original space.
        window:          Number of consecutive valid rows required to confirm
                         a slice position. 1 = single-row check (default).
                         Values of 5-20 are recommended for noisy content.

    Returns:
        List of Slice objects with coordinates in the original image space.
    """
    assert (height <= max_height and max_height != -1) or max_height == -1
    assert (height >= min_height and min_height != -1) or min_height == -1
    assert max_height >= min_height or max_height == -1
    assert window >= 1

    if isinstance(min_height, float):
        min_height = int(height * min_height)
    if isinstance(max_height, float):
        max_height = int(height * max_height)

    threshold = int(255 * (1 - sensitivity / 100))
    df = division_factor

    slices: List[Slice] = []
    images_len = len(images)
    cur_height_o = 0   # rolling accumulator in ORIGINAL pixel space
    start_o = 0        # current segment start in ORIGINAL pixel space
    sp = Slice()

    for idx, img in enumerate(images):
        orig_h = img.height
        orig_w = img.width

        # Downscale for analysis only -- original image is never modified
        if df > 1:
            small = img.resize(
                (orig_w // df, orig_h // df),
                PIL.Image.Resampling.NEAREST,
            )
        else:
            small = img

        _validate_margins(small.width, x_margins)

        # Build grayscale array ONCE per image (uint8 = half the memory of int16)
        arr = np.array(small.convert("L"), dtype=np.uint8)
        valid_rows = _compute_valid_rows(arr, x_margins, threshold)
        confirmed = _apply_window(valid_rows, window)

        start_s = start_o // df   # start position in small-image space
        cur_height_o += orig_h

        while cur_height_o >= height:
            # Target slice position in original space
            target_o = orig_h - max(cur_height_o - height, 1)
            target_s = target_o // df

            # Search bounds in small-image space
            lo_s = start_s + 1
            hi_s = small.height  # exclusive

            if min_height != -1:
                lo_s = max(lo_s, start_s + min_height // df)
            if max_height != -1:
                hi_s = min(hi_s, start_s + max_height // df + 1)

            found_s = _find_nearest_valid_row(confirmed, lo_s, hi_s, target_s)

            if found_s is not None:
                slice_pos_o = found_s * df
            else:
                # No confirmed row found -- fall back to a hard cut at target
                slice_pos_o = target_o

            sp.add((idx, start_o, slice_pos_o))
            sp.width = orig_w
            slices.append(sp)
            sp = Slice()

            start_o = slice_pos_o
            start_s = start_o // df
            cur_height_o = orig_h - slice_pos_o

        if 0 < cur_height_o < height:
            sp.add((idx, start_o, orig_h))
            sp.width = orig_w
            if idx == images_len - 1:
                slices.append(sp)
                break

        # Reset start tracking for the next image
        start_o = 0
        start_s = 0

    return slices
