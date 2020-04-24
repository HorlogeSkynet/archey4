"""
Output class file.
It supports entries lazy-insertion, logo detection, and final printing.
"""

import sys
from subprocess import check_output

import distro

from archey.constants import COLOR_DICT, LOGOS_DICT, Colors
from archey.configuration import Configuration
from archey.distributions import Distributions


class Output:
    """
    This is the object handling output entries populating.
    It also handles the logo choice based on some system detections.
    """
    def __init__(self):
        # First we check whether the Kernel has been compiled as a WSL.
        if 'microsoft' in check_output(['uname', '-r'], universal_newlines=True).lower():
            self._distribution = Distributions.WINDOWS
        else:
            try:
                self._distribution = Distributions(distro.id())
            except ValueError:
                # See <https://www.freedesktop.org/software/systemd/man/os-release.html#ID_LIKE=>.
                for distro_like in distro.like().split(' '):
                    try:
                        self._distribution = Distributions(distro_like)
                    except ValueError:
                        continue
                    break
                else:
                    # Well, we didn't match anything so let's fall-back to default `Linux`.
                    self._distribution = Distributions.LINUX

        # Fetch the colors palette related to this distribution.
        self._colors_palette = COLOR_DICT[self._distribution]

        # If `os-release`'s `ANSI_COLOR` option is set, honor it.
        # See <https://www.freedesktop.org/software/systemd/man/os-release.html#ANSI_COLOR=>.
        ansi_color = distro.os_release_attr('ansi_color')
        if ansi_color and Configuration().get('colors_palette')['honor_ansi_color']:
            # Replace each Archey integrated colors by `ANSI_COLOR`.
            self._colors_palette = len(self._colors_palette) * \
                [Colors.escape_code_from_attrs(ansi_color)]

        # Each class output will be added in the list below afterwards
        self._results = []

    def append(self, key, value):
        """Append a pre-formatted entry to the final output content"""
        self._results.append(
            '{color}{key}:{clear} {value}'.format(
                color=self._colors_palette[0],
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
        self._results[0:0] = [''] * ((18 - len(self._results)) // 2)
        self._results.extend([''] * (18 - len(self._results)))

        try:
            print(
                LOGOS_DICT[self._distribution].format(
                    c=self._colors_palette,
                    r=self._results
                ) + str(Colors.CLEAR)
            )
        except UnicodeError:
            print(
                'Your locale or TTY does not seem to support UTF8 encoding.\n'
                'Please disable Unicode within your configuration file.',
                file=sys.stderr
            )
