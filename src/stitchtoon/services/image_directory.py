from __future__ import annotations

import os
from dataclasses import dataclass, field

from PIL import Image as pilImage
from psd_tools import PSDImage

from ..utils.constants import (
    FORMAT_NAME_MAPPER,
    PHOTOSHOP_FILE_TYPES,
    SUPPORTED_IMG_TYPES,
)
from ..utils.errors import ImageNotOpenedError


@dataclass
class Image:
    path: os.PathLike
    name: str
    format: str = field(default=None)
    pil: pilImage = field(default=None)

    def save(self, fp: os.PathLike, format: str = None, quality: int = 90) -> None:
        if not self.pil:
            return
        if not format:
            format = self.format

        if format in PHOTOSHOP_FILE_TYPES:
            psd_obj = PSDImage.frompil(self.pil)
            psd_obj.save(fp)
            del psd_obj
        else:
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
            raise ImageNotOpenedError("Image is not opened yet")


@dataclass
class ImageDirectory:
    path: os.PathLike
    images: list[Image]
    dirs: list[ImageDirectory] = field(default=None)
