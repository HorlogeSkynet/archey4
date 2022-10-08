"""Archey configuration module"""

import json
import logging
import os
from copy import deepcopy
from typing import Any, Dict

from archey.singleton import Singleton
from archey.utility import Utility

# Below are default required configuration keys which will be used.
DEFAULT_CONFIG: Dict[str, Any] = {
    "allow_overriding": True,
    "parallel_loading": True,
    "suppress_warnings": False,
    "entries_color": "",
    "honor_ansi_color": True,
    "default_strings": {
        "latest": "latest",
        "available": "available",
        "no_address": "No Address",
        "not_detected": "Not detected",
        "virtual_environment": "Virtual Environment",
    },
}


class Configuration(metaclass=Singleton):
    """
    Values present in `DEFAULT_CONFIG` dictionary are required.
    New optional values may be added with `Utility.update_recursive` method.

    If a `config_path` is passed during instantiation, it will be loaded.
    """

    def __init__(self, config_path=None):
        # Deep-copy `DEFAULT_CONFIG` so we have a local copy to safely mutate.
        self._config = deepcopy(DEFAULT_CONFIG)

        # We will track successfully loaded configuration files stat info.
        self._config_files_info = {}

        # If a `config_path` has been specified, (try to) load it directly.
        if config_path:
            self._load_configuration(config_path)
        # If not, load each (optional) configuration file in a "regular" order.
        else:
            self._load_configuration("/etc/archey4/")
            self._load_configuration(os.path.expanduser("~/.config/archey4/"))
            self._load_configuration(os.getcwd())

    def get(self, key: str, default=None) -> Any:
        """
        A binding method to imitate the `dict.get()` behavior.
        """
        return self._config.get(key, default)

    def get_config_files_info(self) -> Dict[str, os.stat_result]:
        """Return a copy of loaded files stat info data"""
        return self._config_files_info.copy()

    def _load_configuration(self, path: str) -> None:
        """
        A method handling configuration loading from a JSON file.
        It will try to load any `config.json` present under `path`.
        """
        # If a previous configuration file has denied overriding...
        if not self.get("allow_overriding"):
            #  ... don't load this one.
            return

        # If the specified `path` is a directory, append the file name we are looking for.
        if os.path.isdir(path):
            path = os.path.join(path, "config.json")

        try:
            with open(path, mode="rb") as f_config:
                Utility.update_recursive(self._config, json.load(f_config))
                self._config_files_info[path] = os.fstat(f_config.fileno())
        except FileNotFoundError:
            return
        except (PermissionError, json.JSONDecodeError) as error:
            logging.error("%s (%s)", error, path)
            return

        # When `suppress_warnings` is set, higher the log level to silence warning messages.
        logging.getLogger().setLevel(
            logging.ERROR if self.get("suppress_warnings") else logging.WARN
        )

    def __iter__(self):
        """When used as an iterator, directly yield `_config` elements"""
        return iter(self._config.items())
