import random

from stitchtoon.core.slices_detectors.slices_detector import SlicesDetector


class TestSlicesDetector:
    def test_stupid_slice_points(self, test_images):
        for i in range(10):
            height = random.randint(100, 50_000)
            slice_points = SlicesDetector.slice_points(
                images=test_images, height=height, smart=False
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

    def test_smart_slice_points(self, test_images):
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
                smart=True,
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

    def test_smart_slice_points_no_min_max(self, test_images):
        for i in range(10):
            min_height = -1
            max_height = -1
            height = random.randint(200, 50_000)
            #  height = 504, 2031, 259, 989
            slice_points = SlicesDetector.slice_points(
                images=test_images,
                height=height,
                smart=True,
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
