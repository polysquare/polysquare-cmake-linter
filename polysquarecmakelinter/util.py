# /polysquarecmakelinter/util.py
#
# Utility functions shared amongst checks
#
# See LICENCE.md for Copyright information
"""Utility functions shared amongst checks."""

from cmakeast.ast import WordType


def replace_word(line, start, word, replacement):
    """Helper function to replace a word starting at start with replacement."""
    return line[:start] + replacement + line[start + len(word):]


def is_word_sink_variable(word_type):
    """Return true if this word can be used to set a value."""
    return word_type in [WordType.Variable, WordType.String]


def is_word_maybe_path(word_type):
    """Return true if this word might be an unquoted path."""
    return word_type in [WordType.VariableDereference,
                         WordType.CompoundLiteral]
