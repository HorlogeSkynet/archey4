"""Test module for Archey's terminal detection module"""

import unittest
from unittest.mock import MagicMock, patch

from archey.configuration import DEFAULT_CONFIG
from archey.entries.terminal import Terminal
from archey.test.entries import HelperMethods


class TestTerminalEntry(unittest.TestCase):
    """
    For this entry, we'll verify that the output contains what the environment
      is supposed to give, plus the right number of "colorized" characters.
    """

    def setUp(self):
        # By default, colors won't be disabled.
        self._should_color_output_patch = patch(
            "archey.colors.Colors.should_color_output",
            return_value=True,
        )
        self._should_color_output_patch.start()

    def tearDown(self):
        self._should_color_output_patch.stop()

    @patch.dict(
        "archey.entries.terminal.os.environ",
        {
            "TERM": "xterm-256color",
            "COLORTERM": "truecolor",
            "TERM_PROGRAM": "A-COOL-TERMINAL-EMULATOR",
        },
        clear=True,
    )
    def test_terminal_emulator_term_program(self):
        """Check that `TERM_PROGRAM` is honored even if `TERM` or `COLORTERM` are defined"""
        self.assertEqual(Terminal().value, "A-COOL-TERMINAL-EMULATOR")

    @patch.dict(
        "archey.entries.terminal.os.environ",
        {"TERM_PROGRAM": "A-COOL-TERMINAL-EMULATOR", "TERM_PROGRAM_VERSION": "vX.Y.Z-beta42"},
        clear=True,
    )
    def test_terminal_emulator_term_program_version(self):
        """Check that `TERM_PROGRAM` and `TERM_PROGRAM_VERSION` are correctly honored"""
        self.assertEqual(Terminal().value, "A-COOL-TERMINAL-EMULATOR vX.Y.Z-beta42")

    @patch.dict(
        "archey.entries.terminal.os.environ",
        {
            "TERM": "OH-A-SPECIAL-CASE",
            "TERMINATOR_UUID": "urn:uuid:xxxxxxxx-yyyy-zzzz-tttt-uuuuuuuuuuuu",  # Ignored.
        },
        clear=True,
    )
    def test_terminal_emulator_special_term(self):
        """Check that `TERM` is honored even if a "known identifier" could be found"""
        self.assertEqual(Terminal().value, "OH-A-SPECIAL-CASE")

    @patch.dict(
        "archey.entries.terminal.os.environ",
        {"TERM": "xterm-256color", "KONSOLE_VERSION": "X.Y.Z"},
        clear=True,
    )
    def test_terminal_emulator_name_normalization(self):
        """Check that our manual terminal detection as long as name normalization are working"""
        self.assertEqual(Terminal().value, "Konsole")

    @patch.dict(
        "archey.entries.terminal.os.environ",
        {"TERM": "xterm-256color"},
        clear=True,
    )
    def test_terminal_emulator_term_fallback_and_unicode(self):
        """Check that `TERM` is honored if present, and Unicode support for the colors palette"""
        terminal = Terminal(options={"use_unicode": True})

        output_mock = MagicMock()
        terminal.output(output_mock)

        self.assertEqual(terminal.value, "xterm-256color")
        self.assertTrue(output_mock.append.call_args[0][1].startswith("xterm-256color"))
        self.assertEqual(output_mock.append.call_args[0][1].count("\u2588"), 7 * 2)

    @patch.dict(
        "archey.entries.terminal.os.environ",
        {"COLORTERM": "kmscon"},
        clear=True,
    )
    def test_terminal_emulator_colorterm(self):
        """Check we can detect terminals using the `COLORTERM` environment variable."""
        self.assertEqual(Terminal().value, "KMSCON")

    @patch.dict(
        "archey.entries.terminal.os.environ",
        {"TERM": "xterm-256color", "KONSOLE_VERSION": "200401", "COLORTERM": "kmscon"},
        clear=True,
    )
    def test_terminal_emulator_colorterm_override(self):
        """
        Check we observe terminal using `COLORTERM` even if `TERM` or a "known identifier" is found.
        """
        self.assertEqual(Terminal().value, "KMSCON")

    @patch.dict(
        "archey.entries.terminal.os.environ",
        {"TERM_PROGRAM": "X-TERMINAL-EMULATOR"},
        clear=True,
    )
    def test_color_disabling(self):
        """Test `Terminal` output behavior when coloration has been disabled"""
        with patch("archey.colors.Colors.should_color_output", return_value=False):
            terminal = Terminal()

            output_mock = MagicMock()
            terminal.output(output_mock)

            self.assertEqual(terminal.value, "X-TERMINAL-EMULATOR")
            self.assertEqual(output_mock.append.call_args[0][1], "X-TERMINAL-EMULATOR")

    @patch.dict(
        "archey.entries.terminal.os.environ",
        {},
        clear=True,
    )
    @HelperMethods.patch_clean_configuration
    def test_not_detected(self):
        """Test terminal emulator (non-)detection, without Unicode support"""
        terminal = Terminal(options={"use_unicode": False})

        output_mock = MagicMock()
        terminal.output(output_mock)
        output = output_mock.append.call_args[0][1]

        self.assertIsNone(terminal.value)
        self.assertTrue(output.startswith(DEFAULT_CONFIG["default_strings"]["not_detected"]))
        self.assertFalse(output.count("\u2588"))


if __name__ == "__main__":
    unittest.main()
