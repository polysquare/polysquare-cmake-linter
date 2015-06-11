# /test/autoderef_list.py
#
# Utility helpers to generate situations where variables might be automatically
# dereferenced.
#
# See /LICENCE.md for Copyright information
"""Generate situations where variables are automatically dereferenced."""

from collections import namedtuple

_AutoderefVariable = namedtuple("_AutoderefVariable", "cmd find")

KNOWN_KEYWORDS = {
    "if": [
        "NOT"
        "AND"
        "OR"
        "STREQUAL"
        "STRLESS"
        "STRGREATER"
        "LESS"
        "GREATER"
        "EQUAL"
        "POLICY"
        "TARGET"
        "EXISTS"
        "IS_NEWER_THAN"
        "DEFINED"
        "VERSION_LESS",
        "VERSION_EQUAL",
        "VERSION_GREATER",
        "ON",
        "OFF",
        "TRUE",
        "FALSE"
    ],
    "foreach": [
        "RANGE",
        "IN"
        "LISTS",
        "ITEMS"
    ]
}

KNOWN_KEYWORDS["while"] = KNOWN_KEYWORDS["if"]
KNOWN_KEYWORDS["elseif"] = KNOWN_KEYWORDS["if"]


def _first_arg():
    """Return a finder for first argument."""
    def generate(transform):
        """Generate one arg."""
        return transform("ARGUMENT")

    return generate


def _last_arg():
    """Return a finder for last argument."""
    def generate(transform):
        """Generate two args, last one being ARGUMENT."""
        return "ONE {0}".format(transform("ARGUMENT"))

    return generate


def _after_arg(arg_name):
    """Return a finder for argument after arg_name."""
    def generate(transform):
        """Generate three args, OTHER, arg_name and ARGUMENT."""
        return "ONE {0} {1}".format(arg_name, transform("ARGUMENT"))

    return generate


def _before_arg(arg_name):
    """Return a finder for argument before arg_name."""
    def generate(transform):
        """Generate three args, ARGUMENT, arg_name and OTHER."""
        return "ONE {0} {1}".format(transform("ARGUMENT"), arg_name)

    return generate


def _handle_autoderef(cmd, generator):
    """Wrap a finder to handle argument ignoring."""
    return (cmd, generator)

