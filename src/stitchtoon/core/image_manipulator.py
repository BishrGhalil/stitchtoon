from io import BytesIO

import PIL.Image
from PIL.Image import Image

from ..decorators import validate_format
from ..logger import logged


class ImageManipulator:
    @staticmethod
    @validate_format
    @logged(inclass=True)
    def convert_format(*, image: Image, format: str, **params) -> Image:
        """in memory convert image format.

        Args:
            image (Image): image to be converted
            format (str): format to convert image format to
            params: parameters for Pillow image writer

        Returns:
            Image: New image specified format

        Raises:
            UnSupportedFormatError: if format is not supported. see stitchtoon.const.FORMATS.
        """
        membuf = BytesIO()
        image.save(membuf, format=format, **params)
        converted_image = PIL.Image.open(membuf)
        return converted_image

    @staticmethod
    @logged(inclass=True)
    def convert_mode(
        image: list[Image],
        mode: str,
        fill_color: tuple[int, int, int] = (255, 255, 255),
    ) -> Image:
        """convert image mode.

        Args:
            image (Image): image to convert
            mode (str): (RGB, RGBA),
            fill_color (tuple[int, int, int]): color to fill transparent areas. Defaults to (255,255,255).

        Returns:
            Image: new image with mode (mode).
        """
        cnvrtd_img = PIL.Image.new(mode, image.size, fill_color)
        if hasattr(image, "filename"):
            cnvrtd_img.filename = image.filename
        mask = None
        if mode.upper() == "RGB":
            # TODOO: replace with getchannel
            channels = image.split()
            mask = channels[3] if len(channels) > 3 else mask
        cnvrtd_img.paste(image, mask=mask)
        return cnvrtd_img

    @classmethod
    @logged(inclass=True)
    def resize_all_width(cls, images: Image, value=None):
        if value is None:
            return cls._resize_all_width_auto(images)
        else:
            return cls._resize_all_width_fixed(images, value)

    @classmethod
    @logged(inclass=True)
    def _resize_all_width_fixed(cls, images: Image, value: int) -> list[Image]:
        resized_imgs = []
        for image in images:
            resized_img = cls.resize(image, width=value)
            resized_imgs.append(resized_img)

        return resized_imgs

    @classmethod
    @logged(inclass=True)
    def _resize_all_width_auto(cls, images: Image) -> list[Image]:
        pass

    @classmethod
    @logged(inclass=True)
    def resize(cls, img, width=None, height=None, respect_ratio=True):
        if width is None and height is None:
            raise RuntimeError("at least one of (width, height) should not be None")
        if (width is None or height is None) and not respect_ratio:
            raise RuntimeError(
                "both width and height should not be provided when respect_ratio is False."
            )

        img_ratio = float(img.height / img.width)
        if width is None:
            if img.height == height:
                return img
            width = int(img_ratio * height)
        elif height is None:
            if img.width == width:
                return img
            height = int(img_ratio * width)
        if height > 0 and width > 0:
            img = img.resize((width, height), PIL.Image.Resampling.LANCZOS)
        return img
