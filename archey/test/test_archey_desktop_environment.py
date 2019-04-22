"""Test module for Archey's desktop environment detection module"""

import unittest
from unittest.mock import patch

from archey.entries.desktop_environment import DesktopEnvironment


class TestDesktopEnvironmentEntry(unittest.TestCase):
    """
    With the help of a fake running processes list, we test the DE matching.
    """
    def test_match(self):
        """Simple list matching"""
        processes = [  # Fake running processes list
            'do',
            'you',
            'like',
            'cinnamon',  # Match !
            'tea'
        ]
        self.assertEqual(
            DesktopEnvironment(processes, 'Not detected').value,
            'Cinnamon'
        )

    @patch(
        'archey.entries.desktop_environment.os.getenv',
        return_value='DESKTOP ENVIRONMENT'
    )
    def test_mismatch(self, _):
        """Simple list (mis-)-matching"""
        processes = [  # Fake running processes list
            'do',
            'you',
            'like',
            'unsweetened',  # Mismatch...
            'coffee'
        ]
        self.assertEqual(
            DesktopEnvironment(processes, 'Not detected').value,
            'DESKTOP ENVIRONMENT'
        )


if __name__ == '__main__':
    unittest.main()
