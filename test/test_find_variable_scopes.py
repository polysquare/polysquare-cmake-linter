# /test/test_find_variable_scopes.py
#
# Tests that we're able to find variables inside the scopes that we expect
#
# See /LICENCE.md for Copyright information
"""Test that we're able to find variables inside the scopes that we expect."""

from test.warnings_test_common import Equals
from test.warnings_test_common import FUNCTIONS_SETTING_VARS
from test.warnings_test_common import format_with_command
from test.warnings_test_common import gen_source_line

from cmakeast import ast

from nose_parameterized import param, parameterized

from polysquarecmakelinter import find_variables_in_scopes

from polysquarecmakelinter.find_variables_in_scopes import VariableSource

from testtools import TestCase

from testtools.matchers import MatchesStructure
from testtools.matchers import Not

VarSrc = VariableSource


class TestFindVariablesInScopes(TestCase):
    """Test fixture for the in_tree function."""

    params = [param(m) for m in FUNCTIONS_SETTING_VARS]

    @parameterized.expand(params, testcase_func_doc=format_with_command())
    def test_global_scope(self, matcher):
        """Test setting and finding vars with {} at global scope."""
        script = "{0}".format(gen_source_line(matcher))
        global_scope = find_variables_in_scopes.set_in_tree(ast.parse(script))

        self.assertThat(global_scope.set_vars[0].node,
                        MatchesStructure(contents=Equals("VALUE")))

    @parameterized.expand(params, testcase_func_doc=format_with_command())
    def test_in_func_scope(self, matcher):
        """Test setting and finding vars with {} in function scope."""
        script = ("function (foo)\n"
                  "    {0}\n"
                  "endfunction ()\n").format(gen_source_line(matcher))
        global_scope = find_variables_in_scopes.set_in_tree(ast.parse(script))

        self.assertThat(global_scope.scopes[0].set_vars[0].node,
                        MatchesStructure(contents=Equals("VALUE")))

    @parameterized.expand(params, testcase_func_doc=format_with_command())
    def test_if_in_func_scope(self, matcher):
        """Test that using {} in an if block propagates variable to func."""
        script = ("function (foo)\n"
                  "    if (CONDITION)\n"
                  "        {0}\n"
                  "    endif (CONDITION)\n"
                  "endfunction ()\n").format(gen_source_line(matcher))
        global_scope = find_variables_in_scopes.set_in_tree(ast.parse(script))
        self.assertThat(global_scope.scopes[0].set_vars[0].node,
                        MatchesStructure(contents=Equals("VALUE")))

    @parameterized.expand(params, testcase_func_doc=format_with_command())
    def test_elseif_in_func_scope(self, matcher):
        """Test that using {} in an elseif statement propagates variable."""
        script = ("function (foo)\n"
                  "    if (CONDITION)\n"
                  "    elseif (CONDITION)\n"
                  "        {0}\n"
                  "    endif (CONDITION)\n"
                  "endfunction ()\n").format(gen_source_line(matcher))
        global_scope = find_variables_in_scopes.set_in_tree(ast.parse(script))
        self.assertThat(global_scope.scopes[0].set_vars[0].node,
                        MatchesStructure(contents=Equals("VALUE")))

    @parameterized.expand(params, testcase_func_doc=format_with_command())
    def test_else_in_func_scope(self, matcher):
        """Test that using {} in an else statement propagates variable."""
        script = ("function (foo)\n"
                  "    if (CONDITION)\n"
                  "    else (CONDITION)\n"
                  "        {0}\n"
                  "    endif (CONDITION)\n"
                  "endfunction ()\n").format(gen_source_line(matcher))
        global_scope = find_variables_in_scopes.set_in_tree(ast.parse(script))
        self.assertThat(global_scope.scopes[0].set_vars[0].node,
                        MatchesStructure(contents=Equals("VALUE")))

    @parameterized.expand(params, testcase_func_doc=format_with_command())
    def test_while_in_func(self, matcher):
        """Test that using {} in a while block propagates variable to func."""
        script = ("function (foo)\n"
                  "    while (CONDITION)\n"
                  "        {0}\n"
                  "    endwhile (CONDITION)\n"
                  "endfunction ()\n").format(gen_source_line(matcher))
        global_scope = find_variables_in_scopes.set_in_tree(ast.parse(script))
        self.assertThat(global_scope.scopes[0].set_vars[0].node,
                        MatchesStructure(contents=Equals("VALUE")))

    @parameterized.expand(params, testcase_func_doc=format_with_command())
    def test_foreach_in_func(self, matcher):
        """Test that using {} in an foreach statements propagates variable."""
        script = ("function (foo)\n"
                  "    foreach (VAR LISTVAR)\n"
                  "        {0}\n"
                  "    endforeach ()\n"
                  "endfunction ()\n").format(gen_source_line(matcher))
        global_scope = find_variables_in_scopes.set_in_tree(ast.parse(script))
        self.assertThat(global_scope.scopes[0].set_vars[0].node,
                        MatchesStructure(contents=Equals("VALUE")))

    def test_foreach_scope(self):
        """Test that setting a variable in an foreach statements propagates."""
        script = ("function (foo)\n"
                  "    foreach (VAR LISTVAR)\n"
                  "    endforeach ()\n"
                  "endfunction ()\n")
        global_scope = find_variables_in_scopes.set_in_tree(ast.parse(script))
        self.assertThat(global_scope.scopes[0].scopes[0].set_vars[0].node,
                        MatchesStructure(contents=Equals("VAR")))

        foreach_type = find_variables_in_scopes.ScopeType.Foreach
        self.assertThat(global_scope.scopes[0].scopes[0].info,
                        MatchesStructure(type=Equals(foreach_type)))

    def test_parent_scope(self):
        """Test that setting a variable in the parent scope propagates."""
        script = ("function (foo)\n"
                  "    function (other)\n"
                  "        set (VARIABLE OTHER PARENT_SCOPE)\n"
                  "    endfunction ()\n"
                  "endfunction ()\n")
        global_scope = find_variables_in_scopes.set_in_tree(ast.parse(script))
        self.assertThat(global_scope.scopes[0].set_vars[0].node,
                        MatchesStructure(contents=Equals("VARIABLE")))

    def test_cache_scope(self):
        """Test that setting a variable in the cache scope is global."""
        script = ("function (foo)\n"
                  "    function (other)\n"
                  "        set (VARIABLE OTHER CACHE)\n"
                  "    endfunction ()\n"
                  "endfunction ()\n")
        global_scope = find_variables_in_scopes.set_in_tree(ast.parse(script))
        self.assertThat(global_scope.set_vars[0].node,
                        MatchesStructure(contents=Equals("VARIABLE")))

    def test_global_setprop_scope(self):
        """Test that setting a variable in the set_property scope is global."""
        script = ("function (foo)\n"
                  "    function (other)\n"
                  "        set_property (GLOBAL PROPERTY VARIABLE OTHER)\n"
                  "    endfunction ()\n"
                  "endfunction ()\n")
        global_scope = find_variables_in_scopes.set_in_tree(ast.parse(script))
        self.assertThat(global_scope.set_vars[0].node,
                        MatchesStructure(contents=Equals("VARIABLE")))

    def test_func_var_scope(self):
        """Test function variable scope."""
        script = ("function (foo VAR)\n"
                  "endfunction ()")
        global_scope = find_variables_in_scopes.set_in_tree(ast.parse(script))
        self.assertThat(global_scope.scopes[0].set_vars[0].node,
                        MatchesStructure(contents=Equals("VAR")))

    def test_macro_var_scope(self):
        """Test macro variable scope."""
        script = ("macro (foo VAR)\n"
                  "endmacro ()")
        global_scope = find_variables_in_scopes.set_in_tree(ast.parse(script))
        self.assertThat(global_scope.scopes[0].set_vars[0].node,
                        MatchesStructure(contents=Equals("VAR")))

