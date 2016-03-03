# /test/test_style_warnings.py
#
# Test cases for style/* checks
#
# See /LICENCE.md for Copyright information
"""Test cases for style/* checks."""

from test.warnings_test_common import DEFINITION_TYPES
from test.warnings_test_common import FUNCTIONS_SETTING_VARS
from test.warnings_test_common import LinterFailure
from test.warnings_test_common import format_with_args
from test.warnings_test_common import format_with_command
from test.warnings_test_common import gen_source_line
from test.warnings_test_common import replacement
from test.warnings_test_common import run_linter_throw

from nose_parameterized import param, parameterized

from testtools import ExpectedException
from testtools import TestCase


class TestSpaceBeforeFunctionCallWarnings(TestCase):
    """Test case for a single space between a function call and name."""

    def test_lint_pass(self):
        """Check that style/space_before_func passes.

        Test passes where there is a single space before a function name
        and a call, like so:

        function_name ()
        """
        result = run_linter_throw("function_call ()\n",
                                  whitelist=["style/space_before_func"])
        self.assertTrue(result)

    def test_lint_pass_comment(self):
        """Check that style/space_before_func passes for commented calls.

        Test passes where there is no space before a function name
        and a call, where that line is commented like so:

        # function_name()
        """
        result = run_linter_throw("# function_call()\n",
                                  whitelist=["style/space_before_func"])
        self.assertTrue(result)

    def test_lint_pass_inside_quotes(self):
        """Check that style/space_before_func passes for quoted calls.

        Test passes where there is no space before a function name
        and a call, where that line is inside quotes

        "function_name()"
        """
        result = run_linter_throw("call (\"function_call()\")\n",
                                  whitelist=["style/space_before_func"])
        self.assertTrue(result)

    def test_lint_fail_nospace(self):   # suppress(no-self-use)
        """Check that style/space_before_func fails.

        Test fails where there is no space between a function name and a
        call, like so:

        function_name()
        """
        with ExpectedException(LinterFailure):
            run_linter_throw("function_call()\n",
                             whitelist=["style/space_before_func"])

    def test_lint_fail_excessive_space(self):  # suppress(no-self-use)
        """Check that style/space_before_func fails.

        Test fails where there is more than one space between a function name
        and a call, like so

        function_name ()
        """
        with ExpectedException(LinterFailure):
            run_linter_throw("function_call  ()\n",
                             whitelist=["style/space_before_func"])

    def test_replace_excess_one_space(self):
        """Check that the style/space_before_func replacement has one space."""
        def get_replacement():
            """Get replacement for function call with excessive whitespace."""
            run_linter_throw("function_call            ()\n",
                             whitelist=["style/space_before_func"])

        exception = self.assertRaises(LinterFailure, get_replacement)
        self.assertEqual(replacement(exception),
                         (1, "function_call ()\n"))

    def test_replace_nospace_one_space(self):
        """Check that the style/space_before_func replacement has one space."""
        def get_replacement():
            """Get replacement for function call with no whitespace."""
            run_linter_throw("function_call()\n",
                             whitelist=["style/space_before_func"])

        exception = self.assertRaises(LinterFailure, get_replacement)
        self.assertEqual(replacement(exception),
                         (1, "function_call ()\n"))


