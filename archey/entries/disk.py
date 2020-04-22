"""Disk usage detection class"""

from bisect import bisect

import re

from subprocess import check_output, CalledProcessError, DEVNULL

from archey.constants import COLOR_DICT
from archey.configuration import Configuration


class Disk:
    """Uses `df` and `btrfs` commands to compute the total disk usage across devices"""
    def __init__(self):
        # This dictionary will store values obtained from sub-processes calls.
        self._usage = {
            'used': 0.0,
            'total': 0.0
        }

        # Fetch the user-defined disk limits from configuration.
        disk_limits = Configuration().get('limits')['disk']

        self._run_df_usage()
        self._run_btrfs_usage()

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
                env={'LANG': 'C'}, universal_newlines=True, stderr=DEVNULL
            ).splitlines()[-1].split()
        except CalledProcessError:
            # It looks like there is not any file system matching our types.
            return

        self._usage['used'] += float(df_output[2].rstrip('MB')) / 1024
        self._usage['total'] += float(df_output[1].rstrip('MB')) / 1024

    def _run_btrfs_usage(self):
        """
        Since btrfs file-systems can span multiple disks, we fetch all mounted
        btrfs file-systems, retrieve the btrfs partitions associated with each,
        and remove all mount-points with common partitions, then query file-system
        usage for each remaining mount-point.
        """
        try:
            # Retrieve all mount-points containing btrfs filesystems.
            df_btrfs_mounts = check_output(
                ['df', '-l', '--output=target', '-t', 'btrfs'],
                env={'LANG': 'C'}, universal_newlines=True, stderr=DEVNULL
            ).splitlines()[1:]
        except CalledProcessError:
            # No btrfs file-systems present.
            return

        # Eliminate duplicate mounts (e.g. different subvolumes).
        btrfs_unique_mounts = []
        for mountpoint in df_btrfs_mounts:
            try:
                btrfs_mount_output = check_output(
                    ['btrfs', 'device', 'usage', mountpoint],
                    env={'LANG': 'C'}, universal_newlines=True, stderr=DEVNULL
                ).splitlines()
            except (FileNotFoundError, CalledProcessError):
                # `btrfs-progs` not available.
                return

            if btrfs_mount_output not in btrfs_unique_mounts:
                btrfs_unique_mounts.append(mountpoint)

        # Query all unique mount-points for usage.
        btrfs_usage_output = check_output(
            ['btrfs', 'filesystem', 'usage', '--gbytes'] + btrfs_unique_mounts,
            env={'LANG': 'C'}, universal_newlines=True, stderr=DEVNULL
        )

        # JSON output support landed very "late" in `btrfs-progs` user-space binaries.
        # We are parsing it the hard way to increase compatibility...
        physical_device_used = re.findall(
            r"Used:\s+(\d+\.\d+)GiB", btrfs_usage_output,
            flags=re.MULTILINE
        )
        physical_device_size = re.findall(
            r"Device size:\s+(\d+\.\d+)GiB", btrfs_usage_output,
            flags=re.MULTILINE
        )
        data_ratios = re.findall(
            r"Data ratio:\s+(\d+\.\d+)", btrfs_usage_output,
            flags=re.MULTILINE
        )

        # Divide physical space by the corresponding data ratio to get space used for that group.
        logical_device_used = [
            float(x) / float(y)
            for x, y in zip(physical_device_used, data_ratios)
        ]
        logical_device_size = [
            float(x) / float(y)
            for x, y in zip(physical_device_size, data_ratios)
        ]

        self._usage['total'] += sum(logical_device_size)
        self._usage['used'] += sum(logical_device_used)
