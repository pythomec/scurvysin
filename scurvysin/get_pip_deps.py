#!/usr/bin/env python3
import json
import subprocess
import tempfile
import os
import shutil
from io import StringIO
import sys

from pip._internal.resolve import Resolver
from pip._internal.exceptions import HashError, HashErrors
from pip._internal import main


def get_dependencies(r):
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()

    try:
        found_reqs = []  # type: List[InstallRequirement]
        
        def new_resolve(self, requirement_set):
            # make the wheelhouse
            if self.preparer.wheel_download_dir:
                ensure_dir(self.preparer.wheel_download_dir)

            # If any top-level requirement has a hash specified, enter
            # hash-checking mode, which requires hashes from all.
            root_reqs = (
                requirement_set.unnamed_requirements +
                list(requirement_set.requirements.values())
            )
            self.require_hashes = (
                requirement_set.require_hashes or
                any(req.has_hash_options for req in root_reqs)
            )

            # Display where finder is looking for packages
            locations = self.finder.get_formatted_locations()
            if locations:
                logger.info(locations)

            # Actually prepare the files, and collect any exceptions. Most hash
            # exceptions cannot be checked ahead of time, because
            # req.populate_link() needs to be called before we can make decisions
            # based on link type.
            hash_errors = HashErrors()

            for req in root_reqs:
                try:
                    found_reqs.extend(
                        self._resolve_one(requirement_set, req)
                    )
                except HashError as exc:
                    exc.req = req
                    hash_errors.append(exc)

            if hash_errors:
                raise hash_errors

        Resolver.resolve = new_resolve

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                os.chdir(tmpdir)
                main(["download", r, "-qqqqq"])
        except:
            pass

        if "Could not find" in sys.stderr.getvalue():
            raise RuntimeError("Not found.")
        
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
    
    return found_reqs


def run():
    req = sys.argv[1]
    try:
        deps = get_dependencies(req)
        data = {
            "requirements": {
                dep.name : str(dep.req) for dep in deps
            }
        }
    except RuntimeError as exc:
        data = {
            "error": str(exc)
        }
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    run()
