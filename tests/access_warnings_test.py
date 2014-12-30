# /tests/access_warnings_test.py
#
# Test cases for access/* checks
#
# Disable no-self-use in this module as all test methods must be member
# functions, regardless of whether self is used.
# pylint:  disable=no-self-use
#
# See LICENCE.md for Copyright information
"""Test cases for access/* checks."""

from nose_parameterized import parameterized

from tests.warnings_test_common import DEFINITION_TYPES
from tests.warnings_test_common import FUNCTIONS_SETTING_VARS
from tests.warnings_test_common import LinterFailure
from tests.warnings_test_common import run_linter_throw

from testtools import (ExpectedException, TestCase)


class TestPrivateFunctionsUsedMustBeDefinedInThisModule(TestCase):

    """Test that private functions used are defined in this module."""

    @parameterized.expand(DEFINITION_TYPES)
    def test_pass_used_own_priv_def(self, definition):
        """access/other_private passes if using own private definition."""
        script = ("{0} (_definition ARGUMENT)\n"
                  "end{0} ()\n"
                  "_definition (ARGUMENT)\n").format(definition)
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["access/other_private"]))

    def test_pass_use_pub_def(self):
        """access/other_private passes if we use public def from other mod."""
        self.assertTrue(run_linter_throw("definition (ARGUMENT)\n",
                                         whitelist=["access/other_private"]))

    def test_pass_use_other_priv_def(self):
        """acess/other_private fails if we use private def from other mod."""
        with ExpectedException(LinterFailure):
            run_linter_throw("_definition (ARGUMENT)\n",
                             whitelist=["access/other_private"])


class TestNoUseOtherPrivateToplevelVars(TestCase):

    """Check that private variables not set by us are not used."""

    parameters = [(m, None) for m in FUNCTIONS_SETTING_VARS]

    def test_pass_pub_var_used(self):
        """Check access/private_var passes if undefined public var is used."""
        script = "message (${VALUE})\n"
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["access/private_var"]))

    @parameterized.expand(parameters)
    def test_pass_variable_used(self, matcher, _):
        """Check access/private_var passes when private var is set and used."""
        xform = lambda x: "_{0}".format(x)  # pylint:disable=unnecessary-lambda
        private_var = matcher.find.generate(matcher.sub, lambda x: x, xform)
        script = ("{0} ({1})\n"
                  "message ({2})\n").format(matcher.cmd,
                                            private_var,
                                            "${_VALUE}")
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["access/private_var"]))

    def test_pass_foreach_set(self):
        """Check access/private_var passes when private var set by foreach."""
        script = ("foreach (_LOOP_VAR ${LIST})\n"
                  "    message (STATUS \"${_LOOP_VAR}\")\n"
                  "endforeach ()\n")
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["access/private_var"]))

    def test_fail_set_outside_scope(self):
        """Check access/private_var fails when var set outside scope."""
        script = ("foreach (_LOOP_VAR ${LIST})\n"
                  "endforeach ()\n"
                  "message (STATUS \"${_LOOP_VAR}\")\n")
        with ExpectedException(LinterFailure):
            run_linter_throw(script, whitelist=["access/private_var"])

    def test_fail_priv_var_used(self):
        """Check access/private_var fails when undef private var is used."""
        script = "message (${_VALUE})\n"
        with ExpectedException(LinterFailure):
            run_linter_throw(script, whitelist=["access/private_var"])
