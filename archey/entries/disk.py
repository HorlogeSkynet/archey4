"""Disk usage detection class"""

import platform
import plistlib
import re
from subprocess import DEVNULL, PIPE, check_output, run
from typing import Dict, Iterable, List

from archey.colors import Colors
from archey.entry import Entry


class Disk(Entry):
    """Uses `df` to compute disk usage across devices"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate an output from `df`
        self._disk_dict = self._get_df_output_dict()

        config_filesystems: List[str] = self.options.get("show_filesystems", ["local"])
        # See `Disk._get_df_output_dict` for the format we use in `self.value`.
        if config_filesystems == ["local"]:
            self.value = self._get_local_filesystems()
        else:
            self.value = self._get_specified_filesystems(config_filesystems)

    def _get_local_filesystems(self) -> Dict[str, dict]:
        """
        Extracts local (i.e. /dev/xxx) filesystems for any *NIX from `self._disk_dict`,
        returning a copy with those filesystems only.

        Ignored device paths are...
        Loop devices:-
            /dev(/...)/loop filesystems (Linux)
            /dev(/...)/*vnd filesystems (BSD)
            /dev(/...)/lofi filesystems (Solaris)
        Device mappers:- (since their partitions are already included!)
            /dev(/...)/dm filesystems (Linux)
        (macOS only) any APFS volumes, only APFS containers are counted
        """
        # Compile a REGEXP pattern to match the device paths we will accept.
        device_path_regexp = re.compile(r"^\/dev\/(?:(?!loop|[rs]?vnd|lofi|dm).)+$")

        # If we are on macOS, then remove APFS volumes from our disk dict
        # and replace them with their respective containers.
        if platform.system() == "Darwin":
            disk_dict = self._replace_apfs_volumes_by_their_containers()
        else:
            disk_dict = self._disk_dict

        # Build the dictionary
        local_disk_dict: Dict[str, dict] = {}
        for mount_point, disk_data in disk_dict.items():
            if (
                device_path_regexp.match(disk_data["device_path"])
                # De-duplication based on `device_path`s:
                and not any(
                    disk_data["device_path"] == present_disk_data["device_path"]
                    for present_disk_data in local_disk_dict.values()
                )
            ):
                local_disk_dict[mount_point] = disk_data

        return local_disk_dict

    def _replace_apfs_volumes_by_their_containers(self) -> Dict[str, dict]:
        # Call `diskutil` to generate a property list (PList) of all APFS containers
        try:
            property_list = plistlib.loads(check_output(["diskutil", "apfs", "list", "-plist"]))
        except FileNotFoundError:
            self._logger.warning(
                "APFS volumes cannot be deduplicated as diskutil program could not be found."
            )
            return self._disk_dict
        except plistlib.InvalidFileException:
            self._logger.error(
                "APFS volumes cannot be deduplicated as diskutil output could not be parsed."
            )
            return self._disk_dict

        # Local (shallow) copy of `_disk_dict`
        disk_dict = self._disk_dict.copy()

        # Generate an inverted disk_dict: from device_path -> mount_point
        inverted_disk_dict = {
            value["device_path"]: mount_point for mount_point, value in disk_dict.items()
        }

        # Remove volumes from disk_dict and replace with their aggregated containers
        for plist_container in property_list["Containers"]:
            # Temporary dict for each container
            container_dict = {
                # the container's "real" location:
                "device_path": f"/dev/{plist_container['DesignatedPhysicalStore']}",
                "used_blocks": 0,
                "total_blocks": 0,
            }
            for plist_volume in plist_container["Volumes"]:
                # Get volumes which start with this volume's device path, i.e. include snapshots
                volume_paths = [
                    device_path
                    for device_path in inverted_disk_dict.keys()
                    if device_path.startswith(f"/dev/{plist_volume['DeviceIdentifier']}")
                ]
                for volume_path in volume_paths:
                    try:
                        # Get this volume from disk_dict (removing it)
                        volume = disk_dict.pop(inverted_disk_dict[volume_path])
                    except KeyError:
                        # skip this volume as it misses from  `disk_dict`
                        continue

                    # Now add it to the container entry
                    container_dict["used_blocks"] += volume["used_blocks"]
                    # Total is always the container total
                    container_dict["total_blocks"] = volume["total_blocks"]

            # Use the "reference" (virtual disk) as the mountpoint, since APFS containers
            # cannot be directly mounted
            disk_dict[plist_container["ContainerReference"]] = container_dict

        return disk_dict

    def _get_specified_filesystems(self, specified_filesystems: Iterable[str]) -> Dict[str, dict]:
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
                if disk_data["device_path"] == filesystem:
                    specified_disk_dict[mount_point] = disk_data
                    # We only need one match, so we can stop when it's found.
                    break

        return specified_disk_dict

    @staticmethod
    def _get_df_output_dict() -> Dict[str, dict]:
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
                ["df", "-P", "-k"],
                env={"LANG": "C"},
                universal_newlines=True,
                stdout=PIPE,
                # On error, `df` may "hold" `EXIT_FAILURE` as exit status code.
                # Thus, we purposely silence STDERR and ignore its returned status code.
                # See #92 (related to flatpak/xdg-desktop-portal#512).
                stderr=DEVNULL,
                check=False,
            ).stdout
        except FileNotFoundError:
            # `df` isn't available on this system.
            return {}

        df_output_dict = {}
        for df_entry_match in re.finditer(
            r"""^(?P<device_path>.+?)\s+
                 (?P<total_blocks>\d+)\s+
                 (?P<used_blocks>\d+)\s+
                 \d+\s+ # avail blocks
                 \d+%\s+ # capacity
                 (?P<mount_point>.*)$""",
            df_output,
            flags=re.MULTILINE | re.VERBOSE,
        ):
            total_blocks = int(df_entry_match.group("total_blocks"))
            # Skip entries missing the number of blocks.
            if total_blocks == 0:
                continue

            df_output_dict[df_entry_match.group("mount_point")] = {
                "device_path": df_entry_match.group("device_path"),
                "used_blocks": int(df_entry_match.group("used_blocks")),
                "total_blocks": total_blocks,
            }

        return df_output_dict

    @staticmethod
    def _blocks_to_human_readable(blocks: float, suffix: str = "B") -> str:
        """
        Returns human-readable format of `blocks` supplied in kibibytes (1024 bytes).
        Taken (and modified) from: <https://stackoverflow.com/a/1094933/13343912>
        """
        for unit in ("Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi", "Yi"):
            if blocks < 1024.0:
                break

            blocks /= 1024.0

        return f"{blocks:02.1f} {unit}{suffix}"

    def output(self, output) -> None:
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
        disk_labels = self.options.get("disk_labels")
        hide_entry_name = self.options.get("hide_entry_name")

        # Combine all entries into one grand-total if configured to do so.
        if self.options.get("combine_total", True):
            name = self.name

            # Rewrite our `filesystems` object as one combining all of them.
            filesystems = {
                None: {
                    "device_path": None,
                    "used_blocks": sum(
                        filesystem_data["used_blocks"] for filesystem_data in filesystems.values()
                    ),
                    "total_blocks": sum(
                        filesystem_data["total_blocks"] for filesystem_data in filesystems.values()
                    ),
                }
            }
        else:
            # We will only use disk labels and entry name hiding if we aren't combining entries.
            name = ""
            # Hide `Disk` from entry name only if the user specified it... as long as a label.
            if not hide_entry_name or not disk_labels:
                name += self.name
            if disk_labels:
                if not hide_entry_name:
                    name += " "
                name += "({disk_label})"

        # We will only run this loop a single time for combined entries.
        for mount_point, filesystem_data in filesystems.items():
            # Select the corresponding level color based on disk percentage usage.
            level_color = Colors.get_level_color(
                (filesystem_data["used_blocks"] / filesystem_data["total_blocks"]) * 100,
                self.options.get("warning_use_percent", 50),
                self.options.get("danger_use_percent", 75),
            )

            # Set the correct disk label
            if disk_labels == "mount_points":
                disk_label = mount_point
            elif disk_labels == "device_paths":
                disk_label = filesystem_data["device_path"]
            else:
                disk_label = None

            pretty_filesystem_value = f"{level_color}{{}}{Colors.CLEAR} / {{}}".format(
                self._blocks_to_human_readable(filesystem_data["used_blocks"]),
                self._blocks_to_human_readable(filesystem_data["total_blocks"]),
            )

            output.append(name.format(disk_label=disk_label), pretty_filesystem_value)
