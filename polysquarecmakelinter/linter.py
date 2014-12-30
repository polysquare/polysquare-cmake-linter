# /polysquarecmakelinter/linter.py
#
# Entry point for linter.
#
# See LICENCE.md for Copyright information
""" Main module for linter."""

import argparse

import os

import re

import sys

from cmakeast import ast

from polysquarecmakelinter import check_access as access
from polysquarecmakelinter import check_correctness as correct
from polysquarecmakelinter import check_structure as structure
from polysquarecmakelinter import check_style as style
from polysquarecmakelinter import check_unused as unused
from polysquarecmakelinter import ignore

_RE_NOLINT = re.compile(r"^.*#\s+NOLINT:")


def should_ignore(line, warning):
    """Specify whether or not to ignore warnings on this line."""
    match = _RE_NOLINT.search(line)
    if match:
        try:
            # Special case, "*" means "all errors"
            if line[match.end():][0] == "*":
                return True
            elif line[match.end():match.end() + len(warning)] == warning:
                return True
        except IndexError:  # pylint:disable=W0704
            pass

    return False


LINTER_FUNCTIONS = {
    "structure/namespace": structure.definitions_namespaced,
    "style/space_before_func": ignore.check_kwargs(style.space_before_call),
    "style/set_var_case": ignore.check_kwargs(style.set_variables_capitalized),
    "style/uppercase_args": ignore.check_kwargs(style.uppercase_arguments),
    "style/lowercase_func": ignore.check_kwargs(style.lowercase_functions),
    "style/argument_align": ignore.check_kwargs(style.func_args_aligned),
    "style/doublequotes": ignore.check_kwargs(style.double_outer_quotes),
    "style/indent": style.calls_indented_correctly,
    "correctness/quotes": ignore.check_kwargs(correct.path_variables_quoted),
    "unused/private": ignore.all_but_ast(unused.private_definitions_used),
    "unused/var_in_func": ignore.all_but_ast(unused.vars_in_func_used),
    "unused/private_var": ignore.all_but_ast(unused.private_vars_at_toplevel),
    "access/other_private": ignore.all_but_ast(access.only_use_own_privates),
    "access/private_var": ignore.all_but_ast(access.only_use_own_priv_vars)
}


def lint(contents,
         whitelist=None,
         blacklist=None,
         **kwargs):
    r"""Actually lints some file contents.

    Contents should be a raw string with \n. whitelist is a list of checks
    to only perform, blacklist is list of checks to never perform.
    """
    abstract_syntax_tree = ast.parse(contents)
    contents_lines = contents.splitlines(True)
    linter_functions = LINTER_FUNCTIONS

    def _keyvalue_pair_if(dictionary, condition):
        """Return a key-value pair in dictionary if condition matched."""
        return {
            k: v for (k, v) in dictionary.items() if condition(k)
        }

    def _check_list(check_list, cond):
        """Return filter function for cond."""
        def _check_against_list(key):
            """Return true if list exists and condition passes."""
            return cond(check_list, key) if check_list is not None else True

        return _check_against_list

    linter_functions = _keyvalue_pair_if(linter_functions,
                                         _check_list(whitelist,
                                                     lambda l, k: k in l))
    linter_functions = _keyvalue_pair_if(linter_functions,
                                         _check_list(blacklist,
                                                     lambda l, k: k not in l))

    linter_errors = []
    for (code, function) in linter_functions.items():
        errors = function(contents_lines,
                          abstract_syntax_tree,
                          **kwargs)
        for error in errors:
            linter_errors.append((code, error))

    return linter_errors


class ShowAvailableChecksAction(argparse.Action):

    """If --checks is encountered, just show available checks and exit."""

    def __call__(self, parser, namespace, values, option_string=None):
        """"Execute action."""
        del namespace
        del parser
        del values

        if option_string == "--checks":
            sys.stdout.write("Available option are:\n")
            for item in LINTER_FUNCTIONS.keys():
                sys.stdout.write(" * {0}\n".format(item))

            sys.exit(0)


def _parse_arguments(arguments=None):
    """Return a parser context result."""
    parser = argparse.ArgumentParser(description="Lint for Polysquare "
                                     "style guide")
    parser.add_argument("--checks",
                        nargs=0,
                        action=ShowAvailableChecksAction,
                        help="list available checks")
    parser.add_argument("files",
                        nargs="*",
                        metavar=("FILE"),
                        help="read FILE",
                        type=argparse.FileType("r+"))
    parser.add_argument("--whitelist",
                        nargs="*",
                        help="list of checks that should only be run",
                        default=None)
    parser.add_argument("--blacklist",
                        nargs="*",
                        help="list of checks that should never be run",
                        default=None)
    parser.add_argument("--indent",
                        nargs=1,
                        type=int,
                        help="Indent level",
                        default=None)
    parser.add_argument("--namespace",
                        nargs=1,
                        type=str,
                        help="Namespace for functions",
                        default=None)
    parser.add_argument("--fix-what-you-can",
                        action="store_const",
                        const=True)

    return parser.parse_args(arguments)


def _report_lint_error(error, file_path):
    """Report a linter error."""
    line = error[1].line
    code = error[0]
    description = error[1].description
    sys.stderr.write("{0}:{1} [{2}] {3}".format(file_path,
                                                line,
                                                code,
                                                description))


def _apply_replacement(error, found_file, file_lines):
    """Apply a single replacement."""
    fixed_lines = file_lines
    fixed_lines[error[1].line - 1] = error[1].replacement
    concatenated_fixed_lines = "".join(fixed_lines)

    # Only fix one error at a time
    found_file.seek(0)
    found_file.write(concatenated_fixed_lines)
    found_file.truncate()


def main(arguments=None):
    """Entry point for the linter."""
    result = _parse_arguments(arguments)

    num_errors = 0
    for found_file in result.files:
        file_path = os.path.abspath(found_file.name)
        file_contents = found_file.read()
        file_lines = file_contents.splitlines(True)
        try:
            kwargs = {}
            if result.namespace is not None:
                kwargs["namespace"] = result.namespace[0]

            if result.indent is not None:
                kwargs["indent"] = result.indent[0]

            errors = lint(file_contents,  # pylint:disable=star-args
                          result.whitelist,
                          result.blacklist,
                          **kwargs)
        except RuntimeError as err:
            msg = "RuntimeError in processing {0} - {1}".format(file_path,
                                                                str(err))
            raise RuntimeError(msg)

        for error in errors:
            if not should_ignore(file_lines[error[1].line - 1], error[0]):
                _report_lint_error(error, file_path)
                if (result.fix_what_you_can and
                        error[1].replacement is not None):
                    _apply_replacement(error, found_file, file_lines)
                    sys.stderr.write(" ... FIXED\n")
                    break

                sys.stderr.write("\n")

                num_errors += 1

    return num_errors


if __name__ == "__main__":
    main()
