import gc
import os
import os.path as osp
from os import PathLike
import json

from stitchtoon.detectors import select_detector
from stitchtoon.services import ImageHandler
from stitchtoon.services import ImageManipulator
from stitchtoon.services import logFunc
from stitchtoon.services import scan
from stitchtoon.services.image_directory import Image
from stitchtoon.services.progressbar import DefaultCliProgress
from stitchtoon.services.progressbar import ProgressHandler
from stitchtoon.utils.constants import DETECTION_TYPE
from stitchtoon.utils.constants import FORMAT_NAME_MAPPER
from stitchtoon.utils.constants import FORMAT_SIZE_MAPPER
from stitchtoon.utils.constants import SIZE_LIMITS
from stitchtoon.utils.constants import SUPPORTS_TRANSPARENCY
from stitchtoon.utils.constants import ProcessDefaults
from stitchtoon.utils.constants import StitchDefaults
from stitchtoon.utils.constants import METADATA_FILENAME
from stitchtoon.utils.errors import EmptyImageDir
from stitchtoon.utils.errors import SizeLimitError
from stitchtoon.utils.errors import NoMetadataError

# Must have a sum of 100
PROGRESS_PERCENTAGE = {
    "scan": 10,
    "stitch": 60,
    "loading": 10,
    "save": 20,
}

Metadata = dict[str, list[dict[str, list[int, int]]]]

@logFunc()
def process(
    input: PathLike,
    output: PathLike,
    *,
    split_height: int = 0,
    images_number: int = 0,
    output_format: str = ProcessDefaults.OUTPUT_FORMAT,
    recursive: bool = ProcessDefaults.RECURSIVE,
    as_archive: bool = ProcessDefaults.AS_ARCHIVE,
    lossy_quality: int = ProcessDefaults.LOSSY_QUALITY,
    show_progress: bool = ProcessDefaults.SHOW_PROGRESS,
    progress: ProgressHandler = None,
    params: dict[str, any],
    write_metadata: bool = False,
    slice_to_metadata: bool = True,
) -> None:
    """stitch images in input and save them to output

    Args:
        input (PathLike)
        output (PathLike)
        split_height (int)
        params (dict[str, any]): stitch params, see stitch function for more info.
        output_format (str, optional): Defaults to ProcessDefaults.OUTPUT_FORMAT.
        recursive (bool, optional): Defaults to ProcessDefaults.RECURSIVE.
        as_archive (bool, optional): Defaults to ProcessDefaults.AS_ARCHIVE.
        lossy_quality (int, optional): Defaults to ProcessDefaults.LOSSY_QUALITY.
        show_progress (bool, optional): Defaults to ProcessDefaults.SHOW_PROGRESS.
        progress (ProgressHandler, optional): progressbar handler. Defaults to None.
        write_metadata (bool, optional): Writes metadata file so you can match source when stitching again, Defaults to False.
        slice_to_metadata (bool, optional): Slice according to metadata file if not available slice to split_height or images_number, Defaults to True.

    Raises:
        FileNotFoundError: When input directory could not be found
        EmptyImageDir: When input directory does not contain supported images
        Exception: When output is not provided
    """
    handler = ImageHandler()
    progress = progress or _get_progressbar(show_progress)

    if not split_height and not images_number and not slice_to_metadata:
        raise Exception(
            "split_height ,images_number and slice_to_metadata are not provided, Must provide one of theme"
        )

    format = _get_format_for_size(
        output_format, max(split_height, params.get("custom_width", 0))
    )

    if not osp.lexists(input):
        raise FileNotFoundError(f"Could not found {input}")
    if not output:
        raise Exception("Output path is not provided")
    working_dirs = scan(input, recursive)
    if not working_dirs:
        raise EmptyImageDir(
            "Input directory does not contain supported images. Try again with batch mode."
        )

    progress.update(progress.value + PROGRESS_PERCENTAGE["scan"], "Stitching")
    working_dirs_len = len(working_dirs)
    for image_dir in working_dirs:
        metadata = {"imgs": []}
        prev_metadata = {}
        using_metadata = False
        if slice_to_metadata:
            if METADATA_FILENAME in os.listdir(input):
                using_metadata = True
                with open(osp.join(image_dir.path, METADATA_FILENAME), "r") as fd:
                    prev_metadata = json.load(fd)
            else:
                if not split_height and not images_number:
                    raise NoMetadataError("metadata file does not exists, try stitching source again with write_metadata option, Or provide split_height or images_number")
                    return None


        images_len = len(image_dir.images)
        per_dir_percentage = PROGRESS_PERCENTAGE["loading"] / working_dirs_len
        transparent = format in SUPPORTS_TRANSPARENCY
        images = handler.load(
            image_dir.images,
            progress=progress,
            increment=per_dir_percentage / images_len,
            transparent=transparent,
        )
        if not images:
            continue

        sub_output = output
        if recursive:
            sub_output = osp.join(output, osp.basename(image_dir.path))
            if as_archive and osp.splitext(output)[1] != ".zip":
                sub_output += ".zip"
        else:
            if as_archive and osp.splitext(output)[1] != ".zip":
                sub_output = osp.join(output, f"{osp.basename(image_dir.path)}.zip")

        for idx, image in enumerate(images):
            metadata["imgs"].append([image.width, image.height])
        total_images_length = sum(image.height for image in images)
        if images_number:
            split_height = total_images_length / images_number
            format = _get_format_for_size(format, split_height)
            params["detection_type"] = DETECTION_TYPE.NO_DETECTION.value

        if using_metadata:
            params["detection_type"] = DETECTION_TYPE.METADATA.value

        per_dir_percentage = PROGRESS_PERCENTAGE["stitch"] / working_dirs_len
        images = stitch(
            images,
            split_height,
            progress=progress,
            increment=per_dir_percentage / images_len,
            metadata = prev_metadata.get("imgs"),
            **params,
        )
        images_len = len(images)
        per_dir_percentage = PROGRESS_PERCENTAGE["save"] / working_dirs_len
        handler.save_all(
            output=sub_output,
            images=images,
            format=format,
            as_archive=as_archive,
            quality=lossy_quality,
            progress=progress,
            increment=per_dir_percentage / images_len,
        )
        if write_metadata:
            progress.update(progress.value, "Writing metadata file")
            with open(osp.join(sub_output, METADATA_FILENAME), "w") as fd:
                json.dump(metadata, fd)

    progress.update(100, "Completed")
    progress.finish()
    gc.collect()


