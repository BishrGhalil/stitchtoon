from enum import StrEnum
from os import PathLike
from typing import Union

_PathType = Union[str, PathLike]

METADATA_FILENAME = ".stitching_metadata.json"

# Maximum allowed size for security reasons
MAX_IMAGE_SIZE = 100_000

# Supported formats
FORMATS = {"JPEG", "PNG", "WEBP", "PSD", "PSB", "BMP", "TIFF", "TGA"}

# Mapper to be used when a format's max size exceeded
FORMAT_SIZE_MAPPER = {"PSD": "PSB"}

# Formats size limits
FORMATS_LIMITS = {
    "JPEG": 65_535,
    "WEBP": 16_383,
    "PNG": MAX_IMAGE_SIZE,
    "PSD": 30_000,
    "PSB": MAX_IMAGE_SIZE,
    "TIFF": 16_383,
    "BMP": MAX_IMAGE_SIZE,
    "TGA": MAX_IMAGE_SIZE,
}

# Formats supporting transparency
SUPPORTS_TRANSPARENCY = {"PNG", "WEBP", "PSD", "PSB", "TGA"}

# Photoshop file formats
PS_FORMATS = {"PSD", "PSB"}

# Detection type values
DetectionType = StrEnum("DetectionType", ["FIXED", "PIXEL", "METADATA_FILE"])
