from __future__ import annotations

import io
import os
import os.path as osp
import zipfile
from datetime import datetime as dt

from ..utils.constants import PHOTOSHOP_FILE_TYPES
from .directory_scanner import Image
from .global_logger import logFunc
from .progress import ProgressHandler
from PIL import Image as pilImage
from psd_tools import PSDImage


class ImageHandler:
    @logFunc(inclass=True)
    def filename_handler(self, filename: str, format: str) -> str:
        if not osp.splitext(filename)[1]:
            filename = f"{filename}.{format}"
        else:
            filename = f"{osp.splitext(filename)[0]}.{format}"

        return filename

    @logFunc(inclass=True)
    def load_zip(self, path):
        pass

    @logFunc(inclass=True)
    def load(
        self, images: list[Image], progress=ProgressHandler(), increament=0
    ) -> list[Image]:
        """Loads all image files into a list of PIL image objects."""
        images_len = len(images)
        for idx, image in enumerate(images, 1):
            if image.format not in PHOTOSHOP_FILE_TYPES:
                image.pil = pilImage.open(image.path)
            else:
                image.pil = PSDImage.open(image.path).topil()
            progress.update(progress.value + increament, f"Loading {idx}/{images_len}")
        return images

    @logFunc(inclass=True)
    def save_archive(
        self,
        output,
        images: list[pilImage.Image],
        img_format: str,
        quality=100,
        progress=ProgressHandler(),
        increament=0,
    ):
        if img_format in PHOTOSHOP_FILE_TYPES:
            # FIXMEE: support archiving psd files
            raise Exception("Can't make PSD archive")

        output_suffix = "" if osp.splitext(output)[1] == ".zip" else ".zip"
        output += output_suffix

        zf = zipfile.ZipFile(output, mode="w")
        images_len = len(images)
        for idx, image in enumerate(images, 1):
            img_byte_arr = io.BytesIO()
            image.pil.save(img_byte_arr, img_format, quality=quality)
            img_byte_arr = img_byte_arr.getvalue()
            zf.writestr(self.filename_handler(f"{idx:02}", img_format), img_byte_arr)
            progress.update(progress.value + increament, f"Archive {idx}/{images_len}")

    def save_all(
        self,
        output,
        images: list[Image],
        format: str = "png",
        as_archive: bool = False,
        quality=100,
        progress=ProgressHandler(),
        increament=0,
    ) -> str:
        if as_archive:
            if osp.isdir(output):
                output = osp.join(output, dt.now().strftime("%d%m%Y_%H%M%S"))
            os.makedirs(osp.dirname(output), exist_ok=True)
            self.save_archive(output, images, format, quality, progress, increament)
        else:
            os.makedirs(output, exist_ok=True)
            images_len = len(images)
            for idx, img in enumerate(images, 1):
                filename = self.filename_handler(f"{idx:02}", format)
                img.save(osp.join(output, filename), format, quality)
                progress.update(progress.value + increament, f"Saving {idx}/{images_len}")
        return output
