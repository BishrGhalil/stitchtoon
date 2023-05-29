from stitchtoon.core.slices_detector import SlicesDetector
import random


class TestImageDetector:
    def test_stupid_slice_points(self, test_images):
        for i in range(10):
            height = random.randint(100, 50_000)
            slice_points = SlicesDetector.slice_points(
                images=test_images, avg_height=height, smart=False
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
