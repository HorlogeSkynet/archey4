"""
Output class file.
It supports entries lazy-insertion, logo detection, and final printing.
"""

import re
import sys
from subprocess import check_output

import distro

from archey.distributions import Distributions
from archey.constants import COLOR_DICT, LOGOS_DICT, Colors


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

        # Fetch the colors palette related to this distribution.
        self.colors_palette = COLOR_DICT[self.distribution]

        # Each class output will be added in the list below afterwards
        self.results = []

    def append(self, key, value):
        """Append a pre-formatted entry to the final output content"""
        self.results.append(
            '{color}{key}:{clear} {value}'.format(
                color=self.colors_palette[0],
                key=key,
                clear=Colors.CLEAR,
                value=value
            )
        )

    def output(self):
        """
        Finally render the output entries.
        It handles text centering additionally to value and colors replacing.
        """
        # Let's center the entries according to the logo (handles odd numbers)
        self.results[0:0] = [''] * ((18 - len(self.results)) // 2)
        self.results.extend([''] * (18 - len(self.results)))

        try:
            print(
                LOGOS_DICT[self.distribution].format(
                    c=self.colors_palette,
                    r=self.results
                ) + str(Colors.CLEAR)
            )
        except UnicodeError:
            print(
                'Your locale or TTY does not seem to support UTF8 encoding.\n'
                'Please disable Unicode within your configuration file.',
                file=sys.stderr
            )
