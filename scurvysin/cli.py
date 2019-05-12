#!/usr/bin/env python3
import sys
import argparse

from scurvysin import try_install, Coflags, Pipflags

def extopts(args: argparse.Namespace):
    return {"show_only" : args.show_only}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', '-d', action='store_true',
                        help="don't let conda/pip perform installation")
    parser.add_argument('--show-only', action='store_true',
                        help="only show what would be done")
    parser.add_argument('req', help="distribution to install")
    args = parser.parse_args()

    try_install(args.req, extopts(args), Coflags(args), Pipflags(args))


if __name__ == "__main__":
    main()
