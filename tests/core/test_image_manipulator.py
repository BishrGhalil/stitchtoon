import pytest

from stitchtoon.core.image_manipulator import ImageManipulator
from stitchtoon.exc import UnSupportedFormatError


class TestImageManipulator:
    def test_convert_format(self, test_images):
        convert_to = "tiff"
        img = test_images[0]
        converted_image = ImageManipulator.convert_format(image=img, format=convert_to)
        assert converted_image.format.lower() == convert_to

    def test_convert_unsupported_format(self, test_images):
        convert_to = "pdf"
        img = test_images[0]

        with pytest.raises(UnSupportedFormatError):
            img = ImageManipulator.convert_format(image=img, format=convert_to)

    def test_convert_image_mode(self, test_images_rgb, test_images_rgba):
        rgb = test_images_rgb[0]
        rgba = test_images_rgba[0]

        assert ImageManipulator.convert_mode(rgb, "RGBA").mode == "RGBA"
        assert ImageManipulator.convert_mode(rgba, "RGB").mode == "RGB"

    def test_resize_all_width_fixed_enforce(self, test_images):
        old_width = [im.width for im in test_images]
        new_width = old_width[0] // 2
        new_imgs = ImageManipulator.resize_all_width(test_images, new_width)
        for img in new_imgs:
            assert img.width == new_width


    def test_resize_all_width_auto(self, test_images):
        ImageManipulator.resize_all_width(test_images)
