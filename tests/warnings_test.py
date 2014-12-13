# /tests/warnings_test.py
#
# Test cases for each warning in polysquare-cmake-linter
#
# See LICENCE.md for Copyright information
"""Test the linter to ensure that each lint use-case triggers warnings"""

from polysquarecmakelinter import linter
from testtools import TestCase


class TestIgnoreLines(TestCase):
    """Test case for line-ignore logic"""
    def test_ignore_nolint_wildcard(self):
        """Ignore all lines with a wildcard NOLINT"""
        self.assertTrue(linter.should_ignore(" # NOLINT:*\n", "some/warning"))

    def test_no_ignore_unmatched_nolint(self):
        """Don't ignore lines that don't match the NOLINT """
        self.assertFalse(linter.should_ignore(" # NOLINT:o/warning\n",
                                              "some/warning"))

    def test_no_ignore_malformed(self):
        """Don't ignore lines where NOLINT is malformed """
        self.assertFalse(linter.should_ignore(" # NOLINT:\n",
                                              "some/warning"))

    def test_ignore_nolint_matching(self):
        """Ignore lines that match the NOLINT """
        self.assertTrue(linter.should_ignore(" # NOLINT:some/warning\n",
                                             "some/warning"))
