# /polysquarecmakelinter/find_set_variables.py
#
# Details to find set variables in a module
#
# See LICENCE.md for Copyright information
"""Details to find set variables in a module"""

from collections import namedtuple
from cmakeast import ast_visitor
from polysquarecmakelinter import ignore


# Subclass namedtuple so that we can have a default argument for sub
class _SetVariable(namedtuple("_SetVariable", "cmd find sub")):
    """_SetVariable namedtuple with default variable for sub"""

    def __new__(cls, cmd, find, sub=None):
        """Factory with sub defaulted out"""
        return super(_SetVariable, cls).__new__(cls, cmd, find, sub)


def _find_arg_no(num):
    """Return an argument finder for argument at num"""
    class Finder(object):
        """Finder for arguments after num"""

        def find(self, arguments):  # pylint:disable=no-self-use
            """Returns argument at num"""
            try:
                return arguments[num]
            except IndexError:
                return None

        def generate(self,  # pylint:disable=no-self-use
                     sub,
                     other_transform,
                     match_transform):
            """Generates argument list of num size"""
            # A cheap hack to ensure that we generate a few extra in the
            # list GET case
            gen_num = abs(num - 1 if sub is not None else num)
            args_before = " ".join([other_transform("ARGUMENT")] * (gen_num))
            match_arg = match_transform("VALUE")
            subcommand = sub + " " if sub is not None else ""
            return subcommand + " ".join([args_before, match_arg])

    return Finder()


def _find_after_arg(argument):
    """Return an argument finder for an argument after argument"""
    class Finder(object):
        """Finder for arguments after argument"""

        def find(self, arguments):  # pylint:disable=no-self-use
            """Returns argument after argument or None if not found"""
            try:
                argument_index = 1
                for argument_index in range(1, len(arguments)):
                    if arguments[argument_index - 1].contents == argument:
                        break

                return arguments[argument_index]
            except IndexError:
                return None

        def generate(self,  # pylint:disable=no-self-use
                     sub,
                     other_transform,
                     match_transform):
            """Generates argument list of ARGUMENT__ {argument} VALUE"""
            args_before = other_transform("ARGUMENT__ {0}".format(argument))
            match_arg = match_transform("VALUE")
            subcommand = sub + " " if sub is not None else ""
            return subcommand + " ".join([args_before, match_arg])

    return Finder()


