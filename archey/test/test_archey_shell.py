"""Test module for Archey's shell detection module"""

import unittest
from unittest.mock import patch

from archey.entries.shell import Shell


class TestShellEntry(unittest.TestCase):
    """
    For this entry, we'll just verify that the output is non-null.
    """
    @patch(
        'archey.entries.shell.os.getenv',
        return_value='SHELL'
    )
    def test(self, _):
        """Simple mock, simple test"""
        self.assertEqual(Shell().value, 'SHELL')


if __name__ == '__main__':
    unittest.main()
