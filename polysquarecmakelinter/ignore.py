# /polysquarecmakelinter/ignore.py
#
# Wrapper functions to ignore certain arguments in callbacks
#
# See LICENCE.md for Copyright information
"""Wrapper functions to ignore certain arguments in callbacks"""


def all_but_ast(check):
    """Only passes AST to check"""

    def _check_wrapper(contents, ast, **kwargs):
        """Wraps check and passes the AST to it"""

        del contents
        del kwargs

        return check(ast)

    return _check_wrapper


def check_kwargs(check):
    """Does not pass kwargs to check"""

    def _check_wrapper(contents, ast, **kwargs):
        """Does not pass kwargs to check"""

        del kwargs

        return check(contents, ast)

    return _check_wrapper


def visitor_depth(visitor):
    """Does not pass depth to visitor"""

    def _visitor_wrapper(name, node, depth):
        """Does not pass depth to visitor"""

        del depth

        visitor(name, node)

    return _visitor_wrapper
