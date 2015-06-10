# /test/test_structure_warnings.py
#
# Test cases for structure/* checks
#
# See /LICENCE.md for Copyright information
"""Test cases for correctness/* checks."""

from test.warnings_test_common import DEFINITION_TYPES
from test.warnings_test_common import LinterFailure
from test.warnings_test_common import replacement
from test.warnings_test_common import run_linter_throw

from nose_parameterized import parameterized

from testtools import ExpectedException
from testtools import TestCase


class TestFunctionsMustBeNamespaces(TestCase):

    """Test that all functions must be namespaced."""

    @parameterized.expand(DEFINITION_TYPES)
    def test_pass_pub_func_namespaced(self, definition):
        """structure/namespace passes when public functions namespaced."""
        script = "{0} (our_call ARGUMENT)\nend{0} ()".format(definition)
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["structure/namespace"],
                                         namespace="our"))

    @parameterized.expand(DEFINITION_TYPES)
    def test_pass_priv_func_namespaced(self, definition):
        """structure/namespace passes when private functions namespaced."""
        script = "{0} (_our_call ARGUMENT)\nend{0} ()".format(definition)
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["structure/namespace"],
                                         namespace="our"))

    @parameterized.expand(DEFINITION_TYPES)
    def test_pass_no_namespace_passed(self, definition):
        """structure/namespace passes when no namespace specified."""
        script = "{0} (call ARGUMENT)\nend{0} ()".format(definition)
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["structure/namespace"]))

    @parameterized.expand(DEFINITION_TYPES)
    def test_fail_outside_namespace(self, definition):  # suppress(no-self-use)
        """structure/namespace fails when definition outside namespace."""
        script = "{0} (not_our_call ARGUMENT)\nend{0} ()".format(definition)
        with ExpectedException(LinterFailure):
            run_linter_throw(script, namespace="our",
                             whitelist=["structure/namespace"])

    @parameterized.expand(DEFINITION_TYPES)
    # suppress(no-self-use)
    def test_fail_priv_out_namespace(self, definition):
        """structure/namespace fails when priv definition outside namespace."""
        script = "{0} (_not_our_call ARGUMENT)\nend{0} ()".format(definition)
        with ExpectedException(LinterFailure):
            run_linter_throw(script, namespace="our",
                             whitelist=["structure/namespace"])

    @parameterized.expand(DEFINITION_TYPES)
    def test_prepend_with_namespace(self, definition):
        """structure/namespace prepends namespace as replacement."""
        name = "not_our_call"
        script = "{0} ({1} ARGUMENT)\nend{0} ()".format(definition, name)

        def get_replacement():
            """Get replacement for un-namespaced definition."""
            run_linter_throw(script, namespace="our",
                             whitelist=["structure/namespace"])

        namespaced_name = "our_{0}".format(name)
        exception = self.assertRaises(LinterFailure, get_replacement)
        self.assertEqual(replacement(exception),
                         (1, "{0} ({1} ARGUMENT)\n".format(definition,
                                                           namespaced_name)))

    @parameterized.expand(DEFINITION_TYPES)
    def test_priv_prepend_namespace(self, definition):
        """structure/namespace prepends namespace after _ as replacement."""
        name = "_not_our_call"
        script = "{0} ({1} ARGUMENT)\nend{0} ()".format(definition, name)

        def get_replacement():
            """Get replacement for un-namespaced private definition."""
            run_linter_throw(script, namespace="our",
                             whitelist=["structure/namespace"])

        namespaced_name = "_our_{0}".format(name)
        exception = self.assertRaises(LinterFailure, get_replacement)
        self.assertEqual(replacement(exception),
                         (1, "{0} ({1} ARGUMENT)\n".format(definition,
                                                           namespaced_name)))
