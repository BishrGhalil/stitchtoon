import PIL.Image
from PIL.Image import Image

from ..const import SUPPORTS_TRANSPARENCY
from ..logger import logged
from .slices_detectors.slices_detector import Slice


class Stitcher:
    @staticmethod
    @logged(inclass=True)
    def stitch(
        images: list[Image],
        slices: list[Slice],
        mode="RGBA",
        fill_color=(255, 255, 255, 0),
    ) -> list[Image]:
        new_images = []
        if mode != "RGBA" and len(fill_color) > 3:
            fill_color = fill_color[0:3]
        for s in slices:
            img = PIL.Image.new(mode, s.size, fill_color)
            cur_height = 0
            for p in s.points:
                img.paste(
                    images[p[0]].crop((0, p[1], images[p[0]].width, p[2])),
                    box=(0, cur_height),
                )
                cur_height += p[2] - p[1]
            new_images.append(img)
            if mode in SUPPORTS_TRANSPARENCY:
                bbox = img.getbbox()
                if bbox:
                    img = img.crop(bbox)

        return new_images
