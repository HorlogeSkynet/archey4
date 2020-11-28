"""Archey configuration module"""

import os
import sys
import json
from copy import deepcopy

from archey.constants import DEFAULT_CONFIG
from archey.singleton import Singleton


class Configuration(metaclass=Singleton):
    """
    Values present in `archey.constants.DEFAULT_CONFIG` dictionary are required.
    New optional values may be added with `update_recursive` method.

    If a `config_path` is passed during instantiation, it will be loaded.
    """
    def __init__(self, config_path=None):
        # Deep-copy `DEFAULT_CONFIG` so we have a local copy to safely mutate.
        self._config = deepcopy(DEFAULT_CONFIG)

        # Let's "save" `STDERR` file descriptor for `suppress_warnings` option
        self._stderr = sys.stderr

        # If a `config_path` has been specified, (try to) load it directly.
        if config_path:
            self._load_configuration(config_path)
        # If not, load each (optional) configuration file in a "regular" order.
        else:
            self._load_configuration('/etc/archey4/')
            self._load_configuration(os.path.expanduser('~/.config/archey4/'))
            self._load_configuration(os.getcwd())

    def get(self, key, default=None):
        """
        A binding method to imitate the `dict.get()` behavior.
        """
        return self._config.get(key, default)

    def _load_configuration(self, path):
        """
        A method handling configuration loading from a JSON file.
        It will try to load any `config.json` present under `path`.
        """
        # If a previous configuration file has denied overriding...
        if not self.get('allow_overriding'):
            #  ... don't load this one.
            return

        # If the specified `path` is a directory, append the file name we are looking for.
        if os.path.isdir(path):
            path = os.path.join(path, 'config.json')

        try:
            with open(path) as f_config:
                self.update_recursive(self._config, json.load(f_config))
        except FileNotFoundError:
            return
        except json.JSONDecodeError as json_decode_error:
            print('Warning: {0} ({1})'.format(json_decode_error, path), file=sys.stderr)
            return

        # If the user does not want any warning to appear : 2> /dev/null
        if self.get('suppress_warnings'):
            # One more if statement to avoid multiple `open` calls.
            if sys.stderr == self._stderr:
                sys.stderr = open(os.devnull, 'w')
        else:
            self._close_and_restore_sys_stderr()

    @classmethod
    def update_recursive(cls, old_dict, new_dict):
        """
        A method for recursively merging dictionaries as `dict.update()` is not able to do this.
        Original snippet taken from here : <https://gist.github.com/angstwad/bf22d1822c38a92ec0a9>
        """
        for key, value in new_dict.items():
            if key in old_dict \
                and isinstance(old_dict[key], dict) \
                and isinstance(value, dict):
                cls.update_recursive(old_dict[key], value)
            else:
                old_dict[key] = value

    def _close_and_restore_sys_stderr(self):
        """If modified, close current and restore `sys.stderr` to its original file descriptor"""
        if sys.stderr != self._stderr:
            sys.stderr.close()
            sys.stderr = self._stderr

    def __del__(self):
        self._close_and_restore_sys_stderr()

    def __iter__(self):
        """When used as an iterator, directly yield `_config` elements"""
        return iter(self._config.items())
