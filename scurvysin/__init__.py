import json
import os
import subprocess
import sys
from typing import Dict


def available_in_conda(req: str) -> bool:
    status, _ = subprocess.getstatusoutput(["conda", "install", "-d", req])
    return not(status)


def install_using_conda(req: str):
    subprocess.call(["conda", "install", "-S", "-y", req])


def install_using_pip(req: str):
    subprocess.call(["pip", "install", req])


def get_pip_requirements(req: str) -> Dict[str, str]:
    abspath = os.path.abspath(os.path.dirname(__file__))
    dep_script = os.path.join(abspath, "get_pip_deps.py")
    output = subprocess.getoutput([sys.executable, dep_script, req])
    try:
        data = json.loads(output)
        if "error" in data:
            print(f"Error: {data['error']}")
            exit(-2)
        else:
            return data["requirements"]
    except json.decoder.JSONDecodeError as err:
        print("Invalid JSON")
        exit(-1)


def try_install(req: str):
    print(f"Checking {req} in conda...")
    if available_in_conda(req):
        print(f"Package {req} found in conda.")
        install_using_conda(req)
    else:
        print(f"Checking dependencies for {req} using pip...")
        requirements = get_pip_requirements(req)
        print(f"Dependencies for {req}: {list(requirements.values())}.")
        for requirement in requirements.values():
            try_install(requirement)
        print(f"Installing {req} using pip.")
        install_using_pip(req)
