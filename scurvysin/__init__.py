"""
ScurvySin
---------
Simple tool that installs a package getting as much
dependencies as possible using `conda` and `pip`
in the remaining items from the dependency tree.
"""

import json
import os
import subprocess
import sys
from pkg_resources import Requirement, Environment
from typing import Dict, List


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

    def expfl(self) -> list:
        if self.dry_run:
            return ['--dry-run']
        else:
            return []


class PipFlags:
    """Class representing optional flags for pip requested by user"""

    def __init__(self, args):
        """
        transform args given to the main program to pip flags
        """
        self.dry_run = args.dry_run

    def expfl(self) -> list:
        # pip does not have a --dry-run option, but download is more or less
        # a dry run counterpart to install.
        if self.dry_run:
            return ['download']
        else:
            return ['install']


def already_satisfied(req: str) -> bool:
    requirement = Requirement(req)
    environment = Environment()
    return any(dist in requirement for dist in environment[requirement.name])


def available_in_conda(req: str) -> bool:
    r = subprocess.run([CONDA_COMMAND, "install", "-d", req],
                       stderr=subprocess.PIPE,
                       stdout=subprocess.PIPE)
    return not(r.returncode)


def install_using_conda(req: str, flags: CondaFlags) -> None:
    subprocess.call([CONDA_COMMAND, "install", "-S", "-y"] + flags.expfl() + [req])


def install_using_pip(req: str, flags: PipFlags) -> None:
    subprocess.call(["pip"] +  flags.expfl() + ["--no-deps", req])


def get_pip_requirements(req: str) -> Dict[str, str]:
    abspath = os.path.abspath(os.path.dirname(__file__))
    dep_script = os.path.join(abspath, "get_pip_deps.py")
    
    r = subprocess.run([sys.executable, dep_script, req],
                       stdout=subprocess.PIPE)
    try:
        # print(r.stdout)
        data = json.loads(r.stdout)
        if "error" in data:
            print(f"Error: {data['error']}")
            exit(1)
        else:
            return data["requirements"]
    except json.decoder.JSONDecodeError as err:
        print("Invalid JSON")
        exit(1)


def parse_requirements_file(path: str) -> List[str]:
    reqs = []
    with open(path, "r") as infile:
        for line in infile:
            line = line.strip()
            if line.startswith("-"):
                raise NotImplementedError("Pip flags in requirements files are not understood.")
            elif not line or line.startswith("#"):
                continue
            else:
                reqs.append(line)
    return list(sorted(reqs))


def try_install(req: str, opts: dict, coflags: CondaFlags, pipflags: PipFlags) -> None:
    if os.environ.get("VIRTUAL_ENV"):
        print("In a virtual environment, please use the `pip` command.")
        exit(-1)        

    if opts.pop("requirement", False):
        print(f"Reading requirements file {req}")
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
        requirements = get_pip_requirements(req)
        print(f"Dependencies for {req}: {list(requirements.values())}.")
        for requirement in requirements.values():
            try_install(requirement, opts, coflags, pipflags)
        if opts["show_only"]:
            print(f"Would install {req} using pip.")
        else:
            print(f"Installing {req} using pip.")
            install_using_pip(req, pipflags)
