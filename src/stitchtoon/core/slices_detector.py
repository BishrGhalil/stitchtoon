from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Tuple

from PIL.Image import Image


@dataclass
class Slice:
    height: int = 0

    # [(image_idx, start_slicing_pos, end_slicing_pos),...]
    points: List[Tuple[int, int, int]] = field(default_factory=list)

    # TODO: Replace assertions
    def add(self, point: list[int, int, int]):
        assert len(point) == 3
        assert point[2] - point[1] >= 0
        self.points.append(point)
        self.height += point[2] - point[1]


# TODO: set a minimum allowed height
class SlicesDetector:
    @classmethod
    def slice_points(
        cls, images: list[Image], avg_height: int, smart: bool = True
    ) -> list[Slice]:
        if smart:
            return cls._smart_slice_points(images, avg_height=avg_height)
        else:
            return cls._direct_slice_points(images, height=avg_height)

    @staticmethod
    def _smart_slice_points(images: list[Image], avg_height: int) -> list[Slice]:
        pass

    @staticmethod
    def _direct_slice_points(images: list[Image], height: int) -> list[Slice]:
        """detect direct slicing points of images according to height.

        Args:
            images (list[Image]): images
            height (int): height

        Returns:
            list[Slice]
        """
        cur_height = 0
        slice_points = []
        images_len = len(images)
        sp = Slice()
        for idx, img in enumerate(images):
            start = 0
            cur_height += img.height

            while cur_height >= height:
                slice_pos = img.height - (cur_height - height)
                sp.add((idx, start, slice_pos))
                slice_points.append(sp)
                cur_height = img.height - slice_pos
                start = slice_pos
                sp = Slice()

            if cur_height < height:
                sp.add((idx, start, img.height))
                if idx == images_len - 1:
                    slice_points.append(sp)

        return slice_points
