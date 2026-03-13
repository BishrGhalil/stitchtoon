from enum import StrEnum
from os import PathLike
from typing import Union

_PathType = Union[str, PathLike]

METADATA_FILENAME = ".stitching_metadata.json"

# Maximum allowed size for security reasons
MAX_IMAGE_SIZE = 100_000

# Supported formats
FORMATS = {"jpg", "jpeg", "png", "webp", "psd", "psb", "bmp", "tiff", "tga"}

# Mapper to be used when a format's max size exceeded
FORMAT_SIZE_MAPPER = {"psd": "psb"}

# Formats size limits
FORMATS_LIMITS = {
    "jpg": 65_535,
    "jpeg": 65_535,
    "webp": 16_383,
    "png": MAX_IMAGE_SIZE,
    "psd": 30_000,
    "psb": MAX_IMAGE_SIZE,
    "tiff": 16_383,
    "bmp": MAX_IMAGE_SIZE,
    "tga": MAX_IMAGE_SIZE,
}

# Formats supporting transparency
SUPPORTS_TRANSPARENCY = {"png", "webp", "psd", "psb", "tga"}

# Photoshop file formats
PS_FORMATS = {"psd", "psb"}

# Detection type values
DetectionType = StrEnum("DetectionType", ["FIXED", "PIXEL", "METADATA_FILE"])
