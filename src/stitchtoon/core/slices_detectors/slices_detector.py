from enum import StrEnum

from PIL.Image import Image

from ...logger import logged
from .auto_detect import auto_detect
from .direct_detect import direct_detect
from .pixel_detect import pixel_detect
from .slice import Slice


class DetectionMethod(StrEnum):
    AUTO = "auto"
    PIXEL = "pixel"
    DIRECT = "direct"


# TODO: set a minimum allowed height
class SlicesDetector:
    @classmethod
    @logged(inclass=True)
    def slice_points(
        cls,
        images: list[Image],
        method: DetectionMethod = DetectionMethod.PIXEL,
        height: int | None = None,
        **params,
    ) -> list[Slice]:
        if method == DetectionMethod.PIXEL:
            return pixel_detect(images, height=height, **params)
        elif method == DetectionMethod.AUTO:
            return auto_detect(images)
        elif method == DetectionMethod.DIRECT:
            return direct_detect(images, height=height)
        else:
            raise ValueError(f"Unknown detection method {method}")
