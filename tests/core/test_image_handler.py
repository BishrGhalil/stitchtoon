import tempfile
from pathlib import Path

import pytest

from stitchtoon.core.image_handler import ImageHandler
from stitchtoon.exc import UnSupportedFormatError


class TestImageHandler:
    def test_convert_format(self, test_images):
        convert_to = "tiff"
        img = test_images[0]
        converted_image = ImageHandler.convert_format(image=img, format=convert_to)
        assert converted_image.format.lower() == convert_to

    def test_convert_unsupported_format(self, test_images):
        convert_to = "pdf"
        img = test_images[0]

        with pytest.raises(UnSupportedFormatError):
            img = ImageHandler.convert_format(image=img, format=convert_to)

    def test_load_image(self, test_images_files):
        img = test_images_files[0]

        loadded_img = ImageHandler.load_image(image_file=img)
        assert loadded_img is not None

    def test_load_wrong_path_image(self):
        with pytest.raises(FileNotFoundError):
            ImageHandler.load_image(image_file="0239sdfamFJSlamN4")

    def test_load_archive(self, test_archive_file):
        ImageHandler.load_archive(path=test_archive_file)

    def test_save_image(self, test_images_rgb):
        with tempfile.TemporaryDirectory() as tmpdirname:
            img = test_images_rgb[0]
            ImageHandler.save_image(
                out=tmpdirname, image=img, format="jpeg", quality=80
            )

    def test_save_images_to_wrong_path(self, test_images_rgb):
        with pytest.raises(FileNotFoundError):
            ImageHandler.save_image(
                out="jslAhsdFjD98023", image=test_images_rgb, format="jpeg"
            )

    def test_archive_images(self, test_images_rgb):
        with tempfile.TemporaryDirectory() as tmpdirname:
            ImageHandler.archive_images(
                out=Path(tmpdirname) / "images.zip",
                images=test_images_rgb,
                format="jpeg",
                quality=80,
            )

    def test_archive_images_to_wrong_path(self, test_images_rgb):
        with pytest.raises(FileNotFoundError):
            ImageHandler.archive_images(
                out="asdfAJKMn90233/asdhsd23f.zip",
                images=test_images_rgb,
                format="jpeg",
                quality=80,
            )

    def test_save_all_RGBA_to_RGB_auto_convert(self, test_images_rgba):
        with tempfile.TemporaryDirectory() as tmpdirname:
            ImageHandler.save_all(
                out=tmpdirname,
                images=test_images_rgba,
                format="jpeg",
                convert_modes=True,
            )

    def test_save_all_RGBA_to_RGB_no_convert(self, test_images_rgba):
        with pytest.raises(OSError):
            with tempfile.TemporaryDirectory() as tmpdirname:
                ImageHandler.save_all(
                    out=tmpdirname,
                    images=test_images_rgba,
                    format="jpeg",
                    convert_modes=False,
                )
