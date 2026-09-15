"""Archey configuration module"""

import json
import logging
import os
from copy import deepcopy
from typing import Any, Dict

from archey.colors import ANSI_TEXT_CODES_REGEXP
from archey.singleton import Singleton
from archey.utility import Utility

# Below are default required configuration keys which will be used.
DEFAULT_CONFIG: Dict[str, Any] = {
    "allow_overriding": True,
    "parallel_loading": True,
    "suppress_warnings": False,
    "entries_color": "",
    "honor_ansi_color": True,
    "entries_icon": False,
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
        # See <https://specifications.freedesktop.org/basedir/latest/#variables>.
        else:
            # 1. Load "system preferences"
            ## Honor `XDG_CONFIG_DIRS` (if set, with fallback to /etc/xdg and /etc).
            config_path_candidates = list(
                filter(
                    os.path.isabs,
                    os.getenv("XDG_CONFIG_DIRS", "/etc/xdg:/etc").split(os.path.pathsep),
                )
            )

            # 2. Load "user preferences"
            ## Honor `XDG_CONFIG_HOME` (if set, with fallback to ~/.config).
            config_home = os.getenv("XDG_CONFIG_HOME")
            if config_home is None or not os.path.isabs(config_home):
                config_home = os.path.expanduser("~/.config")
            config_path_candidates.append(os.path.join(config_home, "archey4"))

            for config_path_candidate in config_path_candidates:
                self._load_configuration(os.path.join(config_path_candidate, "archey4"))

        # Perform various validations
        self._validate_configuration()

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

    def _validate_configuration(self) -> None:
        # entries_color
        entries_color = self._config.get("entries_color")
        if entries_color:
            if (
                not isinstance(entries_color, str)
                or ANSI_TEXT_CODES_REGEXP.fullmatch(entries_color) is None
            ):
                logging.warning(
                    "Couldn't validate 'entries_color' configuration option value, ignoring..."
                )
                self._config["entries_color"] = DEFAULT_CONFIG["entries_color"]

    def __iter__(self):
        """When used as an iterator, directly yield `_config` elements"""
        return iter(self._config.items())
