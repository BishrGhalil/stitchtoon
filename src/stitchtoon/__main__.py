import argparse
import math
import sys

from stitchtoon import __version__
from stitchtoon.services.global_logger import DEFAULT_LOG_LEVEL, Logger, get_logger
from stitchtoon.services.process import process


def positive_int(value):
    if not value.isdigit() or int(value) <= 0:
        raise argparse.ArgumentTypeError("Not a valid integer value")
    return int(value)


def log_level(value):
    import logging

    return {"debug": logging.DEBUG, "info": logging.INFO, "error": logging.ERROR}.get(
        value, DEFAULT_LOG_LEVEL
    )


def size_format(value):
    value = value.replace("x", "X")
    size = value.split("X")
    if len(size) > 2:
        raise argparse.ArgumentTypeError(
            "invalid size format. Supported formats `<height>X<width>` or `<height>`. ex: `5000X760`"
        )

    if len(size) == 1:
        size.append("0")
    for idx, s in enumerate(size):
        if not s.isdigit():
            raise argparse.ArgumentTypeError(
                "invalid size format. Supported formats `<height>X<width>` or `<height>`. ex: `5000X760`"
            )
        else:
            size[idx] = int(s)
    return size


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-i",
        "--input",
        dest="input",
        type=str,
        required=True,
        help="Sets the path of Input Folder",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        type=str,
        required=True,
        help="Saves at specified output path",
    )
    parser.add_argument(
        "-s",
        "--size",
        dest="size",
        type=size_format,
        required=True,
        help="Sets the value of the Rough Panel Height And Width, hXw",
    )
    parser.add_argument(
        "-t",
        "--type",
        dest="output_format",
        type=str,
        default="jpg",
        choices=["png", "jpeg", "jpg", "webp", "psb", "psd"],
        help="Sets the type/format of the Output Image Files",
    )
    parser.add_argument("-r", "--recursive", dest="recursive", action="store_true")
    parser.add_argument("-a", "--as-archive", dest="as_archive", action="store_true")
    parser.add_argument(
        "-p",
        "--progress",
        dest="show_progress",
        action="store_true",
        help="Shows a progress bar",
        default=False,
    )
    advanced = parser.add_argument_group("Advanced")
    advanced.add_argument(
        "-w",
        "--width-enforcement",
        dest="width_enforcement",
        type=str,
        default="none",
        choices=("none", "auto"),
        help="Width Enforcement Technique, Default=None)",
    )
    advanced.add_argument(
        "-d",
        "--detection-type",
        type=str,
        dest="detection_type",
        default="pixel",
        choices=["none", "pixel"],
        help="Sets the type of Slice Location Detection, Default=pixel (Pixel Comparison)",
    )
    advanced.add_argument(
        "-e",
        "--sensitivity",
        dest="sensitivity",
        type=int,
        default=90,
        choices=range(0, 101),
        metavar="[0-100]",
        help="Sets the Object Detection sensitivity Percentage, Default=90 (10 percent tolerance)",
    )
    advanced.add_argument(
        "-q",
        "--quality",
        dest="lossy_quality",
        type=int,
        default=100,
        choices=range(0, 101),
        metavar="[1-100]",
        help="Sets the quality of lossy file types like .jpg if used, Default=100 (100 percent)",
    )
    advanced.add_argument(
        "-g",
        "--ingorable_pixels",
        dest="ignorable_pixels",
        type=positive_int,
        default=5,
        help="Sets the value of Ignorable Border Pixels, Default=5 (5px)",
    )
    advanced.add_argument(
        "-l",
        "--line-steps",
        dest="line_steps",
        type=int,
        default=5,
        choices=range(1, 100),
        metavar="[1-100]",
        help="Sets the value of Scan Line Step, Default=5 (5px)",
    )
    general = parser.add_argument_group("General")
    general.add_argument(
        "--log-level",
        dest="log_level",
        default="error",
        choices=["error", "debug", "info"],
        help="Sets log level",
    )
    general.add_argument(
        "--log-file",
        dest="log_file",
        default=sys.stdout,
        help="Sets the log file, this supports providing datatime format.",
    )
    return parser.parse_args()


def main():
    kwargs = get_args()

    global Logger
    Logger = get_logger(
        log_level=log_level(kwargs.log_level),
        filename=kwargs.log_file,
    )

    stitch_params = {
        "detection_type": kwargs.detection_type,
        "sensitivity": kwargs.sensitivity,
        "width_enforce": kwargs.width_enforcement,
        "custom_width": kwargs.size[1],
        "line_steps": kwargs.line_steps,
        "ignorable_pixels": kwargs.ignorable_pixels,
    }

    try:
        process(
            input=kwargs.input,
            output=kwargs.output,
            split_height=kwargs.size[0],
            output_format=kwargs.output_format,
            recursive=kwargs.recursive,
            as_archive=kwargs.as_archive,
            lossy_quality=kwargs.lossy_quality,
            show_progress=kwargs.show_progress,
            params=stitch_params,
        )
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

    else:
        return 0


if __name__ == "__main__":
    exit(main())
