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

FORMAT_NAME_MAPPER = {
    "jpg": "jpeg",
}

FORMAT_SIZE_MAPPER = {
    "psd": "psb",
}

SIZE_LIMITS = {
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


class ProcessDefaults:
    OUTPUT_FORMAT: str = "jpeg"
    RECURSIVE: bool = True
    AS_ARCHIVE: bool = False
    LOSSY_QUALITY: int = 90
    SHOW_PROGRESS: bool = False


class StitchDefaults:
    INCREAMENT: int = 0
    DETECTION_TYPE: str = DETECTION_TYPE.NO_DETECTION.value
    SENSITIVITY: int = 90
    WIDTH_ENFORCE: str = "none"
    CUSTOM_WIDTH: int = -1
    LINE_STEPS: int = 5
    IGNORABLE_PIXELS: int = 5
