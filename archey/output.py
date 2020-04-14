"""
Output class file.
It supports entries lazy-insertion, logo detection, and final printing.
"""

import re
import sys
from subprocess import check_output

import distro

from archey.distributions import Distributions
from archey.constants import COLOR_DICT, LOGOS_DICT


class Output:
    """
    This is the object handling output entries populating.
    It also handles the logo choice based on some system detections.
    """
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
                        re.IGNORECASE):
                    self.distribution = distribution
                    break

            else:
                self.distribution = Distributions.LINUX

        # Modules will be added to this list in `attach`.
        self.entries = []
        # Output will be added in the list below afterwards
        self.results = []

    def attach(self, module):
        """Append a module to the list of modules"""
        self.entries.append(module)

    def append(self, module_name, module_value):
        """Append a pre-formatted entry to the final output content"""
        self.results.append(
            '{0}{1}:{2} {3}'.format(
                COLOR_DICT[self.distribution][1],
                module_name,
                COLOR_DICT['clear'],
                module_value
            )
        )

    def output(self):
        """
        Get all entries to append their output then render the output entries.
        It handles text centering, and value and color replacement.
        """
        # For now, append module results by iteration.
        for module in self.entries:
            module.output(self)
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
