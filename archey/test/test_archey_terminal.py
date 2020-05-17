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
        {
            'TERM': 'xterm-256color',
            'COLORTERM': 'truecolor',
            'TERM_PROGRAM': 'A-COOL-TERMINAL-EMULATOR'
        },
        clear=True
    )
    @patch(
        'archey.configuration.Configuration.get',
        return_value={'use_unicode': False}
    )
    def test_terminal_emulator_term_program(self, _):
        """Check that `TERM_PROGRAM` is honored even if `TERM` or `COLORTERM` is defined"""
        output = Terminal().value
        self.assertTrue(output.startswith('A-COOL-TERMINAL-EMULATOR'))

    @patch.dict(
        'archey.entries.terminal.os.environ',
        {
            'TERM': 'OH-A-SPECIAL-CASE',
            'TERMINATOR_UUID': 'urn:uuid:xxxxxxxx-yyyy-zzzz-tttt-uuuuuuuuuuuu'  # Ignored.
        },
        clear=True
    )
    @patch(
        'archey.configuration.Configuration.get',
        return_value={'use_unicode': False}
    )
    def test_terminal_emulator_special_term(self, _):
        """Check that `TERM` is honored even if a "known identifier" could be found"""
        output = Terminal().value
        self.assertTrue(output.startswith('OH-A-SPECIAL-CASE'))

    @patch.dict(
        'archey.entries.terminal.os.environ',
        {
            'TERM': 'xterm-256color',
            'KONSOLE_VERSION': 'X.Y.Z'
        },
        clear=True
    )
    @patch(
        'archey.configuration.Configuration.get',
        return_value={'use_unicode': False}
    )
    def test_terminal_emulator_name_normalization(self, _):
        """Check that our manual terminal detection as long as name normalization are working"""
        output = Terminal().value
        self.assertTrue(output.startswith('Konsole'))

    @patch.dict(
        'archey.entries.terminal.os.environ',
        {'TERM': 'xterm-256color'},
        clear=True
    )
    @patch(
        'archey.configuration.Configuration.get',
        return_value={'use_unicode': True}
    )
    def test_terminal_emulator_term_fallback_and_unicode(self, _):
        """Check that `TERM` is honored if present, and Unicode support for the colors palette"""
        output = Terminal().value
        self.assertTrue(output.startswith('xterm-256color'))
        self.assertEqual(output.count('\u2588'), 7 * 2)

    @patch.dict(
        'archey.entries.terminal.os.environ',
        {'COLORTERM': 'kmscon'},
        clear=True
    )
    @patch(
        'archey.configuration.Configuration.get',
        return_value={'use_unicode': False}
    )
    def test_terminal_emulator_colorterm(self, _):
        """Check we can detect terminals using the `COLORTERM` environment variable."""
        output = Terminal().value
        self.assertTrue(output.startswith('KMSCON'))

    @patch.dict(
        'archey.entries.terminal.os.environ',
        {
            'TERM': 'xterm-256color',
            'KONSOLE_VERSION': '200401',
            'COLORTERM': 'kmscon'
        },
        clear=True
    )
    @patch(
        'archey.configuration.Configuration.get',
        return_value={'use_unicode': False}
    )
    def test_terminal_emulator_colorterm_override(self, _):
        """
        Check we observe terminal using `COLORTERM` even if `TERM` or a "known identifier" is found.
        """
        output = Terminal().value
        self.assertTrue(output.startswith('KMSCON'))

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
        """Test terminal emulator (non-)detection, without Unicode support"""
        output = Terminal().value
        self.assertTrue(output.startswith('Not detected'))
        self.assertFalse(output.count('\u2588'))


if __name__ == '__main__':
    unittest.main()