class TestFunctionsMustbeLowercaseOnly(TestCase):
    """Test case for functions and macros being lowercase."""

    def test_pass_lowercase_call(self):
        """style/lowercase passes when calling lowercase func."""
        result = run_linter_throw("lowercase_func (ARGUMENT)\n",
                                  whitelist=["style/lowercase_func"])
        self.assertTrue(result)

    def test_fail_uppercase_call(self):  # suppress(no-self-use)
        """style/lowercase fails when calling uppercase func."""
        with ExpectedException(LinterFailure):
            run_linter_throw("UPPERCASE_FUNC (ARGUMENT)\n",
                             whitelist=["style/lowercase_func"])

    def test_replace_uppercase_call(self):
        """style/lowercase replaces uppercase call with lowercase call."""
        func_name = "UPPERCASE_FUNC"
        error_line = "{0} (ARGUMENT)\n".format(func_name)
        replacement_line = "{0} (ARGUMENT)\n".format(func_name.lower())

        def get_replacement():
            """Replacement for all uppercase function call."""
            run_linter_throw(error_line,
                             whitelist=["style/lowercase_func"])

        exception = self.assertRaises(LinterFailure, get_replacement)
        self.assertEqual(replacement(exception),
                         (1, replacement_line))

    def test_pass_lowercase_func_def(self):
        """style/lowercase passes when defining lowercase func."""
        result = run_linter_throw("function (lowercase_func) endfunction ()\n",
                                  whitelist=["style/lowercase_func"])
        self.assertTrue(result)

    def test_fail_uppercase_func_def(self):  # suppress(no-self-use)
        """style/lowercase fails when defining uppercase func."""
        with ExpectedException(LinterFailure):
            run_linter_throw("function (UPPERCASE_FUNC) endfunction ()\n",
                             whitelist=["style/lowercase_func"])

    def test_replace_uppercase_func_def(self):
        """style/lowercase replaces uppercase call with lowercase call."""
        func_name = "UPPERCASE_FUNC"
        lower_name = func_name.lower()
        error = "function ({0}) endfunction ()\n".format(func_name)
        expected_repl = "function ({0}) endfunction ()\n".format(lower_name)

        def get_replacement():
            """Replace uppercase function call."""
            run_linter_throw(error,
                             whitelist=["style/lowercase_func"])

        exception = self.assertRaises(LinterFailure, get_replacement)
        self.assertEqual(replacement(exception),
                         (1, expected_repl))

    def test_pass_lowercase_macro_def(self):
        """style/lowercase passes when defining lowercase macro."""
        result = run_linter_throw("macro (lowercase_macro) endmacro ()\n",
                                  whitelist=["style/lowercase_func"])
        self.assertTrue(result)

    def test_fail_uppercase_macro(self):  # suppress(no-self-use)
        """style/lowercase fails when defining uppercase macro."""
        with ExpectedException(LinterFailure):
            run_linter_throw("macro (UPPERCASE_MACRO) endmacro ()\n",
                             whitelist=["style/lowercase_func"])

    def test_replace_uppercase_macro(self):
        """style/lowercase replaces uppercase definition with lowercase def."""
        macro_name = "UPPERCASE_MACRO"
        lower_name = macro_name.lower()
        error = "macro ({0}) endmacro ()\n".format(macro_name)
        expected_replacement = "macro ({0}) endmacro ()\n".format(lower_name)

        def get_replacement():
            """Replacement for uppercase macro."""
            run_linter_throw(error,
                             whitelist=["style/lowercase_func"])

        exception = self.assertRaises(LinterFailure, get_replacement)
        self.assertEqual(replacement(exception),
                         (1, expected_replacement))


class TestUppercaseDefinitionArguments(TestCase):
    """Check that all arguments to a definition are uppercase."""

    @parameterized.expand(DEFINITION_TYPES)
    def test_pass_no_args(self, defin):
        """Check style/uppercase_args passes where function has no args."""
        script = "{0} (definition_name)\nend{0} ()\n".format(defin)
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["style/uppercase_args"]))

    @parameterized.expand(DEFINITION_TYPES)
    def test_pass_uppercase_args(self, defin):
        """Check style/uppercase_args passes where args are uppercase."""
        script = "{0} (definition_name UPPERCASE)\nend{0} ()\n".format(defin)
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["style/uppercase_args"]))

    @parameterized.expand(DEFINITION_TYPES)
    def test_fail_lowercase_args(self, defin):  # suppress(no-self-use)
        """Check style/uppercase_args passes where args are lowercase."""
        script = "{0} (definition_name lowercase)\nend{0} ()\n".format(defin)
        with ExpectedException(LinterFailure):
            run_linter_throw(script, whitelist=["style/uppercase_args"])

    @parameterized.expand(DEFINITION_TYPES)
    def test_replace_with_upper(self, defin):
        """Check style/uppercase_args passes where args are lowercase."""
        script = "{0} (name lowercase)\nend{0} ()\n".format(defin)

        def get_replacement():
            """Replacement for lowercase argument."""
            run_linter_throw(script, whitelist=["style/uppercase_args"])

        exception = self.assertRaises(LinterFailure, get_replacement)
        self.assertEqual(replacement(exception),
                         (1, "{0} (name LOWERCASE)\n".format(defin)))


