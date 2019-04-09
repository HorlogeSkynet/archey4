
import unittest
from unittest.mock import patch

from archey.entries.desktop_environment import DesktopEnvironment


class TestDesktopEnvironmentEntry(unittest.TestCase):
    """
    With the help of a fake running processes list, we test the DE matching.
    """
    @patch('archey.archey.PROCESSES', [  # Fake running processes list
        'do',
        'you',
        'like',
        'cinnamon',  # Match !
        'tea'
    ])
    def test_match(self):
        self.assertEqual(DesktopEnvironment().value, 'Cinnamon')

    @patch('archey.archey.PROCESSES', [  # Fake running processes list
        'do',
        'you',
        'like',
        'unsweetened',  # Mismatch...
        'coffee'
    ])
    @patch(
        'archey.archey.os.getenv',
        return_value='DESKTOP ENVIRONMENT'
    )
    def test_mismatch(self, getenv_mock):
        self.assertEqual(DesktopEnvironment().value, 'DESKTOP ENVIRONMENT')


if __name__ == '__main__':
    unittest.main()
