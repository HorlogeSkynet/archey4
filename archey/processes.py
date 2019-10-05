"""Simple class (acting as a singleton) to handle processes listing"""

import os
import sys

from subprocess import check_output

from archey.singleton import Singleton


class Processes(metaclass=Singleton):
    """At startup, instantiate this class to populate a list of running processes"""
    def __init__(self):
        try:
            self.processes = check_output(
                ['ps', '-u' + str(os.getuid()) if os.getuid() != 0 else '-ax',
                 '-o', 'comm', '--no-headers'], universal_newlines=True
            ).splitlines()

        except FileNotFoundError:
            print('Please, install first `procps` on your distribution.',
                  file=sys.stderr)
            sys.exit(1)

    def get(self):
        """Simple getter to retrieve the processes list"""
        return self.processes
