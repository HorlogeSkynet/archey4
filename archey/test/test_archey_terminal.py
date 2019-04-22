"""Test module for Archey's terminal detection module"""

import unittest
from unittest.mock import patch

from archey.entries.terminal import Terminal


class TestTerminalEntry(unittest.TestCase):
    """
    For this entry, we'll verify that the output contains what the environment
      is supposed to give, plus the right number of "colorized" characters.
    """
    @patch(
        'archey.entries.terminal.os.getenv',
        return_value='TERMINAL'
    )
    def test_without_unicode(self, _):
        """Test simple output, without Unicode support (default)"""
        output = Terminal().value
        self.assertTrue(output.startswith('TERMINAL '))
        self.assertEqual(output.count('#'), 7 * 2)

    @patch(
        'archey.entries.terminal.os.getenv',
        return_value='TERMINAL'
    )
    def test_with_unicode(self, _):
        """Test simple output, with Unicode support !"""
        output = Terminal(use_unicode=True).value
        self.assertTrue(output.startswith('TERMINAL '))
        self.assertEqual(output.count('\u2588'), 7 * 2)

    @patch(
        'archey.entries.terminal.os.getenv',
        return_value='Not detected'  # The "Not detected" string is set here, not from configuration
    )
    def test_not_detected(self, _):
        """Test simple output, with Unicode support !"""
        output = Terminal(not_detected='Not detected').value
        self.assertTrue(output.startswith('Not detected '))
        self.assertEqual(output.count('#'), 7 * 2)


if __name__ == '__main__':
    unittest.main()
