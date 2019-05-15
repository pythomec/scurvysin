# Stupid reCURsiVe Yet Superb INstaller

<img src="logo.png" height="256" width="256" />

[![PyPI version](https://badge.fury.io/py/scurvysin.svg)](https://badge.fury.io/py/scurvysin)

Simple tool that installs a package getting as much
dependencies as possible using `conda` and `pip`
in the remaining items from the dependency tree.

**WARNING**: This is pre-alpha quality code. It is not optimized,
it does not cache intermediate results and it prints perhaps
more information than necessary. It also can stop working.

## Requirements

- Python 3.6
- conda *if the tool is to have any sense*

Tested against:

- pip 18.1
- conda 4.6.12

## Installation

Just use the regular pip install:

```
pip install scurvysin
```

## Usage

This package is designed to be used as a command-line tool.
You might reuse it as a library but the API is not designed
with this in mind (and it may lead to complications due 
to global state).

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

Logo courtesy of Pavel Pipek, based on the the official logo of Python from <https://www.python.org/community/logos/>.

