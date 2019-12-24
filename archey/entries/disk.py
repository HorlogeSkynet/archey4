"""Disk usage detection class"""

import re

from bisect import bisect
from subprocess import check_output

from archey.constants import COLOR_DICT
from archey.configuration import Configuration


class Disk:
    """Uses `df` command output to compute the total disk usage across devices"""
    def __init__(self):
        # Fetch the user-defined RAM limits from configuration.
        disk_limits = Configuration().get('limits')['disk']

        total = re.sub(
            ',', '.',
            check_output(
                [
                    'df', '-Tlh', '-B', 'GB', '--total',
                    '-t', 'ext4', '-t', 'ext3', '-t', 'ext2',
                    '-t', 'reiserfs', '-t', 'jfs', '-t', 'zfs',
                    '-t', 'ntfs', '-t', 'fat32', '-t', 'btrfs',
                    '-t', 'fuseblk', '-t', 'xfs', '-t', 'simfs',
                    '-t', 'tmpfs', '-t', 'lxfs'
                ], universal_newlines=True
            ).splitlines()[-1]
        ).split()

        # Based on the disk percentage usage, select the corresponding threshold color.
        color_selector = bisect(
            [disk_limits['warning'], disk_limits['danger']],
            float(total[5][:-1])
        )

        self.value = '{0}{1}{2} / {3}'.format(
            COLOR_DICT['sensors'][color_selector],
            re.sub('GB', ' GB', total[3]),
            COLOR_DICT['clear'],
            re.sub('GB', ' GB', total[2])
        )
