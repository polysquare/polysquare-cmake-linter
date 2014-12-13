# /polysquarecmakelinter/check_style.py
#
# Linter checks for style guide
#
# See LICENCE.md for Copyright information
"""Linter checks for style guide"""

import re

from cmakeast import ast_visitor
from cmakeast.ast import WordType
from polysquarecmakelinter import find_set_variables
from polysquarecmakelinter.types import LinterFailure
from polysquarecmakelinter import ignore
from polysquarecmakelinter import util

_RE_DOUBLE_OUTER_QUOTES = re.compile("^\".*\"$")
_RE_IF_CONDITION = re.compile(r"if|elseif")
_RE_IS_DEFINITION = re.compile(r"function|macro")

_RE_HEADERBODY_LIKE = re.compile(r"WhileStatement|"
                                 "ForeachStatement|"
                                 "FunctionDefinition|"
                                 "MacroDefinition")
_RE_FUNCTION_CALL = re.compile(r"FunctionCall")
_RE_IF_BLOCK = re.compile(r"IfBlock")
_RE_TOPLEVEL = re.compile(r"ToplevelBody")


def space_before_call(contents, abstract_syntax_tree):
    """Checks that each function call is preceded by a single space"""

    errors = []

    def _call_handler(name, node):
        """Handles function calls"""

        assert name == "FunctionCall"

        line_index = node.line - 1
        col_index = node.col - 1
        end_of_name_index = col_index + len(node.name)
        num_spaces_until_openparen = 0
        index = end_of_name_index
        while contents[line_index][index] != "(":
            index += 1

        # AST checks will assert if the open paren is not found here

        num_spaces_until_openparen = index - end_of_name_index

        # Must be one space only
        if num_spaces_until_openparen != 1:
            extra_spaces = num_spaces_until_openparen - 1
            msg = "{0} extra spaces between call of {1}".format(extra_spaces,
                                                                node.name)
            replacement = util.replace_word(contents[line_index],
                                            end_of_name_index,
                                            " " * (extra_spaces + 1),
                                            " ")
            errors.append(LinterFailure(msg, node.line, replacement))

    ast_visitor.recurse(abstract_syntax_tree,
                        function_call=ignore.visitor_depth(_call_handler))

    return errors


def lowercase_functions(contents, abstract_syntax_tree):
    """Checks that function / macro usage is all lowercase"""

    errors = []

    def _call_handler(name, node):
        """Handles function calls"""
        assert name == "FunctionCall"

        if node.name.lower() != node.name:
            msg = "{0} is not lowercase".format(node.name)
            replacement = util.replace_word(contents[node.line - 1],
                                            node.col - 1,
                                            node.name,
                                            node.name.lower())
            errors.append(LinterFailure(msg, node.line, replacement))

    def _definition_handler(name, node):
        """Handles function calls and macro definitions"""
        assert name == "FunctionDefinition" or name == "MacroDefinition"

        definition_name_word = node.header.arguments[0]
        definition_name = definition_name_word.contents

        if definition_name.lower() != definition_name:
            msg = "{0} name {1} is not lowercase".format(name, definition_name)
            line_index = definition_name_word.line - 1
            col_index = definition_name_word.col - 1
            replacement = util.replace_word(contents[line_index],
                                            col_index,
                                            definition_name,
                                            definition_name.lower())
            errors.append(LinterFailure(msg,
                                        definition_name_word.line,
                                        replacement))

    ast_visitor.recurse(abstract_syntax_tree,
                        function_call=ignore.visitor_depth(_call_handler),
                        function_def=ignore.visitor_depth(_definition_handler),
                        macro_def=ignore.visitor_depth(_definition_handler))

    return errors


def uppercase_arguments(contents, abstract_syntax_tree):
    """Checks that arguments to definitions are all uppercase"""

    errors = []

    def _definition_visitor(name, node):
        """Visit all definitions"""

        assert name == "FunctionDefinition" or name == "MacroDefinition"

        if len(node.header.arguments) < 2:
            return

        for arg in node.header.arguments[1:]:
            if arg.contents.upper() != arg.contents:
                msg = "{0} must be uppercase".format(arg.contents)
                line_index = arg.line - 1
                col_index = arg.col - 1
                replacement = util.replace_word(contents[line_index],
                                                col_index,
                                                arg.contents,
                                                arg.contents.upper())
                errors.append(LinterFailure(msg, arg.line, replacement))

    ast_visitor.recurse(abstract_syntax_tree,
                        function_def=ignore.visitor_depth(_definition_visitor),
                        macro_def=ignore.visitor_depth(_definition_visitor))

    return errors


