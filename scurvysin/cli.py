#!/usr/bin/env python3
import sys
import argparse

from scurvysin import try_install, Coflags, Pipflags


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', '-d', action='store_true')
    parser.add_argument('req')
    args = parser.parse_args()

    try_install(args.req, Coflags(args), Pipflags(args))


if __name__ == "__main__":
    main()
