<div align="center">
  <h1>Stitch Toon</h1>
  <p>
    A powerful package for stitching and cutting webtoons/manhwa/manhua raws.
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
 

## New features
- export as archive
- better output naming handling
- size limites for defferent output formats

## Install
Via Pip
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
stitchtoon -i <input-path> -s <split-height>
```
Check out `help` for more advanced options
```
stitchtoon --help
```

 
> All thanks to [MechTechnology](https://github.com/MechTechnology) for creating [SmartStitch](https://github.com/BishrGhalil/stitchtoon) which is the base of this package.
