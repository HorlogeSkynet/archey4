"""Archey configuration module"""

import os
import sys
import json

from archey.singleton import Singleton
import archey.default_configuration as DefaultConfig

class Configuration(metaclass=Singleton):
    """
    Manages loading the configuration for Archey.
    The root configuration object is stored as a dict, which is accessible in
    the same fashion as stdlib dicts.
    """
    def __init__(self):
        # "Save" `STDERR` file descriptor for `suppress_warnings` option.
        self._stderr = sys.stderr

        # Attempt to find configuration files at these paths, in this order.
        configuration_paths = [
            os.path.dirname(os.path.realpath(__file__)), # current $PATH
            '~/.config/archey4/',
            '/etc/archey4/'
        ]

        self.populate_configuration(configuration_paths)

    def populate_configuration(self, configuration_paths):
        """
        A method that populates the configuration of the instance, trying
        `config.json` under each path passed to it, using the first existing
        file.
        """
        # Load the default configuration first
        self._config = DefaultConfig.CONFIGURATION

        # Get the user configuration file with the most precedence
        user_config = None
        for path in configuration_paths:
            file_path = os.path.join(path, 'config.json')
            try:
                with open(file_path) as config_file:
                    user_config = self._load_configuration(config_file)
                break
            except ValueError:
                print('\tin file: {0}'.format(file_path), file=sys.stderr)
            except FileNotFoundError:
                continue

        # If there was a user configuration file, recursively update the defaults
        # with the new definitions (replacing 'entries' entirely with the new one,
        # if it is a new entry)
        if user_config is not None:
            self._update_recursive(self._config, user_config)

    def _load_configuration(self, config_file):
        """
        A method handling configuration loading from a JSON file.
        It will try to load the file passed to it.
        """
        try:
            config = json.load(config_file)

            # If the user does not want any warning to appear : 2> /dev/null
            if config.get('suppress_warnings', False):
                # One more if statement to avoid multiple `open` calls.
                if sys.stderr == self._stderr:
                    sys.stderr = open(os.devnull, 'w')
            else:
                # One more if statement to avoid useless assignments and...
                # ... for closing previously opened new file descriptor.
                if sys.stderr != self._stderr:
                    sys.stderr.close()
                    sys.stderr = self._stderr

        # For backward compatibility with Python versions prior to 3.5.0
        #   we use `ValueError` instead of `json.JSONDecodeError`.
        except ValueError as error:
            print('Warning: {0}'.format(error), file=sys.stderr)
            raise ValueError

        return config

    def _update_recursive(self, old_dict, new_dict):
        """
        A customised method for recursively merging dictionaries as
        `dict.update()` is not able to do this.
        Original snippet taken from here :
        https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
        """
        for key, value in new_dict.items():
            if key == 'entries':
                # Remove all the old entries if a new set exist
                old_dict['entries'] = {}
            if key in old_dict and isinstance(old_dict[key], dict) \
                    and isinstance(value, dict):
                self._update_recursive(old_dict[key], value)

            else:
                old_dict[key] = value

    def __getitem__(self, key):
        """Implement dict-like behaviour"""
        return self._config.get(key)

    def __del__(self):
        if sys.stderr != self._stderr:
            sys.stderr.close()
            sys.stderr = self._stderr
