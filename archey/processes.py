"""Simple class (acting as a singleton) to handle processes listing"""

import logging
import typing
from subprocess import PIPE, CalledProcessError, check_output

from archey.singleton import Singleton


class Processes(metaclass=Singleton):
    """At startup, instantiate this class to populate a list of running processes"""

    def __init__(self):
        self._processes: typing.List[str]

        try:
            ps_output = check_output(["ps", "-eo", "comm"], stderr=PIPE, universal_newlines=True)
        except FileNotFoundError:
            self._processes = []
            logging.warning("`procps` (or `procps-ng`) couldn't be found on your system.")
        except CalledProcessError as process_error:
            self._processes = []
            logging.warning(
                "This implementation of `ps` might not be supported : %s", process_error.stderr
            )
        else:
            # Discard first heading line here.
            self._processes = ps_output.splitlines()[1:]

    @property
    def list(self) -> tuple:
        """Simple getter to retrieve (am immutable copy of) the processes list"""
        return tuple(self._processes)

    @property
    def number(self) -> int:
        """Simple getter to retrieve the number of stored processes"""
        return len(self._processes)
