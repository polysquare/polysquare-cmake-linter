# /polysquarecmakelinter/check_structure.py
#
# Linter checks for script structure
#
# See LICENCE.md for Copyright information
"""Linter checks for script structure."""

from cmakeast import ast_visitor

from polysquarecmakelinter import util

from polysquarecmakelinter.types import LinterFailure


def definitions_namespaced(contents, abstract_syntax_tree, **kwargs):
    """Check that function and macro definitions are namespaced."""
    errors = []

    try:
        namespace = kwargs["namespace"]
    except KeyError:
        return errors

    def _definition_handler(name, node, depth):
        """Visit all definitions."""
        assert name == "FunctionDefinition" or name == "MacroDefinition"
        assert len(node.header.arguments) > 0

        del depth

        definition = node.header.arguments[0]
        def_name = definition.contents

        if not def_name.startswith((namespace, "_" + namespace)):
            msg = "Definition {0} does not start with {1}".format(def_name,
                                                                  namespace)
            replacement_name = "{0}_{1}".format(namespace, def_name)
            if def_name.startswith("_"):
                replacement_name = "_{0}".format(replacement_name)

            replacement = util.replace_word(contents[node.line - 1],
                                            definition.col - 1,
                                            def_name,
                                            replacement_name)

            errors.append(LinterFailure(msg, node.line, replacement))

    ast_visitor.recurse(abstract_syntax_tree,
                        function_def=_definition_handler,
                        macro_def=_definition_handler)

    return errors
