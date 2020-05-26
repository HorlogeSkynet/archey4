"""Disk usage detection class"""

import re
from subprocess import CalledProcessError, check_output
from csv import reader as csv_reader

from archey.colors import Colors
from archey.entry import Entry


class Disk(Entry):
    """Uses `df` to compute disk usage across devices"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate an output from `df`
        self._df_table = self.get_df_output_table()

        # `self.value` will be a list of filesystems represented by dictionaries, with below keys:
        # - `devpath`
        # - `mountpoint`
        # - `used_blocks`
        # - `total_blocks`
        # Hopefully those are self-explanatory!
        self.value = []

        config_filesystems = self._configuration.get('disk')['show_filesystems']
        # This section only adds our filesystems with the device path and mounting point.
        if config_filesystems == ['local']:
            self.value += self._get_local_filesystems()
        else:
            self.value += self._get_specified_filesystems(config_filesystems)

        # Iterate over filesystems, not `df` output, to preserve configuration ordering.
        # Unfortunately, this requires extra iteration over the `df` output...
        for filesystem in self.value:
            # We're adding our used and total blocks here.
            filesystem.update(self._get_filesystem_usage(filesystem))


    def _get_local_filesystems(self):
        """
        Finds local (i.e. /dev/xxx) filesystems for any *NIX using `df`.

        We additionally ignore...
        Loop devices:-
            /dev(/...)/loop filesystems (Linux)
            /dev(/...)/*vnd filesystems (BSD)
            /dev(/...)/lofi filesystems (Solaris)
        Device mappers:- (since their partitions are already included!)
            /dev(/...)/dm filesystems (Linux)
        """
        filesystems = []

        # Compile a REGEXP pattern to match the device paths we will accept.
        devpath_regexp = re.compile(r'^\/dev\/(?:(?!loop|[rs]?vnd|lofi|dm).)+$')

        # Extract `devpath` and `mountpoint` for each disk from `df` output.
        for row in self._df_table:
            # De-duplication using device paths:
            if (devpath_regexp.match(row[0])
                    and not any(disk['devpath'] == row[0] for disk in filesystems)):
                filesystems.append({
                    'devpath': row[0],
                    'mountpoint': row[5]
                })

        return filesystems


    def _get_specified_filesystems(self, specified_filesystems):
        """
        Finds the specified filesystems if found in `df_table`.
        It preserves the mount-point names specified!
        """
        # Extract devpaths and mount-points from df output.
        devpaths, mountpoints = [], []
        for row in self._df_table:
            devpaths.append(row[0])
            mountpoints.append(row[5])

        filesystems = []

        # We could enumerate `devpaths` and `mountpoints` for better performance;
        # however, this method preserves the order of the specified filesystems.
        for file_system in specified_filesystems:
            # EAFP: This is quicker than using `in` followed by `.index` since it
            # saves an extra iteration of `devpaths` and `mountpoints` every loop.
            try:
                # Find the corresponding device path of a mountpoint filesystem.
                devpath = devpaths[mountpoints.index(file_system)]
            except ValueError:
                devpath = file_system

            try:
                # Find the corresponding mountpoint of a device path filesystem.
                mountpoint = mountpoints[devpaths.index(file_system)]
            except ValueError:
                mountpoint = file_system

            # If these differ, we found a matching filesystem.
            if devpath != mountpoint:
                filesystems.append({
                    'devpath': devpath,
                    'mountpoint': mountpoint
                })

        return filesystems


    def _get_filesystem_usage(self, filesystem):
        """
        Gets the used and total blocks of the passed `filesystem`, and returns them in a dict, as:
        {
            'used_blocks': XXX
            'total_blocks': YYY
        }
        """
        # Default to a zero-size and zero-usage disk:
        used_blocks = 0
        total_blocks = 0

        for row in self._df_table:
            if filesystem['devpath'] == row[0] and filesystem['mountpoint'] == row[5]:
                used_blocks = int(row[2])
                total_blocks = int(row[1])
                # We found a match, so we can stop searching.
                break

        return {
            'used_blocks': used_blocks,
            'total_blocks': total_blocks
        }


    @staticmethod
    def get_df_output_table():
        """
        Runs `df -P` and returns a "table" (list) representing its results as nested lists.
        """
        try:
            df_output = check_output(
                ['df', '-P'],
                env={'LANG': 'C'}, universal_newlines=True
            )
        except (FileNotFoundError, CalledProcessError):
            # `df` isn't available on this system.
            return []

        # Parse this output as a table in SSV (space-separated values) format
        ssv_reader = csv_reader(
            df_output.splitlines()[1:],  # Discarding the header row.
            delimiter=' ',
            skipinitialspace=True
        )

        return list(ssv_reader)


    @staticmethod
    def _blocks_to_human_readable(blocks, suffix='B'):
        """
        Returns human-readable format of `blocks` supplied in kibibytes (1024 bytes).
        Taken (and modified) from: <https://stackoverflow.com/a/1094933/13343912>
        """
        for unit in ('Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi'):
            if abs(blocks) < 1024.0:
                break

            blocks /= 1024.0

        return '{0:02.1f} {1}{2}'.format(blocks, unit, suffix)


    def output(self, output):
        """
        Adds the entry to `output` after formatting with color and units.
        Follows the user configuration supplied for formatting.
        """
        # Fetch our `filesystems` object locally so we can modify it safely.
        filesystems = self.value

        if not filesystems:
            # We didn't find any disk, fall back to the default entry behavior.
            super().output(output)
            return

        # DRY configuration object for the output.
        disk_labels = self._configuration.get('disk')['disk_labels']
        hide_entry_name = self._configuration.get('disk')['hide_entry_name']

        # Combine all disks into one grand-total if configured to do so.
        if self._configuration.get('disk')['combine_total']:
            name = self.name

            # Rewrite our `filesystems` object as one combining all of them.
            filesystems = [{
                'devpath': None,
                'mountpoint': None,
                'used_blocks': sum([filesystem['used_blocks'] for filesystem in filesystems]),
                'total_blocks': sum([filesystem['total_blocks'] for filesystem in filesystems])
            }]
        else:
            # We will only use disk labels and entry name hiding if we aren't combining disks.
            name = ''
            if not hide_entry_name:
                name += self.name
            if disk_labels:
                if not hide_entry_name:
                    name += ' '
                name += '({disk_label})'

        # Fetch the user-defined limits from the configuration.
        disk_limits = self._configuration.get('limits')['disk']

        # We will only run this loop a single time for combined disks.
        for filesystem in filesystems:
            # Select the corresponding level color based on disk percentage usage.
            level_color = Colors.get_level_color(
                (filesystem['used_blocks'] / filesystem['total_blocks']) * 100,
                disk_limits['warning'], disk_limits['danger']
            )

            # Set the correct disk label
            if disk_labels == 'mount_points':
                disk_label = filesystem['mountpoint']
            elif disk_labels == 'device_paths':
                disk_label = filesystem['devpath']
            else:
                disk_label = None

            pretty_filesystem_value = '{0}{1}{2} / {3}'.format(
                level_color,
                self._blocks_to_human_readable(filesystem['used_blocks']),
                Colors.CLEAR,
                self._blocks_to_human_readable(filesystem['total_blocks'])
            )

            output.append(
                name.format(disk_label=disk_label),
                pretty_filesystem_value
            )
