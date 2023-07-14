from math import inf as INF
from typing import List
from typing import Union

import numpy as np
from PIL.Image import Image

from ...logger import logged
from .slice import Slice


@logged
def smart_detect(
    images: List[Image],
    height: int,
    step: int = 3,
    hmargins: int = 0,
    sensitivity: int = 100,
    max_height: Union[int, float] = -1,
    min_height: Union[int, float] = -1,
) -> List[Slice]:
    """
    Detects slicing points in the input images using neighboring pixels comparison.

    Args:
        images (List[Image]): A list of input images.
        height (int): The desired average height of each slice in pixels.
        step (int): The scan step for searching slice positions. Default is 3.
        hmargins (int): The number of pixels on the left and right sides of the image
                        to exclude from slice detection. Default is 0.
        sensitivity (int): The accuracy of slice detection in percentage. Default is 100%.
        max_height (Union[int, float]): The maximum height of each slice in pixels.
                                        If set to -1, there is no maximum limit.
                                        If set to a percentage, the maximum height is calculated
                                        as a percentage of the desired height.
                                        Otherwise, a fixed maximum height value can be provided.
        min_height (Union[int, float]): The minimum height of each slice in pixels.
                                        If set to -1, there is no minimum limit. If set to a percentage,
                                        the minimum height is calculated as a percentage of the desired height.
                                        Otherwise, a fixed minimum height value can be provided.

    Returns:
        List[Slice]: A list of Slice objects representing the detected slices.
    """

    assert (height <= max_height and max_height != -1) or max_height == -1
    assert (height >= min_height and min_height != -1) or min_height == -1
    assert max_height >= min_height or max_height == -1
    assert step > 0

    if isinstance(min_height, float):
        min_height = height * min_height
    if isinstance(max_height, float):
        max_height = height * max_height

    threshold = int(255 * (1 - (sensitivity / 100)))

    def is_valid_slice_position(gray_scale_arr, row):
        if len(gray_scale_arr[row]) - hmargins <= hmargins + 1:
            raise RuntimeError("Margins are too big")

        # FIXME: A better approach would be to calculate max and min and compare their difference to threshold
        max_px = -1
        min_px = INF
        for i in range(1, len(gray_scale_arr[row])):
            if gray_scale_arr[row][i] - gray_scale_arr[row][i - 1] > threshold:
                return False
            if max_px < gray_scale_arr[row][i]:
                max_px = gray_scale_arr[row][i]
            if min_px > gray_scale_arr[row][i]:
                min_px = gray_scale_arr[row][i]
        if max_px - min_px > threshold:
            return False
        return True

    slices = []
    images_len = len(images)
    cur_height = 0
    slice_pos = 0
    start = 0
    sp = Slice()
    can_slice = False
    for idx, img in enumerate(images):
        gray_scale_arr = None
        start = 0
        cur_height += img.height
        while cur_height >= height:
            slice_pos = img.height - max(cur_height - height, 1)
            if gray_scale_arr is None:
                gray_scale_arr = np.array(img.convert("L"), dtype=np.int16)

            up = slice_pos
            up_limit = start + 1
            down = slice_pos + step
            dn_limit = img.height - 1
            while up >= up_limit or down <= dn_limit:
                if up >= up_limit:
                    if min_height != -1 and (up - start) < min_height:
                        up = up_limit
                    else:
                        if is_valid_slice_position(gray_scale_arr, up):
                            can_slice = True
                            slice_pos = up
                            break

                if down <= dn_limit:
                    if max_height != -1 and (down - start) > max_height:
                        break
                    else:
                        if is_valid_slice_position(gray_scale_arr, down):
                            can_slice = True
                            slice_pos = down
                            break

                up -= step
                down += step

            if (max_height == -1 or (down - start <= max_height)) and not can_slice:
                slice_pos = img.height

            sp.add((idx, start, slice_pos))
            sp.width = img.width
            slices.append(sp)
            sp = Slice()

            start = slice_pos
            cur_height = img.height - slice_pos
            can_slice = False

        if cur_height < height and cur_height != 0:
            sp.add((idx, start, img.height))
            sp.width = img.width
            if idx == images_len - 1:
                slices.append(sp)
                break

    return slices
