import gc
import os.path as osp
from time import time

from stitchtoon.detectors import select_detector
from stitchtoon.services import GlobalLogger
from stitchtoon.services import ImageHandler
from stitchtoon.services import ImageManipulator
from stitchtoon.services import logFunc
from stitchtoon.services.directory_scanner import Image
from stitchtoon.services.directory_scanner import scan
from stitchtoon.utils.constants import FORMAT_MAPPER
from stitchtoon.utils.constants import OUTPUT_SUFFIX
from stitchtoon.utils.constants import SIZE_LIMIT_MAPPER
from stitchtoon.utils.constants import WIDTH_ENFORCEMENT
from stitchtoon.utils.errors import SizeLimitError


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
    params,
):
    handler = ImageHandler()
    # Starting Stitch Process
    if split_height > SIZE_LIMIT_MAPPER[output_format]:
        raise SizeLimitError(
            f"Image type {output_format} supports size up to {SIZE_LIMIT_MAPPER[output_format]}px only"
        )
    if not osp.lexists(input):
        raise FileNotFoundError(f"Could not found {input}")
    image_dir = scan(input, recursive)
    images = handler.load(image_dir.images)
    images = stitch(images, split_height, **params)
    format = output_format.lstrip(".")
    format = FORMAT_MAPPER.get(format, format)
    handler.save_all(
        output=output,
        images=images,
        format=format,
        as_archive=as_archive,
        quality=lossy_quality,
    )
    gc.collect()


@logFunc()
def stitch(
    images: list[Image],
    split_height: int,
    *,
    detection_type="pixel",
    senstivity=90,
    custom_width=-1,
    line_steps=5,
    ignorable_pixels=5,
):
    manipulator = ImageManipulator()
    detector = select_detector(detection_type=detection_type)
    width_enforce = (
        WIDTH_ENFORCEMENT.MANUAL if custom_width > 0 else WIDTH_ENFORCEMENT.NONE
    )
    images = manipulator.resize(images, width_enforce, custom_width)
    combined_img = manipulator.combine(images)
    slice_points = detector.run(
        combined_img,
        split_height,
        sensitivity=senstivity,
        ignorable_pixels=ignorable_pixels,
        scan_step=line_steps,
    )
    images = manipulator.slice(combined_img, slice_points)

    return images
