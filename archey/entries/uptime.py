"""Uptime detection class"""


import re
import time
import sys
from datetime import timedelta
from subprocess import check_output, CalledProcessError

from archey.entry import Entry


class Uptime(Entry):
    """Returns a pretty-formatted string representing the host uptime"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._uptime = None
        self._get_uptime()

        self._fuptime = int(self._uptime.total_seconds())

        day, self._fuptime = divmod(self._fuptime, 86400)
        hour, self._fuptime = divmod(self._fuptime, 3600)
        minute = self._fuptime // 60

        uptime = ''
        if day:
            uptime += str(day) + ' day'
            if day > 1:
                uptime += 's'

            if hour or minute:
                if bool(hour) != bool(minute):
                    uptime += ' and '

                else:
                    uptime += ', '

        if hour:
            uptime += str(hour) + ' hour'
            if hour > 1:
                uptime += 's'

            if minute:
                uptime += ' and '

        if minute:
            uptime += str(minute) + ' minute'
            if minute > 1:
                uptime += 's'

        else:
            if not day and not hour:
                uptime = '< 1 minute'

        self.value = uptime

    def _get_uptime(self):
        """Sets `self._uptime` trying a variety of methods"""
        # Try the /proc/uptime file
        try:
            self._proc_file_uptime()
            return
        except (PermissionError, FileNotFoundError):
            # Can't read /proc/uptime, so not Linux or limited permissions.
            pass

        # Try the python `time` module clocks
        try:
            self._clock_uptime()
            return
        except RuntimeError:
            # Probably Python <3.7, or not *NIX
            pass

        # FUTURE: Windows support could be added here with the `wmi` or `pywin32` module.

        # Fall back to the `uptime` command
        self._uptime_cmd()


    def _proc_file_uptime(self):
        """Tries to get uptime using the `/proc/uptime` file"""
        with open('/proc/uptime') as file:
            self._uptime = timedelta(
                seconds=int(file.read().split('.')[0])
            )

    def _clock_uptime(self):
        """Tries to get uptime using the clocks from the Python `time` module"""
        # Try: Linux uptime clock, macOS uptime clock, BSD uptime clock.
        for clock in ['CLOCK_BOOTTIME', 'CLOCK_UPTIME_RAW', 'CLOCK_UPTIME']:
            try:
                self._uptime = timedelta(
                    seconds=time.clock_gettime(getattr(time, clock))
                )
                return
            except AttributeError:
                pass

        # Probably Python <3.7, or just not one of the above OSes
        raise RuntimeError

    def _uptime_cmd(self):
        """Tries to get uptime by parsing the `uptime` command"""
        try:
            uptime_output = check_output('uptime')
        except (CalledProcessError, FileNotFoundError):
            # No `uptime` command. Since `procps` is a dependency (which provides `uptime`)
            # we can just exit here.
            sys.exit('Required dependency `procps` (or `procps-ng`) missing. Please install.')

        # Unfortunately the output is not designed to be machine-readable...
        uptime_match = re.search(
            r"""
            up\s+?             # match the `up` preceding the uptime, anchors the start of the regex
            (?:                # non-capture group for days
               (?P<days>       # 'days' named capture group, captures the days digits
                  \d+?
               )
               \s+?            # match whitespace,
               day[s]?         # 'day' or 'days',
               [,\s]+?         # then a comma (if present) followed by more whitespace
            )?                 # match the days non-capture group 0 or 1 times
            (?:                # non-capture group for hours & minutes
               (?:             # non-capture group for just hours
                  (?P<hours>   # 'hours' named capture group, captures the hours digits
                     \d+?
                  )
                  (?:          # non-capture group for hours:minutes colon or 'hrs' text
                     :         # i.e. hours followed by either a single colon
                     |         # OR
                     \s+?hrs   # one or more whitespace chars non-greedily, followed by 'hrs'
                  )
               )?              # match the hours non-capture group 0 or 1 times
               (?:             # non-capture group for minutes
                  (?P<minutes> # 'minutes' named capture group, captures the minutes digits
                     \d+?
                  )
                  (?:          # non-capture group for 'min' or 'mins' text
                     \s+?      # match whitespace,
                     min[s]?   # followed by 'min' or 'mins
                  )?           # match the 'mins' text non-capture group 0 or 1 times,
               )?              # the minutes non-capture group 0 or 1 times
            )?                 # and the entire hours & minutes non-capture group 0 or 1 times
            [,\s]*?            # followed by a comma and/or whitespace,
            \d+?               # some digits for the user count,
            \s+?               # whitespace between the user count and the text 'user',
            user               # and the text 'user' - this is to anchor the end of the expression.
            """,
            uptime_output,
            re.VERBOSE
        )

        times_dict = uptime_match.groupdict()
        timedelta_args = {
            'days': 0,
            'minutes': 0,
            'hours': 0
        }
        for time_unit, value in times_dict.items():
            if value is not None:
                timedelta_args[time_unit] = int(value)

        self._uptime = timedelta(**timedelta_args)
