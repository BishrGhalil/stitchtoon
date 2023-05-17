from ..services.global_logger import logFunc
from ..services.image_directory import Image
from ..utils.constants import SMALLER_ALLOWD_HEIGHT


class DirectSlicingDetector:
    @logFunc(inclass=True)
    def run(self, combined_img: Image, **kwargs) -> list[int]:
        split_height = kwargs.get("split_height")
        if not split_height or split_height < SMALLER_ALLOWD_HEIGHT:
            raise Exception("Height very small to slice")
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
