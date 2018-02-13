
import unittest
from unittest.mock import patch

from archey.archey import Terminal


class TestTerminalEntry(unittest.TestCase):
    """
    For this entry, we'll verify that the output contains what the environment
      is supposed to give, plus the right number of "colorized" characters.
    """
    @patch(
        'archey.archey.getenv',
        return_value='TERMINAL'
    )
    @patch('archey.archey.config.config', {
            'colors_palette': {'use_unicode': False},
            'default_strings': {'not_detected': 'Not detected'}
        }
    )
    def test_without_unicode(self, getenv_mock):
        output = Terminal().value
        self.assertTrue(output.startswith('TERMINAL '))
        self.assertEqual(output.count('#'), 7 * 2)

    @patch(
        'archey.archey.getenv',
        return_value='TERMINAL'
    )
    @patch('archey.archey.config.config', {
            'colors_palette': {'use_unicode': True},
            'default_strings': {'not_detected': 'Not detected'}
        }
    )
    def test_with_unicode(self, getenv_mock):
        output = Terminal().value
        self.assertTrue(output.startswith('TERMINAL '))
        self.assertEqual(output.count('\u2588'), 7 * 2)


if __name__ == '__main__':
    unittest.main()
