"""Test module for Archey's desktop environment detection module"""

import unittest
from unittest.mock import patch

from archey.entries.desktop_environment import DesktopEnvironment


class TestDesktopEnvironmentEntry(unittest.TestCase):
    """
    With the help of a fake running processes list, we test the DE matching.
    """
    @patch(
        'archey.entries.desktop_environment.Processes.get',
        return_value=[  # Fake running processes list
            'do',
            'you',
            'like',
            'cinnamon',  # Match !
            'tea'
        ]
    )
    def test_match(self, _):
        """Simple list matching"""
        self.assertEqual(DesktopEnvironment().value, 'Cinnamon')

    @patch(
        'archey.entries.desktop_environment.Processes.get',
        return_value=[  # Fake running processes list
            'do',
            'you',
            'like',
            'unsweetened',  # Mismatch...
            'coffee'
        ]
    )
    @patch(
        'archey.entries.desktop_environment.os.getenv',
        return_value='DESKTOP ENVIRONMENT'
    )
    def test_mismatch(self, _, __):
        """Simple list (mis-)-matching"""
        self.assertEqual(DesktopEnvironment().value, 'DESKTOP ENVIRONMENT')


if __name__ == '__main__':
    unittest.main()
