"""Test module for `archey._version`"""

import unittest

from archey._version import __version__


class TestVersionUtil(unittest.TestCase):
    """Brain-dead test to verify the version string handling in Archey"""
    def test_load_version(self):
        """Test Archey's `__version__` internal attribute is correctly loadable"""
        self.assertTrue(__version__.startswith('v'))
