# /polysquarecmakelinter/check_style.py
#
# Linter checks for style guide
#
# See /LICENCE.md for Copyright information
"""Linter checks for style guide."""

import re

from collections import namedtuple

from cmakeast import ast_visitor

from cmakeast.ast import WordType

from polysquarecmakelinter import find_set_variables
from polysquarecmakelinter import ignore
from polysquarecmakelinter import util

from polysquarecmakelinter.types import LinterFailure

_RE_DOUBLE_OUTER_QUOTES = re.compile("^\".*\"$")
_RE_IS_DEFINITION = re.compile(r"function|macro")

_RE_HEADERBODY_LIKE = re.compile(r"WhileStatement|"
                                 "ForeachStatement|"
                                 "FunctionDefinition|"
                                 "MacroDefinition")
_RE_FUNCTION_CALL = re.compile(r"FunctionCall")
_RE_IF_BLOCK = re.compile(r"IfBlock")
_RE_TOPLEVEL = re.compile(r"ToplevelBody")


def space_before_call(contents, abstract_syntax_tree):
    """Check that each function call is preceded by a single space."""
    errors = []

    def _call_handler(name, node):
        """Handle function calls."""
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
    """Check that function / macro usage is all lowercase."""
    errors = []

    def _call_handler(name, node):
        """Handle function calls."""
        assert name == "FunctionCall"

        if node.name.lower() != node.name:
            msg = "{0} is not lowercase".format(node.name)
            replacement = util.replace_word(contents[node.line - 1],
                                            node.col - 1,
                                            node.name,
                                            node.name.lower())
            errors.append(LinterFailure(msg, node.line, replacement))

    def _definition_handler(name, node):
        """Handle function calls and macro definitions."""
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
    """Check that arguments to definitions are all uppercase."""
    errors = []

    def _definition_visitor(name, node):
        """Visit all definitions."""
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
    """Check that each variable mutated is capitalized."""
    errors = []

    variables = find_set_variables.in_tree(abstract_syntax_tree)
    for evaluate in variables:

        evaluate_upper = evaluate.contents.upper()

        # Argument should be either String or Variable and a transformation
        # to uppercase should have no effect
        if (util.is_word_sink_variable(evaluate.type) and
                evaluate_upper != evaluate.contents):
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

AlignmentInfo = namedtuple("AlignmentInfo", "col line line_has_kw")


def _expected_alignment(arg,
                        baseline_col,
                        baseline_line,
                        current_align):
    """Get expected alignment for the function argument arg."""
    col = current_align.col
    line = current_align.line
    line_has_kw = current_align.line_has_kw

    if arg.col == baseline_col:
        # Baseline column - reset align.col

        if (arg.type == WordType.Variable or
                arg.line == baseline_line):
            # This might be a keyword arg - allow alignment to this
            # line. Otherwise it is the first argument on this line,
            # or a function call where we allow arguments on any line
            line = arg.line
        else:
            # This is not a keyword arg. Do not allow alignment to
            # this line (only this column)
            line = None

        line_has_kw = (arg.type == WordType.Variable)
        col = arg.col

    # If we're on our currently aligned line, and this line starts
    # with a keyword-like argument, then allow align.col
    # to shift appropriately, check horizontal space
    if line == arg.line and line_has_kw:
        col = arg.col

    return AlignmentInfo(col, line, line_has_kw)


def _check_horizontal_space(node, index, contents):
    """Check horizontal space between arguments on same line."""
    if index > 0:
        current_column = node.arguments[index].col - 1
        previous_column = node.arguments[index - 1].col - 1
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
            return LinterFailure(msg, node.line, replacement)


def _check_alignment(arg,
                     last_align,
                     baseline_col,
                     baseline_line,
                     contents):
    """Check alignment of arg."""
    align = _expected_alignment(arg,
                                baseline_col,
                                baseline_line,
                                last_align)

    misaligned_col = align.col and align.col != arg.col
    misaligned_line = align.line and align.line != arg.line

    def _offset_with_space(line, align_col, arg_col):
        """Insert spaces as required to place arg at align_col."""
        offset = max(0, arg_col - align_col)
        spaces = max(0, align_col - arg_col)
        return util.replace_word(line,
                                 arg_col - 1 - offset,
                                 " " * offset,
                                 " " * spaces)

    if ((misaligned_col or not align.col) and
            (misaligned_line or not align.line)):

        msg_parts_append_table = [
            (lambda: misaligned_line is not None,
             "line {0}".format(align.line)),
            (lambda: misaligned_col is not None,
             "col {0}".format(align.col)),
            (lambda: align.col != baseline_col,
             "col {0}".format(baseline_col))
        ]

        replacement = None
        msg_parts = [msg for c, msg in msg_parts_append_table if c()]

        if misaligned_col and align.col == baseline_col:
            replacement = _offset_with_space(contents[arg.line - 1],
                                             align.col,
                                             arg.col)

        msg = ("Argument {0} must fall on any of: "
               "{1}".format(arg.contents,
                            ", ".join(msg_parts)))
        return align, LinterFailure(msg, arg.line, replacement)

    return align, None


