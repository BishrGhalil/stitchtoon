<div align="center">
  <h1>Stitch Toon</h1>
  <p>
    A powerful package for stitching and cutting webtoons/manhwa/manhua raws.
  </p>
  <p>
    A GUI version is available at <a href="https://github.com/BishrGhalil/stitchtoon-gui"><b>Stitchtoon GUI</b></a>

 <a href="https://discord.gg/vgWyc3tNnK">Discord Server</a>.

  </p>
    <img src="https://github.com/BishrGhalil/stitchtoon/actions/workflows/python-test.yml/badge.svg?branch=new-api">
  <a href="https://github.com/BishrGhalil/stitchtoon/releases/latest">
    <img src="https://img.shields.io/github/v/release/BishrGhalil/stitchtoon">
  </a>
  <a href="https://github.com/BishrGhalil/stitchtoon/releases/latest">
    <img src="https://img.shields.io/github/release-date/BishrGhalil/stitchtoon">
  </a>
  <a href="https://github.com/BishrGhalil/stitchtoon/tree/dev">
    <img src="https://img.shields.io/github/last-commit/BishrGhalil/stitchtoon">
  </a>
  <a href="https://github.com/BishrGhalil/stitchtoon/blob/dev/LICENSE">
    <img src="https://img.shields.io/github/license/BishrGhalil/stitchtoon">
  </a>
  </div>

## Install
Install with pip
```
pip install stitchtoon
```

Install from source
```
git clone https://github.com/BishrGhalil/stitchtoon
cd stitchtoon
pip instal --user requirements.txt
pip install .
```

## Basic usage
 ```
 usage: stitchtoon [-h] [--version] [-f FORMAT] [-r | --recursive | --no-recursive] [--archive] [--width PX]
                  [--progress | --no-progress] [-m {pixel,direct}] [-H PX]
                  [--x-margins PX] [--sensitivity PCT] [--max-height VALUE]
                  [--min-height VALUE] [--division-factor N] [--window N]
                  INPUT OUTPUT

Stitch and slice webtoon/manhwa/manhua raws.

positional arguments:
  INPUT                 Input path: a directory of images or a .zip archive
  OUTPUT                Output directory path

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --progress, --no-progress
                        Show a progress bar while processing (default: True)

I/O Options:
  -f FORMAT, --format FORMAT
                        Output image format. Supported: BMP, jpeg, png, PSB, PSD, tga, tiff, webp (default: jpg)
  -r, --recursive, --no-recursive
                        Recursively scan subdirectories (default: True)
  --archive             Pack each output directory into a zip archive (default: False)
  --width PX            Normalize all images to this width before processing. If omitted, auto-resize to the minimum width found (default: None)

Detection Options:
  -m {pixel,direct}, --method {pixel,direct}
                        Slice detection method (default: pixel)
  -H PX, --height PX    Target slice height in pixels. Required for 'pixel' and 'direct' methods (default: None)

Pixel Detection Options:
  Fine-tuning options only used when --method=pixel

  --x-margins PX        Pixels to ignore on the left and right edges during detection (default: 0)
  --sensitivity PCT     Detection accuracy (1-100 percent; lower = more permissive) (default: 100)
  --max-height VALUE    Maximum slice height. -1 means no limit. A float < height is treated as a fraction of --height; an int is treated as pixels (default: -1)
  --min-height VALUE    Minimum slice height. -1 means no limit. A float < height is treated as a fraction of --height; an int is treated as pixels (default: -1)
  --division-factor N   Downscale factor applied before detection (1-5). Higher values are faster but less accurate (default: 1)
  --window N            Consecutive valid rows required to confirm a slice position. 1 = single-row (default). Values of 5-20 add robustness for noisy content (default: 1)
 ```
