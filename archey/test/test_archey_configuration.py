"""Test module for `archey.configuration`"""

import sys
import tempfile
import unittest
from unittest.mock import patch

import archey.default_configuration as DefaultConfig
from archey.configuration import Configuration


class TestConfigurationUtil(unittest.TestCase):
    """
    Simple test cases to check the behavior of `Configuration` tools.
    """

    def tearDown(self):
        """Runs when each test ends."""
        # Load the default configuration to revert any changes we make in each test,
        # since not all tests use patch methods.
        Configuration()._config = DefaultConfig.CONFIGURATION # pylint: disable=protected-access

    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'entries': {
                'LanIp': {
                    'max_count': 2
                },
                'Temperature': {
                    'use_fahrenheit': False
                }
            }
        }
    )
    def test_get(self):
        """Test the dict-like __get__ method with configuration elements"""
        configuration = Configuration()

        self.assertEqual(
            configuration['entries']['LanIp']['max_count'],
            2
        )
        self.assertFalse(
            configuration['entries']['Temperature']['use_fahrenheit']
        )
        self.assertIsNone(configuration['does_not_exist'])

    def test_load_configuration(self):
        """
        Test for configuration loading from file. We can't use a patch
        method for this one!
        """
        configuration = Configuration()

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
			"use_fahrenheit": false
		},
		"LanIp": {
			"enabled": true,
			"display_text": "LAN IP",
			"max_count": 2,
			"ipv6_support": true
		}
	}
}
""")

            # Let's load it into our `Configuration` instance
            configuration.populate_configuration([temp_dir])

            # Let's check the result :S
            self.assertDictEqual(
                configuration._config,  # pylint: disable=protected-access
                {
                    'suppress_warnings': True,
                    'entries': {
                        'Temperature': {
                            'enabled': True,
                            'display_text': 'Temperature',
                            'char_before_unit': ' ',
                            'use_fahrenheit': False
                        },
                        'LanIp': {
                            'enabled': True,
                            'display_text': 'LAN IP',
                            'max_count': 2,
                            'ipv6_support': True
                        }
                    }
                }
            )
            # The `stderr` file descriptor has changed due to
            #   the `suppress_warnings` option.
            self.assertNotEqual(configuration._stderr, sys.stderr)  # pylint: disable=protected-access

if __name__ == '__main__':
    unittest.main()
