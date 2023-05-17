from ..services import logFunc
from ..utils.constants import DETECTION_TYPE
from .direct_slicing import DirectSlicingDetector
from .metadata_slicing import MetadataSlicingDetector
from .pixel_comparison import PixelComparisonDetector


@logFunc()
def select_detector(detection_type: str):
    if not detection_type or detection_type == DETECTION_TYPE.NO_DETECTION.value:
        return DirectSlicingDetector()
    elif detection_type == DETECTION_TYPE.PIXEL_COMPARISON.value:
        return PixelComparisonDetector()
    elif detection_type == DETECTION_TYPE.METADATA.value:
        return MetadataSlicingDetector()
    else:
        raise Exception("Invalid Detection Type")
