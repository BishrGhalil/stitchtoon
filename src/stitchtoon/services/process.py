import gc
import os.path as osp
from os import PathLike

from stitchtoon.detectors import select_detector
from stitchtoon.services import ImageHandler, ImageManipulator, logFunc, scan
from stitchtoon.services.image_directory import Image
from stitchtoon.services.progressbar import DefaultCliProgress, ProgressHandler
from stitchtoon.utils.constants import (
    FORMAT_NAME_MAPPER,
    FORMAT_SIZE_MAPPER,
    SIZE_LIMITS,
    WIDTH_ENFORCEMENT,
    ProcessDefaults,
    StitchDefaults,
)
from stitchtoon.utils.errors import EmptyImageDir, SizeLimitError

# Must have a sum of 100
PROGRESS_PERCENTAGE = {
    "scan": 10,
    "stitch": 70,
    "loading": 10,
    "save": 10,
}


@logFunc()
def process(
    input: PathLike,
    output: PathLike,
    split_height: int,
    *,
    output_format: str = ProcessDefaults.OUTPUT_FORMAT,
    recursive: bool = ProcessDefaults.RECURSIVE,
    as_archive: bool = ProcessDefaults.AS_ARCHIVE,
    lossy_quality: int = ProcessDefaults.LOSSY_QUALITY,
    show_progress: bool = ProcessDefaults.SHOW_PROGRESS,
    progress: ProgressHandler = None,
    params: dict[str, any],
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

    Raises:
        FileNotFoundError: When input directory could not be found
        EmptyImageDir: When input directory does not contain supported images
        Exception: When output is not provided
    """
    handler = ImageHandler()
    progress = progress or _get_progressbar(show_progress)

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

    progress.update(progress.value + PROGRESS_PERCENTAGE["scan"], "Stichting")
    working_dirs_len = len(working_dirs)
    for image_dir in working_dirs:
        images_len = len(image_dir.images)
        per_dir_percentage = PROGRESS_PERCENTAGE["loading"] / working_dirs_len
        images = handler.load(
            image_dir.images,
            progress=progress,
            increament=per_dir_percentage / images_len,
        )
        if not images:
            continue
        per_dir_percentage = PROGRESS_PERCENTAGE["stitch"] / working_dirs_len
        images = stitch(
            images,
            split_height,
            progress=progress,
            increament=per_dir_percentage / images_len,
            **params,
        )
        images_len = len(images)
        sub_output = output

        if recursive:
            sub_output = osp.join(output, osp.basename(image_dir.path))
            if as_archive and osp.splitext(output)[1] != ".zip":
                sub_output += ".zip"
        else:
            if as_archive and osp.splitext(output)[1] != ".zip":
                sub_output = osp.join(output, f"{osp.basename(image_dir.path)}.zip")

        per_dir_percentage = PROGRESS_PERCENTAGE["save"] / working_dirs_len
        handler.save_all(
            output=sub_output,
            images=images,
            format=format,
            as_archive=as_archive,
            quality=lossy_quality,
            progress=progress,
            increament=per_dir_percentage / images_len,
        )
    progress.update(100, "Completed")
    progress.finish()
    gc.collect()


@logFunc()
def stitch(
    images: list[Image],
    split_height: int,
    *,
    progress: ProgressHandler = None,
    increament: int = StitchDefaults.INCREAMENT,
    detection_type: str = StitchDefaults.DETECTION_TYPE,
    sensitivity: int = StitchDefaults.SENSITIVITY,
    width_enforce: str = StitchDefaults.WIDTH_ENFORCE,
    custom_width: int = StitchDefaults.CUSTOM_WIDTH,
    line_steps: int = StitchDefaults.LINE_STEPS,
    ignorable_pixels: int = StitchDefaults.IGNORABLE_PIXELS,
) -> list[Image]:
    """Stitchs images to specified heigh

    Args:
        images (list[Image])
        split_height (int)
        progress (ProgressHandler, optional): progressbar handler. Defaults to None.
        increament (int, optional): progressbar increament factor. Defaults to StitchDefaults.INCREAMENT.
        detection_type (str, optional): Defaults to StitchDefaults.DETECTION_TYPE.
        sensitivity (int, optional): Defaults to StitchDefaults.SENSITIVITY.
        width_enforce (str, optional): Defaults to StitchDefaults.WIDTH_ENFORCE.
        custom_width (int, optional): Defaults to StitchDefaults.CUSTOM_WIDTH.
        line_steps (int, optional): Defaults to StitchDefaults.LINE_STEPS.
        ignorable_pixels (int, optional): Defaults to StitchDefaults.IGNORABLE_PIXELS.

    Returns:
        list[Images]: stitched images
    """
    if not progress:
        progress = _get_progressbar()
    detector = select_detector(detection_type=detection_type)
    images = ImageManipulator.resize(images, width_enforce, custom_width)
    combined_img = ImageManipulator.combine(
        images, progress=progress, increament=increament
    )
    slice_points = detector.run(
        combined_img,
        split_height,
        sensitivity=sensitivity,
        ignorable_pixels=ignorable_pixels,
        scan_step=line_steps,
    )
    images = ImageManipulator.slice(combined_img, slice_points)

    return images


def _is_size_ok(format: str, size: int) -> bool:
    """Checks if size excedes format size limit

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
        SizeLimitError: Whene size is bigger than format size limit

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