FUNCTIONS_SETTING_VARIABLES = [
    _SetVariable("aux_source_directory", _find_arg_no(1)),
    _SetVariable("build_command", _find_arg_no(0)),
    _SetVariable("cmake_host_system_information", _find_arg_no(1),
                 sub="RESULT"),
    _SetVariable("cmake_policy", _find_arg_no(2), sub="GET"),
    _SetVariable("execute_process", _find_after_arg("RESULT_VARIABLE")),
    _SetVariable("execute_process", _find_after_arg("OUTPUT_VARIABLE")),
    _SetVariable("execute_process", _find_after_arg("ERROR_VARIABLE")),
    _SetVariable("file", _find_arg_no(2), sub="READ"),
    _SetVariable("file", _find_arg_no(2), sub="STRINGS"),
    _SetVariable("file", _find_arg_no(2), sub="MD5"),
    _SetVariable("file", _find_arg_no(2), sub="SHA1"),
    _SetVariable("file", _find_arg_no(2), sub="SHA224"),
    _SetVariable("file", _find_arg_no(2), sub="SHA256"),
    _SetVariable("file", _find_arg_no(2), sub="SHA384"),
    _SetVariable("file", _find_arg_no(2), sub="SHA512"),
    _SetVariable("file", _find_arg_no(1), sub="GLOB"),
    _SetVariable("file", _find_arg_no(1), sub="GLOB_RECURSE"),
    _SetVariable("file", _find_arg_no(1), sub="RELATIVE_PATH"),
    _SetVariable("file", _find_arg_no(2), sub="TO_CMAKE_PATH"),
    _SetVariable("file", _find_arg_no(2), sub="TO_NATIVE_PATH"),
    _SetVariable("file", _find_after_arg("LOG"), sub="DOWNLOAD"),
    _SetVariable("file", _find_after_arg("LOG"), sub="UPLOAD"),
    _SetVariable("file", _find_after_arg("STATUS"), sub="DOWNLOAD"),
    _SetVariable("file", _find_after_arg("STATUS"), sub="UPLOAD"),
    _SetVariable("file", _find_arg_no(2), sub="TIMESTAMP"),
    _SetVariable("find_file", _find_arg_no(0)),
    _SetVariable("find_library", _find_arg_no(0)),
    _SetVariable("find_path", _find_arg_no(0)),
    _SetVariable("find_program", _find_arg_no(0)),
    _SetVariable("get_cmake_property", _find_arg_no(0)),
    _SetVariable("get_directory_property", _find_arg_no(0)),
    _SetVariable("get_filename_component", _find_arg_no(0)),
    _SetVariable("get_property", _find_arg_no(0)),
    _SetVariable("get_source_file_property", _find_arg_no(1)),
    _SetVariable("get_target_property", _find_arg_no(0)),
    _SetVariable("get_test_property", _find_arg_no(0)),
    _SetVariable("include", _find_after_arg("RESULT_VARIABLE")),
    _SetVariable("separate_arguments", _find_arg_no(1)),
    _SetVariable("set", _find_arg_no(0)),
    _SetVariable("unset", _find_arg_no(0)),
    _SetVariable("try_compile", _find_after_arg("RESULT_VAR")),
    _SetVariable("try_compile", _find_after_arg("OUTPUT_VARIABLE")),
    _SetVariable("try_run", _find_after_arg("RUN_RESULT_VAR")),
    _SetVariable("try_run", _find_after_arg("COMPILE_RESULT_VAR")),
    _SetVariable("try_run", _find_after_arg("RUN_OUTPUT_VARIABLE")),
    _SetVariable("try_run", _find_after_arg("OUTPUT_VARIABLE")),
    _SetVariable("list", _find_arg_no(2), sub="LENGTH"),
    _SetVariable("list", _find_arg_no(-1), sub="GET"),
    _SetVariable("list", _find_arg_no(3), sub="FIND"),
    _SetVariable("list", _find_arg_no(2), sub="REMOVE_ITEM"),
    _SetVariable("list", _find_arg_no(1), sub="REMOVE_AT"),
    _SetVariable("list", _find_arg_no(1), sub="REMOVE_DUPLICATES"),
    _SetVariable("list", _find_arg_no(1), sub="REVERSE"),
    _SetVariable("list", _find_arg_no(1), sub="SORT"),
    _SetVariable("list", _find_arg_no(1), sub="APPEND"),
    _SetVariable("list", _find_arg_no(1), sub="INSERT"),
    _SetVariable("match", _find_arg_no(1), sub="EXPR")
]

_FUNCTIONS_SETTING_VARS_INT = (FUNCTIONS_SETTING_VARIABLES +
                               [_SetVariable("set_property",
                                             _find_after_arg("PROPERTY"),
                                             sub="GLOBAL")])


def by_function_call(node):
    """Returns a variable (as a word node) set by a function call, if any"""
    for matcher in _FUNCTIONS_SETTING_VARS_INT:
        if matcher.cmd == node.name:
            # Exclude where subcommand does not match
            # Note: pylint trips up on the generated code and believes that
            # matcher has no attribute named "sub". This is incorrect, so
            # a warning is suppressed here.
            if matcher.sub is not None:  # pylint:disable=no-member
                try:
                    if (matcher.sub !=  # pylint:disable=no-member
                            node.arguments[0].contents):
                        continue
                except IndexError:
                    continue

            evaluate = matcher.find.find(node.arguments)

            if evaluate:
                return evaluate

    return None


def in_tree(abstract_syntax_tree):
    """Find all assigned variables in this abstract_syntax_tree"""

    variables = []

    def _call_visitor(name, node):
        """Visits all function calls"""
        assert name == "FunctionCall"

        evaluate = by_function_call(node)
        if evaluate:
            variables.append(evaluate)

    ast_visitor.recurse(abstract_syntax_tree,
                        function_call=ignore.visitor_depth(_call_visitor))

    return variables