def set_variables_capitalized(contents, abstract_syntax_tree):
    """Checks that each variable mutated is capitalized"""

    errors = []

    variables = find_set_variables.in_tree(abstract_syntax_tree)
    for evaluate in variables:

        evaluate_upper = evaluate.contents.upper()

        # Argument should be either String, VariableDereference
        # or Variable and a transformation to uppercase
        # should have no effect
        if not (util.is_word_sink_variable(evaluate.type) and
                evaluate_upper == evaluate.contents):
            desc = "{0} must be uppercase".format(evaluate.contents)
            line = evaluate.line - 1
            replacement = util.replace_word(contents[line],
                                            evaluate.col - 1,
                                            evaluate.contents,
                                            evaluate_upper)
            errors.append(LinterFailure(desc,
                                        evaluate.line,
                                        replacement))
            break

    return errors


def func_args_aligned(contents, abstract_syntax_tree):
    """Checks that function arguments are aligned


    Function arguments must be aligned either to the same line or
    must fall on the same column as the last argument on the line of
    the function call. The only special case is for definitions, where we
    align after the second argument, (eg the first argument to the defined
    function or macro)
    """

    errors = []

    def _check_horizontal_space(node, index):
        """Checks horizontal space between arguments on same line"""
        if index > 0:
            current_column = node.arguments[index].col
            previous_column = node.arguments[index - 1].col
            previous_len = len(node.arguments[index - 1].contents)
            spaces_start = previous_column + previous_len
            num_spaces = current_column - (previous_column + previous_len)

            line_number = node.arguments[index].line - 1

            if num_spaces != 1:
                cur = node.arguments[index].contents
                prev = node.arguments[index - 1].contents

                msg = "Must be a single space between {0} and {1}".format(cur,
                                                                          prev)
                replacement = util.replace_word(contents[line_number],
                                                spaces_start,
                                                " " * num_spaces,
                                                " ")
                errors.append(LinterFailure(msg, node.line, replacement))

    def _call_visitor(name, node):
        """Visits all function calls"""
        assert name == "FunctionCall"

        class AlignmentInfo(object):
            """Mutable alignment info"""

            def __init__(self):
                """Initialize"""

                super(AlignmentInfo, self).__init__()

                self.col = None
                self.line = None
                self.line_has_kw = False

        align = AlignmentInfo()
        arguments_len = len(node.arguments)

        if arguments_len == 0:
            return

        # Check if this was a defintion. If so, then we align after the last
        # argument and not after the first.
        is_definition = (_RE_IS_DEFINITION.match(node.name) is not None)
        is_if_cond = (_RE_IF_CONDITION.match(node.name) is not None)

        if is_definition and arguments_len > 1:
            baseline_col = node.arguments[1].col
        else:
            baseline_col = node.arguments[0].col

        align.col = node.arguments[0].col
        align.line = node.arguments[0].line

        def _check_alignment(arg, index):
            """Checks alignment of arg"""

            if align.line == arg.line:
                _check_horizontal_space(node, index)

            if arg.col == baseline_col:
                # Baseline column - reset align.col

                if (arg.type == WordType.Variable or
                        is_if_cond or
                        arg.line == node.arguments[0].line):
                    # This might be a keyword arg - allow alignment to this
                    # line. Otherwise it is the first argument on this line,
                    # or a function call where we allow arguments on any line
                    align.line = arg.line
                else:
                    # This is not a keyword arg. Do not allow alignment to
                    # this line (only this column)
                    align.line = None

                if arg.type == WordType.Variable:
                    align.line_has_kw = True
                else:
                    align.line_has_kw = False
                align.col = arg.col

            # If we're on our currently aligned line, and this line starts
            # with a keyword-like argument, then allow align.col
            # to shift appropriately, check horizontal space
            if align.line == arg.line and align.line_has_kw:
                align.col = arg.col

            misaligned_col = align.col and align.col != arg.col
            misaligned_line = align.line and align.line != arg.line

            if ((misaligned_col or not align.col) and
                    (misaligned_line or not align.line)):

                msg_parts = []
                replacement = None

                if misaligned_line is not None:
                    msg_parts.append("line {0}".format(align.line))

                if misaligned_col is not None:
                    msg_parts.append("col {0}".format(align.col))

                if align.col != baseline_col:
                    msg_parts.append("col {0}".format(baseline_col))

                if misaligned_line is None:
                    line_idx = arg.line - 1
                    offset = min(0, align.col - arg.col)
                    spaces = max(0, align.col - arg.col)
                    replacement = util.replace_word(contents[line_idx],
                                                    arg.col + offset,
                                                    " " * offset,
                                                    " " * spaces)

                msg = ("Argument {0} must fall on any of: "
                       "{1}".format(arg.contents,
                                    ", ".join(msg_parts)))
                errors.append(LinterFailure(msg,
                                            arg.line,
                                            replacement))

        for index in range(0, len(node.arguments)):
            arg = node.arguments[index]
            # If the argument is on the same line as the function call, then
            # update align.col and make sure that the argument is one
            # space away fromt the last argument
            _check_alignment(arg, index)

    ast_visitor.recurse(abstract_syntax_tree,
                        function_call=ignore.visitor_depth(_call_visitor))
    return errors


