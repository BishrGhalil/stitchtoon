import pytest
import random
from pathlib import Path

from stitchtoon import scanimgdir, walkimgdir, ImageDirectory, Image, is_supported_img
from stitchtoon.utils.constants import SUPPORTED_IMG_TYPES

SCAN_DIR = Path(__file__).parent / "data"


class TestIsSupportedImage:
    def test_not_supported_image(self):
        assert not is_supported_img(filename=str(random.randbytes(50)))

    def test_supported_image(self):
        for img_t in SUPPORTED_IMG_TYPES:
            assert is_supported_img(format=img_t)


class TestScanImageDir:
    def test_scan_invalid_path(self):
        with pytest.raises(FileNotFoundError):
            scanimgdir(str(random.randbytes(20)))

    def test_scan(self):
        res = scanimgdir(SCAN_DIR)
        assert len(res) == 1
        assert len(res[0].images) == 5


class TestWalkImageDir:
    def test_scan_invalid_path(self):
        with pytest.raises(FileNotFoundError):
            walkimgdir(str(random.randbytes(20)))

    def test_scan(self):
        res = walkimgdir(SCAN_DIR.parent)
        assert len(res) == 1
        assert len(res[0].images) == 5
