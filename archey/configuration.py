"""Archey configuration module"""

import os
import sys
import json

from importlib import import_module

from archey.singleton import Singleton


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
        for path in configuration_paths:
            file_path = os.path.join(path, 'config.json')
            try:
                with open(file_path) as config_file:
                    self._config = self._load_configuration(config_file)
                break
            except ValueError:
                print('\tin file: {0}'.format(file_path), file=sys.stderr)
            except FileNotFoundError:
                continue

        # Load the default configuration if no files were found.
        if not hasattr(self, "_config"):
            self._config = import_module('archey.default_configuration').CONFIGURATION

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

    def __getitem__(self, key):
        """Implement dict-like behaviour"""
        return self._config.get(key)

    def __del__(self):
        if sys.stderr != self._stderr:
            sys.stderr.close()
            sys.stderr = self._stderr
