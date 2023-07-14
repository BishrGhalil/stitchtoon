from PIL.Image import Image

from ...logger import logged
from .direct_detector import direct_detect
from .slice import Slice
from .smart_detector import smart_detect


# TODO: set a minimum allowed height
class SlicesDetector:
    @classmethod
    @logged(inclass=True)
    def slice_points(
        cls, images: list[Image], height: int, smart: bool = True, **params
    ) -> list[Slice]:
        if smart:
            return smart_detect(images, height=height, **params)
        else:
            return direct_detect(images, height=height)
