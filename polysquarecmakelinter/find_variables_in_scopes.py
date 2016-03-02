# /polysquarecmakelinter/find_variables_in_scopes.py
#
# Find all variables and order by scope. Scoping in CMake is a bit strange,
# by default, all variables will have function scope, or failing that, global
# scope. Any variable set by foreach as a loop variable has scope only within
# that loop. Macro arguments have scope within their respective macros and
# anything set inside of a foreach loop has scope inside of its
# enclosing function.
#
# These functions don't necessarily follow the same scoping structure that
# CMake uses internally - scoping in CMake is actually based on the
# runtime call tree, so if function A calls function B then whatever
# was visible in function A will also be visible in function B. However,
# setting that variable will cause it to be set in function B's scope.
#
# Instead, the model followed is "logical scope" - variables from function
# B called from function B are not visible in function B, except if function
# B was defined inside function A. The same rules apply for macros.
#
# In the author's opinion, checks that rely on CMake's own scoping behavior
# are really enforcing bad behavior - implicit variable visibility is bad
# for maintainability and shouldn't be relied on in any case.
#
# Global Scope:
# set (VARIABLE VALUE)
#
# macro (my_macro MACRO_ARG)
#     MACRO_ARG has my_macro scope
#     set (MY_MACRO_VAR VALUE) MY_MACRO_VAR has my_function scope because it
#     was called by my_function
# endmacro ()
#
# function (my_other_function)
#     set (PARENT_VAR VALUE PARENT_SCOPE) PARENT_VAR has my_function scope
# endfunction ()
#
# function (my_function ARGUMENT)
#     ARGUMENT has my_function scope
#     set (MY_FUNC_VAR VALUE) MY_FUNC_VAR has my_function scope
#     foreach (LOOP_VAR ${MY_FUNC_VAR})
#         LOOP_VAR has foreach scope
#         set (VAR_SET_IN_LOOP VALUE) VAR_SET_IN_LOOP has my_function scope
#     endforeach ()
#     my_other_function ()
#     my_macro ()
# endfunction ()
#
# See /LICENCE.md for Copyright information
"""Find all set variables and order by scope."""

import re

from collections import namedtuple

from polysquarecmakelinter import find_set_variables

Variable = namedtuple("Variable", "node source")
ScopeInfo = namedtuple("ScopeInfo", "name type")

_RE_VARIABLE_USE = re.compile(r"(?<![^\${])[0-9A-Za-z_]+(?![^]}])")

FOREACH_KEYWORDS = [
    "IN",
    "LISTS",
    "ITEMS"
]

IF_KEYWORDS = [
    "NOT",
    "STREQUAL",
    "STRLESS",
    "STRGREATER",
    "LESS",
    "EQUAL",
    "GREATER",
    "VERSION_LESS",
    "VERSION_EQUAL",
    "VERSION_GREATER",
    "EXISTS",
    "COMMAND",
    "POLICY",
    "TARGET",
    "IS_NEWER_THAN",
    "IS_DIRECTORY",
    "IS_ABSOLUTE",
    "MATCHES",
    "DEFINED",
    "AND",
    "OR",
    "OFF",
    "ON",
    "TRUE",
    "FALSE",
    "YES",
    "Y",
    "NO",
    "N",
    "IGNORE",
    "NOTFOUND"
]


# We use a class with constant variables here so that we can get int->int
# comparison. Comparing enums is slow because of the type lookup.
class VariableSource(object):  # suppress(too-few-public-methods)
    """The source of a variable in a scope."""

    ForeachVar = 0
    MacroArg = 1
    FunctionArg = 2
    FunctionVar = 3
    MacroVar = 4
    GlobalVar = 5


class ScopeType(object):  # suppress(too-few-public-methods)
    """The source of a variable in a scope."""

    Foreach = 0
    Macro = 1
    Function = 2
    Global = 3


class _Scope(object):  # suppress(too-few-public-methods)
    """A place where variables are hoisted."""

    def __init__(self, info, parent):
        """Initialize parent."""
        super(_Scope, self).__init__()

        self.parent = parent
        self.info = info
        self.scopes = []

    def add_subscope(self, name, node, parent, factory):
        """Add a new subscope."""
        assert node.__class__.__name__ != "ToplevelBody"

        node_scope_types = {
            "ForeachStatement": ScopeType.Foreach,
            "MacroDefinition": ScopeType.Macro,
            "FunctionDefinition": ScopeType.Function
        }

        assert node.__class__.__name__ in node_scope_types
        scope_type = node_scope_types[node.__class__.__name__]

        self.scopes.append(factory(ScopeInfo(name,
                                             scope_type),
                                   parent))


