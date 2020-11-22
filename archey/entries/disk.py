"""Disk usage detection class"""

import re
from subprocess import DEVNULL, PIPE, run
from csv import reader as csv_reader

from archey.colors import Colors
from archey.entry import Entry


class Disk(Entry):
    """Uses `df` to compute disk usage across devices"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate an output from `df`
        self._disk_dict = self._get_df_output_dict()

        config_filesystems = self.options.get('show_filesystems', ['local'])
        # See `Disk._get_df_output_dict` for the format we use in `self.value`.
        if config_filesystems == ['local']:
            self.value = self._get_local_filesystems()
        else:
            self.value = self._get_specified_filesystems(config_filesystems)


    def _get_local_filesystems(self):
        """
        Extracts local (i.e. /dev/xxx) filesystems for any *NIX from `self._disk_dict`,
        returning a copy with those filesystems only.

        We specifically ignore...
        Loop devices:-
            /dev(/...)/loop filesystems (Linux)
            /dev(/...)/*vnd filesystems (BSD)
            /dev(/...)/lofi filesystems (Solaris)
        Device mappers:- (since their partitions are already included!)
            /dev(/...)/dm filesystems (Linux)
        """
        # Compile a REGEXP pattern to match the device paths we will accept.
        device_path_regexp = re.compile(r'^\/dev\/(?:(?!loop|[rs]?vnd|lofi|dm).)+$')

        # Build the dictionary
        local_disk_dict = {}
        for mount_point, disk_data in self._disk_dict.items():
            if (
                    device_path_regexp.match(disk_data['device_path'])
                    # De-duplication based on `device_path`s:
                    and not any(
                        disk_data['device_path'] == present_disk_data['device_path']
                        for present_disk_data in local_disk_dict.values()
                    )
            ):
                local_disk_dict[mount_point] = disk_data

        return local_disk_dict


    def _get_specified_filesystems(self, specified_filesystems):
        """
        Extracts the specified filesystems (if found) from `self._disk_dict`,
        returning a copy with those filesystems only, preserving specified mount point names.

        Searching for non-existent filesystems or filesystems based on device paths is slower,
        so try to only search for existing *mount points* if possible!
        """
        specified_disk_dict = {}

        for filesystem in specified_filesystems:
            # Let's use EAFP and first assume the filesystem is a mount point,
            # since the dictionary lookup is O(1).
            try:
                specified_disk_dict[filesystem] = self._disk_dict[filesystem]
                # If we reach here, we found the filesystem - we can move on to the next.
                continue
            except KeyError:
                # It's not a mount point!
                pass

            # Now assume this is a device path.
            for mount_point, disk_data in self._disk_dict.items():
                if disk_data['device_path'] == filesystem:
                    specified_disk_dict[mount_point] = disk_data
                    # We only need one match, so we can stop when it's found.
                    break

        return specified_disk_dict


    @staticmethod
    def _get_df_output_dict():
        """
        Runs `df -P -k` and returns disks in a dict formatted as:
        {
            'mount_point_1': {
                'device_path': AAA,
                'used_blocks': BBB,
                'total_blocks': CCC
            },
            'mount_point_2': {
                'device_path': XXX,
                'used_blocks': YYY,
                'total_blocks': ZZZ
            }
        }
        Mount points are used as keys since they are always unique.
        """
        try:
            df_output = run(
                ['df', '-P', '-k'],
                env={'LANG': 'C'}, universal_newlines=True,
                stdout=PIPE,
                # On error, `df` may "hold" `EXIT_FAILURE` as exit status code.
                # Thus, we purposely silence STDERR and ignore its returned status code.
                # See #92 (related to flatpak/xdg-desktop-portal#512).
                stderr=DEVNULL, check=False
            ).stdout
        except FileNotFoundError:
            # `df` isn't available on this system.
            return {}

        # Parse this output as a table in SSV (space-separated values) format
        ssv_reader = csv_reader(
            df_output.splitlines()[1:],  # Discard the header row here.
            delimiter=' ',
            skipinitialspace=True
        )

        return {
            line[5]: {  # 6th column === mount point.
                'device_path': line[0],
                'used_blocks': int(line[2]),
                'total_blocks': int(line[1])
            } for line in ssv_reader
        }


    @staticmethod
    def _blocks_to_human_readable(blocks, suffix='B'):
        """
        Returns human-readable format of `blocks` supplied in kibibytes (1024 bytes).
        Taken (and modified) from: <https://stackoverflow.com/a/1094933/13343912>
        """
        for unit in ('Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi'):
            if blocks < 1024.0:
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
        disk_labels = self.options.get('disk_labels')
        hide_entry_name = self.options.get('hide_entry_name')

        # Combine all entries into one grand-total if configured to do so.
        if self.options.get('combine_total', True):
            name = self.name

            # Rewrite our `filesystems` object as one combining all of them.
            filesystems = {
                None: {
                    'device_path': None,
                    'used_blocks': sum([
                        filesystem_data['used_blocks']
                        for filesystem_data in filesystems.values()
                    ]),
                    'total_blocks': sum([
                        filesystem_data['total_blocks']
                        for filesystem_data in filesystems.values()
                    ])
                }
            }
        else:
            # We will only use disk labels and entry name hiding if we aren't combining entries.
            name = ''
            # Hide `Disk` from entry name only if the user specified it... as long as a label.
            if not hide_entry_name or not disk_labels:
                name += self.name
            if disk_labels:
                if not hide_entry_name:
                    name += ' '
                name += '({disk_label})'

        # We will only run this loop a single time for combined entries.
        for mount_point, filesystem_data in filesystems.items():
            # Select the corresponding level color based on disk percentage usage.
            level_color = Colors.get_level_color(
                (filesystem_data['used_blocks'] / filesystem_data['total_blocks']) * 100,
                self.options.get('warning_use_percent', 50),
                self.options.get('danger_use_percent', 75)
            )

            # Set the correct disk label
            if disk_labels == 'mount_points':
                disk_label = mount_point
            elif disk_labels == 'device_paths':
                disk_label = filesystem_data['device_path']
            else:
                disk_label = None

            pretty_filesystem_value = '{0}{1}{2} / {3}'.format(
                level_color,
                self._blocks_to_human_readable(filesystem_data['used_blocks']),
                Colors.CLEAR,
                self._blocks_to_human_readable(filesystem_data['total_blocks'])
            )

            output.append(
                name.format(disk_label=disk_label),
                pretty_filesystem_value
            )
