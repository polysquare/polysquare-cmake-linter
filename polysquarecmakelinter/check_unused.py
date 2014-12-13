# /polysquarecmakelinter/check_unused.py
#
# Linter checks for unused definitions
#
# See LICENCE.md for Copyright information
"""Linter checks for Linter checks for unused definitions"""

import re

from cmakeast.ast import WordType
from polysquarecmakelinter.types import LinterFailure
from polysquarecmakelinter import (find_variables_in_scopes,
                                   find_all)

_RE_VARIABLE_USE = re.compile(r"(?<![^\${])[0-9A-Za-z_]+(?![^]}])")


def vars_in_func_used(abstract_syntax_tree):
    """Checks that variables defined in a function are used later"""

    errors = []

    set_scopes = find_variables_in_scopes.set_in_tree(abstract_syntax_tree)
    used_scopes = find_variables_in_scopes.used_in_tree(abstract_syntax_tree)

    # Iterate through the set and used variables - making sure that any set
    # variables are used somewhere down the scope chain
    def _scope_visitor(set_scope, used_scope):
        """Visits both scopes at the same level"""

        assert len(set_scope.scopes) == len(used_scope.scopes)

        def _used_scope_finder(used_scope, node):
            """Searches for uses of variable_node"""

            def _is_candidate_use(use, node):
                """Checks if use_node is not node, but also a candidate"""
                if use.node == node:
                    return False

                used_vars_in_node = _RE_VARIABLE_USE.findall(use.node.contents)
                for used_var in used_vars_in_node:
                    if used_var == node.contents:
                        return True

            used_vs = used_scope.used_vars
            matched_uses = [u for u in used_vs if _is_candidate_use(u, node)]

            # Found use, done
            if len(matched_uses):
                return True

            # Didn't find use - keep going down if possible:
            for subscope in used_scope.scopes:
                if _used_scope_finder(subscope, node):
                    return True

            return False

        # Ignore the global scope
        if id(set_scopes) != id(set_scope):
            for var in set_scope.set_vars:

                if var.node.type != WordType.Variable:
                    return

                if not _used_scope_finder(used_scope, var.node):
                    msg = "Unused local variable {0}".format(var.node.contents)
                    errors.append(LinterFailure(msg, var.node.line))

        for index in range(0, len(set_scope.scopes)):
            _scope_visitor(set_scope.scopes[index],
                           used_scope.scopes[index])

    _scope_visitor(set_scopes, used_scopes)

    return errors


def private_vars_at_toplevel(abstract_syntax_tree):
    """Checks that private variables defined at the top level are used later"""

    errors = []

    variables_set = find_all.toplevel_set_private_vars(abstract_syntax_tree)

    def _not_in_variables_set(node):
        """Returns false if in variables_set"""

        try:
            return not (node.line, node.col) in variables_set[node.contents]
        except KeyError:
            return True

    def _starts_with_underscore(name):
        """Returns true if variable name starts with _"""

        return name.startswith("_")

    variables_used = find_all.variables_used_matching(abstract_syntax_tree,
                                                      _not_in_variables_set,
                                                      _starts_with_underscore)

    # Check the intersection
    for var in variables_set.keys():
        if var not in variables_used.keys():
            msg = "Unused set variable at toplevel {0}".format(var)
            errors.append(LinterFailure(msg, variables_set[var][0][0]))

    return errors


def private_definitions_used(abstract_syntax_tree):
    """Checks that all private definitions are used by this module"""

    calls, defs = find_all.private_calls_and_definitions(abstract_syntax_tree)

    errors = []

    for definition, info in defs.items():
        if definition not in calls.keys():
            for line in info:
                msg = "Unused private definition {0}".format(definition)
                errors.append(LinterFailure(msg, line))

    return errors