def traverse_scopes(abstract_syntax_tree,  # NOQA
                    body_function_call,
                    header_function_call,
                    factory):
    """Find all set variables in tree and orders into scopes."""
    global_scope = factory(ScopeInfo("toplevel", ScopeType.Global), None)

    def _header_body_visitor(enclosing_scope, header_scope, header, body):
        """Visit a header-body like node."""
        if header is not None:

            header_function_call(header, enclosing_scope, header_scope)

        for statement in body:
            _node_recurse(statement, enclosing_scope, header_scope)

    def _node_recurse(node, enclosing_scope, header_scope):
        """Visit any node, adjusts scopes."""
        def _handle_if_block(node):
            """Handle if blocks."""
            _header_body_visitor(enclosing_scope,
                                 header_scope,
                                 node.if_statement.header,
                                 node.if_statement.body)

            for elseif in node.elseif_statements:
                _header_body_visitor(enclosing_scope,
                                     header_scope,
                                     elseif.header,
                                     elseif.body)

            if node.else_statement:
                _header_body_visitor(enclosing_scope,
                                     header_scope,
                                     node.else_statement.header,
                                     node.else_statement.body)

        def _handle_foreach_statement(node):
            """Handle foreach statements."""
            header_scope.add_subscope("foreach", node, header_scope, factory)

            _header_body_visitor(enclosing_scope,
                                 header_scope.scopes[-1],
                                 node.header,
                                 node.body)

        def _handle_while_statement(node):
            """Handle while statements."""
            _header_body_visitor(enclosing_scope,
                                 header_scope,
                                 node.header,
                                 node.body)

        def _handle_function_declaration(node):
            """Handle function declarations."""
            header_scope.add_subscope(node.header.arguments[0].contents,
                                      node,
                                      header_scope,
                                      factory)

            _header_body_visitor(header_scope.scopes[-1],
                                 header_scope.scopes[-1],
                                 node.header,
                                 node.body)

        def _handle_macro_declaration(node):
            """Handle macro declarations."""
            header_scope.add_subscope(node.header.arguments[0].contents,
                                      node,
                                      header_scope,
                                      factory)

            _header_body_visitor(header_scope.scopes[-1],
                                 header_scope.scopes[-1],
                                 node.header,
                                 node.body)

        def _handle_function_call(node):
            """Handle function calls - does nothing, nothing to recurse."""
            body_function_call(node, enclosing_scope, header_scope)

        def _handle_toplevel_body(node):
            """Handle the special toplevel body node."""
            _header_body_visitor(enclosing_scope,
                                 header_scope,
                                 None,
                                 node.statements)

        node_dispatch = {
            "IfBlock": _handle_if_block,
            "ForeachStatement": _handle_foreach_statement,
            "WhileStatement": _handle_while_statement,
            "FunctionDefinition": _handle_function_declaration,
            "MacroDefinition": _handle_macro_declaration,
            "ToplevelBody": _handle_toplevel_body,
            "FunctionCall": _handle_function_call
        }

        node_dispatch[node.__class__.__name__](node)

    _node_recurse(abstract_syntax_tree, global_scope, global_scope)

    return global_scope


def _scope_to_bind_var_to(function_call, enclosing):
    """Find a scope to bind variables set by function_call."""
    if function_call.name == "set":
        try:
            if function_call.arguments[2].contents == "PARENT_SCOPE":
                assert enclosing.parent is not None
                enclosing = enclosing.parent
            elif function_call.arguments[2].contents == "CACHE":
                while enclosing.parent is not None:
                    enclosing = enclosing.parent
        except IndexError:  # suppress(pointless-except)
            pass

    # Another special case for set_property with GLOBAL as the
    # first argument. Create a notional "variable"
    elif function_call.name == "set_property":
        assert len(function_call.arguments[0]) >= 3
        if function_call.arguments[0].contents == "GLOBAL":
            while enclosing.parent is not None:
                enclosing = enclosing.parent

    return enclosing


