# /polysquarecmakelinter/ignore.py
#
# Wrapper functions to ignore certain arguments in callbacks
#
# See LICENCE.md for Copyright information
"""Wrapper functions to ignore certain arguments in callbacks."""


def all_but_ast(check):
    """Only passes AST to check."""
    def _check_wrapper(contents, ast, **kwargs):
        """Wrap check and passes the AST to it."""
        del contents
        del kwargs

        return check(ast)

    return _check_wrapper


def check_kwargs(check):
    """Return wrapper for check function."""
    def _check_wrapper(contents, ast, **kwargs):
        """Do not pass kwargs to check."""
        del kwargs

        return check(contents, ast)

    return _check_wrapper


def visitor_depth(visitor):
    """Return wrapper for depth function."""
    def _visitor_wrapper(name, node, depth):
        """Do not pass depth to visitor."""
        del depth

        visitor(name, node)

    return _visitor_wrapper
