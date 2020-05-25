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

    def get(self):
        """Simple getter to retrieve the processes list"""
        return self._processes
