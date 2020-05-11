"""Simple class (acting as a singleton) to handle processes listing"""

import os
import sys

from subprocess import CalledProcessError, DEVNULL, check_output

from archey.singleton import Singleton


class Processes(metaclass=Singleton):
    """At startup, instantiate this class to populate a list of running processes"""
    def __init__(self):
        try:
            self._processes = check_output(
                [
                    'ps',
                    (('-u' + str(os.getuid())) if os.getuid() != 0 else '-ax'),
                    '-o', 'comm',
                    '--no-headers'
                ],
                universal_newlines=True, stderr=DEVNULL
            ).splitlines()
        except CalledProcessError:
            # The available `ps` implementation may not support passed parameters (hello BusyBox).
            # Let's fall-back on a much simpler approach.
            self._processes = check_output(
                ['ps', '-o', 'comm'],
                universal_newlines=True
            ).splitlines()[1:]
        except FileNotFoundError:
            sys.exit("Please, install first `procps` (or `procps-ng`) on your system.")

    def get(self):
        """Simple getter to retrieve the processes list"""
        return self._processes
