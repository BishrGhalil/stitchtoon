from __future__ import annotations

import io
import os
import os.path as osp
import zipfile
from datetime import datetime as dt

from PIL import Image as pilImage
from psd_tools import PSDImage

from ..utils.constants import PHOTOSHOP_FILE_TYPES
from .global_logger import logFunc
from .image_directory import Image
from .progressbar import ProgressHandler


class ImageHandler:
    @logFunc(inclass=True)
    def filename_handler(self, filename: str, format: str) -> str:
        if not osp.splitext(filename)[1]:
            filename = f"{filename}.{format}"
        else:
            filename = f"{osp.splitext(filename)[0]}.{format}"

        return filename

    # TODOO: Load images from ao zip/cbz archive.
    @logFunc(inclass=True)
    def load_zip(
        self,
        path: os.PathLike,
        progress: ProgressHandler = ProgressHandler(),
        increament: int = 0,
    ) -> list[Image]:
        pass

    @logFunc(inclass=True)
    def load(
        self,
        images: list[Image],
        progress: ProgressHandler = ProgressHandler(),
        increament: int = 0,
    ) -> list[Image]:
        """Loads all image files into a list of PIL image objects."""
        images_len = len(images)
        for idx, image in enumerate(images, 1):
            if image.format not in PHOTOSHOP_FILE_TYPES:
                image.pil = pilImage.open(image.path)
            else:
                psd = PSDImage.open(image.path)
                image.pil = psd.topil()
                del psd
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
    ) -> os.PathLike:
        if img_format in PHOTOSHOP_FILE_TYPES:
            # FIXMEE: support archiving psd files
            raise Exception("Can't make PSD archive")

        zf = zipfile.ZipFile(output, mode="w")
        images_len = len(images)
        for idx, image in enumerate(images, 1):
            img_byte_arr = io.BytesIO()
            image.pil.save(img_byte_arr, img_format, quality=quality)
            img_byte_arr = img_byte_arr.getvalue()
            zf.writestr(self.filename_handler(f"{idx:02}", img_format), img_byte_arr)
            progress.update(progress.value + increament, f"Archive {idx}/{images_len}")

        return output

    @logFunc(inclass=True)
    def save_all(
        self,
        output: os.PathLike,
        images: list[Image],
        format: str = "png",
        as_archive: bool = False,
        quality: int = 100,
        progress=ProgressHandler(),
        increament: int = 0,
    ) -> os.PathLike:
        progress.update(progress.value, "Saving, Please wait...")
        if as_archive:
            os.makedirs(osp.dirname(output), exist_ok=True)
            self.save_archive(output, images, format, quality, progress, increament)
        else:
            os.makedirs(output, exist_ok=True)
            images_len = len(images)
            for idx, img in enumerate(images, 1):
                filename = self.filename_handler(f"{idx:02}", format)
                img.save(osp.join(output, filename), format, quality)
                progress.update(
                    progress.value + increament, f"Saving {idx}/{images_len}"
                )
        return output
