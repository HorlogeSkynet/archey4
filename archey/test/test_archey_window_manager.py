"""Test module for Archey's window manager detection module"""

import unittest
from unittest.mock import patch

from archey.entries.window_manager import WindowManager


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
        'archey.entries.window_manager.Processes.get',
        return_value=[  # Fake running processes list
            'some',
            'awesome',  # Match !
            'programs',
            'running',
            'here'
        ]
    )
    def test_no_wmctrl_match(self, _, __):
        """Test basic detection based on a (fake) processes list"""
        self.assertEqual(WindowManager().value, 'Awesome')

    @patch(
        'archey.entries.window_manager.check_output',
        side_effect=FileNotFoundError()  # `wmctrl` call will fail
    )
    @patch(
        'archey.entries.window_manager.Processes.get',
        return_value=[  # Fake running processes list
            'some',
            'weird',  # Mismatch !
            'programs',
            'running',
            'here'
        ]
    )
    @patch(
        'archey.entries.window_manager.Configuration.get',
        return_value={
            'not_detected': 'Not detected'
        }
    )
    def test_no_wmctrl_mismatch(self, _, __, ___):
        """Test (non-detection) when processes list do not contain any known value"""
        self.assertEqual(
            WindowManager().value,
            'Not detected'
        )


if __name__ == '__main__':
    unittest.main()
