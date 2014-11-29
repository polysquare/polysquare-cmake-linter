# /polysquarecmakelinter/check_correctness.py
#
# Linter checks for potentially buggy behaviour
#
# See LICENCE.md for Copyright information
"""Linter checks for potentially buggy behaviour"""

from cmakeast import ast_visitor
from cmakeast.ast import WordType
from collections import namedtuple
from polysquarecmakelinter import util
from polysquarecmakelinter.types import LinterFailure

import re

_RE_PATH_SLASH = re.compile(r"[\\/]")

_AlwaysQuote = namedtuple("_AlwaysQuoteT", "variable regex")


def _always_quote_if_at_end(variable):
    """Returns an _AlwaysQuote with regex matching variable at end"""
    regex = r"\${.*(?<=[_{])" + variable + "}"
    return _AlwaysQuote(variable, re.compile(regex))

ALWAYS_QUOTE_VARIABLES_CONTAINING = [
    _always_quote_if_at_end("PATH"),
    _always_quote_if_at_end("FILE"),
    _always_quote_if_at_end("SOURCE"),
    _always_quote_if_at_end("HEADER"),
    _always_quote_if_at_end("DIRECTORY"),
    _always_quote_if_at_end("EXECUTABLE"),
    _always_quote_if_at_end("DIR"),
]

_ALWAYS_QUOTE_MATCHERS_INT = (ALWAYS_QUOTE_VARIABLES_CONTAINING +
                              [_AlwaysQuote("CMAKE_COMMAND",
                                            re.compile(r"\${CMAKE_COMMAND}"))])


def path_variables_quoted(contents, abstract_syntax_tree):
    """Checks that each variable mutated is capitalized"""

    errors = []

    def _word_visitor(name, node, depth):
        """Visits all words"""
        assert name == "Word"

        del depth

        def _generate_error(node):
            """Generates an error and replacement for node in violation"""
            msg = "Path {0} must be quoted".format(node.contents)
            line_index = node.line - 1
            col_index = node.col - 1
            quoted = "\"{0}\""
            replacement = util.replace_word(contents[line_index],
                                            col_index,
                                            node.contents,
                                            quoted.format(node.contents))
            return LinterFailure(msg, node.line, replacement)

        if util.is_word_maybe_path(node.type):
            # CompoundLiterals definitely cannot have slashes
            if node.type == WordType.CompoundLiteral:
                if _RE_PATH_SLASH.search(node.contents):
                    errors.append(_generate_error(node))
                    return

            for always_quote_word in _ALWAYS_QUOTE_MATCHERS_INT:
                result = always_quote_word.regex.search(node.contents)
                if result is not None:
                    errors.append(_generate_error(node))
                    return

    ast_visitor.recurse(abstract_syntax_tree, word=_word_visitor)

    return errors
