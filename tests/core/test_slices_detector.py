import random

import PIL.Image
import pytest

from stitchtoon.core.slices_detectors.slices_detector import SlicesDetector, DetectionMethod


class TestSlicesDetector:
    def test_stupid_slice_points(self, test_images):
        for i in range(3):
            height = random.randint(100, 50_000)
            slice_points = SlicesDetector.slice_points(
                images=test_images, height=height, method=DetectionMethod.DIRECT
            )

            imgs = set()
            total_slice_points_height = sum([sp.height for sp in slice_points])
            for sp in slice_points:
                for p in sp.points:
                    if p[0] not in imgs:
                        imgs.add(p[0])

            assert len(imgs) == len(test_images)

            for sp in slice_points[:-1]:
                assert sp.height == height

            total_images_height = sum(img.height for img in test_images)
            assert total_slice_points_height == total_images_height

    def test_pixel_slice_points(self, test_images):
        i = 0
        heights = (504, 2031, 259, 989)
        while i < 10:
            if i < len(heights):
                height = heights[i]
            else:
                height = random.randint(200, 50_000)

            min_height = random.randint(1, height)
            max_height = random.randint(height, 2 * height)
            slice_points = SlicesDetector.slice_points(
                images=test_images,
                height=height,
                method=DetectionMethod.PIXEL,
                max_height=max_height,
                min_height=min_height,
            )
            imgs = set()
            total_slice_points_height = sum([sp.height for sp in slice_points])
            for sp in slice_points:
                for p in sp.points:
                    if p[0] not in imgs:
                        imgs.add(p[0])

            assert len(imgs) == len(test_images)

            for sp in slice_points[:-1]:
                assert min_height <= sp.height

            total_images_height = sum(img.height for img in test_images)
            assert total_slice_points_height == total_images_height

            i += 1

    def test_pixel_slice_points_no_min_max(self, test_images):
        for i in range(3):
            min_height = -1
            max_height = -1
            height = random.randint(200, 50_000)
            #  height = 504, 2031, 259, 989
            slice_points = SlicesDetector.slice_points(
                images=test_images,
                height=height,
                method=DetectionMethod.PIXEL,
                max_height=max_height,
                min_height=min_height,
            )
            imgs = set()
            total_slice_points_height = sum([sp.height for sp in slice_points])
            for sp in slice_points:
                for p in sp.points:
                    if p[0] not in imgs:
                        imgs.add(p[0])

            assert len(imgs) == len(test_images)

            total_images_height = sum(img.height for img in test_images)
            assert total_slice_points_height == total_images_height

    def test_auto_slice_points(self, test_images):
        with pytest.raises(NotImplementedError):
            slice_points = SlicesDetector.slice_points(
                images=test_images, method=DetectionMethod.AUTO
            )

    # ------------------------------------------------------------------
    # division_factor coordinate regression tests
    # ------------------------------------------------------------------

    def test_pixel_division_factor_total_height(self, test_images):
        """Coordinates must be in original space regardless of division_factor.

        Previously, slice coordinates were stored in the downscaled space,
        causing the total slice height to be 1/df of the actual image height.
        """
        total_images_height = sum(img.height for img in test_images)
        for df in (1, 2, 4):
            slices = SlicesDetector.slice_points(
                images=test_images,
                height=500,
                method=DetectionMethod.PIXEL,
                division_factor=df,
            )
            total_slices_height = sum(sp.height for sp in slices)
            assert total_slices_height == total_images_height, (
                f"division_factor={df}: coordinate mismatch "
                f"({total_slices_height} != {total_images_height})"
            )

    # ------------------------------------------------------------------
    # window parameter tests
    # ------------------------------------------------------------------

    def test_pixel_window_total_height(self, test_images):
        """Total height coverage must be preserved for any window size."""
        total_images_height = sum(img.height for img in test_images)
        for window in (1, 3, 10):
            slices = SlicesDetector.slice_points(
                images=test_images,
                height=500,
                method=DetectionMethod.PIXEL,
                window=window,
            )
            total_slices_height = sum(sp.height for sp in slices)
            assert total_slices_height == total_images_height, (
                f"window={window}: total height mismatch"
            )

    def test_pixel_window_solid_image(self):
        """On a solid-white image every row is valid, so any window size works."""
        img = PIL.Image.new("RGB", (800, 3_000), (255, 255, 255))
        total_h = img.height
        for window in (1, 10, 50):
            slices = SlicesDetector.slice_points(
                images=[img],
                height=1_000,
                method=DetectionMethod.PIXEL,
                window=window,
                sensitivity=100,
            )
            assert sum(sp.height for sp in slices) == total_h, (
                f"window={window}: coverage mismatch on solid image"
            )
