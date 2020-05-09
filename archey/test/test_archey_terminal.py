"""Test module for Archey's terminal detection module"""

import unittest
from unittest.mock import patch

from archey.entries.terminal import Terminal


class TestTerminalEntry(unittest.TestCase):
    """
    For this entry, we'll verify that the output contains what the environment
      is supposed to give, plus the right number of "colorized" characters.
    """
    @patch.dict(
        'archey.entries.terminal.os.environ',
        {'TERM_PROGRAM': 'A-COOL-TERMINAL-EMULATOR'},
        clear=True
    )
    @patch(
        'archey.configuration.Configuration.get',
        return_value={'use_unicode': False}
    )
    def test_term_program_without_unicode(self, _):
        """Test simple output, without Unicode support (default)"""
        output = Terminal().value
        self.assertTrue(output.startswith('A-COOL-TERMINAL-EMULATOR'))
        self.assertEqual(output.count('#'), 7 * 2)

    @patch.dict(
        'archey.entries.terminal.os.environ',
        {'TERM': 'xterm-256color'},
        clear=True
    )
    @patch(
        'archey.configuration.Configuration.get',
        return_value={'use_unicode': True}
    )
    def test_term_fallback_with_unicode(self, _):
        """Test simple output, with Unicode support !"""
        output = Terminal().value
        self.assertTrue(output.startswith('xterm-256color'))
        self.assertEqual(output.count('\u2588'), 7 * 2)

    @patch.dict(
        'archey.entries.terminal.os.environ',
        {'KONSOLE_VERSION': 'vX.Y.Z'},
        clear=True
    )
    @patch(
        'archey.configuration.Configuration.get',
        return_value={'use_unicode': False}
    )
    def test_terminal_name_normalization(self, _):
        """Test our manual name normalization for emulators not propagating `TERM_PROGRAM`"""
        self.assertTrue(Terminal().value.startswith('Konsole'))

    @patch.dict(
        'archey.entries.terminal.os.environ',
        {},
        clear=True
    )
    @patch(
        'archey.configuration.Configuration.get',
        side_effect=[
            {'not_detected': 'Not detected'},
            {'use_unicode': False},
        ]
    )
    def test_not_detected(self, _):
        """Test simple output, without Unicode support"""
        output = Terminal().value
        self.assertTrue(output.startswith('Not detected'))


if __name__ == '__main__':
    unittest.main()
