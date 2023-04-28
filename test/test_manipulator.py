import pytest

from pathlib import Path
from stitchtoon import scan, Image
from stitchtoon.services import ImageManipulator
from stitchtoon.utils.constants import DETECTION_TYPE, WIDTH_ENFORCEMENT

SCAN_DIR = Path(__file__).parent / "data"
SPLIT_HEIGHT = 100
FIXED_WIDTH = 100


@pytest.fixture
def images_fixture() -> list[Image]:
    res = scan(SCAN_DIR)
    scan_images = res[0].images
    images = []
    for image in scan_images:
        images.append(image.open())

    return images


class TestManipulator:
    def test_resize_fixed_width(self, images_fixture):
        resized = ImageManipulator.resize(
            images_fixture, WIDTH_ENFORCEMENT.FIXED.value, FIXED_WIDTH
        )
        assert resized[0].width == FIXED_WIDTH

    def test_resize_auto_width(self, images_fixture):
        resized = ImageManipulator.resize(images_fixture, WIDTH_ENFORCEMENT.AUTO.value)
        assert resized[1].width == resized[0].width

    def test_combine(self, images_fixture):
        combined = ImageManipulator.combine(images_fixture)
        assert combined.height == sum(img.height for img in images_fixture)
