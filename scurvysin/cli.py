#!/usr/bin/env python3
import sys

from scurvysin import try_install


def main():
    req = sys.argv[1]
    try_install(req)


if __name__ == "__main__":
    main()