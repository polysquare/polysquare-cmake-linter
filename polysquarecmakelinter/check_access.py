# /polysquarecmakelinter/check_access.py
#
# Linter checks for access rights
#
# See /LICENCE.md for Copyright information
"""Linter checks for access rights."""

from polysquarecmakelinter import find_all
from polysquarecmakelinter import find_variables_in_scopes

from polysquarecmakelinter.types import LinterFailure


def only_use_own_privates(abstract_syntax_tree):
    """Check that all private definitions used are defined here."""
    calls, defs = find_all.private_calls_and_definitions(abstract_syntax_tree)

    errors = []

    for call, info in calls.items():
        if call not in defs.keys():
            for line in info:
                msg = "Used external private definition {0}".format(call)
                errors.append(LinterFailure(msg, line))

    return errors


def _find_violating_priv_uses(variable, current_scope):
    """Generate a list of uses of private variables not in this module."""
    for use in find_all.variables_used_in_expr(variable.node):
        if use.startswith("_"):
            # Used a private, check if it was set
            private_var_was_set = False

            traverse_scope = current_scope
            while traverse_scope is not None:
                for set_var in traverse_scope.set_vars:
                    if (set_var.node.contents == use and
                            (set_var.node.line,
                             set_var.node.col) != variable):
                        private_var_was_set = True
                        break

                traverse_scope = traverse_scope.parent

            if not private_var_was_set:
                yield (use, variable.node.line)


def only_use_own_priv_vars(ast):
    """Check that all private variables used are defined here."""
    used_privs = []

    global_set_vars = find_variables_in_scopes.set_in_tree(ast)
    global_used_vars = find_variables_in_scopes.used_in_tree(ast)

    _, global_definitions = find_all.private_calls_and_definitions(ast)

    # The big assumption here is that the "scopes" structure in both
    # trees are the same
    def _scope_visitor(set_vars_scope, used_vars_scope):
        """Visit scope's set vars and used vars.

        If a var was private and used, but not set in this scope or any
        parents, then report an error
        """
        assert len(set_vars_scope.scopes) == len(used_vars_scope.scopes)

        for index in range(0, len(set_vars_scope.scopes)):
            _scope_visitor(set_vars_scope.scopes[index],
                           used_vars_scope.scopes[index])

        for variable in used_vars_scope.used_vars:
            used_privs.extend(list(_find_violating_priv_uses(variable,
                                                             set_vars_scope)))

    _scope_visitor(global_set_vars, global_used_vars)

    # Filter out definitions of private functions of the same name
    # as functions can be used as variables.
    used_privs = [up for up in used_privs if up[0] not in global_definitions]

    err_msg = "Referenced external private variable {0}"
    return [LinterFailure(err_msg.format(u[0]), u[1]) for u in used_privs]
