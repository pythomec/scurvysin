import json
from optparse import Values
import os
import sys
import tempfile
import warnings
from io import StringIO
from typing import List

import pip


def _version_to_string(version: List[int]) -> str:
    return ".".join(str(v) for v in version)


MIN_ALLOWED_PIP = [21, 1]
pip_major_minor = [int(v) for v in pip.__version__.split(".")[:2]]
if pip_major_minor < MIN_ALLOWED_PIP:
    raise ImportError(
        f"Invalid pip version: {_version_to_string(pip_major_minor)}, "
        "please use at least {_version_to_string(MIN_ALLOWED_PIP)}."
    )

# Sin: Importing from protected modules
from pip._internal.commands.download import (
    DownloadCommand,
    make_target_python,
    normalize_path,
    ensure_dir,
    TempDirectory,
    get_requirement_tracker,
    with_cleanup,
    cmdoptions,
    SUCCESS,
)
from pip._internal.req.req_install import InstallRequirement


def get_pip_dependencies(r: str) -> List[InstallRequirement]:
    """Get direct dependencies for a requirement string.

    :param r: Requirement - it can be a package name or a name
       with version specification.

    It runs the equivalent of `pip download` command
    with a patched run.

    Examples:
        >>> get_dependencies("pandas==0.24")
        [<InstallRequirement object: numpy>=1.12.0 (from pandas==0.24) editable=False>,
         <InstallRequirement object: python-dateutil>=2.5.0 (from pandas==0.24) editable=False>,
         <InstallRequirement object: pytz>=2011k (from pandas==0.24) editable=False>]
    """
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()

    requirements = []

    class FakeDownloadCommand(DownloadCommand):
        @with_cleanup
        def run(self, options: Values, args: List[str]) -> int:
            print(options)

            options.ignore_installed = True
            # editable doesn't really make sense for `pip download`, but the bowels
            # of the RequirementSet code require that property.
            options.editables = []

            cmdoptions.check_dist_restriction(options)

            options.download_dir = normalize_path(options.download_dir)
            ensure_dir(options.download_dir)

            session = self.get_default_session(options)

            target_python = make_target_python(options)
            finder = self._build_package_finder(
                options=options,
                session=session,
                target_python=target_python,
                ignore_requires_python=options.ignore_requires_python,
            )

            req_tracker = self.enter_context(get_requirement_tracker())

            directory = TempDirectory(
                delete=not options.no_clean,
                kind="download",
                globally_managed=True,
            )

            reqs = self.get_requirements(args, options, finder, session)

            preparer = self.make_requirement_preparer(
                temp_build_dir=directory,
                options=options,
                req_tracker=req_tracker,
                session=session,
                finder=finder,
                download_dir=options.download_dir,
                use_user_site=False,
            )

            resolver = self.make_resolver(
                preparer=preparer,
                finder=finder,
                options=options,
                ignore_requires_python=options.ignore_requires_python,
                py_version_info=options.python_version,
            )

            self.trace_basic_info(finder)

            requirement_set = resolver.resolve(reqs, check_supported_wheels=True)

            nonlocal requirements
            for req in requirement_set.requirements.values():
                requirements.append(req)

            return SUCCESS

    try:
        command = FakeDownloadCommand("ignore", "ignore")
        command.main([r])
        requirements.sort(key=lambda l: l.name)

        # The set contains the package itself, so we need to remove it.
        return [l for l in requirements if str(l.req) != r]

    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
