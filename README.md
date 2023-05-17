<div align="center">
  <h1>Stitch Toon</h1>
  <p>
    A powerful package for stitching and cutting webtoons/manhwa/manhua raws.
  </p>
  <p>
    A GUI version is available at <a href="https://github.com/BishrGhalil/stitchtoon-gui"><b>Stitchtoon GUI</b></a>
  </p>
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
stitchtoon -i <input-path> -s <split-height> -o <output-path>
```
Options
```
usage: stitchtoon [-h] [-V] -i INPUT -o OUTPUT -s SIZE -n IMAGES_NUMBER [-t {png,jpeg,jpg,webp,psb,psd}] [-r] [-a] [-p] [-w {none,auto,copywrite}] [-d {none,pixel}] [-e [0-100]] [-q [1-100]]
                  [-g IGNORABLE_PIXELS] [-l [1-100]] [--write-metadata] [--slice-to-metadata] [--log-level {error,debug,info}] [--log-file LOG_FILE]

options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -i INPUT, --input INPUT
                        Sets the path of Input Folder
  -o OUTPUT, --output OUTPUT
                        Saves at specified output path
  -s SIZE, --size SIZE  Sets the value of the Rough Panel Height And Width, hXw
  -n IMAGES_NUMBER, --images-number IMAGES_NUMBER
                        Sets the value of the Rough Panel Height And Width, hXw
  -t {png,jpeg,jpg,webp,psb,psd}, --type {png,jpeg,jpg,webp,psb,psd}
                        Sets the type/format of the Output Image Files
  -r, --recursive
  -a, --as-archive
  -p, --progress        Shows a progress bar

Advanced:
  -w {none,auto,copywrite}, --width-enforcement {none,auto,copywrite}
                        Width Enforcement Technique, Default=None)
  -d {none,pixel}, --detection-type {none,pixel}
                        Sets the type of Slice Location Detection, Default=pixel (Pixel Comparison)
  -e [0-100], --sensitivity [0-100]
                        Sets the Object Detection sensitivity Percentage, Default=90 (10 percent tolerance)
  -q [1-100], --quality [1-100]
                        Sets the quality of lossy file types like .jpg if used, Default=100 (100 percent)
  -g IGNORABLE_PIXELS, --ignorable_pixels IGNORABLE_PIXELS
                        Sets the value of Ignorable Border Pixels, Default=5 (5px)
  -l [1-100], --line-steps [1-100]
                        Sets the value of Scan Line Step, Default=5 (5px)
  --write-metadata      Writes metadata file, Used to save current images sizes so you can slice to the same sizes when stitching again.
  --slice-to-metadata   Reads metadata file if available, If not available slices according to split_height and images_number options.

General:
  --log-level {error,debug,info}
                        Sets log level
  --log-file LOG_FILE   Sets the log file, this supports providing datatime format.
```

 
> All thanks to [MechTechnology](https://github.com/MechTechnology) for creating [SmartStitch](https://github.com/BishrGhalil/stitchtoon) which is the base of this package.