VARIABLE_USAGE_METHODS = [
    "${VALUE}",
    "${VALUE}_",
    "${VALUE}_${OTHER}",
    "${VALUE}/${OTHER}",
    "${VARIABLE_${VALUE}_OTHER}",
    "VALUE",
]


class TestUsedInTree(TestCase):
    """Test fixture for used_in_tree func."""

    @parameterized.expand(VARIABLE_USAGE_METHODS)
    def test_use_at_toplevel(self, call):
        """Test that a variable is marked as used at the toplevel."""
        script = "f ({0})".format(call)
        global_scope = find_variables_in_scopes.used_in_tree(ast.parse(script))
        self.assertThat(global_scope.used_vars[0],
                        MatchesStructure(source=Equals(VarSrc.GlobalVar)))

    @parameterized.expand(VARIABLE_USAGE_METHODS)
    def test_used_in_func(self, call):
        """Test that a variable is marked as used in a function."""
        script = ("function (name)\n"
                  "    f ({0})\n"
                  "endfunction ()\n").format(call)
        global_scope = find_variables_in_scopes.used_in_tree(ast.parse(script))
        self.assertThat(global_scope.scopes[0].used_vars[0],
                        MatchesStructure(source=Equals(VarSrc.FunctionVar)))

    @parameterized.expand(VARIABLE_USAGE_METHODS)
    def test_used_in_macro(self, call):
        """Test that a variable is marked as used in a macro."""
        script = ("macro (name)\n"
                  "    f ({0})\n"
                  "endmacro ()\n").format(call)
        global_scope = find_variables_in_scopes.used_in_tree(ast.parse(script))
        self.assertThat(global_scope.scopes[0].used_vars[0],
                        MatchesStructure(source=Equals(VarSrc.MacroVar)))

    @parameterized.expand(VARIABLE_USAGE_METHODS)
    def test_used_in_func_nest(self, call):
        """Test that a variable is marked as used in a function when nested."""
        script = ("function (name)\n"
                  "    if ()"
                  "        f ({0})\n"
                  "    endif ()"
                  "endfunction ()\n").format(call)
        global_scope = find_variables_in_scopes.used_in_tree(ast.parse(script))
        self.assertThat(global_scope.scopes[0].used_vars[0],
                        MatchesStructure(source=Equals(VarSrc.FunctionVar)))

    @parameterized.expand(VARIABLE_USAGE_METHODS)
    def test_used_in_func_if(self, call):
        """Test that a variable is marked as used in a function when nested."""
        script = ("function (name)\n"
                  "    if ({0})"
                  "    endif ()"
                  "endfunction ()\n").format(call)
        global_scope = find_variables_in_scopes.used_in_tree(ast.parse(script))
        self.assertThat(global_scope.scopes[0].used_vars[0],
                        MatchesStructure(source=Equals(VarSrc.FunctionVar)))

    @parameterized.expand(VARIABLE_USAGE_METHODS)
    def test_used_in_macro_if(self, call):
        """Test that a variable is marked as used in a function when nested."""
        script = ("macro (name)\n"
                  "    if ({0})"
                  "    endif ()"
                  "endmacro ()\n").format(call)
        global_scope = find_variables_in_scopes.used_in_tree(ast.parse(script))
        self.assertThat(global_scope.scopes[0].used_vars[0],
                        MatchesStructure(source=Equals(VarSrc.MacroVar)))

    @parameterized.expand(VARIABLE_USAGE_METHODS)
    def test_used_in_func_foreach(self, call):
        """Test that a variable is marked as used in a function when nested."""
        script = ("function (name)\n"
                  "    foreach (VAR {0})"
                  "    endforeach ()"
                  "endfunction ()\n").format(call)
        global_scope = find_variables_in_scopes.used_in_tree(ast.parse(script))
        self.assertThat(global_scope.scopes[0].used_vars[0],
                        MatchesStructure(source=Equals(VarSrc.FunctionVar)))

    @parameterized.expand(VARIABLE_USAGE_METHODS)
    def test_used_in_macro_foreach(self, call):
        """Test that a variable is marked as used in a function when nested."""
        script = ("macro (name)\n"
                  "    foreach (VAR {0})"
                  "    endforeach ()"
                  "endmacro ()\n").format(call)
        global_scope = find_variables_in_scopes.used_in_tree(ast.parse(script))
        self.assertThat(global_scope.scopes[0].used_vars[0],
                        MatchesStructure(source=Equals(VarSrc.MacroVar)))

    def test_not_used_in_function_hdr(self):
        """Test that there is no use in a function header."""
        script = ("function (name ARGUMENT)\n"
                  "endfunction ()")
        global_scope = find_variables_in_scopes.used_in_tree(ast.parse(script))
        self.assertEqual(len(global_scope.scopes[0].used_vars), 0)

    def test_no_use_by_foreach_var(self):
        """Test that there is no use for a foreach var."""
        script = ("foreach (VAR ${LIST})\n"
                  "endforeach ()")
        global_scope = find_variables_in_scopes.used_in_tree(ast.parse(script))
        self.assertThat(global_scope.used_vars[0].node,
                        MatchesStructure(contents=Not(Equals("VAR"))))

    @parameterized.expand(find_variables_in_scopes.FOREACH_KEYWORDS)
    def test_exclude_foreach_kws(self, keyword):
        """Test that there is no use for a foreach keyword."""
        script = ("foreach (VAR {0} LIST)\n"
                  "endforeach ()").format(keyword)
        global_scope = find_variables_in_scopes.used_in_tree(ast.parse(script))
        self.assertThat(global_scope.used_vars[0].node,
                        MatchesStructure(contents=Not(Equals(keyword))))

    @parameterized.expand(find_variables_in_scopes.IF_KEYWORDS)
    def test_exclude_if_kws(self, keyword):
        """Test that there is no use for an if keyword."""
        script = ("if ({0} OTHER)\n"
                  "endif ()").format(keyword)
        global_scope = find_variables_in_scopes.used_in_tree(ast.parse(script))
        self.assertThat(global_scope.used_vars[0].node,
                        MatchesStructure(contents=Not(Equals(keyword))))
