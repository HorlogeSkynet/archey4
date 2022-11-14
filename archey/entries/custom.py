"""Custom entry class"""

import logging
import os
import stat
from contextlib import suppress
from subprocess import DEVNULL, PIPE, CalledProcessError, run
from typing import List, Union

from archey.configuration import Configuration
from archey.entry import Entry


class Custom(Entry):
    """Custom entry gathering info based on configuration options"""

    def __new__(cls, *_, **kwargs):
        # Don't load this entry if a configuration file has too broad permissions.
        # We want to mitigate LPE attacks, as arbitrary commands could be run from a configuration
        # file under another user's control (with write permissions).
        geteuid = getattr(os, "geteuid", None)
        for config_path, stat_info in Configuration().get_config_files_info().items():
            if (
                stat_info.st_uid != 0 and geteuid is not None and stat_info.st_uid != geteuid()
            ) or stat_info.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
                logging.getLogger(cls.__module__).warning(
                    "Not loading %s entry as %s config file has too broad permissions (%s).",
                    cls.__name__,
                    config_path,
                    stat.filemode(stat_info.st_mode),
                )
                return None

        return super().__new__(cls, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        command: Union[str, List[str]]

        shell = self.options.get("shell", False)
        if shell:
            command = self.options["command"]
        else:
            command = self.options["command"]

        log_stderr = self.options.get("log_stderr", True)

        with suppress(CalledProcessError):
            proc = run(
                command,
                stdout=PIPE,
                stderr=PIPE if log_stderr else DEVNULL,
                shell=shell,
                check=self.options.get("check", True),
                universal_newlines=True,
            )
            if proc.stdout:
                self.value = proc.stdout.rstrip().splitlines()

            if log_stderr and proc.stderr:
                self._logger.warning("%s", proc.stderr.rstrip())

    def output(self, output) -> None:
        if not self.value:
            output.append(self.name, self._default_strings.get("not_detected"))
            return

        # Join the results only if `one_line` option is enabled.
        if self.options.get("one_line", True):
            output.append(self.name, ", ".join(self.value))
        else:
            for element in self.value:
                output.append(self.name, element)
