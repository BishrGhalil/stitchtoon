import multiprocessing
import os.path as osp
import zipfile
from io import BytesIO
from os import makedirs
from typing import Optional

import PIL.Image
from PIL.Image import Image
from psd_tools import PSDImage
from psd_tools.constants import ChannelID

from ..const import FORMATS
from ..const import PS_FORMATS
from ..const import SUPPORTS_TRANSPARENCY
from ..const import _PathType
from ..decorators import validate_format
from ..decorators import validate_path
from ..logger import logged
from .image_manipulator import ImageManipulator


class ImageIO:
    error_callback = lambda e: print(
        f"Exception raised in ImageIO.save_image: {type(e).__name__}: {str(e)}"
    )

    @staticmethod
    @validate_path("image_file")
    @validate_format(filename_arg="image_file")
    @logged(inclass=True)
    def load_image(*, image_file: _PathType) -> Image:
        """load image file into Image object.

        Args:
            image_file (Union[str, Path]): image_file

        Returns:
            lazy loaded Image if not a Photoshop format, else a loaded image.

        Raises:
            FileNotFoundError: if 'image_file' does not exists.
        """

        file_ext = osp.splitext(image_file)[1].strip(".")

        img = None

        if file_ext.upper() in PS_FORMATS:
            psd = PSDImage.open(image_file)
            img = psd.composite()
            img.format = "psd"
            if psd.channels >= 4:
                # the alpha (channel) in photoshop
                alpha = psd.topil(ChannelID.TRANSPARENCY_MASK)
                img.putalpha(alpha)
        else:
            img = PIL.Image.open(image_file)

        return img

    @staticmethod
    @validate_path("path")
    @logged(inclass=True)
    def load_archive(path: _PathType) -> Optional[list[Image]]:
        """load images from an archive.

        Raises:
            FileNotFoundError: if 'path' does not exists.
            ValueError: see zipfile.ZipFile.testzip and zipfile.ZipFile.read for more info.
        """
        zf = zipfile.ZipFile(path, "r")
        zf.testzip()
        zf_files = zf.namelist()

        img_files = []
        for file in zf_files:
            if osp.splitext(file)[1].strip(".").upper() in FORMATS:
                img_files.append(file)
        if not img_files:
            return None

        imgs = []
        for img_file in img_files:
            data = zf.read(img_file)
            membuf = BytesIO(data)
            img = PIL.Image.open(membuf)
            imgs.append(img)

        return imgs

    @staticmethod
    @logged(inclass=True)
    def load_all(*, files: list[_PathType]):
        pool = multiprocessing.Pool()
        async_res = [
            pool.apply_async(
                ImageIO.load_image,
                kwds={"image_file": imf},
                error_callback=ImageIO.error_callback,
            )
            for imf in files
        ]

        pool.close()
        pool.join()

        return [ar.get(0.5) for ar in async_res]

    @staticmethod
    @validate_format
    @validate_path("out", validate_parents=True)
    @logged(inclass=True)
    def save_image(*, out: _PathType, image: Image, format: str, **params) -> None:
        """save image.

        Args:
            out (_PathType): output path with image file name, or output path directory.
            image (Image): image to be saved.
            format (str): format to save image in.
            params: parameters to Pillow image writer.

        Raises:
            FileNotFoundError: if out directory or one of it's parents does not exists.
            UnSupportedFormatError: if format is not supported. see stitchtoon.const.FORMATS.
            OSError: when trying to write RGBA as RGB.
        """
        if not osp.splitext(out)[1]:
            out = osp.join(out, image.filename)
        if format.upper() in PS_FORMATS:
            psd = PSDImage.frompil(image)
            psd.save(out)
        else:
            image.save(out, format=format, **params)

    @staticmethod
    @validate_format
    @validate_path("out", validate_parents=True)
    @logged(inclass=True)
    def archive_images(
        *,
        out: _PathType,
        images: list[Image],
        format: str,
        mode: str = "w",
        **params,
    ) -> None:
        """save images into an archive file.

        Args:
            out (_PathType): output file name, or output directory (file name will be a time stamp).
            images (list[Image]): list of images to archive.
            format (str): format to save images in.
            mode (str): archive creation mode. Defaults to 'w'. see zipfile.ZipFile for more info.
            params: parameters for Pillow image writer.

        Raises:
            FileNotFoundError: if out directory or one of it's parents does not exists.
            UnSupportedFormatError: if format is not supported. see stitchtoon.const.FORMATS.
            OSError: when trying to write RGBA as RGB.
        """
        if format in PS_FORMATS:
            # TODOO: add support for making psd/psb archives
            raise Exception("Can't make PSD/PSB archive.")

        zf = zipfile.ZipFile(out, mode)

        for idx, image in enumerate(images, 1):
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format, **params)
            img_byte_arr = img_byte_arr.getvalue()
            zf.writestr(
                ImageIO.filename_format_handler(f"{idx:03}", format), img_byte_arr
            )
        zf.close()

    @staticmethod
    @validate_format
    @logged(inclass=True)
    def save_all(
        *,
        out: _PathType,
        images: list[Image],
        format: str,
        archive=False,
        convert_modes=True,
        make_dirs=False,
        **params,
    ) -> None:
        """save all images to 'out'.

        Args:
            out (_PathType): directory path if archive=False. Otherwise see ImageIO.archive_images for more info.
            images (list[Image]): list of images to save.
            format (str): format to save to images in.
            archive: if true, images will be saved into an archive. Defaults to False.
            convert_modes: if true, images modes will be auto converted according to format. Defaults to True
            make_dirs: make 'out' and it's parents directories if not exists. Defaults to False
            params: parameters for Pillow image writer.

        Raises:
            UnSupportedFormatError: when format is not supported. see stitchtoon.const.FORMATS.
        """
        if make_dirs:
            outdirs = osp.dirname(out) if out.splitext()[1] else out
            makedirs(outdirs, exist_ok=True)

        # TODO: only convert incompatible images
        if convert_modes:
            if format in SUPPORTS_TRANSPARENCY:
                mode = "RGBA"
            else:
                mode = "RGB"
            cnvrtd_imgs = [ImageManipulator.convert_mode(img, mode) for img in images]
            del images
            images = cnvrtd_imgs

        if archive:
            ImageIO.archive_images(out=out, images=images, format=format, **params)
        else:
            pool = multiprocessing.Pool()
            for idx, img in enumerate(images, 1):
                outpath = osp.join(
                    out, ImageIO.filename_format_handler(f"{idx:03}", format)
                )
                pool.apply_async(
                    ImageIO.save_image,
                    kwds={"out": outpath, "image": img, "format": format, **params},
                    error_callback=ImageIO.error_callback,
                )

            pool.close()
            pool.join()

    @staticmethod
    @logged(inclass=True)
    def filename_format_handler(filename: str, ext: str) -> str:
        """add or change filename extension.

        Args:
            filename (str): filename
            ext (str): extension.

        Returns:
            str: filename with new extension.
        """
        if not osp.splitext(filename)[1]:
            filename = f"{filename}.{ext}"
        else:
            filename = f"{osp.splitext(filename)[0]}.{ext}"

        return filename
