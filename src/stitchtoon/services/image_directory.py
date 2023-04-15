from __future__ import annotations

import os
from dataclasses import dataclass
from dataclasses import field

from ..utils.constants import FORMAT_MAPPER
from ..utils.constants import PHOTOSHOP_FILE_TYPES
from ..utils.constants import SUPPORTED_IMG_TYPES
from PIL import Image as pilImage
from psd_tools import PSDImage


@dataclass
class Image:
    path: os.PathLike
    name: str
    format: str = field(default=None)
    pil: pilImage = field(default=None)

    def save(self, fp: os.PathLike, format: str = None, quality: int = 90):
        if not self.pil:
            return
        if not format:
            format = self.format

        if format in PHOTOSHOP_FILE_TYPES:
            psd_obj = PSDImage.frompil(self.pil)
            psd_obj.save(fp)
        else:
            self.pil.save(fp, format=format, quality=quality)
            self.pil.close()

    def copy(self):
        return Image(path=self.path, format=self.format, name=self.name, pil=self.pil)


@dataclass
class ImageDirectory:
    path: os.PathLike
    images: list[Image]
    dirs: list[ImageDirectory] = field(default=())
