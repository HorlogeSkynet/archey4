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
        # "Save" `STDERR` file descriptor for `suppress_warnings` option.
        self._stderr = sys.stderr

        # We will later attempt to find configuration files at these paths,
        # in this order.
        configuration_paths = [
            os.path.dirname(os.path.realpath(__file__)), # current $PATH
            '~/.config/archey4/',
            '/etc/archey4/'
        ]

        # Load configuration from the first path that contains one.
        for path in configuration_paths:
            try:
                self._config = self.load_configuration(path)
                break
            except FileNotFoundError:
                continue

        # Exit with an error if no configuration is found.
        if not hasattr(self, "_config"):
            sys.exit("FATAL: No configuration file found.")

        # Create an iterable `entries` consisting of the keys in the root
        # configuration object.
        self.entries = iter(self._config.get("entries"))

    def load_configuration(self, path):
        """
        A method handling configuration loading from a JSON file.
        It will try to load any `config.json` present under `path`.
        """

        path = os.path.join(path, 'config.json')

        try:
            with open(path) as file:
                config = json.load(file)

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
            print('Warning: {0} ({1})'.format(error, path), file=sys.stderr)

        return config

    def __getitem__(self, key):
        return self._config.get(key)

    def __del__(self):
        if sys.stderr != self._stderr:
            sys.stderr.close()
            sys.stderr = self._stderr
