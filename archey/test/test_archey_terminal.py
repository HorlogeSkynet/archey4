"""Test module for Archey's terminal detection module"""

import unittest
from unittest.mock import patch

from archey.entries.terminal import Terminal
from archey.configuration import Configuration
from archey.singleton import Singleton
import archey.default_configuration as DefaultConfig


class TestTerminalEntry(unittest.TestCase):
    """
    For this entry, we'll verify that the output contains what the environment
      is supposed to give, plus the right number of "colorized" characters.
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
        'archey.entries.terminal.os.getenv',
        return_value='TERMINAL'
    )
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'colors_palette': {
                'use_unicode': False
            },
            'default_strings': {
                'not_detected': None # Required KV pair
            }
        }
    )
    def test_without_unicode(self, _):
        """[Entry] [Terminal] Test simple output, without Unicode support (default)"""
        output = Terminal().value
        self.assertTrue(output.startswith('TERMINAL '))
        self.assertEqual(output.count('#'), 7 * 2)

    @patch(
        'archey.entries.terminal.os.getenv',
        return_value='TERMINAL'
    )
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'colors_palette': {
                'use_unicode': True
            },
            'default_strings': {
                'not_detected': None # Required KV pair
            }
        }
    )
    def test_with_unicode(self, _):
        """[Entry] [Terminal] Test simple output, with Unicode support !"""
        output = Terminal().value
        self.assertTrue(output.startswith('TERMINAL '))
        self.assertEqual(output.count('\u2588'), 7 * 2)

    @patch(
        'archey.entries.terminal.os.getenv',
        return_value='Not detected'  # Set the "Not detected" string here, as we mock `os.getenv`.
    )
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'colors_palette': {
                'use_unicode': False
            },
            'default_strings': {
                'not_detected': None # Required KV pair
            }
        }
    )
    def test_not_detected(self, _):
        """[Entry] [Terminal] Test simple output, with Unicode support !"""
        output = Terminal().value
        self.assertTrue(output.startswith('Not detected '))
        self.assertEqual(output.count('#'), 7 * 2)


if __name__ == '__main__':
    unittest.main()
