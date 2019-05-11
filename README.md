# Stupid reCURsiVe Yet Superb INstaller

Simple tool that installs a package getting as much
dependencies as possible using `conda` and `pip`
in the remaining items from the dependency tree.

**WARNING**: This is pre-alpha quality code.

## Usage

```
scurvy name-of-the-packages
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

Non-existent package:

```
scurvy non-existent-package-0xxuhihihui
```