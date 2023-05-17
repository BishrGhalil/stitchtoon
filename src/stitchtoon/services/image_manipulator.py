from PIL import Image as pilImage

from ..utils.constants import WIDTH_ENFORCEMENT
from ..utils.errors import SizeLimitError
from .global_logger import logFunc
from .image_directory import Image
from .progressbar import ProgressHandler


class ImageManipulator:
    @logFunc
    @staticmethod
    def _resize_img(img: Image, new_img_width) -> Image:
        if img.width == new_img_width:
            return img
        img_ratio = float(img.height / img.width)
        new_img_height = int(img_ratio * new_img_width)
        if new_img_height > 0:
            img.pil = img.pil.resize(
                (new_img_width, new_img_height), pilImage.Resampling.LANCZOS
            )
        return img

    @logFunc(inclass=True)
    @staticmethod
    def resize(
        img_objs: list[Image],
        enforce_setting: WIDTH_ENFORCEMENT,
        custom_width: int = 720,
    ) -> list[Image]:
        """Resizes all given images according to the set enforcement setting.

        Args:
            img_objs (list[Image])
            enforce_setting WIDTH_ENFORCEMENT
            custom_width (int, optional). Defaults to 720.

        Returns:
            list[Image]
        """

        if enforce_setting == WIDTH_ENFORCEMENT.NONE.value and not custom_width:
            return img_objs

        new_img_width = 0
        if enforce_setting == WIDTH_ENFORCEMENT.COPYWRITE.value:
            if len(img_objs) >= 2:
                new_img_width = img_objs[1].width
                ImageManipulator._resize_img(img_objs[0], new_img_width)
            return img_objs

        elif enforce_setting == WIDTH_ENFORCEMENT.AUTO.value:
            widths, heights = zip(*(img.size for img in img_objs))
            new_img_width = min(widths)

        elif enforce_setting == WIDTH_ENFORCEMENT.FIXED.value or custom_width:
            new_img_width = custom_width

        for img in img_objs:
            ImageManipulator._resize_img(img, new_img_width)

        return img_objs

    @logFunc(inclass=True)
    @staticmethod
    def combine(
        img_objs: list[Image], progress: ProgressHandler = None, increment: int = 0
    ) -> Image:
        """Combines given image objs to a single vertically stacked single image obj.

        Args:
            img_objs (list[Image])
            progress (_type_, optional)
            increment (int, optional). Defaults to 0.

        Returns:
            Image
        """

        if not progress:
            progress = ProgressHandler()
        widths, heights = zip(*(img.size for img in img_objs))
        combined_img_width = max(widths)
        combined_img_height = sum(heights)
        combined_img = pilImage.new("RGBA", (combined_img_width, combined_img_height))
        combine_offset = 0
        images_len = len(img_objs)
        for idx, img in enumerate(img_objs, 1):
            combined_img.paste(img.pil, (0, combine_offset))
            combine_offset += img.height
            img.pil.close()
            progress.update(progress.value + increment, f"Combined {idx}/{images_len}")

        img = Image(
            path=img_objs[0].path, format=img_objs[0].format, name=img_objs[0].name
        )
        img.pil = combined_img
        progress.update(progress.value, "All combined")
        return img

    @logFunc(inclass=True)
    @staticmethod
    def slice(
        combined_img: Image,
        slice_locations: list[int],
        progress: ProgressHandler = None,
        increment: int = 0,
    ) -> list[Image]:
        """Combines given combined img to into multiple img slices given the slice locations.

        Args:
            combined_img (Image)
            slice_locations (list[int])

        Returns:
            list[Image]
        """

        if not progress:
            progress = ProgressHandler()

        max_width = combined_img.width
        min_width = 0
        img_objs = []
        total_slices = len(slice_locations)
        for index in range(1, total_slices):
            upper_limit = slice_locations[index - 1]
            lower_limit = slice_locations[index]
            if lower_limit < upper_limit:
                continue
            slice_boundaries = (min_width, upper_limit, max_width, lower_limit)
            try:
                img_slice = combined_img.pil.crop(slice_boundaries)
                bbox = img_slice.getbbox()
                if bbox:
                    img_slice = img_slice.crop(bbox)
                progress.update(
                    progress.value + increment, f"sliced {index}/{total_slices}"
                )
            except ValueError:
                raise SizeLimitError("Images to small to slice")
            img = combined_img.copy()
            img.pil = img_slice
            img_objs.append(img)
        combined_img.pil.close()
        progress.update(progress.value, "All sliced")
        return img_objs
