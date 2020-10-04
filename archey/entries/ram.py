"""RAM usage detection class"""

import re

from subprocess import check_output

from archey.colors import Colors
from archey.entry import Entry


class RAM(Entry):
    """
    First tries to use the `free` command to retrieve RAM usage.
    If not available, falls back on the parsing of `/proc/meminfo` file.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        used, total = self._get_used_total_values()
        if not total:
            return

        self.value = {
            'used': used,
            'total': total,
            'unit': 'MiB'
        }

    def _get_used_total_values(self):
        """
        Returns a tuple containing used and total RAM values.
        Tries a variety of methods, increasing compatibility for a wide range of systems.
        """
        try:
            return self._run_free_dash_m()
        except (IndexError, FileNotFoundError):
            pass

        try:
            return self._read_proc_meminfo()
        except (PermissionError, FileNotFoundError):
            pass

        return None, None

    @staticmethod
    def _run_free_dash_m():
        """Call `free -m` and parse its output to retrieve current used and total RAM"""
        memory_usage = ''.join(
            filter(
                re.compile('Mem').search,
                check_output(
                    ['free', '-m'],
                    env={'LANG': 'C'}, universal_newlines=True
                ).splitlines()
            )
        ).split()

        return float(memory_usage[2]), float(memory_usage[1])

    @staticmethod
    def _read_proc_meminfo():
        """Same behavior but by reading from `/proc/meminfo` directly"""
        with open('/proc/meminfo') as f_mem_info:
            mem_info_lines = f_mem_info.read().splitlines()

        # Store memory information into a dictionary.
        mem_info = {}
        for line in filter(None, mem_info_lines):
            key, value = line.split(':', maxsplit=1)
            mem_info[key] = float(value.strip(' kB')) / 1024

        total = mem_info['MemTotal']
        # Here, let's imitate Neofetch's behavior.
        # See <https://github.com/dylanaraps/neofetch/wiki/Frequently-Asked-Questions>.
        used = total + mem_info['Shmem'] - (
            mem_info['MemFree'] + mem_info['Cached']
            + mem_info['SReclaimable'] + mem_info['Buffers']
        )
        # Imitates what `free` does when the obtained value happens to be incorrect.
        # See <https://gitlab.com/procps-ng/procps/blob/master/proc/sysinfo.c#L790>.
        if used < 0:
            used = total - mem_info['MemFree']

        return used, total


    def output(self, output):
        """
        Adds the entry to `output` after pretty-formatting the RAM usage with color and units.
        """
        if not self.value:
            # Fall back on the default behavior if no RAM usage could be detected.
            super().output(output)
            return

        # DRY some constants
        used = self.value['used']
        total = self.value['total']
        unit = self.value['unit']

        # Based on the RAM percentage usage, select the corresponding level color.
        level_color = Colors.get_level_color(
            (used / total) * 100,
            self.options.get('warning_use_percent', 33.3),
            self.options.get('danger_use_percent', 66.7)
        )

        output.append(
            self.name,
            '{0}{1} {unit}{2} / {3} {unit}'.format(
                level_color,
                int(used),
                Colors.CLEAR,
                int(total),
                unit=unit
            )
        )
