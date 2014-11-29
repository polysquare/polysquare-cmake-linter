# /polysquarecmakelinter/types.py
#
# Some types that are shared amongst linters and checks
#
# See LICENCE.md for Copyright information
"""Some types that are shared amongst linters and checks"""

from collections import namedtuple


# Subclass instead of assignment so that we have override __new__
# and provide a default value
class LinterFailure(namedtuple("LinterFailure",
                               "description line replacement")):
    """An immutable type representing a linter failure"""

    def __new__(cls, description, line, replacement=None):
        """Factory function"""
        return super(LinterFailure, cls).__new__(cls,
                                                 description,
                                                 line,
                                                 replacement)
