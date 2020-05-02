"""
Output class file.
It supports entries lazy-insertion, logo detection, and final printing.
"""

import os
import re

from subprocess import check_output
from shutil import get_terminal_size

import sys

import distro

from archey.constants import COLOR_DICT, LOGOS_DICT, Colors
from archey.configuration import Configuration
from archey.distributions import Distributions
from archey.logos import get_logo_width


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

        # Each entry will be added to this list
        self._entries = []
        # Each class output will be added in the list below afterwards
        self._results = []

    def add_entry(self, module):
        """Append an entry to the list of entries to output"""
        self._entries.append(module)

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
        First we get entries to add their outputs to the results.
        It then handles text centering additionally to value and colors replacing.
        """
        # Iterate through the entries and run their output method to add their content.
        for entry in self._entries:
            entry.output(self)

        # Let's copy the logo (so we don't modify the constant!)
        logo = LOGOS_DICT[self._distribution].copy()
        logo_width = get_logo_width(logo, len(self._colors_palette))

        # Let's center the entries and the logo (handles odd numbers)
        height_diff = len(logo) - len(self._results)
        if height_diff >= 0:
            self._results[0:0] = [''] * (height_diff // 2)
            self._results.extend([''] * (len(logo) - len(self._results)))
        else:
            colored_empty_line = [str(self._colors_palette[0]) + ' ' * logo_width]
            logo[0:0] = colored_empty_line * (-height_diff // 2)
            logo.extend(colored_empty_line * (len(self._results) - len(logo)))

        entry_max_width = get_terminal_size().columns - logo_width

        wrapped_entries = []
        ansi_color_re = re.compile(r'\x1b\[\d+?;?\d*?m')
        for entry in self._results:
            # Remove the entries' color control codes, so we can wrap them
            entry_no_color = ansi_color_re.sub('', entry)

            if len(entry_no_color) > entry_max_width:
                extra_width = len(entry_no_color) - entry_max_width
                wrapped_entry = entry_no_color[:-(extra_width + 3)] + '...'
                # Naively add all of the colour control codes back into position
                for color_code_match in ansi_color_re.finditer(entry):
                    match_idx = color_code_match.start()
                    # Subtracting the '...'
                    if match_idx < (len(wrapped_entry) - 3):
                        wrapped_entry = (
                            wrapped_entry[:match_idx]
                            + color_code_match.group()
                            + wrapped_entry[match_idx:]
                        )

                # Add a colour reset before the '...' in case we still have a colour applied
                wrapped_entry = (
                    wrapped_entry[:-3]
                    + str(Colors.CLEAR)
                    + wrapped_entry[-3:]
                )
                wrapped_entries.append(wrapped_entry)

            else:
                wrapped_entries.append(entry)

        # Append entry results to our logo
        logo_with_entries = os.linesep.join([
            logo_part + entry_part
            for logo_part, entry_part
            in zip(logo, wrapped_entries)
        ])

        try:
            print(
                logo_with_entries.format(
                    c=self._colors_palette
                ) + str(Colors.CLEAR)
            )
        except UnicodeError:
            print(
                'Your locale or TTY does not seem to support UTF8 encoding.\n'
                'Please disable Unicode within your configuration file.',
                file=sys.stderr
            )
