# /tests/structure_warnings_test.py
#
# Test cases for structure/* checks
#
# Disable no-self-use in this module as all test methods must be member
# functions, regardless of whether self is used.
# pylint:  disable=no-self-use
#
# See LICENCE.md for Copyright information
"""Test cases for correctness/* checks"""

from tests.warnings_test_common import (LinterFailure,
                                        run_linter_throw,
                                        replacement,
                                        DEFINITION_TYPES)
from nose_parameterized import parameterized
from testtools import (ExpectedException, TestCase)


class TestFunctionsMustBeNamespaces(TestCase):
    """Tests that all functions must be namespaced"""

    @parameterized.expand(DEFINITION_TYPES)
    def test_pass_pub_func_namespaced(self, definition):
        """structure/namespace passes when public functions namespaced"""
        script = "{0} (our_call ARGUMENT)\nend{0} ()".format(definition)
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["structure/namespace"],
                                         namespace="our"))

    @parameterized.expand(DEFINITION_TYPES)
    def test_pass_priv_func_namespaced(self, definition):
        """structure/namespace passes when private functions namespaced"""
        script = "{0} (_our_call ARGUMENT)\nend{0} ()".format(definition)
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["structure/namespace"],
                                         namespace="our"))

    @parameterized.expand(DEFINITION_TYPES)
    def test_pass_no_namespace_passed(self, definition):
        """structure/namespace passes when no namespace specified"""
        script = "{0} (call ARGUMENT)\nend{0} ()".format(definition)
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["structure/namespace"]))

    @parameterized.expand(DEFINITION_TYPES)
    def test_fail_outside_namespace(self, definition):
        """structure/namespace fails when definition outside namespace"""
        script = "{0} (not_our_call ARGUMENT)\nend{0} ()".format(definition)
        with ExpectedException(LinterFailure):
            run_linter_throw(script, namespace="our",
                             whitelist=["structure/namespace"])

    @parameterized.expand(DEFINITION_TYPES)
    def test_fail_priv_out_namespace(self, definition):
        """structure/namespace fails when priv definition outside namespace"""
        script = "{0} (_not_our_call ARGUMENT)\nend{0} ()".format(definition)
        with ExpectedException(LinterFailure):
            run_linter_throw(script, namespace="our",
                             whitelist=["structure/namespace"])

    @parameterized.expand(DEFINITION_TYPES)
    def test_prepend_with_namespace(self, definition):
        """structure/namespace prepends namespace as replacement"""
        name = "not_our_call"
        script = "{0} ({1} ARGUMENT)\nend{0} ()".format(definition, name)

        def get_replacement():
            """Gets replacement for un-namespaced definition"""
            run_linter_throw(script, namespace="our",
                             whitelist=["structure/namespace"])

        namespaced_name = "our_{0}".format(name)
        exception = self.assertRaises(LinterFailure, get_replacement)
        self.assertEqual(replacement(exception),
                         (1, "{0} ({1} ARGUMENT)\n".format(definition,
                                                           namespaced_name)))

    @parameterized.expand(DEFINITION_TYPES)
    def test_priv_prepend_namespace(self, definition):
        """structure/namespace prepends namespace after _ as replacement"""
        name = "_not_our_call"
        script = "{0} ({1} ARGUMENT)\nend{0} ()".format(definition, name)

        def get_replacement():
            """Gets replacement for un-namespaced private definition"""
            run_linter_throw(script, namespace="our",
                             whitelist=["structure/namespace"])

        namespaced_name = "_our_{0}".format(name)
        exception = self.assertRaises(LinterFailure, get_replacement)
        self.assertEqual(replacement(exception),
                         (1, "{0} ({1} ARGUMENT)\n".format(definition,
                                                           namespaced_name)))