def double_outer_quotes(contents, abstract_syntax_tree):
    """Checks that all outer quotes are double quotes"""

    errors = []

    def _word_visitor(name, node):
        """Visits all arguments"""
        assert name == "Word"

        if node.type == WordType.String:
            if not _RE_DOUBLE_OUTER_QUOTES.match(node.contents):
                msg = "{0} must use double quotes".format(node.contents)
                replacement_word = "\"{0}\"".format(node.contents[1:-1])
                replacement = util.replace_word(contents[node.line - 1],
                                                node.col - 1,
                                                node.contents,
                                                replacement_word)
                errors.append(LinterFailure(msg, node.line, replacement))

    ast_visitor.recurse(abstract_syntax_tree,
                        word=ignore.visitor_depth(_word_visitor))

    return errors


def calls_indented_correctly(contents, abstract_syntax_tree, **kwargs):
    """Check that all calls to functions are indented at the correct level"""

    errors = []

    try:
        indent = kwargs["indent"]
    except KeyError:
        return errors

    def _visit_function_call(node, depth):
        """Hanldes function calls"""

        col = node.col
        expected = 1 + (depth * indent)
        if node.col != expected:
            delta = expected - node.col
            msg = "Expected {0} to be on column {1}".format(node.name,
                                                            expected)
            replacement = util.replace_word(contents[node.line - 1],
                                            col - 1 + min(0, delta),
                                            " " * max(0, delta * -1),
                                            " " * max(0, delta))
            errors.append(LinterFailure(msg, node.line, replacement))

    def _visit_header_body_block(node, depth):
        """Handles header/body like statements"""

        _visit_function_call(node.header, depth)

        for sub in node.body:
            _node_dispatch(sub, depth + 1)

        if getattr(node, "footer", None) is not None:
            _visit_function_call(node.footer, depth)

    def _visit_if_block(node, depth):
        """Handles if blocks"""

        _visit_header_body_block(node.if_statement, depth)

        for elseif_statement in node.elseif_statements:
            _visit_header_body_block(elseif_statement, depth)

        if node.else_statement:
            _visit_header_body_block(node.else_statement, depth)

        _visit_function_call(node.footer, depth)

    def _visit_toplevel(node, depth):
        """Handles toplevel blocks"""
        assert depth == 0

        for statement in node.statements:
            _node_dispatch(statement, depth)

    indent_node_dispatch = [
        (_RE_HEADERBODY_LIKE, _visit_header_body_block),
        (_RE_IF_BLOCK, _visit_if_block),
        (_RE_FUNCTION_CALL, _visit_function_call),
        (_RE_TOPLEVEL, _visit_toplevel)
    ]

    def _node_dispatch(node, depth):
        """Dispatches per-node, handling depth like actual indent depth"""

        for regex, handler in indent_node_dispatch:
            if regex.match(node.__class__.__name__):
                handler(node, depth)

    _node_dispatch(abstract_syntax_tree, 0)

    return errors
