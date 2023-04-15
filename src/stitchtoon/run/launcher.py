import argparse
import sys

from .. import __version__
from ..services.process import process


def positive_int(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-i",
        dest="input",
        type=str,
        required=True,
        help="Sets the path of Input Folder",
    )
    parser.add_argument(
        "-o",
        dest="output",
        type=str,
        required=False,
        help="Saves at specified output path",
    )
    parser.add_argument(
        "-sh",
        dest="split_height",
        type=positive_int,
        required=True,
        help="Sets the value of the Rough Panel Height",
    )
    parser.add_argument(
        "-t",
        "--type",
        dest="output_format",
        type=str,
        default="jpg",
        choices=["png", "jpg", "webp", "psb", "psd"],
        help="Sets the type/format of the Output Image Files",
    )
    parser.add_argument("-r", "--recursive", dest="recursive", action="store_true")
    parser.add_argument("-a", "--as-archive", dest="as_archive", action="store_true")
    advanced = parser.add_argument_group("Advanced")
    advanced.add_argument(
        "-cw",
        dest="custom_width",
        type=positive_int,
        default=-1,
        help="[Advanced] Forces Fixed Width for All Output Image Files, Default=None (Disabled)",
    )
    advanced.add_argument(
        "-dt",
        type=str,
        dest="detection_type",
        default="pixel",
        choices=["none", "pixel"],
        help="[Advanced] Sets the type of Slice Location Detection, Default=pixel (Pixel Comparison)",
    )
    advanced.add_argument(
        "-s",
        dest="senstivity",
        type=int,
        default=90,
        choices=range(0, 101),
        metavar="[0-100]",
        help="[Advanced] Sets the Object Detection Senstivity Percentage, Default=90 (10 percent tolerance)",
    )
    advanced.add_argument(
        "-lq",
        dest="lossy_quality",
        type=int,
        default=100,
        choices=range(0, 101),
        metavar="[1-100]",
        help="[Advanced] Sets the quality of lossy file types like .jpg if used, Default=100 (100 percent)",
    )
    advanced.add_argument(
        "-ip",
        dest="ignorable_pixels",
        type=positive_int,
        default=5,
        help="[Advanced] Sets the value of Ignorable Border Pixels, Default=5 (5px)",
    )
    advanced.add_argument(
        "-sl",
        dest="line_steps",
        type=int,
        default=5,
        choices=range(1, 100),
        metavar="[1-100]",
        help="[Advanced] Sets the value of Scan Line Step, Default=5 (5px)",
    )
    return parser.parse_args()


def launch():
    kwargs = get_args()

    stitch_params = {
        "detection_type": kwargs.detection_type,
        "senstivity": kwargs.senstivity,
        "custom_width": kwargs.custom_width,
        "line_steps": kwargs.line_steps,
        "ignorable_pixels": kwargs.ignorable_pixels,
    }

    process(
        input=kwargs.input,
        output=kwargs.output,
        split_height=kwargs.split_height,
        output_format=kwargs.output_format,
        recursive=kwargs.recursive,
        as_archive=kwargs.as_archive,
        lossy_quality=kwargs.lossy_quality,
        params=stitch_params,
    )


if __name__ == "__main__":
    launch()
