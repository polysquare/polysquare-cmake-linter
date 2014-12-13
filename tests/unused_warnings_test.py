# /tests/unused_warnings_test.py
#
# Test cases for style/* checks
#
# Disable no-self-use in this module as all test methods must be member
# functions, regardless of whether self is used.
# pylint:  disable=no-self-use
#
# See LICENCE.md for Copyright information
"""Test cases for style/* checks"""

from tests.warnings_test_common import (LinterFailure,
                                        run_linter_throw,
                                        gen_source_line,
                                        DEFINITION_TYPES)
from tests import autoderef_list

from nose_parameterized import parameterized
from polysquarecmakelinter import find_set_variables
from testtools import (ExpectedException, TestCase)


class TestPrivateFunctionsMustBeUsed(TestCase):
    """Tests that private functions must be used"""

    @parameterized.expand(DEFINITION_TYPES)
    def test_pass_priv_func_used(self, definition):
        """unused/private passes if private function used"""
        script = ("{0} (_definition ARGUMENT)\n"
                  "end{0} ()\n"
                  "_definition (ARGUMENT)\n").format(definition)
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/private"]))

    @parameterized.expand(DEFINITION_TYPES)
    def test_pass_pub_func_unused(self, definition):
        """unused/private passes if public function unused"""
        script = ("{0} (definition ARGUMENT)\n"
                  "end{0} ()\n").format(definition)
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/private"]))

    @parameterized.expand(DEFINITION_TYPES)
    def test_fail_priv_func_unused(self, definition):
        """unused/private passes if private function unused"""
        script = ("{0} (_definition ARGUMENT)\n"
                  "end{0} ()\n").format(definition)
        with ExpectedException(LinterFailure):
            run_linter_throw(script, whitelist=["unused/private"])


class TestUnusedSetVariablesInBody(TestCase):
    """Check for unused set variables in a function/macro body"""

    functions_set_vars = find_set_variables.FUNCTIONS_SETTING_VARIABLES
    parameters = [(m, None) for m in functions_set_vars]

    @parameterized.expand(parameters)
    def test_pass_variable_used(self, matcher, _):
        """Check unused/var_in_func passes when var is used"""
        script = ("function (f)\n"
                  "    {0}\n"
                  "    message ({1})\n"
                  "endfunction ()\n").format(gen_source_line(matcher),
                                             "${VALUE}")
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/var_in_func"]))

    @parameterized.expand(parameters)
    def test_pass_nested_use(self, matcher, _):
        """Check unused/var_in_func passes when var is used"""
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
        """Check unused/var_in_func passes when var is used in nested ctx"""

        script = ("function (f)\n"
                  "    set_property (GLOBAL PROPERTY VALUE)\n"
                  "endfunction (f)\n"
                  "function (g)\n"
                  "    get_property (VAR GLOBAL PROPERTY VALUE)\n"
                  "    message (${VAR})\n"
                  "endfunction ()\n")
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/var_in_func"]))

    @parameterized.expand(parameters)
    def test_pass_deref_unused(self, matcher, _):
        """Check unused/var_in_func passes when dereference var passed"""
        call = gen_source_line(matcher,
                               match_transform=lambda x: "${" + x + "}")
        script = ("function (f)\n"
                  "    {0}\n"
                  "endfunction ()\n").format(call)
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/var_in_func"]))

    @parameterized.expand(autoderef_list.VARIABLES)
    def test_pass_use_autoderef(self, cmd, generator):
        """Check that unused/var_in_func passes when var autodereffed"""

        script = ("function (f)\n"
                  "    set (_ARGUMENT 0)\n"
                  "    {0} ({1})\n"
                  "    end{0} ()\n"
                  "endfunction ()").format(cmd, generator(lambda x: "_" + x))
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/private_var"]))

    @parameterized.expand(parameters)
    def test_pass_compound_unused(self, matcher, _):
        """Check unused/var_in_func passes when compound_lit var passed"""
        call = gen_source_line(matcher,
                               match_transform=lambda x: "${" + x + "}/Other")
        script = ("function (f)\n"
                  "    {0}\n"
                  "endfunction ()\n").format(call)
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/var_in_func"]))

    @parameterized.expand(parameters)
    def test_fail_variable_unused(self, matcher, _):
        """Check unused/var_in_func fails when var is unused"""
        call = gen_source_line(matcher)
        script = ("function (f)\n"
                  "    {0}\n"
                  "endfunction ()\n").format(call)

        with ExpectedException(LinterFailure):
            run_linter_throw(script, whitelist=["unused/var_in_func"])

    @parameterized.expand(parameters)
    def test_fail_nested_var_unused(self, matcher, _):
        """Check unused/var_in_func fails when nested var is unused"""
        call = gen_source_line(matcher)
        script = ("function (f)\n"
                  "    if (COND)\n"
                  "        {0}\n"
                  "    endif (COND)\n"
                  "endfunction ()\n").format(call)

        with ExpectedException(LinterFailure):
            run_linter_throw(script, whitelist=["unused/var_in_func"])


class TestUnusedPrivateToplevelVars(TestCase):
    """Check for unused set private variables at the top level"""

    functions_set_vars = find_set_variables.FUNCTIONS_SETTING_VARIABLES
    parameters = [(m, None) for m in functions_set_vars]

    @parameterized.expand(parameters)
    def test_pass_variable_used(self, matcher, _):
        """Check unused/private_var passes when var is used"""
        find = matcher.find
        xform = lambda x: "_{0}".format(x)  # pylint:disable=unnecessary-lambda
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

    @parameterized.expand(parameters)
    def test_pass_nested_use(self, matcher, _):
        """Check unused/private_var passes when var is used in nested ctx"""
        find = matcher.find
        xform = lambda x: "_{0}".format(x)  # pylint:disable=unnecessary-lambda
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
        """Check unused/private_var passes when var is used in nested ctx"""

        script = ("function (f)\n"
                  "    set_property (GLOBAL PROPERTY _VALUE)\n"
                  "endfunction (f)\n"
                  "function (g)\n"
                  "    get_property (VAR GLOBAL PROPERTY _VALUE)\n"
                  "endfunction ()\n")
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/private_var"]))

    @parameterized.expand(parameters)
    def test_pass_pub_var_unused(self, matcher, _):
        """Check unused/private_var passes when public var is unused"""
        find = matcher.find
        script = ("{0} ({1})\n").format(matcher.cmd,
                                        find.generate(matcher.sub,
                                                      lambda x: x,
                                                      lambda x: x))
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/private_var"]))

    @parameterized.expand(autoderef_list.VARIABLES)
    def test_pass_use_var_autoderef(self, cmd, generator):
        """Check that unused/private_var passes when var autodereffed"""

        script = ("set (_ARGUMENT 0)\n"
                  "{0} ({1})\n"
                  "end{0} ()\n").format(cmd, generator(lambda x: "_" + x))
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["unused/private_var"]))

    @parameterized.expand(parameters)
    def test_fail_variable_unused(self, matcher, _):
        """Check unused/var_in_func fails when private var is unused"""
        find = matcher.find
        xform = lambda x: "_{0}".format(x)  # pylint:disable=unnecessary-lambda
        script = ("{0} ({1})\n").format(matcher.cmd,
                                        find.generate(matcher.sub,
                                                      lambda x: x,
                                                      xform))

        with ExpectedException(LinterFailure):
            run_linter_throw(script, whitelist=["unused/private_var"])
