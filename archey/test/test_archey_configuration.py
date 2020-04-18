"""Test module for `archey.configuration`"""

import sys
import tempfile
import unittest
from unittest.mock import patch

from archey.configuration import Configuration
from archey.singleton import Singleton
import archey.default_configuration as DefaultConfig


class TestConfigurationUtil(unittest.TestCase):
    """
    Simple test cases to check the behavior of `Configuration` tools.
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
        """[Configuration] Test the dict-like __get__ method with configuration elements"""
        self.assertEqual(
            Configuration()['entries']['LanIp']['max_count'],
            3
        )
        self.assertTrue(
            Configuration()['entries']['Temperature']['use_fahrenheit']
        )
        self.assertIsNone(Configuration()['does_not_exist'])

    def test_load_configuration(self):
        """[Configuration] Test for configuration loading from file."""
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

            # Let's check the results :S
            self.assertTrue(Configuration()['suppress_warnings'])
            self.assertDictEqual(
                Configuration()['entries'],
                {
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
            )
            # The `stderr` file descriptor has changed due to
            #   the `suppress_warnings` option.
            self.assertNotEqual(Configuration()._stderr, sys.stderr)  # pylint: disable=protected-access

    def test_update_recursive(self):
        """[Entry] [Configuration] Test for the `_update_recursive` private method"""
        configuration = Configuration()
        configuration._config = {  # pylint: disable=protected-access
            'allow_overriding': True,
            'suppress_warnings': False,
            'default_strings': {
                'no_address': 'No Address',
                'not_detected': 'Not detected'
            },
            'colors_palette': {
                'use_unicode': False
            },
            'ip_settings': {
                'lan_ip_max_count': 2
            },
            'temperature': {
                'use_fahrenheit': False
            }
        }

        # We change existing values, add new ones, and omit some others.
        configuration._update_recursive(  # pylint: disable=protected-access
            configuration._config,  # pylint: disable=protected-access
            {
                'suppress_warnings': True,
                'colors_palette': {
                    'use_unicode': False
                },
                'default_strings': {
                    'no_address': '\xde\xad \xbe\xef',
                    'not_detected': 'Not detected',
                    'virtual_environment': 'Virtual Environment'
                },
                'temperature': {
                    'a_weird_new_dict': [
                        None,
                        'l33t',
                        {
                            'really': 'one_more_?'
                        }
                    ]
                }
            }
        )

        self.assertDictEqual(
            configuration._config,  # pylint: disable=protected-access
            {
                'allow_overriding': True,
                'suppress_warnings': True,
                'colors_palette': {
                    'use_unicode': False
                },
                'default_strings': {
                    'no_address': '\xde\xad \xbe\xef',
                    'not_detected': 'Not detected',
                    'virtual_environment': 'Virtual Environment'
                },
                'ip_settings': {
                    'lan_ip_max_count': 2
                },
                'temperature': {
                    'use_fahrenheit': False,
                    'a_weird_new_dict': [
                        None,
                        'l33t',
                        {
                            'really': 'one_more_?'
                        }
                    ]
                }
            }
        )

if __name__ == '__main__':
    unittest.main()
