import json
import os
import subprocess
import sys
from typing import Dict

class Coflags:
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

class Pipflags:
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


def available_in_conda(req: str) -> bool:
    r = subprocess.run(["conda", "install", "-d", req],
                       stderr=subprocess.PIPE,
                       stdout=subprocess.PIPE)
    return not(r.returncode)


def install_using_conda(req: str, flags: Coflags):
    subprocess.call(["conda", "install", "-S", "-y"] + flags.expfl() + [req])


def install_using_pip(req: str, flags: Pipflags):
    subprocess.call(["pip"] +  flags.expfl() + ["--no-deps", req])


def get_pip_requirements(req: str) -> Dict[str, str]:
    abspath = os.path.abspath(os.path.dirname(__file__))
    dep_script = os.path.join(abspath, "get_pip_deps.py")
    r = subprocess.run([sys.executable, dep_script, req],
                       stdout=subprocess.PIPE)
    try:
        data = json.loads(r.stdout)
        if "error" in data:
            print(f"Error: {data['error']}")
            exit(1)
        else:
            return data["requirements"]
    except json.decoder.JSONDecodeError as err:
        print("Invalid JSON")
        exit(1)


def try_install(req: str, opts: dict, coflags: Coflags, pipflags: Pipflags):
    print(f"Checking {req} in conda...")
    if available_in_conda(req):
        print(f"Package {req} found in conda.")
        if opts["show_only"]:
            print(f"Would install {req} using conda.")
        else:
            print(f"Installing {req} using conda.")
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
