from enum import Enum, IntEnum

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
}

SIZE_LIMIT_MAPPER = {
    "jpg": 65_535,
    "jpeg": 65_535,
    "webp": 16_383,
    "png": 300_000,
    "psd": 30_000,
    "psb": 300_000,
}

PHOTOSHOP_FILE_TYPES = ("psd", "psb")


# Static Enums
class WIDTH_ENFORCEMENT(Enum):
    NONE = "none"
    AUTO = "auto"
    FIXED = "fixed"


class DETECTION_TYPE(Enum):
    NO_DETECTION = "none"
    PIXEL_COMPARISON = "pixel"