@logFunc()
def stitch(
    images: list[Image],
    split_height: int,
    *,
    progress: ProgressHandler = None,
    increment: int = StitchDefaults.increment,
    detection_type: str = StitchDefaults.DETECTION_TYPE,
    sensitivity: int = StitchDefaults.SENSITIVITY,
    width_enforce: str = StitchDefaults.WIDTH_ENFORCE,
    custom_width: int = StitchDefaults.CUSTOM_WIDTH,
    line_steps: int = StitchDefaults.LINE_STEPS,
    ignorable_pixels: int = StitchDefaults.IGNORABLE_PIXELS,
    metadata: list[list[int, int]] = None,
) -> list[Image]:
    """Stitchs images to specified heigh

    Args:
        images (list[Image])
        split_height (int)
        progress (ProgressHandler, optional): progressbar handler. Defaults to None.
        increment (int, optional): progressbar increment factor. Defaults to StitchDefaults.increment.
        detection_type (str, optional): Defaults to StitchDefaults.DETECTION_TYPE.
        sensitivity (int, optional): Defaults to StitchDefaults.SENSITIVITY.
        width_enforce (str, optional): Defaults to StitchDefaults.WIDTH_ENFORCE.
        custom_width (int, optional): Defaults to StitchDefaults.CUSTOM_WIDTH.
        line_steps (int, optional): Defaults to StitchDefaults.LINE_STEPS.
        ignorable_pixels (int, optional): Defaults to StitchDefaults.IGNORABLE_PIXELS.
        metadata list[list[int, int]]: Slice to metadata values, This option overrides split_height, Defaults to None,

    Returns:
        list[Images]: stitched images
    """
    if not progress:
        progress = _get_progressbar()
    images = ImageManipulator.resize(images, width_enforce, custom_width)
    combined_img = ImageManipulator.combine(
        images, progress=progress, increment=increment
    )
    progress.update(progress.value, "Calculating slicing points")
    detector = select_detector(detection_type=detection_type)
    slice_points = detector.run(
        combined_img = combined_img,
        split_height=split_height,
        sensitivity=sensitivity,
        ignorable_pixels=ignorable_pixels,
        scan_step=line_steps,
        metadata=metadata,
    )
    images = ImageManipulator.slice(combined_img, slice_points)

    return images


def _is_size_ok(format: str, size: int) -> bool:
    """Checks if size exceeds format size limit

    Args:
        format (str)
        size (int)

    Returns:
        bool
    """

    if size > SIZE_LIMITS[format]:
        return False

    return True


def _get_format_for_size(format: str, size: int) -> str:
    """Gets the right format alternative for current size or raise

    Args:
        format (str)
        size (int)

    Raises:
        SizeLimitError: When size is bigger than format size limit

    Returns:
        str: format
    """

    format = format.lower()
    format = FORMAT_NAME_MAPPER.get(format, format)

    if FORMAT_SIZE_MAPPER.get(format) and not _is_size_ok(format, size):
        format = FORMAT_SIZE_MAPPER.get(format)

    if not _is_size_ok(format, size):
        raise SizeLimitError(
            f"Image type {format} supports size up to {SIZE_LIMITS[format]}px only"
        )
    else:
        return format


def _get_progressbar(show: bool = False) -> ProgressHandler:
    """Returns a progress bar handler

    Args:
        show (bool, optional): Shows a progress bar on the command line. Defaults to False.

    Returns:
        ProgressHandler
    """

    if show:
        return DefaultCliProgress()
    else:
        return ProgressHandler()
