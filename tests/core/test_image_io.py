from pathlib import Path

import pytest

from stitchtoon.core.image_io import ImageIO
from PIL.Image import Image


class TestImageIO:
    def test_load_image(self, test_images_files):
        img = test_images_files[0]

        loadded_img = ImageIO.load_image(image_file=img)
        assert loadded_img is not None

    def test_load_all(self, test_images_files):
        imgs = ImageIO.load_all(files=test_images_files)

        assert len(imgs) == len(test_images_files)
        for img in imgs:
            assert isinstance(img, Image)

    def test_load_wrong_path_image(self):
        with pytest.raises(FileNotFoundError):
            ImageIO.load_image(image_file="0239sdfamFJSlamN4")

    def test_load_archive(self, test_archive_file):
        ImageIO.load_archive(path=test_archive_file)

    def test_save_image(self, test_images_rgb, tmp_path):
        img = test_images_rgb[0]
        ImageIO.save_image(out=tmp_path / "01", image=img, format="jpeg", quality=80)

    def test_save_images_to_wrong_path(self, test_images_rgb):
        with pytest.raises(FileNotFoundError):
            ImageIO.save_image(
                out="jslAhsdFjD98023", image=test_images_rgb, format="jpeg"
            )

    def test_archive_images(self, test_images_rgb, tmp_path):
        ImageIO.archive_images(
            out=Path(tmp_path) / "images.zip",
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

    def test_save_all_RGBA_to_RGB_auto_convert(self, test_images_rgba, tmp_path):
        ImageIO.save_all(
            out=tmp_path,
            images=test_images_rgba,
            format="jpeg",
            convert_modes=True,
        )

    def test_save_image_RGBA_to_RGB_no_convert(self, test_images_rgba, tmp_path):
        for img in test_images_rgba:
            if img.mode == "RGBA":
                with pytest.raises(OSError):
                    ImageIO.save_image(
                        out=tmp_path / "logo.jpeg",
                        image=img,
                        format="jpeg",
                    )
