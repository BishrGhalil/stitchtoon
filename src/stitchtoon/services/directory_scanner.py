from __future__ import annotations

import os
import os.path as osp
from typing import Callable
from typing import Iterable
from typing import Union

from ..utils.constants import PHOTOSHOP_FILE_TYPES
from ..utils.constants import SUPPORTED_IMG_TYPES
from .global_logger import logFunc
from .image_directory import Image
from .image_directory import ImageDirectory
from natsort import natsorted


@logFunc()
def is_supported_img(*, format=None, filename=None):
    format = format or filename.split(".")[-1].lower()
    if format in SUPPORTED_IMG_TYPES:
        return True
    return False


@logFunc
def get_format(filename):
    return filename.split(".")[-1].lower()


@logFunc()
def scanimgdir(input, sort=True) -> Iterable[ImageDirectory]:
    images = []
    for ent in os.scandir(input):
        if ent.is_file() and is_supported_img(filename=ent.name):
            images.append(Image(ent.path, ent.name, format=get_format(ent.name)))

    if not images:
        return None
    images = natsorted(images, key=lambda x: x.path)
    image_dir = ImageDirectory(input, images)
    return (image_dir,)


@logFunc()
def walkimgdir(input, sort=True) -> Iterable[ImageDirectory]:
    images = []
    dirspaths = []
    dirs = []
    for ent in os.scandir(input):
        if ent.is_file() and is_supported_img(filename=ent.name):
            images.append(Image(ent.path, ent.name, format=get_format(ent.name)))

        elif ent.is_dir():
            dirspaths.append(ent.path)

    if images:
        images = natsorted(images, key=lambda x: x.path)

    if dirspaths:
        dirspaths = natsorted(dirspaths)

    for dir in dirspaths:
        res = walkimgdir(dir, sort)
        if res:
            dirs.extend(res)

    image_dir = ImageDirectory(input, images)
    return (image_dir, *dirs)


@logFunc()
def scan(input, recursive=True) -> ImageDirectory:
    strategy = walkimgdir if recursive else scanimgdir
    return strategy(osp.abspath(input))
