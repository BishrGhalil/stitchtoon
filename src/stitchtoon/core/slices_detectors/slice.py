from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Tuple


# TODO: Change points from a tuple to a class
@dataclass
class Slice:
    _height: int = 0
    _width: int = 0

    # [(image_idx, start_slicing_pos, end_slicing_pos),...]
    points: List[Tuple[int, int, int]] = field(default_factory=list)

    # TODO: Replace assertions
    def add(self, point: list[int, int, int]):
        assert len(point) == 3
        assert point[2] - point[1] >= 0
        self.points.append(point)
        self._height += point[2] - point[1]

    @property
    def height(self) -> int:
        return self._height

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, value: int):
        if value > self.width:
            self._width = value

    @property
    def size(self) -> tuple[int, int]:
        return (self.width, self.height)
