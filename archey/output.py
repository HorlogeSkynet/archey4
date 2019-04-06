import re
import sys
import distro
from subprocess import check_output

from distributions import Distributions
from constants import LOGOS_DICT, COLOR_DICT

# ----------- Output handler ---------- #


class Output:
    def __init__(self):
        # First we check whether the Kernel has been compiled as a WSL.
        if re.search(
                'Microsoft',
                check_output(['uname', '-r'], universal_newlines=True)):
            self.distribution = Distributions.WINDOWS

        else:
            distribution_id = distro.id()

            for distribution in Distributions:
                if re.fullmatch(
                       distribution.value,
                       distribution_id,
                        re.IGNORECASE
                   ):
                    self.distribution = distribution
                    break

            else:
                self.distribution = Distributions.LINUX

        # Each class output will be added in the list below afterwards
        self.results = []

    def append(self, key, value):
        self.results.append(
            '{0}{1}:{2} {3}'.format(
                COLOR_DICT[self.distribution][1],
                key,
                COLOR_DICT['clear'],
                value
            )
        )

    def output(self):
        # Let's center the entries according to the logo (handles odd numbers)
        self.results[0:0] = [''] * ((18 - len(self.results)) // 2)
        self.results.extend([''] * (18 - len(self.results)))

        try:
            print(
                LOGOS_DICT[self.distribution].format(
                    c=COLOR_DICT[self.distribution],
                    r=self.results
                ) + COLOR_DICT['clear']
            )

        except UnicodeError:
            print(
                'Your locale or TTY seems not supporting UTF8 encoding.\n'
                'Please disable Unicode within your configuration file.',
                file=sys.stderr
            )