_FORMAT_WITH_DEREFFED_VAR = format_with_command(lambda x: "${" + x + "}")
_FORMAT_WITH_LOWERCASE_VAR = format_with_command(lambda x: x.lower())
_FORMAT_WITH_OTHER_QUOTES = format_with_command(other_xform=lambda x: ("\"" +
                                                                       x +
                                                                       "\""))
_FORMAT_QUOTES_AND_LOWER = format_with_command(var_xform=lambda x: x.lower(),
                                               other_xform=lambda x: ("\"" +
                                                                      x +
                                                                      "\""))


class TestUppercaseVariableNamesOnly(TestCase):
    """Test case for uppercase variable names only."""

    parameters = [param(m) for m in FUNCTIONS_SETTING_VARS]

    @parameterized.expand(parameters, testcase_func_doc=format_with_args(0))
    def test_pass_no_var_set(self, matcher):
        """Check that style/set_var_case passes with {0.cmd}.

        Where no variable is actually set, then there is no linter failure
        """
        # This will trip up matchers that match other arguments
        result = run_linter_throw("{0} ()\n".format(matcher.cmd),
                                  whitelist=["style/set_var_case"])
        self.assertTrue(result)

    @parameterized.expand(parameters,
                          testcase_func_doc=format_with_command())
    def test_pass_no_quotes(self, matcher):
        """Check that style/set_var_case passes with {}.

        Variables set by another CMake command should only be uppercase
        """
        result = run_linter_throw(gen_source_line(matcher),
                                  whitelist=["style/set_var_case"])
        self.assertTrue(result)

    @parameterized.expand(parameters,
                          testcase_func_doc=_FORMAT_WITH_DEREFFED_VAR)
    def test_pass_inside_deref(self, matcher):
        """Check that style/set_var_case passes when var in deref, like {}.

        Pass if variable is uppercase and inside of a deref, because variable
        dereferences are not sink variables.
        """
        xform = lambda x: "${" + x + "}"  # suppress(E731)
        result = run_linter_throw(gen_source_line(matcher,
                                                  match_transform=xform),
                                  whitelist=["style/set_var_case"])
        self.assertTrue(result)

    @parameterized.expand(parameters,
                          testcase_func_doc=_FORMAT_WITH_OTHER_QUOTES)
    def test_pass_other_quotes(self, matcher):
        """Check that style/set_var_case pass with other args quoted in {}."""
        quote = "\"{0}\""
        xform = lambda x: quote.format(x)  # suppress(unnecessary-lambda,E731)
        line = gen_source_line(matcher,
                               other_transform=xform)
        result = run_linter_throw(line,
                                  whitelist=["style/set_var_case"])
        self.assertTrue(result)

    @parameterized.expand(parameters,
                          testcase_func_doc=_FORMAT_WITH_LOWERCASE_VAR)
    def test_fail_no_quotes(self, matcher):  # suppress(no-self-use)
        """Check that style/set_var_case fails with {}, because lowercase."""
        line = gen_source_line(matcher,
                               match_transform=lambda x: x.lower())
        with ExpectedException(LinterFailure):
            run_linter_throw(line,
                             whitelist=["style/set_var_case"])

    @parameterized.expand(parameters,
                          testcase_func_doc=_FORMAT_QUOTES_AND_LOWER)
    def test_fail_other_quotes(self, matcher):  # suppress(no-self-use)
        """Check that style/set_var_case fails with other args quoted in {}."""
        quote = "\"{0}\""
        xform = lambda x: quote.format(x)  # suppress(unnecessary-lambda,E731)
        line = gen_source_line(matcher,
                               match_transform=lambda x: x.lower(),
                               other_transform=xform)
        with ExpectedException(LinterFailure):
            run_linter_throw(line,
                             whitelist=["style/set_var_case"])

    @parameterized.expand(parameters,
                          testcase_func_doc=_FORMAT_WITH_LOWERCASE_VAR)
    def test_replace_no_quotes(self, matcher):
        """Check that style/set_var_case replaces {} with uppercase var.

        Replacement should have uppercase matched argument
        """
        correct = gen_source_line(matcher)
        incorrect = gen_source_line(matcher,
                                    match_transform=lambda x: x.lower())

        def get_replacement():
            """Replacement for lowercase variable."""
            run_linter_throw(incorrect,
                             whitelist=["style/set_var_case"])

        exception = self.assertRaises(LinterFailure, get_replacement)
        self.assertEqual(replacement(exception),
                         (1, correct))


