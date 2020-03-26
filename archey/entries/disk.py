"""Disk usage detection class"""

from bisect import bisect

import re

from subprocess import check_output, CalledProcessError

from archey.constants import COLOR_DICT
from archey.configuration import Configuration


class Disk:
    """Uses `df` command output to compute the total disk usage across devices"""
    def __init__(self):
        # This dictionary will store values obtained from sub-processes calls.
        self._usage = {
            'used': 0.0,
            'total': 0.0
        }

        # Fetch the user-defined RAM limits from configuration.
        disk_limits = Configuration().get('limits')['disk']

        self._run_df_usage()
        self._run_btrfs_fi_show()

        # Based on the disk percentage usage, select the corresponding threshold color.
        color_selector = bisect(
            [disk_limits['warning'], disk_limits['danger']],
            (self._usage['used'] / (self._usage['total'] or 1)) * 100
        )

        self.value = '{0}{1} GiB{2} / {3} GiB'.format(
            COLOR_DICT['sensors'][color_selector],
            round(self._usage['used'], 1),
            COLOR_DICT['clear'],
            round(self._usage['total'], 1)
        )

    def _run_df_usage(self):
        try:
            df_output = check_output(
                [
                    'df', '-l', '-P', '-B', 'MB', '--total',
                    '-t', 'ext2', '-t', 'ext3', '-t', 'ext4',
                    '-t', 'fat32',
                    '-t', 'fuseblk',
                    '-t', 'jfs',
                    '-t', 'lxfs',
                    '-t', 'ntfs',
                    '-t', 'reiserfs',
                    '-t', 'simfs',
                    '-t', 'xfs',
                    '-t', 'zfs'
                ],
                env={'LANG': 'C'}, universal_newlines=True
            ).splitlines()[-1].split()
        except CalledProcessError:
            # It looks like there is not any file system matching our types.
            return

        self._usage['used'] += float(df_output[2].rstrip('MB')) / 1024
        self._usage['total'] += float(df_output[1].rstrip('MB')) / 1024

    def _run_btrfs_fi_show(self):
        try:
            # Here we ask for (local) BTRFS file-systems details.
            btrfs_output = check_output(
                ['btrfs', 'filesystem', 'show', '--gbytes'],
                env={'LANG': 'C'}, universal_newlines=True
            )
        except (FileNotFoundError, CalledProcessError):
            # `btrfs` CLI tool doesn't look available.
            return

        # JSON output support landed very "late" in `btrfs-progs` user-space binaries.
        # We are parsing it the hard way to increase compatibility...
        for total, used in re.findall(
                r"size (\d+\.\d+)GiB used (\d+\.\d+)GiB",
                btrfs_output,
                flags=re.MULTILINE
            ):
            self._usage['used'] += float(used)
            self._usage['total'] += float(total)
