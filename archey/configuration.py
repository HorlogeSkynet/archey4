"""Archey configuration module"""

import os
import sys
import json

from archey.singleton import Singleton


class Configuration(metaclass=Singleton):
    """
    The default needed configuration which will be used by Archey is present below.
    Values present in the `self.config` dictionary below are needed.
    New optional values may be added with `_update_recursive()` method.
    """
    def __init__(self):
        self._config = {
            'colors_palette': {
                'use_unicode': False
            },
            'default_strings': {
                'no_address': 'No Address',
                'not_detected': 'Not detected',
                'virtual_environment': 'Virtual Environment'
            },
            'ip_settings': {
                'lan_ip_max_count': 2,
                'lan_ip_v6_support': True,
                'wan_ip_v6_support': True
            },
            'limits': {
                'ram': {
                    'warning': 33.3,
                    'danger': 66.7
                },
                'disk': {
                    'warning': 50,
                    'danger': 75
                }
            },
            'temperature': {
                'char_before_unit': ' ',
                'use_fahrenheit': False
            },
            'timeout': {
                'ipv4_detection': 1,
                'ipv6_detection': 1
            }
        }

        # Let's "save" `STDERR` file descriptor for `suppress_warnings` option
        self._stderr = sys.stderr

        # Now, let's load each optional configuration file in a "regular" order
        self.load_configuration('/etc/archey4/')
        self.load_configuration(os.path.expanduser('~/.config/archey4/'))
        self.load_configuration(os.path.dirname(os.path.realpath(__file__)))

    def get(self, key, default=None):
        """
        A binding method to imitate the `dict.get()` behavior.
        """
        return self._config.get(key, default)

    def load_configuration(self, path):
        """
        A method handling configuration loading from a JSON file.
        It will try to load any `config.json` present under `path`.
        """
        # If a previous configuration file has denied overriding...
        if not self._config.get('allow_overriding', True):
            #  ... don't load this one.
            return

        path = os.path.join(path, 'config.json')

        try:
            with open(path) as file:
                self._update_recursive(self._config, json.load(file))

            # If the user does not want any warning to appear : 2> /dev/null
            if self._config.get('suppress_warnings', False):
                # One more if statement to avoid multiple `open` calls.
                if sys.stderr == self._stderr:
                    sys.stderr = open(os.devnull, 'w')

            else:
                # One more if statement to avoid useless assignments and...
                # ... for closing previously opened new file descriptor.
                if sys.stderr != self._stderr:
                    sys.stderr.close()
                    sys.stderr = self._stderr

        except FileNotFoundError:
            pass

        # For backward compatibility with Python versions prior to 3.5.0
        #   we use `ValueError` instead of `json.JSONDecodeError`.
        except ValueError as error:
            print('Warning: {0} ({1})'.format(error, path), file=sys.stderr)

    def _update_recursive(self, old_dict, new_dict):
        """
        A method for recursively merging dictionaries as...
        ... `dict.update()` is not able to do this.
        Original snippet taken from here :
        https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
        """
        for key, value in new_dict.items():
            if key in old_dict and isinstance(old_dict[key], dict) \
                    and isinstance(value, dict):
                self._update_recursive(old_dict[key], value)

            else:
                old_dict[key] = value

    def __del__(self):
        if sys.stderr != self._stderr:
            sys.stderr.close()
            sys.stderr = self._stderr
