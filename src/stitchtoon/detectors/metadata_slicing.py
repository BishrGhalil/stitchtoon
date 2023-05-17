from ..services.global_logger import logFunc
from ..services.image_directory import Image
from ..utils.errors import NoMetadataError


class MetadataSlicingDetector:
    @logFunc(inclass=True)
    def run(self, combined_img: Image, **kwargs) -> list[int]:
        metadata = kwargs.get("metadata")
        if not metadata:
            raise NoMetadataError
        last_row = combined_img.height
        slice_locations = [0]
        row = 0
        i = 0
        while row < last_row and i < len(metadata):
            row += metadata[i][1]
            slice_locations.append(row)
            i += 1
        if slice_locations[-1] != last_row - 1:
            slice_locations.append(last_row - 1)
        return slice_locations
