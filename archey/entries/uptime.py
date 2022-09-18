"""Uptime detection class"""

import re
import time
from contextlib import suppress
from datetime import timedelta
from subprocess import check_output

from archey.entry import Entry
from archey.exceptions import ArcheyException


class Uptime(Entry):
    """Returns a pretty-formatted string representing the host uptime"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        uptime_seconds = int(self._get_uptime_delta().total_seconds())

        days, uptime_seconds = divmod(uptime_seconds, 86400)
        hours, uptime_seconds = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(uptime_seconds, 60)

        self.value = {"days": days, "hours": hours, "minutes": minutes, "seconds": seconds}

    def _get_uptime_delta(self) -> timedelta:
        """
        Returns a `datetime.timedelta` instance containing the machine uptime.
        Tries a variety of methods, increasing compatibility for a wide range of systems.
        """
        # Try the /proc/uptime file
        try:
            return self._proc_file_uptime()
        except OSError:
            # Can't read /proc/uptime.
            # Not GNU/Linux ? Limited permissions ?
            pass

        # Try the python `time` module clocks
        try:
            return self._clock_uptime()
        except RuntimeError:
            # Probably Python <3.7, or not *NIX
            pass

        # FUTURE: Windows support could be added here with the `wmi` or `pywin32` module.

        # Fall back to the `uptime` command.
        return self._parse_uptime_cmd()

    @staticmethod
    def _proc_file_uptime() -> timedelta:
        """Tries to get uptime using the `/proc/uptime` file"""
        with open("/proc/uptime", encoding="ASCII") as f_uptime:
            return timedelta(seconds=float(f_uptime.read().split()[0]))

    @staticmethod
    def _clock_uptime() -> timedelta:
        """Tries to get uptime using the clocks from the Python `time` module"""
        # Try: Linux and BSD uptime clocks.
        for clock in ("CLOCK_BOOTTIME", "CLOCK_UPTIME"):
            with suppress(AttributeError):
                return timedelta(seconds=time.clock_gettime(getattr(time, clock)))

        # Probably Python <3.7, or just not one of the above OSes
        raise RuntimeError

    @staticmethod
    def _parse_uptime_cmd() -> timedelta:
        """Tries to get uptime by parsing the `uptime` command"""
        try:
            uptime_output = check_output("uptime", env={"LANG": "C"})
        except FileNotFoundError as error:
            raise ArcheyException("Couldn't find `uptime` command on this system.") from error

        # Unfortunately the output is not designed to be machine-readable...
        uptime_match = re.search(
            rb"""
            up\s+?             # match the `up` preceding the uptime (anchor the start of the regex)
            (?:                # non-capture group for days section.
               (?P<days>       # 'days' named capture group, captures the days digits.
                  \d+?
               )
               \s+?            # match whitespace,
               days?           #   'day' or 'days',
               [,\s]+?         #   then a comma (if present) followed by more whitespace.
            )?                 # match the days non-capture group 0 or 1 times.
            (?:                # non-capture group for hours & minutes section.
               (?:             # non-capture group for just hours section.
                  (?P<hours>   # 'hours' named capture group, captures the hours digits.
                     \d+?
                  )
                  (?:          # non-capture group for hours:minutes colon or 'hrs' text...
                     :         #   i.e. hours followed by either a single colon
                     |         #   OR
                     \s+?      #   1 or more whitespace chars non-greedily,
                     hrs?      #   followed by 'hr' or 'hrs'.
                  )
               )?              # match the hours non-capture group 0 or 1 times.
               (?:             # non-capture group for minutes section.
                  (?P<minutes> # 'minutes' named capture group, captures the minutes digits.
                     \d+?
                  )
                  (?:          # non-capture group for 'min' or 'mins' text.
                     \s+?      # match whitespace,
                     mins?     #   followed by 'min' or 'mins'.
                  )?           # match the text 0 or 1 times (0 times is for the hh:mm format case).
                  (?!          # negative lookahead group
                     \d+       #   this prevents matching seconds digits as minutes...
                     \s+?      #   since we only non-greedily match minutes digits earlier.
                     secs?     #   here's the part that matches the 'sec' or 'secs' text.
                  )            # the minutes group is discarded if this lookahead matches!
               )?              # match the minutes non-capture group 0 or 1 times.
            )?                 # match the entire hours & minutes non-capture group 0 or 1 times.
            (?:                # non-capture group for seconds.
               (?P<seconds>    # 'seconds' named capture group, captures the seconds digits.
                  \d+?
               )
               \s+?            # match whitespace,
               secs?           #  then 'sec' or 'secs'.
            )?                 # match the seconds non-capture group 0 or 1 times.
            [,\s]*?            # after the groups, match a comma and/or whitespace 0 or more times,
            \d+?               #   one or more digits for the user count,
            \s+?               #   whitespace between the user count and the text 'user',
            user               #   and the text 'user' (to anchor the end of the expression).
            """,
            uptime_output,
            re.VERBOSE,
        )
        if not uptime_match:
            raise ArcheyException("Couldn't parse `uptime` output, please open an issue.")

        # Only `days`, `hours`, `minutes` or `seconds` could have been captured.
        # `timedelta` directly accepts them as arguments.
        uptime_args = uptime_match.groupdict()
        return timedelta(
            days=int(uptime_args.get("days") or 0),
            hours=int(uptime_args.get("hours") or 0),
            minutes=int(uptime_args.get("minutes") or 0),
            seconds=int(uptime_args.get("seconds") or 0),
        )

    def output(self, output) -> None:
        """Adds the entry to `output` after pretty-formatting the uptime to a string."""
        days = self.value["days"]
        hours = self.value["hours"]
        minutes = self.value["minutes"]

        uptime = ""
        if days:
            uptime += str(days) + " day"
            if days > 1:
                uptime += "s"

            if hours or minutes:
                if bool(hours) != bool(minutes):
                    uptime += " and "
                else:
                    uptime += ", "

        if hours:
            uptime += str(hours) + " hour"
            if hours > 1:
                uptime += "s"

            if minutes:
                uptime += " and "

        if minutes:
            uptime += str(minutes) + " minute"
            if minutes > 1:
                uptime += "s"
        elif not days and not hours:
            uptime = "< 1 minute"

        output.append(self.name, uptime)
