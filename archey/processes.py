"""Simple class (acting as a singleton) to handle processes listing"""

import sys

from subprocess import check_output

from archey.singleton import Singleton


class Processes(metaclass=Singleton):
    """At startup, instantiate this class to populate a list of running processes"""
    def __init__(self):
        try:
            self._processes = check_output(
                ['ps', '-eo', 'comm'],
                universal_newlines=True
            ).splitlines()[1:]
        except FileNotFoundError:
            sys.exit("Please, install first `procps` (or `procps-ng`) on your system.")

    @property
    def list(self):
        """Simple getter to retrieve (am immutable copy of) the processes list"""
        return tuple(self._processes)

    @property
    def number(self):
        """Simple getter to retrieve the number of stored processes"""
        return len(self._processes)
