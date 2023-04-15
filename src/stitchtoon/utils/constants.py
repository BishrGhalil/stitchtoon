from enum import IntEnum


# Static Variables
LOG_REL_DIR = "__logs__"
SETTINGS_REL_DIR = "__settings__"
OUTPUT_SUFFIX = "[stitched]"
SUPPORTED_IMG_TYPES = (
    "png",
    "webp",
    "jpeg",
    "jpg",
    "psd",
    "psb",
)

FORMAT_MAPPER = {
    "jpg": "jpeg",
    "psd": "psb",
}

SIZE_LIMIT_MAPPER = {
    "jpg": 65_535,
    "webp": 16_383,
    "png": 300_000,
    "psd": 30_000,
    "psb": 300_000,
}

PHOTOSHOP_FILE_TYPES = ("psd", "psb")


# Static Enums
class WIDTH_ENFORCEMENT(IntEnum):
    NONE = 0
    AUTOMATIC = 1
    MANUAL = 2


class DETECTION_TYPE(IntEnum):
    NO_DETECTION = 0
    PIXEL_COMPARISON = 1
