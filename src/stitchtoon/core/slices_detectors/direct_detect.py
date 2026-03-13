from PIL.Image import Image

from ...logger import logged
from .slice import Slice


@logged
def direct_detect(images: list[Image], height: int) -> list[Slice]:
    """detect direct slicing points of images according to height.

    Args:
        images (list[Image]): images
        height (int): height

    Returns:
        list[Slice]
    """
    cur_height = 0
    slices = []
    images_len = len(images)
    sp = Slice()
    for idx, img in enumerate(images):
        start = 0
        cur_height += img.height

        while cur_height >= height:
            slice_pos = img.height - (cur_height - height)
            sp.add((idx, start, slice_pos))
            sp.width = img.width
            slices.append(sp)
            cur_height = img.height - slice_pos
            start = slice_pos
            sp = Slice()

        if cur_height < height:
            sp.add((idx, start, img.height))
            sp.width = img.width
            if idx == images_len - 1:
                slices.append(sp)

    return slices
