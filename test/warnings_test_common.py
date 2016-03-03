# /test/warnings_test_common.py
#
# Some common functionality for all of the warnings tests
#
# See /LICENCE.md for Copyright information
"""Some common functionality for all of the warnings tests."""

from polysquarecmakelinter import find_set_variables
from polysquarecmakelinter import linter

from testtools.matchers import Equals as TTEqMatcher


def _arg_no_mixin(num):
    """Return FindArgNoMixin for num."""
    class FindArgNoMixin(object):  # suppress(too-few-public-methods)
        """Mixin that provides generate() for finding args by number."""

        def generate(self,  # suppress(no-self-use)
                     sub,
                     other_transform,
                     match_transform):
            """Generate argument list of num size."""
            # A cheap hack to ensure that we generate a few extra in the
            # list GET case
            gen_num = abs(num - 1 if sub is not None else num)
            args_before = (" ".join([other_transform("ARGUMENT")] *
                                    gen_num))
            match_arg = match_transform("VALUE")
            subcommand = sub + " " if sub is not None else ""
            return subcommand + " ".join([args_before, match_arg])

    return FindArgNoMixin


def _after_arg_mixin(argument):
    """Return FindAfterArgMixin for argument."""
    class FindAfterArgMixin(object):  # suppress(too-few-public-methods)
        """Mixin that provides generate() for finding args after args."""

        def generate(self,  # suppress(no-self-use)
                     sub,
                     other_transform,
                     match_transform):
            """Generate argument list of ARGUMENT__ {argument} VALUE."""
            args_before = other_transform("ARGUMENT__ {0}".format(argument))
            match_arg = match_transform("VALUE")
            subcommand = sub + " " if sub is not None else ""
            return subcommand + " ".join([args_before, match_arg])

    return FindAfterArgMixin

FUNCTIONS_SETTING_VARS = find_set_variables.all_functions(_arg_no_mixin,
                                                          _after_arg_mixin)


# Pychecker complains about the Equals matcher failing to override comparator
# so do that here
class Equals(TTEqMatcher):  # suppress(R0903)
    """Matcher which tests equality."""

    def __init__(self, matchee):
        """Forward matchee to parent class."""
        super(Equals, self).__init__(matchee)

    def comparator(self, expected, other):
        """Check that expected == other."""
        return other == expected


class LinterFailure(Exception):
    """Exception raised when the linter reports a message."""

    def __init__(self, message, repl):
        """Initialize exception with message and replacement."""
        super(LinterFailure, self).__init__()
        self.message = message
        self.replacement = repl

    def __str__(self):
        """Return exception as string."""
        return str("{0}".format(self.message))


def run_linter_throw(contents, whitelist=None, blacklist=None, **kwargs):
    """Run linter.lint and throws if it reports a message."""
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
    """Return replacement for a LinterFailure, else asserts."""
    assert exception.__class__.__name__ == "LinterFailure"
    return exception.replacement


def gen_source_line(matcher, match_transform=None, other_transform=None):
    """Generate a source line for use with tests, no quotes used."""
    m_xform = match_transform if match_transform is not None else lambda x: x
    o_xform = other_transform if other_transform is not None else lambda x: x
    finder = matcher.find
    line = "{0} (".format(matcher.cmd)
    line += finder.generate(matcher.sub, o_xform, m_xform)
    line += ")\n"
    return line


def format_with_command(var_xform=None,
                        other_xform=None):
    """Return function formatting docstring with 'set variable' tuple.

    Specify var_xform to transform the name of the variable
    which is set by the command.
    """
    def formatter(func, _, params):
        """Return formatted docstring with command setting variable."""
        source_line = gen_source_line(params.args[0],
                                      match_transform=var_xform,
                                      other_transform=other_xform)
        return func.__doc__.format(source_line)

    return formatter


def format_with_args(*args):
    """Return a function that formats a docstring."""
    def formatter(func, _, params):
        """Return formatted docstring with argument numbers in args."""
        pa = params.args
        format_args = [pa[i] for i in range(0, len(pa)) if i in args]

        return func.__doc__.format(*format_args)

    return formatter

DEFINITION_TYPES = [
    "function",
    "macro"
]
