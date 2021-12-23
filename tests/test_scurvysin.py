import os
import subprocess
import unittest

from scurvysin import get_pip_requirements, NotFoundError


class TestGetPipDeps(unittest.TestCase):
    def setUp(self) -> None:
        # TODO: Forbid all custom pypi indices.
        os.environ["PIP_INDEX_URL"] = "https://pypi.python.org/simple"

    def test_non_existent(self):
        def invoke():
            get_pip_requirements("non-existent-package-please-do-not-create-it-qqqqq")
        self.assertRaises(NotFoundError, invoke)

    def test_existent(self):
        # TODO: Implement
        fail


if __name__ == '__main__':
    unittest.main()