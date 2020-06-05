"""Test module for Archey's window manager detection module"""

import unittest
from unittest.mock import MagicMock, patch

from archey.entries.window_manager import WindowManager
from archey.test.entries import HelperMethods
from archey.constants import DEFAULT_CONFIG


class TestWindowManagerEntry(unittest.TestCase):
    """
    Here, we mock the `check_output` call and check afterwards
      that the output is correct.
    We've to test the case where `wmctrl` is not installed too.
    """
    @patch(
        'archey.entries.window_manager.check_output',
        return_value="""\
Name: WINDOW MANAGER
Class: N/A
PID: N/A
Window manager's "showing the desktop" mode: OFF
""")
    def test_wmctrl(self, _):
        """Test `wmctrl` output parsing"""
        self.assertEqual(WindowManager().value, 'WINDOW MANAGER')

    @patch(
        'archey.entries.window_manager.check_output',
        side_effect=FileNotFoundError()  # `wmctrl` call will fail
    )
    @patch(
        'archey.entries.window_manager.Processes.list',
        (  # Fake running processes list
            'some',
            'awesome',  # Match !
            'programs',
            'running',
            'here'
        )
    )
    def test_no_wmctrl_match(self, _):
        """Test basic detection based on a (fake) processes list"""
        self.assertEqual(WindowManager().value, 'Awesome')

    @patch(
        'archey.entries.window_manager.check_output',
        side_effect=FileNotFoundError()  # `wmctrl` call will fail
    )
    @patch(
        'archey.entries.window_manager.Processes.list',
        (  # Fake running processes list
            'some',
            'weird',  # Mismatch !
            'programs',
            'running',
            'here'
        )
    )
    @HelperMethods.patch_clean_configuration
    def test_no_wmctrl_mismatch(self, _):
        """Test (non-detection) when processes list do not contain any known value"""
        window_manager = WindowManager()

        output_mock = MagicMock()
        window_manager.output(output_mock)

        self.assertIsNone(window_manager.value)
        self.assertEqual(
            output_mock.append.call_args[0][1],
            DEFAULT_CONFIG['default_strings']['not_detected']
        )


if __name__ == '__main__':
    unittest.main()
