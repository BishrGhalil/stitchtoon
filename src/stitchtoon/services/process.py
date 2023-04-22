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
    if output_format == "psd" and split_height > SIZE_LIMIT_MAPPER[output_format]:
        output_format = "psb"
    if split_height > SIZE_LIMIT_MAPPER[output_format]:
        # FIXMEE: add size limit to width also
        raise SizeLimitError(
            f"Image type {output_format} supports size up to {SIZE_LIMIT_MAPPER[output_format]}px only"
        )
    if not osp.lexists(input):
        raise FileNotFoundError(f"Could not found {input}")
    working_dirs = scan(input, recursive)
    if not working_dirs:
        raise Exception(
            """Input directory does not contain supported images.
            try `-r` option for recursive scanning or try another input directory"""
        )
    for image_dir in working_dirs:
        images = handler.load(image_dir.images)
        if not images:
            continue
        images = stitch(images, split_height, **params)
        format = output_format.lstrip(".")
        format = FORMAT_MAPPER.get(format, format)
        sub_output = output
        if recursive:
            sub_output = osp.join(output, osp.basename(image_dir.path))

        handler.save_all(
            output=sub_output,
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
    width_enforce="none",
    custom_width=-1,
    line_steps=5,
    ignorable_pixels=5,
):
    manipulator = ImageManipulator()
    detector = select_detector(detection_type=detection_type)
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
