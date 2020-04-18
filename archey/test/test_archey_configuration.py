"""Test module for `archey.configuration`"""

import sys
import tempfile
import unittest
from unittest.mock import patch

from archey.configuration import Configuration

class TestConfigurationUtil(unittest.TestCase):
    """
    Simple test cases to check the behavior of `Configuration` tools.
    """

    @patch.object(
        Configuration(),
        '_config',
        {
            'entries': {
                'LanIp': {
                    'max_count': 3
                },
                'Temperature': {
                    'use_fahrenheit': True
                }
            }
        },
        create=True
    )
    def test_get(self):
        """Test the dict-like __get__ method with configuration elements"""
        self.assertEqual(
            Configuration()['entries']['LanIp']['max_count'],
            3
        )
        self.assertTrue(
            Configuration()['entries']['Temperature']['use_fahrenheit']
        )
        self.assertIsNone(Configuration()['does_not_exist'])

    # Without this patch, we appear to permanently modify the configuration instance.
    # It can no longer be mocked or deleted, so we *must* patch it here so that we
    # only modify a mock and not the global singleton.
    @patch.object(
        Configuration(),
        '_config',
        {},
        create=True
    )
    def test_load_configuration(self):
        """
        Test for configuration loading from file.
        """
        with tempfile.TemporaryDirectory(suffix='/') as temp_dir:
            # We create a fake temporary configuration file
            with open(temp_dir + 'config.json', 'w') as file:
                file.write("""\
{
	"suppress_warnings": true,
	"entries": {
		"Temperature": {
			"enabled": true,
			"display_text": "Temperature",
			"char_before_unit": " ",
			"use_fahrenheit": true
		},
		"LanIp": {
			"enabled": true,
			"display_text": "LAN IP",
			"max_count": 3,
			"ipv6_support": true
		}
	}
}
""")

            # Let's load it into our `Configuration` instance
            Configuration().populate_configuration([temp_dir])

            # Let's check the result :S
            self.assertDictEqual(
                Configuration()._config,  # pylint: disable=protected-access
                {
                    'suppress_warnings': True,
                    'entries': {
                        'Temperature': {
                            'enabled': True,
                            'display_text': 'Temperature',
                            'char_before_unit': ' ',
                            'use_fahrenheit': True
                        },
                        'LanIp': {
                            'enabled': True,
                            'display_text': 'LAN IP',
                            'max_count': 3,
                            'ipv6_support': True
                        }
                    }
                }
            )
            # The `stderr` file descriptor has changed due to
            #   the `suppress_warnings` option.
            self.assertNotEqual(Configuration()._stderr, sys.stderr)  # pylint: disable=protected-access

if __name__ == '__main__':
    unittest.main()
