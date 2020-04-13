"""Disk usage detection class"""

from bisect import bisect

from subprocess import check_output, CalledProcessError, DEVNULL

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

        # Fetch the user-defined disk limits from configuration.
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
                env={'LANG': 'C'}, universal_newlines=True, stderr=DEVNULL
            ).splitlines()[-1].split()
        except CalledProcessError:
            # It looks like there is not any file system matching our types.
            return

        self._usage['used'] += float(df_output[2].rstrip('MB')) / 1024
        self._usage['total'] += float(df_output[1].rstrip('MB')) / 1024

    def _run_btrfs_fi_show(self):
        """
        Since btrfs filesystems can span multiple disks, we fetch all mounted
        btrfs filesystems, retrieve the btrfs partitions associated with each,
        and remove all mountpoints with common partitions, then query filesystem
        usage for each remaining mountpoint.
        """
        try:
            # Retrieve all mountpoints containing btrfs filesystems
            df_btrfs_output = check_output(
                ['df', '-l', '-P', '-t', 'btrfs'],
                env={'LANG': 'C'}, universal_newlines=True, stderr=DEVNULL
            ).splitlines()[1:]
            btrfs_mounts = [line.split()[5] for line in df_btrfs_output]
        except CalledProcessError:
            # No btrfs filesystems present.
            return

        # Eliminate duplicate mounts (e.g. different subvolumes)
        btrfs_unique_mounts = []
        for mountpoint in btrfs_mounts:
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

        # Query all unique mountpoints for usage.
        btrfs_command = ['btrfs', 'filesystem', 'usage', '-g']
        btrfs_command.extend(btrfs_unique_mounts)
        btrfs_mount_output = [
            line.strip() for line in check_output(
                btrfs_command, env={'LANG': 'C'}, universal_newlines=True, stderr=DEVNULL
            ).splitlines()
        ]
        # JSON output support landed very "late" in `btrfs-progs` user-space binaries.
        # We are parsing it the hard way to increase compatibility...
        physical_device_used = []
        physical_device_size = []
        data_ratios = []
        for line in btrfs_mount_output:
            if line.startswith("Used"):
                physical_device_used.append(float(line.split()[1].rstrip("GiB")))
            if line.startswith("Device size"):
                physical_device_size.append(float(line.split()[2].rstrip("GiB")))
            if line.startswith("Data ratio"):
                data_ratios.append(float(line.split()[2]))

        # Divide physical space by the corresponding data ratio to get space
        # used for that group.
        logical_device_used = [x / y for x, y in zip(physical_device_used, data_ratios)]
        logical_device_size = [x / y for x, y in zip(physical_device_size, data_ratios)]
        self._usage['total'] += sum(logical_device_size)
        self._usage['used'] += sum(logical_device_used)
