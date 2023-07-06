from stitchtoon.core.slices_detectors.slices_detector import SlicesDetector
from stitchtoon.core.stitcher import Stitcher

class TestStitcher:
    def test_stitcher(self, test_images):
        slices = SlicesDetector.slice_points(test_images, height=2000, smart=False)
        images = Stitcher.stitch(test_images, slices)

        assert len(images) == len(slices)
        for i in range(len(slices)):
            assert images[i].height == slices[i].height
