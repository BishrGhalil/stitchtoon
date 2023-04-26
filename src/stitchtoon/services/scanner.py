from __future__ import annotations

import os
import os.path as osp
from typing import Callable, Iterable, Union

from natsort import natsorted

from ..utils.constants import PHOTOSHOP_FILE_TYPES, SUPPORTED_IMG_TYPES
from .global_logger import logFunc
from .image_directory import Image, ImageDirectory


@logFunc()
def is_supported_img(*, format: str = None, filename: os.PathLike = None) -> bool:
    """Checks if an image format is supported

    Args:
        format (str, optional): image format. Defaults to None.
        filename (os.PathLike, optional): filename with image format extention. Defaults to None.

    Returns:
        bool
    """

    format = format or osp.splitext(filename)[1].lower()
    format = format.strip(".")
    if format in SUPPORTED_IMG_TYPES:
        return True
    return False


@logFunc
def get_format(filename: os.PathLike) -> str:
    """Gets filename extention

    Args:
        filename (os.PathLike)

    Returns:
        str
    """

    return osp.splitext(filename)[1].lower().strip(".")


@logFunc()
def scanimgdir(input: os.PathLike, sort: bool = True) -> Iterable[ImageDirectory]:
    """Scan a directory for supported images

    Args:
        input (os.PathLike): directory path
        sort (bool, optional): natural sorting. Defaults to True.

    Returns:
        Iterable[ImageDirectory]
    """

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
def walkimgdir(input: os.PathLike, sort: bool = True) -> Iterable[ImageDirectory]:
    """Recursivaly scan a directory for supported images

    Args:
        input (os.PathLike): directory path
        sort (bool, optional): natural sorting. Defaults to True.

    Returns:
        Iterable[ImageDirectory]
    """

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
        dirs.append(ImageDirectory(input, images))

    if dirspaths:
        dirspaths = natsorted(dirspaths)

    for dir in dirspaths:
        res = walkimgdir(dir, sort)
        if res:
            dirs.extend(res)

    return dirs


@logFunc()
def scan(input: os.PathLike, recursive: bool = True) -> Iterable[ImageDirectory]:
    """scan a directory for supported images

    Args:
        input (os.PathLike)
        recursive (bool, optional) Defaults to True.

    Returns:
        Iterable[ImageDirectory]
    """

    strategy = walkimgdir if recursive else scanimgdir
    return strategy(osp.abspath(input))
