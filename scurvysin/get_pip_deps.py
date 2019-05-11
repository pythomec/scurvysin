#!/usr/bin/env python3
import json
import subprocess
import tempfile
import os
from itertools import chain
import shutil

import click

from pip._internal.resolve import Resolver
from pip._internal.exceptions import HashError, HashErrors
from pip._internal import main


def get_dependencies(r):
    try:
        found_reqs = []
        
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
            discovered_reqs = []  # type: List[InstallRequirement]
            hash_errors = HashErrors()

            steps = 0
            for req in chain(root_reqs, discovered_reqs):
                try:
                    discovered_reqs.extend(
                        self._resolve_one(requirement_set, req)
                    )
                    steps += 1
                    if steps == 1:
                        break
                except HashError as exc:
                    exc.req = req
                    hash_errors.append(exc)

            found_reqs.extend(discovered_reqs)
            if hash_errors:
                raise hash_errors

        Resolver.resolve = new_resolve

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                os.chdir(tmpdir)
                main(["download", r, "-qqqqq"])
        except:
            pass
        
    finally:
        pass
    
    return found_reqs


@click.command()
@click.argument("REQ")
def run(req):
    deps = get_dependencies(req)
    data  = {dep.name : str(dep.req) for dep in deps}
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    run()