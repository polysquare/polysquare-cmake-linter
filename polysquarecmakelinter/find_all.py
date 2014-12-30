# /polysquarecmakelinter/find_all.py
#
# Details to find certain occurrences of nodes
#
# See LICENCE.md for Copyright information
"""Detail to find certain occurrences of nodes."""

import re

from cmakeast import ast_visitor

from polysquarecmakelinter import find_set_variables
from polysquarecmakelinter import find_variables_in_scopes
from polysquarecmakelinter import util

_RE_VARIABLE_USE = re.compile(r"(?<![^\${])[0-9A-Za-z_]+(?![^]}])")


def _append_line_occurence(tracker, name, line):
    """Append line to name entry in tracker."""
    if name not in tracker.keys():
        tracker[name] = []

    tracker[name].append(line)


def calls(abstract_syntax_tree, track_call):
    """Return a dict of calls mapped to where they occurred."""
    call_lines = {}

    def _call_handler(name, node, depth):
        """Viit all calls in this module."""
        assert name == "FunctionCall"

        del depth

        if track_call(node):
            _append_line_occurence(call_lines, node.name, node.line)

    ast_visitor.recurse(abstract_syntax_tree,
                        function_call=_call_handler)

    return call_lines


def definitions(abstract_syntax_tree, track_definition):
    """Return a dict of definitions mapped to where they occurred."""
    definition_lines = {}

    def _definition_handler(name, node, depth):
        """Visit all definitions."""
        assert name == "FunctionDefinition" or name == "MacroDefinition"
        assert len(node.header.arguments) > 0

        del depth

        if track_definition(node):
            _append_line_occurence(definition_lines,
                                   node.header.arguments[0].contents,
                                   node.line)

    ast_visitor.recurse(abstract_syntax_tree,
                        function_def=_definition_handler,
                        macro_def=_definition_handler)

    return definition_lines


def private_calls_and_definitions(abstract_syntax_tree):
    """Return a tuple of all private calls and definitions."""
    def _definition_is_private(node):
        """Check if a definition is private."""
        return node.header.arguments[0].contents.startswith("_")

    private_calls = calls(abstract_syntax_tree,
                          lambda x: x.name.startswith("_"))
    private_defs = definitions(abstract_syntax_tree,
                               _definition_is_private)

    return (private_calls, private_defs)


def _append_to_set_variables(name, node, set_variables):
    """Append to a dict of set variables."""
    if name not in set_variables.keys():
        set_variables[name] = []

    set_variables[name].append((node.line, node.col))


def toplevel_set_private_vars(abstract_syntax_tree):
    """Find all toplevel private variables.

    Returns a dict of variable names to places where such variables were set
    """
    set_variables = {}

    for statement in abstract_syntax_tree.statements:

        # We only want bare function calls, not definitions or the like
        if statement.__class__.__name__ != "FunctionCall":
            continue

        # Scan the statement for any variables set and append
        set_variable = find_set_variables.by_function_call(statement)

        if set_variable is not None:
            if (set_variable and
                    util.is_word_sink_variable(set_variable.type) and
                    set_variable.contents.startswith("_")):
                _append_to_set_variables(set_variable.contents,
                                         set_variable,
                                         set_variables)

    return set_variables


def variables_used_in_expr(word_node):
    """Return a set of variable names "used" by a node."""
    assert word_node.__class__.__name__ == "Word"

    used_variables_set = {}
    uses = _RE_VARIABLE_USE.findall(word_node.contents)

    for name in uses:
        if name not in used_variables_set.keys():
            used_variables_set[name] = []

        used_variables_set[name].append((word_node.line, word_node.col))

    return used_variables_set


def variables_used_matching(abstract_syntax_tree,
                            node_matcher,
                            name_matcher):
    """Return a set of variable names used whose nodes satisfy matchers."""
    variables_used = {}

    global_scope = find_variables_in_scopes.used_in_tree(abstract_syntax_tree)

    def _visit_scope(scope):
        """Visit a scope."""
        for subscope in scope.scopes:
            _visit_scope(subscope)

        for word, _ in scope.used_vars:

            if not node_matcher(word):
                continue

            variable_uses = _RE_VARIABLE_USE.findall(word.contents)

            for match in variable_uses:
                if not name_matcher(match):
                    continue

                _append_to_set_variables(match, word, variables_used)

    _visit_scope(global_scope)

    return variables_used
