# /test/test_unused_warnings.py
#
# Test cases for style/* checks
#
# Disable no-self-use in this module as all test methods must be member
# functions, regardless of whether self is used.
#
# See /LICENCE.md for Copyright information
"""Test cases for style/* checks."""

from test import autoderef_list

from test.warnings_test_common import DEFINITION_TYPES
from test.warnings_test_common import FUNCTIONS_SETTING_VARS
from test.warnings_test_common import LinterFailure
from test.warnings_test_common import format_with_command
from test.warnings_test_common import gen_source_line
from test.warnings_test_common import run_linter_throw

from nose_parameterized import param, parameterized

from testtools import (ExpectedException, TestCase)


class TestPrivateFunctionsMustBeUsed(TestCase):
    """Test that private functions must be used."""

    @parameterized.expand(DEFINITION_TYPES)
    def test_pass_priv_func_used(self, definition):
        """unused/private passes if private function used."""
        script = ("{0} (_definition ARGUMENT)\n"
                  "end{0} ()\n"
                  "_definition (ARGUMENT)\n").format(definition)
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/private"]))

    @parameterized.expand(DEFINITION_TYPES)
    def test_pass_priv_func_as_var(self, definition):
        """unused/private passes if private function used as a variable."""
        script = ("{0} (_definition ARGUMENT)\n"
                  "end{0} ()\n"
                  "call (_definition)\n").format(definition)
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/private"]))

    @parameterized.expand(DEFINITION_TYPES)
    def test_pass_pub_func_unused(self, definition):
        """unused/private passes if public function unused."""
        script = ("{0} (definition ARGUMENT)\n"
                  "end{0} ()\n").format(definition)
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/private"]))

    @parameterized.expand(DEFINITION_TYPES)
    def test_fail_priv_func_unused(self, definition):  # suppress(no-self-use)
        """unused/private passes if private function unused."""
        script = ("{0} (_definition ARGUMENT)\n"
                  "end{0} ()\n").format(definition)
        with ExpectedException(LinterFailure):
            run_linter_throw(script, whitelist=["unused/private"])

_FORMAT_WITH_DEREFFED_VAR = format_with_command(lambda x: "${" + x + "}")


def _format_with_generator(func, _, params):
    """Return formatted docstring with generated command."""
    cmd = params.args[0]
    generator = params.args[1]
    return func.__doc__.format("{0} ({1})".format(cmd,
                                                  generator(lambda x: ("_" +
                                                                       x))))


class TestUnusedSetVariablesInBody(TestCase):
    """Check for unused set variables in a function/macro body."""

    parameters = [param(m) for m in FUNCTIONS_SETTING_VARS]

    @parameterized.expand(parameters, testcase_func_doc=format_with_command())
    def test_pass_variable_used(self, matcher):
        """Check unused/var_in_func passes when var is used with {}."""
        script = ("function (f)\n"
                  "    {0}\n"
                  "    message ({1})\n"
                  "endfunction ()\n").format(gen_source_line(matcher),
                                             "${VALUE}")
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/var_in_func"]))

    @parameterized.expand(parameters, testcase_func_doc=format_with_command())
    def test_pass_nested_use(self, matcher):
        """Check unused/var_in_func passes with {}, with use nested."""
        script = ("function (f)\n"
                  "    {0}\n"
                  "    foreach (VAR LIST)\n"
                  "        message ({1} VAR)\n"
                  "    endforeach ()\n"
                  "endfunction ()\n").format(gen_source_line(matcher),
                                             "${VALUE}")
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/var_in_func"]))

    def test_global_used(self):
        """Check unused/var_in_func passes when global property is used."""
        script = ("function (f)\n"
                  "    set_property (GLOBAL PROPERTY VALUE)\n"
                  "endfunction (f)\n"
                  "function (g)\n"
                  "    get_property (VAR GLOBAL PROPERTY VALUE)\n"
                  "    message (${VAR})\n"
                  "endfunction ()\n")
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/var_in_func"]))

    @parameterized.expand(parameters,
                          testcase_func_doc=_FORMAT_WITH_DEREFFED_VAR)
    def test_pass_deref_unused(self, matcher):
        """Check unused/var_in_func passes when deref var is set with {}."""
        call = gen_source_line(matcher,
                               match_transform=lambda x: "${" + x + "}")
        script = ("function (f)\n"
                  "    {0}\n"
                  "endfunction ()\n").format(call)
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/var_in_func"]))

    @parameterized.expand(autoderef_list.VARIABLES,
                          testcase_func_doc=_format_with_generator)
    def test_pass_use_autoderef(self, cmd, generator):
        """Check that unused/var_in_func passes when var autodereffed in {}."""
        script = ("function (f)\n"
                  "    set (_ARGUMENT 0)\n"
                  "    {0} ({1})\n"
                  "    end{0} ()\n"
                  "endfunction ()").format(cmd, generator(lambda x: "_" + x))
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/private_var"]))

    @parameterized.expand(parameters,
                          testcase_func_doc=_FORMAT_WITH_DEREFFED_VAR)
    def test_pass_compound_unused(self, matcher):
        """Check unused/var_in_func passes if compound_lit var passed in {}."""
        call = gen_source_line(matcher,
                               match_transform=lambda x: "${" + x + "}/Other")
        script = ("function (f)\n"
                  "    {0}\n"
                  "endfunction ()\n").format(call)
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/var_in_func"]))

    @parameterized.expand(parameters, testcase_func_doc=format_with_command())
    def test_fail_variable_unused(self, matcher):  # suppress(no-self-use)
        """Check unused/var_in_func fails when var is unused in {}."""
        call = gen_source_line(matcher)
        script = ("function (f)\n"
                  "    {0}\n"
                  "endfunction ()\n").format(call)

        with ExpectedException(LinterFailure):
            run_linter_throw(script, whitelist=["unused/var_in_func"])

    @parameterized.expand(parameters, testcase_func_doc=format_with_command())
    def test_fail_nested_var_unused(self, matcher):  # suppress(no-self-use)
        """Check unused/var_in_func fails when nested var is unused in {}."""
        call = gen_source_line(matcher)
        script = ("function (f)\n"
                  "    if (COND)\n"
                  "        {0}\n"
                  "    endif (COND)\n"
                  "endfunction ()\n").format(call)

        with ExpectedException(LinterFailure):
            run_linter_throw(script, whitelist=["unused/var_in_func"])

