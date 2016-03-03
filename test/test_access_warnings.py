# /test/test_access_warnings.py
#
# Test cases for access/* checks
#
# See /LICENCE.md for Copyright information
"""Test cases for access/* checks."""

from test.warnings_test_common import DEFINITION_TYPES
from test.warnings_test_common import FUNCTIONS_SETTING_VARS
from test.warnings_test_common import LinterFailure
from test.warnings_test_common import format_with_command
from test.warnings_test_common import run_linter_throw

from nose_parameterized import param, parameterized

from testtools import (ExpectedException, TestCase)


class TestPrivateFunctionsUsedMustBeDefinedInThisModule(TestCase):
    """Test that private functions used are defined in this module."""

    @parameterized.expand(DEFINITION_TYPES)
    # suppress (no-self-use)
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

    def test_fail_use_other_priv_def(self):  # suppress(no-self-use)
        """acess/other_private fails if we use private def from other mod."""
        with ExpectedException(LinterFailure):
            run_linter_throw("_definition (ARGUMENT)\n",
                             whitelist=["access/other_private"])

# suppress(unnecessary-lambda)
_PRIVATE_VAR_SET_FORMAT = format_with_command(lambda x: "_{}".format(x))


class TestNoUseOtherPrivateToplevelVars(TestCase):
    """Check that private variables not set by us are not used."""

    parameters = [param(m) for m in FUNCTIONS_SETTING_VARS]

    def test_pass_pub_var_used(self):
        """Check access/private_var passes if undefined public var is used."""
        script = "message (${VALUE})\n"
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["access/private_var"]))

    @parameterized.expand(parameters,
                          testcase_func_doc=_PRIVATE_VAR_SET_FORMAT)
    def test_pass_variable_used(self, matcher):
        """Check access/private_var passes when priv var set by {}."""
        # suppress(unnecessary-lambda,E731)
        xform = lambda x: "_{0}".format(x)
        private_var = matcher.find.generate(matcher.sub,
                                            lambda x: x, xform)
        script = ("{0} ({1})\n"
                  "message ({2})\n").format(matcher.cmd,
                                            private_var,
                                            "${_VALUE}")
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["access/private_var"]))

    def test_pass_priv_func_used(self):
        """Check access/private_var passes when using private func as var."""
        script = ("function (_private_function)\n"
                  "endfunction ()\n"
                  "call (_private_function)\n")
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["access/private_var"]))

    def test_pass_foreach_set(self):
        """Check access/private_var passes when private var set by foreach."""
        script = ("foreach (_LOOP_VAR ${LIST})\n"
                  "    message (STATUS \"${_LOOP_VAR}\")\n"
                  "endforeach ()\n")
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["access/private_var"]))

    def test_fail_set_outside_scope(self):  # suppress(no-self-use)
        """Check access/private_var fails when var set outside scope."""
        script = ("foreach (_LOOP_VAR ${LIST})\n"
                  "endforeach ()\n"
                  "message (STATUS \"${_LOOP_VAR}\")\n")
        with ExpectedException(LinterFailure):
            run_linter_throw(script, whitelist=["access/private_var"])

    def test_fail_priv_var_used(self):  # suppress(no-self-use)
        """Check access/private_var fails on undefined private var used."""
        script = "message (${_VALUE})\n"
        with ExpectedException(LinterFailure):
            run_linter_throw(script, whitelist=["access/private_var"])
