import gc
import os.path as osp
from time import time

from stitchtoon.detectors import select_detector
from stitchtoon.services import GlobalLogger, ImageHandler, ImageManipulator, logFunc, scan
from stitchtoon.services.image_directory import Image
from stitchtoon.services.progressbar import DefaultCliProgress, ProgressHandler
from stitchtoon.utils.constants import FORMAT_MAPPER, OUTPUT_SUFFIX, SIZE_LIMIT_MAPPER, WIDTH_ENFORCEMENT
from stitchtoon.utils.errors import SizeLimitError

# Must have a sum of 100
PROGRESS_PERCENTAGE = {
    "scan": 10,
    "stitch": 70,
    "loading": 10,
    "save": 10,
}


@logFunc()
def process(
    input,
    output,
    split_height,
    *,
    output_format="jpeg",
    recursive=True,
    as_archive=False,
    lossy_quality=90,
    progress=None,
    show_progress=False,
    params,
):
    handler = ImageHandler()
    if not progress:
        progress = ProgressHandler()
    if show_progress:
        progress = DefaultCliProgress()
    progress.start()
    output_format = output_format.lower()

    # Starting Stitch Process
    if output_format == "psd" and split_height > SIZE_LIMIT_MAPPER[output_format]:
        output_format = "psb"
    if split_height > SIZE_LIMIT_MAPPER[output_format]:
        # FIXMEE: add size limit to width also
        raise SizeLimitError(
            f"Image type {output_format} supports size up to {SIZE_LIMIT_MAPPER[output_format]}px only"
        )
    if not osp.lexists(input):
        raise FileNotFoundError(f"Could not found {input}")
    if not output:
        raise Exception("Output path is not provided")
    working_dirs = scan(input, recursive)
    if not working_dirs:
        raise Exception(
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
        format = output_format.lstrip(".")
        format = FORMAT_MAPPER.get(format, format)
        sub_output = output
        if recursive:
            sub_output = osp.join(output, osp.basename(image_dir.path))

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
    progress=ProgressHandler(),
    increament=0,
    detection_type="pixel",
    senstivity=90,
    width_enforce="none",
    custom_width=-1,
    line_steps=5,
    ignorable_pixels=5,
):
    manipulator = ImageManipulator()
    detector = select_detector(detection_type=detection_type)
    images = manipulator.resize(images, width_enforce, custom_width)
    combined_img = manipulator.combine(images, progress=progress, increament=increament)
    slice_points = detector.run(
        combined_img,
        split_height,
        sensitivity=senstivity,
        ignorable_pixels=ignorable_pixels,
        scan_step=line_steps,
    )
    images = manipulator.slice(combined_img, slice_points)

    return images
