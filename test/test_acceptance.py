# /test/test_acceptance.py
#
# Test cases for usage of polysquarecmakelinter.main() and command line
# parsing.
#
# See /LICENCE.md for Copyright information
"""Test cases for usage of polysquarecmakelinter.main()."""

import os

import tempfile

from polysquarecmakelinter import linter

from testtools import TestCase


def run_linter_main(filename, *args, **kwargs):
    """Run linter.main() (as an integration test)."""
    del args

    arguments = [filename]

    def _convert_kv_to_switches(key, value):
        """Convert a key-value pair to command-line switches."""
        append_args = ["--{0}".format(key).replace("_", "-")]

        type_dispatch = {
            bool: [],
            list: value,
            str: [value]
        }

        # We assume that the types in type_dispatch are the only types
        # we'll encounter, all others will throw an exception.
        append_args += type_dispatch[type(value)]
        return append_args

    for key, value in kwargs.items():
        arguments += _convert_kv_to_switches(key, value)

    return linter.main(arguments)


class TestLinterAcceptance(TestCase):
    """Acceptance tests for linter.main()."""

    def __init__(self, *args, **kwargs):
        """"Initialize class variables."""
        cls = TestLinterAcceptance
        super(cls, self).__init__(*args,  # suppress(R0903
                                  **kwargs)
        self._temporary_file = None

    def setUp(self):  # NOQA
        """Create a temporary file."""
        super(TestLinterAcceptance, self).setUp()
        self._temporary_file = tempfile.mkstemp()

    def tearDown(self):  # NOQA
        """Remove temporary file."""
        os.remove(self._temporary_file[1])
        super(TestLinterAcceptance, self).tearDown()

    def test_blacklist(self):
        """Check that blacklisting a test causes it not to run."""
        contents = "function_call()\n"

        with os.fdopen(self._temporary_file[0], "a+") as process_file:
            process_file.write(contents)

        result = run_linter_main(self._temporary_file[1],
                                 blacklist=["style/space_before_func"])
        self.assertEqual(result, 0)

    def test_whitelist_pass(self):
        """Check that whitelisting a test causes only it to run."""
        contents = "    FUNCTION_CALL ()\n"

        with os.fdopen(self._temporary_file[0], "a+") as process_file:
            process_file.write(contents)

        result = run_linter_main(self._temporary_file[1],
                                 whitelist=["style/space_before_func"])

        self.assertEqual(result, 0)

    def test_namespace_pass(self):
        """Check passing a test when using --namespace."""
        contents = "function (our_function)\nendfunction ()\n"

        with os.fdopen(self._temporary_file[0], "a+") as process_file:
            process_file.write(contents)

        result = run_linter_main(self._temporary_file[1],
                                 whitelist=["structure/namespace"],
                                 namespace="our")

        self.assertEqual(result, 0)

    def test_namespace_fail(self):
        """Check failing a test when using --namespace."""
        contents = "function (func)\nendfunction ()\n"

        with os.fdopen(self._temporary_file[0], "a+") as process_file:
            process_file.write(contents)

        result = run_linter_main(self._temporary_file[1],
                                 whitelist=["structure/namespace"],
                                 namespace="our")

        self.assertEqual(result, 1)

    def test_indent_pass(self):
        """Check passing a test when using --indent."""
        contents = "function (our_function)\n  call ()\nendfunction ()\n"

        with os.fdopen(self._temporary_file[0], "a+") as process_file:
            process_file.write(contents)

        result = run_linter_main(self._temporary_file[1],
                                 whitelist=["style/indent"],
                                 indent="2")

        self.assertEqual(result, 0)

    def test_indent_fail(self):
        """Check failing a test when using --indent."""
        contents = "function (our_function)\n  call ()\nendfunction ()\n"

        with os.fdopen(self._temporary_file[0], "a+") as process_file:
            process_file.write(contents)

        result = run_linter_main(self._temporary_file[1],
                                 whitelist=["style/indent"],
                                 indent="4")

        self.assertEqual(result, 1)

    def test_whitelist_fail(self):
        """Check that whitelisting a test causes only it to run."""
        contents = "    FUNCTION_CALL()\n"

        with os.fdopen(self._temporary_file[0], "a+") as process_file:
            process_file.write(contents)

        result = run_linter_main(self._temporary_file[1],
                                 whitelist=["style/space_before_func"])

        self.assertEqual(result, 1)

    def test_fix_what_you_can(self):
        """Check that --fix-what-you-can modifies file correctly."""
        contents = "function_call()\n"

        with os.fdopen(self._temporary_file[0], "a+") as process_file:
            process_file.write(contents)

        run_linter_main(self._temporary_file[1],
                        whitelist=["style/space_before_func"],
                        fix_what_you_can=True)

        with open(self._temporary_file[1], "r") as processed_file:
            self.assertEqual("function_call ()\n", processed_file.read())