def set_in_tree(abstract_syntax_tree):
    """Find variables set by scopes."""
    def scope_factory(info, parent):
        """Construct a "set variables" scope."""
        class SetVariablesScope(_Scope):  # suppress(too-few-public-methods)
            """Set variables in this scope."""

            def __init__(self, info, parent):
                """Initialize set_vars member."""
                super(SetVariablesScope, self).__init__(info, parent)
                self.set_vars = []

        return SetVariablesScope(info, parent)

    def body_function_call(node, enclosing, body_header):
        """Handle function calls in a body and provides scope."""
        del body_header

        var_types = {
            ScopeType.Macro: VariableSource.MacroVar,
            ScopeType.Function: VariableSource.FunctionVar,
            ScopeType.Global: VariableSource.GlobalVar
        }

        set_var = find_set_variables.by_function_call(node)
        if set_var:

            # Special case for "set" and PARENT_SCOPE/CACHE scope
            enclosing = _scope_to_bind_var_to(node, enclosing)

            info = enclosing.info
            enclosing.set_vars.append(Variable(set_var,
                                               var_types[info.type]))

    def header_function_call(node, header_enclosing, header):
        """Handle the "header" function call and provides scope."""
        del header_enclosing

        def _get_header_vars(header):
            """Add variables implicitly set by header function call."""
            header_variables = {
                "foreach": lambda h: [h.arguments[0]],
                "function": lambda h: h.arguments[1:],
                "macro": lambda h: h.arguments[1:]
            }

            try:
                return header_variables[header.name](header)
            except KeyError:
                return []

        var_types = {
            ScopeType.Foreach: VariableSource.ForeachVar,
            ScopeType.Function: VariableSource.FunctionArg,
            ScopeType.Macro: VariableSource.MacroArg
        }

        nodes = _get_header_vars(node)
        info = header.info
        header.set_vars += [Variable(v, var_types[info.type]) for v in nodes]

    return traverse_scopes(abstract_syntax_tree,
                           body_function_call,
                           header_function_call,
                           scope_factory)


def used_in_tree(abstract_syntax_tree):
    """Find variables used in scopes."""
    def scope_factory(info, parent):
        """Construct a "set variables" scope."""
        class UsedVariablesScope(_Scope):  # suppress(too-few-public-methods)
            """Used variables in this scope."""

            def __init__(self, info, parent):
                """Initialize used_vars member."""
                super(UsedVariablesScope, self).__init__(info, parent)
                self.used_vars = []

        return UsedVariablesScope(info, parent)

    def body_function_call(node, body_enclosing, header):
        """Handle function calls in a node body."""
        del body_enclosing

        var_types = {
            ScopeType.Foreach: VariableSource.ForeachVar,
            ScopeType.Function: VariableSource.FunctionVar,
            ScopeType.Macro: VariableSource.MacroVar,
            ScopeType.Global: VariableSource.GlobalVar
        }

        info = header.info
        header.used_vars.extend([Variable(a,
                                          var_types[info.type])
                                 for a in node.arguments
                                 if _RE_VARIABLE_USE.search(a.contents)])

    def header_function_call(node, header_enclosing, current_header):
        """Handle function calls in a node header."""
        del header_enclosing

        var_types = {
            ScopeType.Foreach: lambda p: var_types[p.info.type](p.parent),
            ScopeType.Function: lambda _: VariableSource.FunctionVar,
            ScopeType.Macro: lambda _: VariableSource.MacroVar,
            ScopeType.Global: lambda _: VariableSource.GlobalVar
        }

        starts_new_header = ["foreach", "function", "macro"]
        if node.name in starts_new_header:
            header = current_header.parent
        else:
            header = current_header

        sct = header.info.type

        kw_exclude = {
            "if":  IF_KEYWORDS,
            "elseif": IF_KEYWORDS,
            "while": IF_KEYWORDS,
            "foreach": FOREACH_KEYWORDS,
            "function": [],
            "macro": [],
            "else": []
        }

        header_pos_exclude = {
            "if": lambda _: False,
            "elseif": lambda _: False,
            "while": lambda _: False,
            "foreach": lambda n: n == 0,
            "function": lambda _: True,
            "macro": lambda _: True,
            "else": lambda _: True
        }

        for index, argument in enumerate(node.arguments):
            is_var_use = _RE_VARIABLE_USE.search(argument.contents) is not None
            not_kw_excluded = argument.contents not in kw_exclude[node.name]
            not_pos_excluded = not header_pos_exclude[node.name](index)

            if is_var_use and not_kw_excluded and not_pos_excluded:
                variable_type = var_types[sct](header.parent)
                header.used_vars.append(Variable(argument, variable_type))

    return traverse_scopes(abstract_syntax_tree,
                           body_function_call,
                           header_function_call,
                           scope_factory)
