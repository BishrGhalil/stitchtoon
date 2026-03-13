from PIL.Image import Image

from ...logger import logged
from .slice import Slice


@logged
def auto_detect(images: list[Image]) -> list[Slice]:
    """auto-detect slicing points of images.

    Args:
        images (list[Image]): images

    Returns:
        list[Slice]
    """
    raise NotImplementedError