class TestFunctionArgumentsFallOnLine(TestCase):
    """Test alignment of function arguments."""

    def test_pass_args_on_same_line(self):
        """style/argument_align passes when args on same line."""
        self.assertTrue(run_linter_throw("call ($[ONE} TWO THREE \"FOUR\")\n",
                                         whitelist=["style/argument_align"]))

    def test_fail_args_unevenly_spaced(self):  # suppress(no-self-use)
        """style/argument_align fails if args on same line spaced unevenly."""
        with ExpectedException(LinterFailure):
            run_linter_throw("call (ONE   TWO)\n",
                             whitelist=["style/argument_align"])

    def test_suggest_even_spacing(self):
        """style/argument_align suggests even spacing on the same line."""
        def get_replacement():
            """Get replacement for unevenly spaced lines."""
            run_linter_throw("call (ONE   TWO)\n",
                             whitelist=["style/argument_align"])

        exception = self.assertRaises(LinterFailure, get_replacement)
        self.assertEqual(replacement(exception),
                         (1, "call (ONE TWO)\n"))

    def test_fail_args_not_aligned(self):  # suppress(no-self-use)
        """style/argument_align fails when args do not fall on baseline col."""
        with ExpectedException(LinterFailure):
            run_linter_throw("call (ONE\nTWO)\n",
                             whitelist=["style/argument_align"])

    def test_fail_args_dispersed(self):  # suppress(no-self-use)
        """style/argument_align fails if args on same line spaced unevenly."""
        with ExpectedException(LinterFailure):
            run_linter_throw("call (ONE\n"
                             "      ${TWO} \"THREE\"\n"
                             "      FOUR)\n",
                             whitelist=["style/argument_align"])

    def test_fail_bad_kw_align(self):  # suppress(no-self-use)
        """style/argument_align fails if args on same line spaced unevenly."""
        with ExpectedException(LinterFailure):
            run_linter_throw("call (ONE\n"
                             "      TWO THREE\n"
                             "        FOUR)\n",
                             whitelist=["style/argument_align"])

    def test_fail_inconsistent_align(self):  # suppress(no-self-use)
        """style/argument_align fails when args not aligned after first."""
        with ExpectedException(LinterFailure):
            run_linter_throw("call (${ONE} TWO\n"
                             "             THREE)\n",
                             whitelist=["style/argument_align"])

    # Over and under-indent
    @parameterized.expand([
        "     THREE)\n",
        "         THREE)\n"
    ])
    def test_suggest_baseline_align(self, third_line):
        """style/argument_align suggests alignment to the baseline."""
        def get_replacement():
            """Get replacement for unevenly spaced lines."""
            run_linter_throw("call (ONE\n"
                             "      TWO\n" +
                             third_line,
                             whitelist=["style/argument_align"])

        exception = self.assertRaises(LinterFailure, get_replacement)
        self.assertEqual(replacement(exception),
                         # eg  call (ONE
                         (3, ("      THREE)\n")))

    def test_fail_align_func_name(self):  # suppress(no-self-use)
        """style/argument_align fails when args not aligned after second."""
        with ExpectedException(LinterFailure):
            run_linter_throw("function (ONE TWO\n"
                             "          THREE)\n"
                             "endfunction ()\n",
                             whitelist=["style/argument_align"])

    def test_fail_align_macro_name(self):  # suppress(no-self-use)
        """style/argument_align fails when args not aligned after second."""
        with ExpectedException(LinterFailure):
            run_linter_throw("macro (name TWO\n"
                             "       THREE)\n"
                             "endmacro ()\n",
                             whitelist=["style/argument_align"])

    def test_suggest_align_first_arg(self):
        """style/argument_align suggests alignment to function's first arg."""
        def get_replacement():
            """Get replacement for unevenly spaced lines."""
            run_linter_throw("function (name ONE\n"
                             "            TWO)\n"
                             "endfunction ()\n",
                             whitelist=["style/argument_align"])

        exception = self.assertRaises(LinterFailure, get_replacement)
        self.assertEqual(replacement(exception),
                         # eg, function (name ONE
                         (2, ("               TWO)\n")))

    def test_pass_args_aligend(self):
        """style/argument_align passes when args aligned."""
        self.assertTrue(run_linter_throw("call (ONE\n"
                                         "      TWO)\n",
                                         whitelist=["style/argument_align"]))

    def test_pass_align_after(self):
        """style/argument_align passes when args aligned after first."""
        self.assertTrue(run_linter_throw("call (ONE TWO\n"
                                         "      THREE)\n",
                                         whitelist=["style/argument_align"]))

    def test_pass_args_after_keyword(self):
        """style/argument_align passes with args after keyword arg."""
        self.assertTrue(run_linter_throw("call (ONE\n"
                                         "      KEYWORD TWO\n"
                                         "      KEYWORD THREE)\n",
                                         whitelist=["style/argument_align"]))

    def test_pass_align_after_keyword(self):
        """style/argument_align passes with args after keyword arg."""
        self.assertTrue(run_linter_throw("call (ONE\n"
                                         "      KEYWORD TWO\n"
                                         "              THREE)\n",
                                         whitelist=["style/argument_align"]))

    nonvariable_keywords = [
        "${KEYWORD}",
        "\"KEYWORD\"",
        "KEYWORD/ARGUMENT\"",
        "1234"
    ]

    @parameterized.expand(nonvariable_keywords)
    def test_fail_if_kw_not_var_align(self, keyword):  # suppress(no-self-use)
        """style/argument_align fails when args not aligned after second."""
        kw_len = len(keyword)
        with ExpectedException(LinterFailure):
            run_linter_throw("call (ONE\n"
                             "      {0} ONE".format(keyword) +
                             "      " + " " * kw_len + " TWO)",
                             whitelist=["style/argument_align"])

    @parameterized.expand(nonvariable_keywords)
    def test_fail_if_kw_not_var_after(self, keyword):  # suppress(no-self-use)
        """style/argument_align fails when args not aligned after second."""
        with ExpectedException(LinterFailure):
            run_linter_throw("call (ONE\n"
                             "      {0} ONE)\n".format(keyword),
                             whitelist=["style/argument_align"])

    def test_pass_align_after_func(self):
        """style/argument_align passes when args aligned after second."""
        self.assertTrue(run_linter_throw("function (name TWO\n"
                                         "               THREE)\n"
                                         "endfunction ()\n",
                                         whitelist=["style/argument_align"]))

    def test_pass_align_after_macro(self):
        """style/argument_align passes when args aligned after second."""
        self.assertTrue(run_linter_throw("macro (name TWO\n"
                                         "            THREE)\n"
                                         "endmacro ()\n",
                                         whitelist=["style/argument_align"]))

    def test_pass_dispersed_if_cond(self):
        """style/argument_align passes when arguments to if are dispersed."""
        self.assertTrue(run_linter_throw("if (CONDITION AND OTHER_COND OR\n"
                                         "    FINAL_CONDITION AND NOT COND)\n"
                                         "endif ()",
                                         whitelist=["unused/private_var"]))


