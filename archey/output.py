"""
Output class file.
It supports entries lazy-insertion, logo detection, and final printing.
"""

from textwrap import TextWrapper
from shutil import get_terminal_size

import os
import sys

from archey.api import API
from archey.colors import ANSI_ECMA_REGEXP, Colors
from archey.constants import COLORS_DICT, LOGOS_DICT
from archey.configuration import Configuration
from archey.distributions import Distributions
from archey.logos import get_logo_width


class Output:
    """
    This is the object handling output entries populating.
    It also handles the logo choice based on some system detections.
    """
    def __init__(self, **kwargs):
        # Fetches passed arguments.
        self._format_to_json = kwargs.get('format_to_json')

        try:
            # If set, force the distribution to `preferred_distribution` argument.
            self._distribution = Distributions(kwargs.get('preferred_distribution'))
        except ValueError:
            # If not (or unknown), run distribution detection.
            self._distribution = Distributions.run_detection()

        # Fetch the colors palette related to this distribution.
        self._colors_palette = COLORS_DICT[self._distribution]

        # If `os-release`'s `ANSI_COLOR` option is set, honor it.
        ansi_color = Distributions.get_ansi_color()
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
        Main `Output`'s `output` method.
        First we get entries to add their outputs to the results and then
        calls specific `output` methods based (for instance) on preferred format.
        """
        if self._format_to_json:
            self._output_json()
        else:
            # Iterate through the entries and run their output method to add their content.
            for entry in self._entries:
                entry.output(self)
            self._output_text()

    def _output_json(self):
        """
        Finally outputs entries data to JSON format.
        See `archey.api.JSONAPI` for further documentation.
        """
        print(
            API(self._entries).json_serialization(
                indent=(self._format_to_json - 1)
            )
        )

    def _output_text(self):
        """
        Finally render the output entries.
        It handles text centering additionally to value and colors replacing.
        """
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

        text_wrapper = TextWrapper(
            width=(get_terminal_size().columns - logo_width),
            expand_tabs=False,
            replace_whitespace=False,
            drop_whitespace=False,
            break_on_hyphens=False,
            max_lines=1,
            placeholder='...'
        )
        placeholder_length = len(text_wrapper.placeholder)

        # Using `TextWrapper`, shortens each entry to remove any line overlapping
        for i, entry in enumerate(self._results):
            # Shortens the entry according to the terminal width.
            # We have to remove any ANSI color, or the result would be skewed.
            wrapped_entry = text_wrapper.fill(Colors.remove_colors(entry))
            placeholder_offset = (
                placeholder_length if wrapped_entry.endswith(text_wrapper.placeholder) else 0
            )

            # By using previous positions, re-inserts ANSI colors back in the wrapped string.
            for color_match in ANSI_ECMA_REGEXP.finditer(entry):
                match_index = color_match.start()
                if match_index <= len(wrapped_entry) - placeholder_offset:
                    wrapped_entry = (wrapped_entry[:match_index]
                                     + color_match.group()
                                     + wrapped_entry[match_index:])

            # Add a color reset character before the placeholder (if any).
            # Rationale :
            # We cannot set `Colors.CLEAR` in the placeholder as it would skew its internals.
            if placeholder_offset:
                wrapped_entry = (wrapped_entry[:-placeholder_length]
                                 + str(Colors.CLEAR)
                                 + wrapped_entry[-placeholder_length:])

            self._results[i] = wrapped_entry

        # Merge entry results to the distribution logo.
        logo_with_entries = os.linesep.join([
            logo_part + entry_part
            for logo_part, entry_part in zip(logo, self._results)
        ])

        try:
            print(
                logo_with_entries.format(
                    c=self._colors_palette
                ) + str(Colors.CLEAR)
            )
        except UnicodeError:
            sys.exit(
                """\
Your locale or TTY does not seem to support UTF-8 encoding.
Please disable Unicode within your configuration file.\
""")
