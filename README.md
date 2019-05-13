# Stupid reCURsiVe Yet Superb INstaller

<img src="scurvy-logo.svg" style="height:256px;width:256px" />

Simple tool that installs a package getting as much
dependencies as possible using `conda` and `pip`
in the remaining items from the dependency tree.

**WARNING**: This is pre-alpha quality code.

## Usage

```
scurvy name-of-the-package
```

## Examples

Package in pip with conda-available dependencies:

```
scurvy fmf
```

Package available in conda:

```
scurvy flask
```

Package in pip with dependencies with conda-available dependencies:

```
scurvy modin
```

Non-existent package:

```
scurvy non-existent-package-0xxuhihihui
```

## Acknowledgements

The image is a blend of <https://commons.wikimedia.org/wiki/File:Face-badtooth.svg> and
the official logo of Python from <https://www.python.org/community/logos/>.