def func_args_aligned(contents, abstract_syntax_tree):
    """Check that function arguments are aligned.

    Function arguments must be aligned either to the same line or
    must fall on the same column as the last argument on the line of
    the function call. The only special case is for definitions, where we
    align after the second argument, (eg the first argument to the defined
    function or macro)
    """
    errors = []

    def _call_visitor(name, node):
        """Visit all function calls."""
        assert name == "FunctionCall"

        def _align_violations(node):
            """All alignment violations in node."""
            arguments_len = len(node.arguments)

            if arguments_len == 0:
                return

            # Check if this was a definition. If so, then we align after the
            # last argument and not after the first.
            is_definition = (_RE_IS_DEFINITION.match(node.name) is not None)

            if is_definition and arguments_len > 1:
                baseline_col = node.arguments[1].col
            else:
                baseline_col = node.arguments[0].col

            align = AlignmentInfo(col=node.arguments[0].col,
                                  line=node.arguments[0].line,
                                  line_has_kw=False)

            for index in range(0, len(node.arguments)):
                arg = node.arguments[index]
                # If the argument is on the same line as the function call,
                # then update align.col and make sure that the argument is one
                # space away from the last argument
                if align.line == arg.line:
                    yield _check_horizontal_space(node, index, contents)

                align, error = _check_alignment(arg,
                                                align,
                                                baseline_col,
                                                node.arguments[0].line,
                                                contents)

                yield error

        errors.extend([e for e in _align_violations(node) if e is not None])

    ast_visitor.recurse(abstract_syntax_tree,
                        function_call=ignore.visitor_depth(_call_visitor))
    return errors


def double_outer_quotes(contents, abstract_syntax_tree):
    """Check that all outer quotes are double quotes."""
    errors = []

    def _word_visitor(name, node):
        """Visit all arguments."""
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


# The mccabe checker complains here but that's because it contains lots
# of nested functions. There's not much we can do for that.
def _visit_with_flat_if_depth(abstract_syntax_tree,  # NOQA
                              function_visitor):
    """Visit function calls with IfBlock nodes flattened."""
    def _visit_header_body_block(node, depth):
        """Handle header/body like statements."""
        function_visitor(node.header, depth)

        for sub in node.body:
            _node_dispatch(sub, depth + 1)

        if getattr(node, "footer", None) is not None:
            function_visitor(node.footer, depth)

    def _visit_if_block(node, depth):
        """Handle if blocks."""
        substatements = ([node.if_statement] +
                         node.elseif_statements +
                         [node.else_statement])

        for substatement in substatements:
            if substatement:
                _visit_header_body_block(substatement, depth)

        function_visitor(node.footer, depth)

    def _visit_toplevel(node, depth):
        """Handle toplevel blocks."""
        assert depth == 0

        for statement in node.statements:
            _node_dispatch(statement, depth)

    indent_node_dispatch = [
        (_RE_HEADERBODY_LIKE, _visit_header_body_block),
        (_RE_IF_BLOCK, _visit_if_block),
        (_RE_FUNCTION_CALL, function_visitor),
        (_RE_TOPLEVEL, _visit_toplevel)
    ]

    def _node_dispatch(node, depth):
        """Dispatch per-node, handling depth like actual indent depth."""
        for regex, handler in indent_node_dispatch:
            if regex.match(node.__class__.__name__):
                handler(node, depth)

    _node_dispatch(abstract_syntax_tree, 0)


def calls_indented_correctly(contents, abstract_syntax_tree, **kwargs):
    """Check that all calls to functions are indented at the correct level."""
    errors = []

    try:
        indent = kwargs["indent"]
    except KeyError:
        return errors

    def _visit_function_call(node, depth):
        """Handle function calls."""
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

    _visit_with_flat_if_depth(abstract_syntax_tree, _visit_function_call)

    return errors
