import tempfile
from pathlib import Path

import pytest

from stitchtoon.core.image_io import ImageIO


class TestImageIO:
    def test_load_image(self, test_images_files):
        img = test_images_files[0]

        loadded_img = ImageIO.load_image(image_file=img)
        assert loadded_img is not None

    def test_load_wrong_path_image(self):
        with pytest.raises(FileNotFoundError):
            ImageIO.load_image(image_file="0239sdfamFJSlamN4")

    def test_load_archive(self, test_archive_file):
        ImageIO.load_archive(path=test_archive_file)

    def test_save_image(self, test_images_rgb):
        with tempfile.TemporaryDirectory() as tmpdirname:
            img = test_images_rgb[0]
            ImageIO.save_image(out=tmpdirname, image=img, format="jpeg", quality=80)

    def test_save_images_to_wrong_path(self, test_images_rgb):
        with pytest.raises(FileNotFoundError):
            ImageIO.save_image(
                out="jslAhsdFjD98023", image=test_images_rgb, format="jpeg"
            )

    def test_archive_images(self, test_images_rgb):
        with tempfile.TemporaryDirectory() as tmpdirname:
            ImageIO.archive_images(
                out=Path(tmpdirname) / "images.zip",
                images=test_images_rgb,
                format="jpeg",
                quality=80,
            )

    def test_archive_images_to_wrong_path(self, test_images_rgb):
        with pytest.raises(FileNotFoundError):
            ImageIO.archive_images(
                out="asdfAJKMn90233/asdhsd23f.zip",
                images=test_images_rgb,
                format="jpeg",
                quality=80,
            )

    def test_save_all_RGBA_to_RGB_auto_convert(self, test_images_rgba):
        with tempfile.TemporaryDirectory() as tmpdirname:
            ImageIO.save_all(
                out=tmpdirname,
                images=test_images_rgba,
                format="jpeg",
                convert_modes=True,
            )

    def test_save_all_RGBA_to_RGB_no_convert(self, test_images_rgba):
        with pytest.raises(OSError):
            with tempfile.TemporaryDirectory() as tmpdirname:
                ImageIO.save_all(
                    out=tmpdirname,
                    images=test_images_rgba,
                    format="jpeg",
                    convert_modes=False,
                )
