"""Disk usage detection class"""

from bisect import bisect
from subprocess import check_output

from archey.constants import COLOR_DICT
from archey.configuration import Configuration


class Disk:
    """Uses `df` command output to compute the total disk usage across devices"""
    def __init__(self):
        # This dictionary will store values obtained from sub-processes calls.
        self._usage = {
            'used': 0,
            'total': 0
        }

        # Fetch the user-defined RAM limits from configuration.
        disk_limits = Configuration().get('limits')['disk']

        self._run_df_usage()

        # Based on the disk percentage usage, select the corresponding threshold color.
        color_selector = bisect(
            [disk_limits['warning'], disk_limits['danger']],
            (self._usage['used'] / self._usage['total']) * 100
        )

        self.value = '{0}{1} GB{2} / {3} GB'.format(
            COLOR_DICT['sensors'][color_selector],
            self._usage['used'],
            COLOR_DICT['clear'],
            self._usage['total']
        )

    def _run_df_usage(self):
        df_output = check_output(
            [
                'df', '-l', '-B', 'GB', '--total',
                '-t', 'ext4', '-t', 'ext3', '-t', 'ext2',
                '-t', 'reiserfs', '-t', 'jfs', '-t', 'zfs',
                '-t', 'ntfs', '-t', 'fat32', '-t', 'fuseblk',
                '-t', 'xfs', '-t', 'simfs', '-t', 'lxfs'
            ],
            env={'LANG': 'C'}, universal_newlines=True
        ).splitlines()[-1].split()

        self._usage['used'] += int(df_output[2].rstrip('GB'))
        self._usage['total'] += int(df_output[1].rstrip('GB'))
