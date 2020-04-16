"""Test module for `archey.configuration`"""

import sys
import tempfile
import unittest

from archey.configuration import Configuration


class TestConfigurationUtil(unittest.TestCase):
    """
    Simple test cases to check the behavior of `Configuration` tools.
    We can't use the `patch` method as the dictionary state after
      the initializations is unknown due to user's configuration files.
    Values will be manually set in the tests below.
    """
    def test_get(self):
        """Test the __get__ method with configuration elements"""
        configuration = Configuration()
        configuration._config = {  # pylint: disable=protected-access
            'entries': {
                'LanIp': {
                    'max_count': 2
                },
                'Temperature': {
                    'use_fahrenheit': False
                }
            }
        }

        self.assertEqual(
            configuration['entries']['LanIp']['max_count'],
            2
        )
        self.assertFalse(
            configuration['entries']['Temperature']['use_fahrenheit']
        )
        self.assertIsNone(configuration['does_not_exist'])

    def test_load_configuration(self):
        """Test for configuration loading from file"""
        configuration = Configuration()
        configuration._config = {  # pylint: disable=protected-access
            'suppress_warnings': False,
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
