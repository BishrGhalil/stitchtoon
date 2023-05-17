from __future__ import annotations

import os
from dataclasses import dataclass
from dataclasses import field

from PIL import Image as pilImage
from psd_tools import PSDImage

from ..utils.constants import PHOTOSHOP_FILE_TYPES
from ..utils.constants import SUPPORTS_TRANSPARENCY


@dataclass
class Image:
    path: os.PathLike
    name: str
    format: str = field(default=None)
    pil: pilImage = field(default=None)

    def save(self, fp: os.PathLike, format: str = None, quality: int = 90) -> None:
        if not self.pil:
            self._raise_if_not_opened()
        if not format:
            format = self.format

        if format in PHOTOSHOP_FILE_TYPES:
            psd_obj = PSDImage.frompil(self.pil)
            psd_obj.save(fp)
            del psd_obj
        else:
            if self.pil.mode == "RGBA" and format.lower() not in SUPPORTS_TRANSPARENCY:
                self.pil.load()
                background = pilImage.new("RGB", self.size, (255, 255, 255))
                background.paste(
                    self.pil, mask=self.pil.split()[3]
                )  # 3 is the alpha channel
                self.pil = background

            self.pil.save(fp, format=format, quality=quality)
            self.pil.close()

    def copy(self) -> Image:
        return Image(path=self.path, format=self.format, name=self.name, pil=self.pil)

    def topil(self) -> pilImage:
        if not self.pil:
            self.open()

        return self.pil

    def open(self) -> Image:
        if self.pil:
            return self
        self.pil = pilImage.open(self.path)
        return self

    @property
    def width(self) -> int:
        self._raise_if_not_opened()
        return self.pil.size[0]

    @property
    def height(self) -> int:
        self._raise_if_not_opened()
        return self.pil.size[1]

    @property
    def size(self) -> tuple[int, int]:
        self._raise_if_not_opened()
        return self.pil.size

    def _raise_if_not_opened(self) -> None:
        if not self.pil:
            raise Exception("Image should be opened first")


@dataclass
class ImageDirectory:
    path: os.PathLike
    images: list[Image]
    dirs: list[ImageDirectory] = field(default=None)

    def __str__(self):
        return self.path

    def __repr__(self):
        return self.path
    
    def __hash__(self):
        return hash(repr(self))