class TestSingleQuoteUsage(TestCase):
    """Test that we are only allowed to use double quotes for strings."""

    def test_pass_use_double_quotes(self):
        """Check style/doublequotes passes when strings use double quotes."""
        self.assertTrue(run_linter_throw("call (\"ARGUMENT\")\n",
                                         whitelist=["style/doublequotes"]))

    def test_pass_sigle_in_double(self):
        """Check style/doublequotes passes if strings use internal single."""
        self.assertTrue(run_linter_throw("call (\"\'ARGUMENT\'\")\n",
                                         whitelist=["style/doublequotes"]))

    def test_fail_use_single_quotes(self):  # suppress(no-self-use)
        """Check style/doublequotes fails when strings use single quotes."""
        with ExpectedException(LinterFailure):
            run_linter_throw("call (\'ARGUMENT\')\n",
                             whitelist=["style/doublequotes"])

    def test_replace_single_with_double(self):
        """Check style/doublequotes replaces single quote use with double."""
        def get_replacement():
            """Replacement for single outer quotes."""
            run_linter_throw("call (\'ARGUMENT\')\n",
                             whitelist=["style/doublequotes"])

        exception = self.assertRaises(LinterFailure, get_replacement)
        self.assertEqual(replacement(exception),
                         (1, "call (\"ARGUMENT\")\n"))

    def test_replace_only_outerquotes(self):
        """Check style/doublequotes only replaces outer quotes."""
        def get_replacement():
            """Replacement for single outer quote."""
            run_linter_throw("call (\'ARG \\'U\\' MENT\')\n",
                             whitelist=["style/doublequotes"])

        exception = self.assertRaises(LinterFailure, get_replacement)
        self.assertEqual(replacement(exception),
                         (1, "call (\"ARG \\'U\\' MENT\")\n"))


