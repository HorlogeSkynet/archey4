"""
Output class file.
It supports entries lazy-insertion, logo detection, and final printing.
"""

import logging
import os
import sys
from bisect import insort
from concurrent.futures import Future, wait
from shutil import get_terminal_size
from textwrap import TextWrapper
from typing import cast

from archey.api import API
from archey.colors import ANSI_ECMA_REGEXP, Colors, CursorPosition, Style, TerminalMovements
from archey.configuration import Configuration
from archey.distributions import Distributions
from archey.entry import Entry
from archey.exceptions import ArcheyException
from archey.logos import get_logo_width, lazy_load_logo_module


class Output:
    """
    This is the object handling output entries populating.
    It also handles the logo choice based on some system detections.
    """

    __LOGO_RIGHT_PADDING = "   "

    def __init__(self, **kwargs):
        self.configuration = Configuration()
        self._logger = logging.getLogger(self.__module__)

        # Fetches passed arguments.
        self._format_to_json = kwargs.get("format_to_json")
        preferred_logo_style = (
            kwargs.get("preferred_logo_style") or self.configuration.get("logo_style") or ""
        ).upper()

        try:
            # If set, force the distribution to `preferred_distribution` argument.
            self._distribution = Distributions(kwargs.get("preferred_distribution"))
        except ValueError:
            # If not (or unknown), run distribution detection.
            self._distribution = Distributions.get_local()

        # Retrieve distribution's logo module before copying and DRY-ing its attributes.
        logo_module = lazy_load_logo_module(self._distribution.value)

        # If set and available, fetch an alternative logo style from module.
        if preferred_logo_style and hasattr(logo_module, f"LOGO_{preferred_logo_style}"):
            self._logo = getattr(logo_module, f"LOGO_{preferred_logo_style}").copy()
            self._colors = getattr(logo_module, f"COLORS_{preferred_logo_style}").copy()
        else:
            self._logo, self._colors = logo_module.LOGO.copy(), logo_module.COLORS.copy()

        # Compute the effective logo "width" and "height" from the loaded ASCII art.
        self.logo_width = get_logo_width(self._logo, len(self._colors)) + len(
            self.__LOGO_RIGHT_PADDING
        )
        self.logo_height = len(self._logo)
        self.output_exceeded_term_flag = False

        # If `os-release`'s `ANSI_COLOR` option is set, honor it.
        ansi_color = Distributions.get_ansi_color()
        if ansi_color and self.configuration.get("honor_ansi_color"):
            # Replace each Archey integrated colors by `ANSI_COLOR`.
            self._colors = len(self._colors) * [Style.escape_code_from_attrs(ansi_color)]

        entries_color = self.configuration.get("entries_color")
        self._entries_color = (
            Style.escape_code_from_attrs(entries_color) if entries_color else self._colors[0]
        )

        # Each entry will be added to this list
        self._entries = []
        # Each entry `Future` will be added to this set
        self._entry_futures = set()

    def add_entry(self, module: Entry) -> None:
        """Append an entry to the list of entries to output"""
        self._entries.append(module)

    def add_entry_concurrent(self, entry_future: Future):
        """Append an entry to the list of future entries to output"""
        self._entry_futures.add(entry_future)

    def entry_future_done_callback(self, entry_future: Future):
        """Add entry to entries list once it has instantiated"""
        entry = entry_future.result()
        self._entries.append(entry)
        if not self._format_to_json and self.configuration.get("output_concurrency"):
            self._output_update()

    def begin_output(self) -> None:
        """
        Main method for `Output` to begin outputting entries.
        Used to enable to output of logo and finished entries while others are still being
        instantiated.
        """
        if not self._format_to_json and self.configuration.get("output_concurrency"):
            self._output_logo_standalone(0, 0)  # assume no padding is necessary to begin with

    def finish_output(self) -> None:
        """
        Method to end `Output` output, used to stop output as all entries are finished.
        The API requires completion of all entries before output begins, so it's only interacted
        with here.
        """
        if self._format_to_json:
            wait(self._entry_futures)
            self._output_json()
        elif self.configuration.get("output_concurrency"):
            print(CursorPosition.move(TerminalMovements.DOWN, self.logo_height - 1))
            if self.output_exceeded_term_flag:
                self._logger.warning("The output was cut off due to the terminal height.")
        else:
            wait(self._entry_futures)
            self._output_legacy()

    def _output_json(self) -> None:
        """
        Finally outputs entries data to JSON format.
        See `archey.api` for further documentation.
        """
        print(API(self._entries).json_serialization(indent=cast(int, self._format_to_json) - 1))

    def _output_logo_standalone(self, padding_top: int, padding_bottom: int) -> None:
        # Safely mutable local copy
        logo = self._logo.copy()

        # Add padding to the top & bottom of the logo for centering
        colored_empty_line = [str(self._colors[0]) + " " * self.logo_width]
        logo[0:0] = colored_empty_line * padding_top
        logo.extend(colored_empty_line * padding_bottom)

        avail_term_height = get_terminal_size().lines - 1  # - 1 due to ending newline
        self.logo_height = min(len(logo), avail_term_height)

        # If the output was cut-off then set a flag that it happened
        if len(logo) != self.logo_height:
            self.output_exceeded_term_flag = True

        logo_output = os.linesep.join(
            [f"{logo_part}{self.__LOGO_RIGHT_PADDING}" for logo_part in logo][-avail_term_height:]
        )

        try:
            # Print the logo (the default `end` adds a trailing newline)
            print(logo_output.format(c=self._colors) + str(Colors.CLEAR))

            # Move the cursor to the top-left
            print(CursorPosition.move(TerminalMovements.PREV_LINE, self.logo_height), end="")

        except UnicodeError as unicode_error:
            raise ArcheyException(
                """\
Your locale or TTY does not seem to support UTF-8 encoding.
Please disable Unicode within your configuration file.\
"""
            ) from unicode_error

    def _output_update(self) -> None:
        # Build a dict of entries
        entries_dict = {}
        for entry in self._entries:
            entries_dict[entry.index] = entry

        # List of all entry lines
        results = []
        # The total number of futures we have is the number of entries we have.
        # Assume one blank line for each incomplete one, inserting available entries.
        for idx in range(len(self._entry_futures)):
            try:
                # Add entry's lines to results
                for entry_line in entries_dict[idx].pretty_value:
                    results.append(
                        f"{self._entries_color}{entry_line[0]}:{Colors.CLEAR} {entry_line[1]}"
                    )
            except KeyError:
                # Entry not available yet, add a blank line
                results.append("")

        # Let's center the entries and the logo vertically (handles odd numbers)
        logo_padding_top = 0
        logo_padding_bottom = 0
        height_diff = len(self._logo) - len(results)
        if height_diff >= 0:
            results[0:0] = [""] * (height_diff // 2)
            results.extend([""] * (len(self._logo) - len(results)))
        else:
            logo_padding_top = -height_diff // 2
            logo_padding_bottom = len(results) - (len(self._logo) + logo_padding_top)

        # Redraw the logo
        self._output_logo_standalone(logo_padding_top, logo_padding_bottom)

        # When writing to a pipe (for instance), prevent `TextWrapper` from truncating output.
        if not sys.stdout.isatty():
            text_width = cast(int, float("inf"))
        else:
            text_width = get_terminal_size().columns - self.logo_width

        for idx, result in enumerate(results):
            if isinstance(result, tuple):
                results[idx] = result[1]
        avail_term_height = get_terminal_size().lines - 1  # - 1 due to ending newline
        results = self._wrap_text_list_to_width(text_width, results)[-avail_term_height:]
        # todo: wrap text *and* logo (possibly warn if wrapping out the text entirely?)

        try:
            for raw_line in results:
                output_line = raw_line.format(c=self._colors) + str(Colors.CLEAR)
                # Move the cursor to the end of the logo on this line
                print(CursorPosition.move(TerminalMovements.FORWARD, self.logo_width), end="")
                # Clear from this position to the end of the line
                print(CursorPosition.move(TerminalMovements.ERASE_LINE), end="")
                # Print the output
                print(output_line, end="")
                # Move the cursor down (safe, as the logo print has already made the new lines)
                print(CursorPosition.move(TerminalMovements.NEXT_LINE, 1), end="")

            # Move the cursor to the top-left corner
            height = max(len(results), self.logo_height)
            print(CursorPosition.move(TerminalMovements.PREV_LINE, height), end="")

        except UnicodeError as unicode_error:
            raise ArcheyException(
                """\
            Your locale or TTY does not seem to support UTF-8 encoding.
            Please disable Unicode within your configuration file.\
            """
            ) from unicode_error

    @staticmethod
    def _wrap_text_list_to_width(width: int, text: list[str]) -> list[str]:
        """
        Wraps the list of `text` to the width `width` using `TextWrapper`, including handling ANSI
        color escape codes.
        """
        text_wrapper = TextWrapper(
            width=width,
            expand_tabs=False,
            replace_whitespace=False,
            drop_whitespace=False,
            break_on_hyphens=False,
            max_lines=1,
            placeholder="...",
        )
        placeholder_length = len(text_wrapper.placeholder)
        results = []

        for line in text:
            # We have to remove any ANSI color, or the result would be skewed.
            wrapped_line = text_wrapper.fill(Style.remove_colors(line))
            placeholder_end_offset = (
                placeholder_length if wrapped_line.endswith(text_wrapper.placeholder) else 0
            )

            # By using previous positions, re-inserts ANSI colors back in the wrapped string.
            for color_match in ANSI_ECMA_REGEXP.finditer(line):
                match_index = color_match.start()
                # Only re-insert before the wrapping placeholder is reached
                if match_index <= len(wrapped_line) - placeholder_end_offset:
                    wrapped_line = (
                        wrapped_line[:match_index]
                        + color_match.group()
                        + wrapped_line[match_index:]
                    )

            # Add a color reset character before the placeholder (if one was inserted).
            # Rationale : We cannot set `Colors.CLEAR` in the placeholder as it would skew the
            # `TextWrapper` internals.
            if placeholder_end_offset:
                wrapped_line = (
                    wrapped_line[:-placeholder_length]
                    + str(Colors.CLEAR)
                    + wrapped_line[-placeholder_length:]
                )

            results.append(wrapped_line)

        return results

    def _output_legacy(self) -> None:
        """
        Render the output entries all at once (legacy method).
        It handles text centering additionally to value and colors replacing.
        """
        # List to hold entry results
        results = []
        # Iterate through the entries and get their content.
        for entry in self._entries:
            for entry_line in entry.pretty_value:
                results.append(
                    f"{self._entries_color}{entry_line[0]}:{Colors.CLEAR} {entry_line[1]}"
                )

        # Let's center the entries and the logo vertically (handles odd numbers)
        height_diff = len(self._logo) - len(results)
        if height_diff >= 0:
            results[0:0] = [""] * (height_diff // 2)
            results.extend([""] * (len(self._logo) - len(results)))
        else:
            colored_empty_line = [str(self._colors[0]) + " " * self.logo_width]
            self._logo[0:0] = colored_empty_line * (-height_diff // 2)
            self._logo.extend(colored_empty_line * (len(results) - len(self._logo)))

        # When writing to a pipe (for instance), prevent `TextWrapper` from truncating output.
        if not sys.stdout.isatty():
            text_width = cast(int, float("inf"))
        else:
            text_width = (
                get_terminal_size().columns - self.logo_width - len(self.__LOGO_RIGHT_PADDING)
            )

        results = self._wrap_text_list_to_width(text_width, results)

        # Merge entry results to the distribution logo.
        logo_with_entries = os.linesep.join(
            [
                f"{logo_part}{self.__LOGO_RIGHT_PADDING}{entry_part}"
                for logo_part, entry_part in zip(self._logo, results)
            ]
        )

        try:
            print(logo_with_entries.format(c=self._colors) + str(Colors.CLEAR))
        except UnicodeError as unicode_error:
            raise ArcheyException(
                """\
Your locale or TTY does not seem to support UTF-8 encoding.
Please disable Unicode within your configuration file.\
"""
            ) from unicode_error
