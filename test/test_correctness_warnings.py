# /test/test_correctness_warnings.py
#
# Test cases for correctness/* checks
#
# See /LICENCE.md for Copyright information
"""Test cases for correctness/* checks."""

from test.warnings_test_common import LinterFailure
from test.warnings_test_common import replacement
from test.warnings_test_common import run_linter_throw

from nose_parameterized import parameterized

from polysquarecmakelinter import check_correctness

from testtools import ExpectedException
from testtools import TestCase

# Generate some quote-only variable combinations
QUOTE_ONLY_TEST_VARIABLES = []
for variable in check_correctness.ALWAYS_QUOTE_VARIABLES_CONTAINING:
    QUOTE_ONLY_TEST_VARIABLES += [
        "${_" + variable.variable + "}",
        "${" + variable.variable + "}",
        "${A_" + variable.variable + "}",
        "${" + variable.variable + "}/Other",
        "Other/${" + variable.variable + "}"
    ]

NO_QUOTE_TEST_VARIABLES = []
for variable in check_correctness.ALWAYS_QUOTE_VARIABLES_CONTAINING:
    NO_QUOTE_TEST_VARIABLES += [
        "${A" + variable.variable + "}",
        "${" + variable.variable + "A}",
        "${" + variable.variable + "_}"
    ]


class TestQuoteVariablesWhichMayHaveSpaces(TestCase):

    """Test case for ensuring that certain variables are always quoted."""

    @parameterized.expand(QUOTE_ONLY_TEST_VARIABLES)
    def test_fail_deref_certain_vars(self, bad_deref):  # suppress(no-self-use)
        """Test correctness/quotes fails if dereffing some variable names."""
        with ExpectedException(LinterFailure):
            run_linter_throw("call ({0})".format(bad_deref),
                             whitelist=["correctness/quotes"])

    def test_fail_when_using_slashes(self):  # suppress(no-self-use)
        """Test correctness/quotes fails when using raw unquoted path."""
        with ExpectedException(LinterFailure):
            run_linter_throw("call (abc/def)\n",
                             whitelist=["correctness/quotes"])

    @parameterized.expand(NO_QUOTE_TEST_VARIABLES)
    def test_pass_deref_nonpath_var(self, deref):
        """Test correctness/quotes passes with modified path var name."""
        self.assertTrue(run_linter_throw("call ({0})".format(deref),
                                         whitelist=["correctness/quotes"]))

    def test_replace_when_using_slashes(self):
        """Test correctness/quotes replaces raw unquoted path with quotes."""
        def get_replacement():
            """Get the replacement for raw unquoted path."""
            run_linter_throw("call (abc/def)\n",
                             whitelist=["correctness/quotes"])

        exception = self.assertRaises(LinterFailure, get_replacement)
        self.assertEqual(replacement(exception),
                         (1, "call (\"abc/def\")\n"))

    @parameterized.expand(QUOTE_ONLY_TEST_VARIABLES)
    def test_replace_deref_certain_vars(self, bad_deref):
        """Test correctness/quotes replaces variable derefs with quotes."""
        def get_replacement():
            """Get the replacement for the dereferenced path."""
            run_linter_throw("call ({0})".format(bad_deref),
                             whitelist=["correctness/quotes"])

        exception = self.assertRaises(LinterFailure, get_replacement)
        self.assertEqual(replacement(exception),
                         (1, "call (\"{0}\")".format(bad_deref)))