# suppress(unnecessary-lambda)
_PRIVATE_VAR_SET_FORMAT = format_with_command(lambda x: "_{}".format(x))


class TestUnusedPrivateToplevelVars(TestCase):
    """Check for unused set private variables at the top level."""

    parameters = [param(m) for m in FUNCTIONS_SETTING_VARS]

    @parameterized.expand(parameters,
                          testcase_func_doc=_PRIVATE_VAR_SET_FORMAT)
    def test_pass_variable_used(self, matcher):
        """Check unused/private_var passes when var set by {} is used."""
        find = matcher.find
        xform = lambda x: "_{0}".format(x)  # suppress(unnecessary-lambda,E731)
        script = ("function (f)\n"
                  "    {0} ({1})\n"
                  "    message ({2})\n"
                  "endfunction ()\n").format(matcher.cmd,
                                             find.generate(matcher.sub,
                                                           lambda x: x,
                                                           xform),
                                             "${_VALUE}")
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/private_var"]))

    @parameterized.expand(parameters,
                          testcase_func_doc=_PRIVATE_VAR_SET_FORMAT)
    def test_pass_nested_use(self, matcher):
        """Check unused/private_var passes when {} is used in nested ctx."""
        find = matcher.find
        xform = lambda x: "_{0}".format(x)  # suppress(unnecessary-lambda,E731)
        script = ("{0} ({1})\n"
                  "function (f)\n"
                  "    foreach (VAR LIST)\n"
                  "        message ({2})\n"
                  "    endforeach ()\n"
                  "endfunction (f)\n").format(matcher.cmd,
                                              find.generate(matcher.sub,
                                                            lambda x: x,
                                                            xform),
                                              "${_VALUE}")
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/private_var"]))

    def test_global_priv_used(self):
        """Check unused/private_var passes when var is used in nested ctx."""
        script = ("function (f)\n"
                  "    set_property (GLOBAL PROPERTY _VALUE)\n"
                  "endfunction (f)\n"
                  "function (g)\n"
                  "    get_property (VAR GLOBAL PROPERTY _VALUE)\n"
                  "endfunction ()\n")
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/private_var"]))

    @parameterized.expand(parameters,
                          testcase_func_doc=_PRIVATE_VAR_SET_FORMAT)
    def test_pass_pub_var_unused(self, matcher):
        """Check unused/private_var passes when public var is unused in {}."""
        find = matcher.find
        script = ("{0} ({1})\n").format(matcher.cmd,
                                        find.generate(matcher.sub,
                                                      lambda x: x,
                                                      lambda x: x))
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/private_var"]))

    @parameterized.expand(autoderef_list.VARIABLES,
                          testcase_func_doc=_format_with_generator)
    def test_pass_use_var_autoderef(self, cmd, generator):
        """Check that unused/private_var passes when var autodereffed in {}."""
        script = ("set (_ARGUMENT 0)\n"
                  "{0} ({1})\n"
                  "end{0} ()\n").format(cmd, generator(lambda x: "_" + x))
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/private_var"]))

    @parameterized.expand(parameters,
                          testcase_func_doc=_PRIVATE_VAR_SET_FORMAT)
    def test_fail_variable_unused(self, matcher):  # suppress(no-self-use)
        """Check unused/var_in_func fails when private var is unused in {}."""
        find = matcher.find
        xform = lambda x: "_{0}".format(x)  # suppress(unnecessary-lambda,E731)
        script = ("{0} ({1})\n").format(matcher.cmd,
                                        find.generate(matcher.sub,
                                                      lambda x: x,
                                                      xform))

        with ExpectedException(LinterFailure):
            run_linter_throw(script, whitelist=["unused/private_var"])