# This constant is used in the unused warnings test.
#
# suppress(unused-variable)
VARIABLES = [
    _handle_autoderef("if", _first_arg()),
    _handle_autoderef("if", _after_arg("NOT")),
    _handle_autoderef("if", _before_arg("AND")),
    _handle_autoderef("if", _after_arg("AND")),
    _handle_autoderef("if", _before_arg("OR")),
    _handle_autoderef("if", _after_arg("OR")),
    _handle_autoderef("if", _before_arg("OR")),
    _handle_autoderef("if", _after_arg("OR")),
    _handle_autoderef("if", _before_arg("STREQUAL")),
    _handle_autoderef("if", _after_arg("STREQUAL")),
    _handle_autoderef("if", _before_arg("STRLESS")),
    _handle_autoderef("if", _after_arg("STRLESS")),
    _handle_autoderef("if", _before_arg("STRGREATER")),
    _handle_autoderef("if", _after_arg("STRGREATER")),
    _handle_autoderef("if", _before_arg("LESS")),
    _handle_autoderef("if", _after_arg("LESS")),
    _handle_autoderef("if", _before_arg("GREATER")),
    _handle_autoderef("if", _after_arg("GREATER")),
    _handle_autoderef("if", _before_arg("EQUAL")),
    _handle_autoderef("if", _after_arg("EQUAL")),
    _handle_autoderef("if", _before_arg("VERSION_LESS")),
    _handle_autoderef("if", _after_arg("VERSION_LESS")),
    _handle_autoderef("if", _before_arg("VERSION_GREATER")),
    _handle_autoderef("if", _after_arg("VERSION_GREATER")),
    _handle_autoderef("if", _before_arg("VERSION_EQUAL")),
    _handle_autoderef("if", _after_arg("VERSION_EQUAL")),
    _handle_autoderef("if", _before_arg("MATCHES")),
    _handle_autoderef("if", _after_arg("DEFINED")),
    _handle_autoderef("while", _first_arg()),
    _handle_autoderef("while", _after_arg("NOT")),
    _handle_autoderef("while", _before_arg("AND")),
    _handle_autoderef("while", _after_arg("AND")),
    _handle_autoderef("while", _before_arg("OR")),
    _handle_autoderef("while", _after_arg("OR")),
    _handle_autoderef("while", _before_arg("OR")),
    _handle_autoderef("while", _after_arg("OR")),
    _handle_autoderef("while", _before_arg("STREQUAL")),
    _handle_autoderef("while", _after_arg("STREQUAL")),
    _handle_autoderef("while", _before_arg("STRLESS")),
    _handle_autoderef("while", _after_arg("STRLESS")),
    _handle_autoderef("while", _before_arg("STRGREATER")),
    _handle_autoderef("while", _after_arg("STRGREATER")),
    _handle_autoderef("while", _before_arg("LESS")),
    _handle_autoderef("while", _after_arg("LESS")),
    _handle_autoderef("while", _before_arg("GREATER")),
    _handle_autoderef("while", _after_arg("GREATER")),
    _handle_autoderef("while", _before_arg("EQUAL")),
    _handle_autoderef("while", _after_arg("EQUAL")),
    _handle_autoderef("while", _before_arg("VERSION_LESS")),
    _handle_autoderef("while", _after_arg("VERSION_LESS")),
    _handle_autoderef("while", _before_arg("VERSION_GREATER")),
    _handle_autoderef("while", _after_arg("VERSION_GREATER")),
    _handle_autoderef("while", _before_arg("VERSION_EQUAL")),
    _handle_autoderef("while", _after_arg("VERSION_EQUAL")),
    _handle_autoderef("while", _before_arg("MATCHES")),
    _handle_autoderef("while", _after_arg("DEFINED")),
    _handle_autoderef("elseif", _first_arg()),
    _handle_autoderef("elseif", _after_arg("NOT")),
    _handle_autoderef("elseif", _before_arg("AND")),
    _handle_autoderef("elseif", _after_arg("AND")),
    _handle_autoderef("elseif", _before_arg("OR")),
    _handle_autoderef("elseif", _after_arg("OR")),
    _handle_autoderef("elseif", _before_arg("OR")),
    _handle_autoderef("elseif", _after_arg("OR")),
    _handle_autoderef("elseif", _before_arg("STREQUAL")),
    _handle_autoderef("elseif", _after_arg("STREQUAL")),
    _handle_autoderef("elseif", _before_arg("STRLESS")),
    _handle_autoderef("elseif", _after_arg("STRLESS")),
    _handle_autoderef("elseif", _before_arg("STRGREATER")),
    _handle_autoderef("elseif", _after_arg("STRGREATER")),
    _handle_autoderef("elseif", _before_arg("LESS")),
    _handle_autoderef("elseif", _after_arg("LESS")),
    _handle_autoderef("elseif", _before_arg("GREATER")),
    _handle_autoderef("elseif", _after_arg("GREATER")),
    _handle_autoderef("elseif", _before_arg("EQUAL")),
    _handle_autoderef("elseif", _after_arg("EQUAL")),
    _handle_autoderef("elseif", _before_arg("VERSION_LESS")),
    _handle_autoderef("elseif", _after_arg("VERSION_LESS")),
    _handle_autoderef("elseif", _before_arg("VERSION_GREATER")),
    _handle_autoderef("elseif", _after_arg("VERSION_GREATER")),
    _handle_autoderef("elseif", _before_arg("VERSION_EQUAL")),
    _handle_autoderef("elseif", _after_arg("VERSION_EQUAL")),
    _handle_autoderef("elseif", _before_arg("MATCHES")),
    _handle_autoderef("elseif", _after_arg("DEFINED")),
    _handle_autoderef("foreach", _last_arg()),
    _handle_autoderef("list", _after_arg("LENGTH")),
    _handle_autoderef("list", _after_arg("GET")),
    _handle_autoderef("list", _after_arg("FIND"))
]
