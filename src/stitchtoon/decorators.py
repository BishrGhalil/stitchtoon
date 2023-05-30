import functools
import os.path as osp

from .const import FORMATS
from .const import _PathType
from .exc import UnSupportedFormatError


def validate_format(
    func=None, *, format_arg: str = "format", filename_arg: _PathType = None
):
    def decorator_validate_format(func):
        @functools.wraps(func)
        def wrapper_validate_format(*args, **kwargs):
            format = None
            format = kwargs.get(format_arg)
            if format is None and filename_arg is None:
                raise Exception(
                    f"{format_arg} is not a valid argument for function '{func.__name__}', or has not been passed as keyword argument"
                )
            elif filename_arg and kwargs.get(filename_arg) is None:
                raise Exception(
                    f"{filename_arg} is not a valid argument for function '{func.__name__}', or has not been passed as keyword argument"
                )
            elif filename_arg:
                filename = kwargs.get(filename_arg)
                format = osp.splitext(filename)[1]
                format = format.strip(".")
            if format.upper() not in FORMATS:
                raise UnSupportedFormatError(f"file format {format} is not supported.")
            return func(*args, **kwargs)

        return wrapper_validate_format

    if func is None:
        return decorator_validate_format
    return decorator_validate_format(func)


def validate_path(path_arg, validate_parents=False):
    def decorator_validate_path(func):
        @functools.wraps(func)
        def wrapper_validate_path(*args, **kwargs):
            if args:
                raise Exception(
                    f"function '{func.__name__}' takes keyword arguments only"
                )
            path = kwargs.get(path_arg)
            if path is None:
                raise Exception(
                    f"{path_arg} is not a valid argument for function '{func.__name__}'"
                )
            if validate_parents:
                path = osp.dirname(path)
            if not osp.lexists(path):
                raise FileNotFoundError(f"{kwargs.get(path_arg, '')} does not exists.")
            return func(*args, **kwargs)

        return wrapper_validate_path

    return decorator_validate_path
