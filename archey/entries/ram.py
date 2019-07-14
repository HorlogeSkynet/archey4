"""RAM usage detection class"""

import re

from subprocess import check_output

from archey.constants import COLOR_DICT


class RAM:
    """
    First tries to use the `free` command to retrieve RAM usage.
    If not available, falls back on the parsing of `/proc/meminfo` file.
    """
    def __init__(self):
        try:
            ram = ''.join(
                filter(
                    re.compile('Mem').search,
                    check_output(
                        ['free', '-m'],
                        env={'LANG': 'C'}, universal_newlines=True
                    ).splitlines()
                )
            ).split()
            used = float(ram[2])
            total = float(ram[1])

        except (IndexError, FileNotFoundError):
            # An in-digest one-liner to retrieve memory info into a dictionary
            with open('/proc/meminfo') as file:
                ram = {
                    i.split(':')[0]: float(i.split(':')[1].strip(' kB')) / 1024
                    for i in filter(None, file.read().splitlines())
                }

            total = ram['MemTotal']
            # Here, let's imitate the `free` command behavior
            # (https://gitlab.com/procps-ng/procps/blob/master/proc/sysinfo.c#L787)
            used = total - (ram['MemFree'] + ram['Cached'] + ram['Buffers'])
            if used < 0:
                used += ram['Cached'] + ram['Buffers']

        self.value = '{0}{1} MB{2} / {3} MB'.format(
            COLOR_DICT['sensors'][int(((used / total) * 100) // 33.34)],
            int(used),
            COLOR_DICT['clear'],
            int(total)
        )
