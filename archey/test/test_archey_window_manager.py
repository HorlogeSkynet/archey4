"""Test module for Archey's window manager detection module"""

import unittest
from unittest.mock import patch

from archey.entries.windowmanager import WindowManager
from archey.configuration import Configuration
from archey.singleton import Singleton
import archey.default_configuration as DefaultConfig


class TestWindowManagerEntry(unittest.TestCase):
    """
    Here, we mock the `check_output` call and check afterwards
      that the output is correct.
    We've to test the case where `wmctrl` is not installed too.
    """

    def setUp(self):
        """Runs when each test begins"""
        # Set up a default configuration instance.
        config = Configuration()
        config._config = DefaultConfig.CONFIGURATION # pylint: disable=protected-access

    def tearDown(self):
        """Runs when each test finishes testing"""
        # Destroy the singleton configuration instance (if created)
        try:
            del Singleton._instances[Configuration] # pylint: disable=protected-access
        except KeyError:
            pass

    @patch(
        'archey.entries.windowmanager.check_output',
        return_value="""\
Name: WINDOW MANAGER
Class: N/A
PID: N/A
Window manager's "showing the desktop" mode: OFF
""")
    def test_wmctrl(self, _):
        """[Entry] [WindowManager] Test `wmctrl` output parsing"""
        self.assertEqual(WindowManager().value, 'WINDOW MANAGER')

    @patch(
        'archey.entries.windowmanager.check_output',
        side_effect=FileNotFoundError()  # `wmctrl` call will fail
    )
    @patch(
        'archey.entries.windowmanager.Processes.get',
        return_value=[  # Fake running processes list
            'some',
            'awesome',  # Match !
            'programs',
            'running',
            'here'
        ]
    )
    def test_no_wmctrl_match(self, _, __):
        """[Entry] [WindowManager] Test basic detection based on a (fake) processes list"""
        self.assertEqual(WindowManager().value, 'Awesome')

    @patch(
        'archey.entries.windowmanager.check_output',
        side_effect=FileNotFoundError()  # `wmctrl` call will fail
    )
    @patch(
        'archey.entries.windowmanager.Processes.get',
        return_value=[  # Fake running processes list
            'some',
            'weird',  # Mismatch !
            'programs',
            'running',
            'here'
        ]
    )
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'default_strings': {
                'not_detected': 'Not detected'
            }
        }
    )
    def test_no_wmctrl_mismatch(self, _, __):
        """
        [Entry] [WindowManager] Test (non-detection) when processes list...
        ...do not contain any known value
        """
        self.assertEqual(
            WindowManager().value,
            'Not detected'
        )


if __name__ == '__main__':
    unittest.main()
