from PIL import Image as pilImage

from ..services.global_logger import logFunc
from ..services.image_directory import Image


class DirectSlicingDetector:
    @logFunc(inclass=True)
    def run(self, combined_img: Image, split_height: int, **kwargs) -> list[int]:
        # Changes from a pil image to an numpy pixel array
        last_row = combined_img.height
        # Initializes some variables
        slice_locations = [0]
        row = split_height
        while row < last_row:
            slice_locations.append(row)
            row += split_height
        if slice_locations[-1] != last_row - 1:
            slice_locations.append(last_row - 1)
        return slice_locations