HEADER_BODY_STRUCTURES = [
    "function",
    "macro",
    "while",
    "foreach",
    "if"
]


class TestIndentation(TestCase):
    """Test indentation checks."""

    def test_pass_no_indent_spec(self):
        """style/indent passes when no indentation is specified."""
        self.assertTrue(run_linter_throw("function_call ()\n",
                                         whitelist=["style/indent"]))

    def test_pass_top_call_noindent(self):
        """style/indent passes with zero indents for toplevel calls."""
        self.assertTrue(run_linter_throw("function_call ()\n",
                                         whitelist=["style/indent"],
                                         indent=1))

    def test_pass_top_def_noindent(self):
        """style/indent passes with zero indents for toplevel definitions."""
        self.assertTrue(run_linter_throw("function (f ARG)\nendfunction()\n",
                                         whitelist=["style/indent"],
                                         indent=1))

    def test_pass_call_one_indent(self):
        """style/indent passes with one indent for nested calls."""
        script = "function (f ARG)\n call (ARG)\nendfunction ()"
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["style/indent"],
                                         indent=1))

    def test_pass_if_body_one_indent(self):
        """style/indent passes with one indent for if body."""
        script = "if (COND)\n call (ARG)\nendif ()"
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["style/indent"],
                                         indent=1))

    def test_pass_nest_if_indent(self):
        """style/indent passes with one indent for if body."""
        script = "if (COND)\n if (OTHER)\n  call (ARG)\n endif ()\nendif ()"
        self.assertTrue(run_linter_throw(script,
                                         whitelist=["style/indent"],
                                         indent=1))

    def test_fail_one_indent_top_call(self):  # suppress(no-self-use)
        """style/indent fails with one indent for toplevel calls."""
        with ExpectedException(LinterFailure):
            run_linter_throw(" function_call ()\n",
                             whitelist=["style/indent"],
                             indent=1)

    def test_fail_one_indent_toplevel(self):  # suppress(no-self-use)
        """style/indent fails with one indent for toplevel defs."""
        with ExpectedException(LinterFailure):
            run_linter_throw(" function (definition ARG)\n endfunction ()",
                             whitelist=["style/indent"],
                             indent=1)

    @parameterized.expand(HEADER_BODY_STRUCTURES)
    def test_fail_bad_term_indent(self, structure):  # suppress(no-self-use)
        """style/indent fails with one indent terminator."""
        with ExpectedException(LinterFailure):
            run_linter_throw("{0} ()\n end{0} ()".format(structure),
                             whitelist=["style/indent"],
                             indent=1)

    @parameterized.expand([
        "else",
        "elseif"
    ])  # suppress(no-self-use)
    def test_fail_mismatch_if_alt(self, alt):
        """style/indent fails when else, elseif has mismatched indent."""
        with ExpectedException(LinterFailure):
            script = "if (COND)\n {0} (COND)\nendif ()"
            run_linter_throw(script.format(alt),
                             whitelist=["style/indent"],
                             indent=1)

    def test_fail_noindent_nested_call(self):  # suppress(no-self-use)
        """style/indent fails with zero indents for a nested call."""
        with ExpectedException(LinterFailure):
            script = "function (f ARG)\ncall (ARG)\nendfunction ()"
            run_linter_throw(script, whitelist=["style/indent"], indent=1)

    def test_suggest_more_indent(self):
        """style/indent suggests more indentation where required."""
        script = "function (f ARG)\ncall (ARG)\nendfunction ()"

        def get_replacement():
            """Replacement for lack of indent."""
            run_linter_throw(script, whitelist=["style/indent"], indent=1)

        exception = self.assertRaises(LinterFailure, get_replacement)
        self.assertEqual(replacement(exception),
                         (2, " call (ARG)\n"))

    def test_suggest_less_indent(self):
        """style/indent suggests less indentation where required."""
        script = "function (f ARG)\n call (ARG)\n endfunction ()\n"

        def get_replacement():
            """Replacement for too much indent."""
            run_linter_throw(script, whitelist=["style/indent"], indent=1)

        exception = self.assertRaises(LinterFailure, get_replacement)
        self.assertEqual(replacement(exception),
                         (3, "endfunction ()\n"))
