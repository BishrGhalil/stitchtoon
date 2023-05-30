from pathlib import Path

import pytest
from PIL import Image

from stitchtoon.const import FORMATS

DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def test_images_files(data_dir: Path = DATA_DIR) -> list[str]:
    imgs_files = (
        [ent for ent in data_dir.glob("*.jpeg")]
        + [ent for ent in data_dir.glob("*.png")]
        + [ent for ent in data_dir.glob("*.webp")]
    )
    return imgs_files


@pytest.fixture
def test_images(test_images_files) -> list[Image.Image]:
    return [Image.open(imgf) for imgf in test_images_files]


@pytest.fixture
def test_images_rgb(data_dir: Path = DATA_DIR) -> list[Image.Image]:
    return [Image.open(ent) for ent in data_dir.glob("*.jpeg")]


@pytest.fixture
def test_images_rgba(data_dir: Path = DATA_DIR) -> list[Image.Image]:
    return [Image.open(ent) for ent in data_dir.glob("*.webp")] + [
        Image.open(ent) for ent in data_dir.glob("*.png")
    ]


@pytest.fixture
def test_archive_file(data_dir: Path = DATA_DIR) -> str:
    return [ent for ent in data_dir.glob("*.zip")][0]
