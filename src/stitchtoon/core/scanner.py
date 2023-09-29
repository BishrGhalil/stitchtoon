from __future__ import annotations

import os
import os.path as osp

from natsort import natsorted

from ..const import FORMATS
from ..logger import logged
from typing import Iterable

ScanResult = Iterable[Iterable[str, Iterable[str] | None]]


@logged
def is_supported_img(*, format: str = None, filename: os.PathLike = None) -> bool:
    """Checks if an image format is supported

    Args:
        format (str, optional): image format. Defaults to None.
        filename (os.PathLike, optional): filename with image format extention. Defaults to None.

    Returns:
        bool
    """

    format = format or osp.splitext(filename)[1]
    format = format.strip(".").upper()
    if format in FORMATS:
        return True
    return False


@logged
def get_format(filename: os.PathLike) -> str:
    """Gets filename extention

    Args:
        filename (os.PathLike)

    Returns:
        str
    """

    return osp.splitext(filename)[1].lower().strip(".")


@logged
def scanimgdir(input_path: os.PathLike) -> ScanResult | tuple:
    """Scan a directory for supported images

    Args:
        input_path (os.PathLike): directory path

    Returns:
        Iterable[ImageDirectory]
    """

    images = []
    for ent in os.scandir(input_path):
        if ent.is_file() and is_supported_img(filename=ent.name):
            images.append(osp.abspath(ent.path))

    images = natsorted(images)
    image_dir = (osp.abspath(input_path), images)
    return (image_dir,)


@logged
def walkimgdir(input_path: os.PathLike, sort: bool = True) -> ScanResult:
    """Recursively scan a directory for supported images

    Args:
        input_path (os.PathLike): directory path
        sort (bool, optional): natural sorting. Defaults to True.

    Returns:
        Iterable[ImageDirectory]
    """

    images = []
    dirspaths = []
    dirs = []
    for ent in os.scandir(input_path):
        if ent.is_file() and is_supported_img(filename=ent.name):
            images.append(osp.abspath(ent.path))

        elif ent.is_dir():
            dirspaths.append(osp.abspath(ent.path))

    if images:
        images = natsorted(images)
        dirs.append((osp.abspath(input_path), images))

    if dirspaths:
        dirspaths = natsorted(dirspaths)

    for _dir in dirspaths:
        res = walkimgdir(_dir, sort=sort)
        if res:
            dirs.extend(res)

    return dirs


@logged
def scan(input_path: os.PathLike, recursive: bool = True) -> ScanResult:
    """scan a directory for supported images

    Args:
        input_path (os.PathLike)
        recursive (bool, optional) Defaults to True.

    Returns:
        Iterable[ImageDirectory]
    """

    strategy = walkimgdir if recursive else scanimgdir
    return strategy(osp.abspath(input_path))
