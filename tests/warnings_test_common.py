# /tests/warnings_test_common.py
#
# Some common functionality for all of the warnings tests
#
# See LICENCE.md for Copyright information
"""Some common functionality for all of the warnings tests"""

from polysquarecmakelinter import linter
from testtools.matchers import Equals as TTEqMatcher


# Pychecker complains about the Equals matcher failing to override comparator
# so do that here
class Equals(TTEqMatcher):
    """Matcher which tests equality"""

    def __init__(self, matchee):
        super(Equals, self).__init__(matchee)

    def comparator(self, expected, other):
        return other == expected


class LinterFailure(Exception):
    """Exception raised when the linter reports a message"""
    def __init__(self, message, repl):
        super(LinterFailure, self).__init__()
        self.message = message
        self.replacement = repl

    def __str__(self):
        return str("{0}".format(self.message))


def run_linter_throw(contents, whitelist=None, blacklist=None, **kwargs):
    """Runs linter.lint and throws if it reports a message"""

    errors = linter.lint(contents,
                         whitelist=whitelist,
                         blacklist=blacklist,
                         **kwargs)

    if len(errors):
        raise LinterFailure("{0} [{1}]".format(errors[0][1].line,
                                               errors[0][0]),
                            (errors[0][1].line, errors[0][1].replacement))

    return True


def replacement(exception):
    """Returns replacement for a LinterFailure, else asserts"""
    assert exception.__class__.__name__ == "LinterFailure"
    return exception.replacement


def gen_source_line(matcher, match_transform=None, other_transform=None):
    """Generates a source line for use with tests, no quotes used"""
    m_xform = match_transform if match_transform is not None else lambda x: x
    o_xform = other_transform if other_transform is not None else lambda x: x
    finder = matcher.find
    line = "{0} (".format(matcher.cmd)
    line += finder.generate(matcher.sub, o_xform, m_xform)
    line += ")\n"
    return line

DEFINITION_TYPES = [
    "function",
    "macro"
]
