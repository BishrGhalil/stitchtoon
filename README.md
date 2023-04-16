# StitchToon
A powerful package for stitching and cutting webtoons/manhwa/manhua raws.

All thanks to [MechTechnology](https://github.com/MechTechnology) for creating [SmartStitch](https://github.com/MechTechnology/SmartStitch) which is the base of this package.


## New features
- export as archive
- better output naming handling
- size limites for defferent output formats

## Install

Build from source
```
git clone https://github.com/BishrGhalil/stitchtoon
cd stitchtoon
pip instal --user requirements.txt
pip install .
```

## Basic usage
```
stitchtoon -i <input-path> -sh <split-height>
```
Check out `help` for more advanced options
```
stitchtoon --help
```
