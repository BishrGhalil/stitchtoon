import functools
import io
import os.path as osp
from os import makedirs
import zipfile
from io import BytesIO

from PIL import Image
from psd_tools import PSDImage

from ..const import FORMATS, PS_FORMATS, _PathType, SUPPORTS_TRANSPARENCY
from ..exc import UnSupportedFormatError


def validate_format(
    func=None, *, format_arg: str = "format", filename_arg: _PathType = None
):
    def decorator_validate_format(func):
        @functools.wraps(func)
        def wrapper_validate_format(*args, **kwargs):
            format = None
            format = kwargs.get(format_arg)
            if format is None and filename_arg is None:
                raise Exception(
                    f"{format_arg} is not a valid argument for function '{func.__name__}', or has not been passed as keyword argument"
                )
            elif filename_arg and kwargs.get(filename_arg) is None:
                raise Exception(
                    f"{filename_arg} is not a valid argument for function '{func.__name__}', or has not been passed as keyword argument"
                )
            elif filename_arg:
                filename = kwargs.get(filename_arg)
                format = osp.splitext(filename)[1]
                format = format.strip(".")
            if format.upper() not in FORMATS:
                raise UnSupportedFormatError(f"file format {format} is not supported.")
            return func(*args, **kwargs)

        return wrapper_validate_format

    if func is None:
        return decorator_validate_format
    return decorator_validate_format(func)


def validate_path(path_arg, validate_parents=False):
    def decorator_validate_path(func):
        @functools.wraps(func)
        def wrapper_validate_path(*args, **kwargs):
            if args:
                raise Exception(
                    f"function '{func.__name__}' takes keyword arguments only"
                )
            path = kwargs.get(path_arg)
            if path is None:
                raise Exception(
                    f"{path_arg} is not a valid argument for function '{func.__name__}'"
                )
            if validate_parents:
                path = osp.dirname(path)
            if not osp.lexists(path):
                raise FileNotFoundError(f"{kwargs.get(path_arg, '')} does not exists.")
            return func(*args, **kwargs)

        return wrapper_validate_path

    return decorator_validate_path


class ImageHandler:
    @staticmethod
    @validate_format
    def convert_format(*, image: Image.Image, format: str) -> Image.Image:
        """in memory convert image format.

        Args:
            image (PIL.Image.Image): image to be converted
            format (str): format to convert image format to

        Returns:
            PIL.Image.Image: New image specified format

        Raises:
            UnSupportedFormatError: if format is not supported. see stitchtoon.const.FORMATS.
        """
        membuf = BytesIO()
        image.save(membuf, format=format)
        converted_image = Image.open(membuf)
        return converted_image

    @staticmethod
    @validate_path("image_file")
    @validate_format(filename_arg="image_file")
    def load_image(*, image_file: _PathType) -> Image.Image:
        """load image file into PIL.Image.Image object.

        Args:
            image_file (Union[str, Path]): image_file

        Returns:
            PIL.Image.Image

        Raises:
            FileNotFoundError: if 'image_file' does not exists.
        """

        file_ext = osp.splitext(image_file)[1].strip(".")

        img = None

        if file_ext in PS_FORMATS:
            psd = PSDImage.open(image_file)
            img = psd.composite()
            img.format = "psd"
        else:
            img = Image.open(image_file)

        return img

    @staticmethod
    @validate_format
    @validate_path("out", validate_parents=True)
    def save_image(*, out: _PathType, image: list[Image], format: str, **params) -> None:
        """save image.

        Args:
            out (_PathType): output path with image file name, or output path directory.
            image (list[PIL.Image.Image]): image
            format (str): format to save image in.
            params: parameters to Pillow image writer.

        Raises:
            FileNotFoundError: if out directory or one of it's parents does not exists.
            UnSupportedFormatError: if format is not supported. see stitchtoon.const.FORMATS.
            OSError: when trying to write RGBA as RGB.
        """
        if not osp.splitext(out)[1]:
            out = osp.join(out, image.filename)
        if format in PS_FORMATS:
            psd = PSDImage.frompil(image)
            psd.save(out)
        else:
            image.save(out, format=format, **params)

    @staticmethod
    @validate_format
    @validate_path("out", validate_parents=True)
    def archive_images(
        *,
        out: _PathType,
        images: list[Image.Image],
        format: str,
        mode: str = "w",
        **params,
    ) -> None:
        """save images into an archive file.

        Args:
            out (_PathType): output file name, or output directory (file name will be a time stamp).
            images (list[Image.Image]): list of images to archive.
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
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format, **params)
            img_byte_arr = img_byte_arr.getvalue()
            zf.writestr(
                ImageHandler.filename_format_handler(f"{idx:03}", format), img_byte_arr
            )
        zf.close()

    @staticmethod
    @validate_format
    def save_all(
        *,
        out: _PathType,
        images: list[Image.Image],
        format: str,
        archive=False,
        convert_modes=True,
        make_dirs=False,
        **params,
    ) -> None:
        """save all images to 'out'.

        Args:
            out (_PathType): directory path if archive=False. Otherwise see ImageHandler.archive_images for more info.
            images (list[PIL.Image.Image]): list of images to save.
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

        if convert_modes:
            if format in SUPPORTS_TRANSPARENCY:
                mode = "RGBA"
            else:
                mode = "RGB"
            cnvrtd_imgs = ImageHandler.convert_images_mode(images, mode)
            for img in images:
                img.close()
            images = cnvrtd_imgs

        if archive:
            ImageHandler.archive_images(out=out, images=images, format=format, **params)
        else:
            for idx, img in enumerate(images, 1):
                outpath = osp.join(
                    out, ImageHandler.filename_format_handler(f"{idx:03}", format)
                )
                ImageHandler.save_image(out=outpath, image=img, format=format, **params)

    @staticmethod
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

    @staticmethod
    def convert_images_mode(
        images: list[Image.Image],
        mode: str,
        fill_color: tuple[int, int, int] = (255, 255, 255),
    ) -> list[Image.Image]:
        """convert images mode.

        Args:
            images (list[PIL.Image.Image]): images
            mode (str): (RGB, RGBA),
            fill_color (tuple[int, int, int]): color to fill transparent areas. Defaults to (255,255,255).

        Returns:
            list[Image.Image]: images with new mode.
        """
        cnvrtd_imgs = []
        for img in images:
            cnvrtd_img = Image.new(mode, img.size, fill_color)
            cnvrtd_img.filename = img.filename
            mask = None
            if mode.upper() == "RGB":
                channels = img.split()
                mask = channels[3] if len(channels) > 3 else mask
            cnvrtd_img.paste(img, mask=mask)
            cnvrtd_imgs.append(cnvrtd_img)

        return cnvrtd_imgs
