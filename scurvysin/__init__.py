"""
ScurvySin
---------
Simple tool that installs a package getting as much
dependencies as possible using `conda` and `pip`
in the remaining items from the dependency tree.
"""

import argparse
import json
import os
import subprocess
import sys
from pkg_resources import Requirement, Environment
from typing import Dict, List

from scurvysin.pip_deps import get_pip_dependencies

__version__ = "2021.0"


MAMBA_AVAILABLE = subprocess.getstatusoutput("mamba -V")[0] == 0
CONDA_AVAILABLE = subprocess.getstatusoutput("conda -V")[0] == 0

if not CONDA_AVAILABLE and not MAMBA_AVAILABLE:
    print("Neither conda nor mamba is available.")
    exit(1)

if MAMBA_AVAILABLE and not os.environ.get("DISABLE_MAMBA"):
    CONDA_COMMAND = "mamba"
else:
    CONDA_COMMAND = "conda"


class CondaFlags:
    """Class representing optional flags for conda requested by user"""

    def __init__(self, args):
        """
        transform args given to the main program to anaconda flags
        """
        self.dry_run = args.dry_run

    def expfl(self) -> List[str]:
        if self.dry_run:
            flags = ["--dry-run"]
        else:
            flags = []
        if CONDA_COMMAND == "mamba":
            flags.append("--no-banner")
        return flags


class PipFlags:
    """Class representing optional flags for pip requested by user"""

    def __init__(self, args):
        """
        transform args given to the main program to pip flags
        """
        self.dry_run = args.dry_run

    def expfl(self) -> List[str]:
        # pip does not have a --dry-run option, but download is more or less
        # a dry run counterpart to install.
        if self.dry_run:
            return ["download"]
        else:
            return ["install"]


class PipArgumentParser(argparse.ArgumentParser):
    """Parser to support additional pip --arguments"""

    def __init__(self):
        super().__init__()
        self.add_argument(
            "-r",
            "--requirement",
            dest="requirement_file",
            help="Path to pip requirements file.",
        )


def already_satisfied(req: str) -> bool:
    requirement = Requirement(req)
    environment = Environment()
    return any(dist in requirement for dist in environment[requirement.name])


def available_in_conda(req: str) -> bool:
    r = subprocess.run(
        [CONDA_COMMAND, "install", "-d", req],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    return not (r.returncode)


def install_using_conda(req: str, flags: CondaFlags) -> None:
    subprocess.call([CONDA_COMMAND, "install", "-S", "-y"] + flags.expfl() + [req])


def install_using_pip(req: str, flags: PipFlags) -> None:
    subprocess.call(["pip"] + flags.expfl() + ["--no-deps", req])


def parse_requirements_file(path: str) -> List[str]:
    reqs = []
    with open(path, "r") as infile:
        for line in infile:
            line = line.split("#", maxsplit=1)[0].strip()
            if line.startswith("-"):
                try:
                    pip_args = PipArgumentParser().parse_args(line.split())
                except Exception as err:
                    print(f"Error parsing pip args: {err}")
                reqs += parse_requirements_file(
                    os.path.join(os.path.dirname(path), pip_args.requirement_file)
                )
            elif not line:
                continue
            else:
                reqs.append(line)
    return list(sorted(reqs))


def try_install(req: str, opts: dict, coflags: CondaFlags, pipflags: PipFlags) -> None:
    print(f"Trying to install {req}...")
    if os.environ.get("VIRTUAL_ENV"):
        print("In a virtual environment, please use the `pip` command.")
        exit(-1)

    if opts.pop("requirement", False):
        print(f"Reading requirements file {req}...")
        requirements = parse_requirements_file(req)
        print(f"Dependencies from {req}: {requirements}.")
        for requirement in requirements:
            try_install(requirement, opts, coflags, pipflags)
        return
    if already_satisfied(req):
        print(f"Condition {req} already satistfied.")
        return
    print(f"Checking {req} using {CONDA_COMMAND}...")
    if available_in_conda(req):
        print(f"Package {req} found with {CONDA_COMMAND}.")
        if opts["show_only"]:
            print(f"Would install {req} using {CONDA_COMMAND}.")
        else:
            print(f"Installing {req} using {CONDA_COMMAND}.")
            install_using_conda(req, coflags)
    else:
        print(f"Checking dependencies for {req} using pip...")
        requirements = get_pip_dependencies(req)
        req_strings = [str(req.req) for req in requirements]
        print(f"Dependencies for {req}: {req_strings}.")
        for requirement in req_strings:
            try_install(requirement, opts, coflags, pipflags)
        if opts["show_only"]:
            print(f"Would install {req} using pip.")
        else:
            print(f"Installing {req} using pip.")
            install_using_pip(req, pipflags)
