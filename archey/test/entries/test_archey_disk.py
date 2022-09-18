"""Test module for Archey's disks usage detection module"""

import unittest
from unittest.mock import MagicMock, call, patch

from archey.colors import Colors
from archey.entries.disk import Disk
from archey.test.entries import HelperMethods


class TestDiskEntry(unittest.TestCase):
    """
    Here, we mock `subprocess.run` calls to disk utility tools.
    """

    def setUp(self):
        """We use these mocks so often, it's worth defining them here."""
        self.disk_instance_mock = HelperMethods.entry_mock(Disk)
        self.output_mock = MagicMock()

    # Used to make `_replace_apfs_volumes_by_their_containers` call void (see below).
    @patch.object(
        Disk,
        "_replace_apfs_volumes_by_their_containers",
    )
    def test_disk_get_local_filesystems(self, apfs_disk_dict_mock):
        """Tests `Disk._get_local_filesystems`."""
        with self.subTest("Ignoring loop devs, dev mappers & network shares."):
            # This minimal `_disk_dict` is sufficient for this test.
            self.disk_instance_mock._disk_dict = {  # pylint: disable=protected-access
                "/very/good/mountpoint": {
                    "device_path": "/dev/sda1",
                },
                "/mounted/here/too": {
                    "device_path": "/dev/sda1",
                },
                "/other/acceptable/device/paths": {
                    "device_path": "/dev/anything-really",
                },
                "/a/samba/share": {
                    "device_path": "//server.local/cool_share",  # ignored - not `/dev/...`
                },
                "/linux/loop/device/one": {
                    "device_path": "/dev/loop0",  # ignored - loop device
                },
                "/linux/loop/device/two": {
                    "device_path": "/dev/blah/loop0",  # ignored - loop device
                },
                "/bsd/s/loop/device/one": {
                    "device_path": "/dev/svnd",  # ignored - loop device
                },
                "/bsd/s/loop/device/two": {
                    "device_path": "/dev/blah/svnd1",  # ignored - loop device
                },
                "/bsd/r/loop/device/one": {
                    "device_path": "/dev/rvnd",  # ignored - loop device
                },
                "/bsd/r/loop/device/two": {
                    "device_path": "/dev/blah/rvnd1",  # ignored - loop device
                },
                "/solaris/loop/device/one": {
                    "device_path": "/dev/lofi1",  # ignored - loop device
                },
                "/solaris/loop/device/two": {
                    "device_path": "/dev/blah/lofi",  # ignored - loop device
                },
                "/linux/device/mapper": {
                    "device_path": "/dev/dm-1",  # ignored - device mapper
                },
            }

            apfs_disk_dict_mock.return_value = (
                self.disk_instance_mock._disk_dict  # pylint: disable=protected-access
            )

            self.assertDictEqual(
                Disk._get_local_filesystems(  # pylint: disable=protected-access
                    self.disk_instance_mock
                ),
                {
                    "/very/good/mountpoint": {
                        "device_path": "/dev/sda1",
                    },
                    "/other/acceptable/device/paths": {
                        "device_path": "/dev/anything-really",
                    },
                },
            )

    @patch(
        "archey.entries.disk.check_output",
        # This diskutil output is greatly simplified for brevity
        return_value=b"""\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Containers</key>
	<array>
		<dict>
			<key>ContainerReference</key>
			<string>disk1</string>
			<key>DesignatedPhysicalStore</key>
			<string>disk0s1</string>
			<key>Volumes</key>
			<array>
				<dict>
					<key>DeviceIdentifier</key>
					<string>disk1s1</string>
				</dict>
				<dict>
					<key>DeviceIdentifier</key>
					<string>disk1s2</string>
				</dict>
			</array>
		</dict>
		<dict>
			<key>ContainerReference</key>
			<string>disk2</string>
			<key>DesignatedPhysicalStore</key>
			<string>disk0s3</string>
			<key>Volumes</key>
			<array>
				<dict>
					<key>DeviceIdentifier</key>
					<string>disk2s1</string>
				</dict>
			</array>
		</dict>
		<dict>
			<key>ContainerReference</key>
			<string>disk3</string>
			<key>DesignatedPhysicalStore</key>
			<string>disk0s2</string>
			<key>Volumes</key>
			<array>
				<dict>
					<key>DeviceIdentifier</key>
					<string>disk3s1</string>
				</dict>
				<dict>
					<key>DeviceIdentifier</key>
					<string>disk3s5</string>
				</dict>
				<dict>
					<key>DeviceIdentifier</key>
					<string>disk3s6</string>
				</dict>
			</array>
		</dict>
	</array>
</dict>
</plist>
""",
    )
    def test_replace_apfs_volumes_by_their_containers(self, _):
        """Tests `Disk._replace_apfs_volumes_by_their_containers` for APFS volumes deduplication."""
        with self.subTest("Ignoring APFS volumes on macOS"):
            # Shortened example from issue #115, ie standard macOS 12.4 install on M1
            # see https://eclecticlight.co/2021/01/14/m1-macs-radically-change-boot-and-recovery/
            self.disk_instance_mock._disk_dict = {  # pylint: disable=protected-access
                "/": {
                    "device_path": "/dev/disk3s1s1",  # in apfs container (disk0s2)
                    "used_blocks": 0,
                    "total_blocks": 0,
                },
                "/System/Volumes/VM": {
                    "device_path": "/dev/disk3s6",  # in apfs container (disk0s2)
                    "used_blocks": 0,
                    "total_blocks": 0,
                },
                "/System/Volumes/xarts": {
                    "device_path": "/dev/disk1s2",  # in iboot system container (disk0s1)
                    "used_blocks": 0,
                    "total_blocks": 0,
                },
                "/System/Volumes/iSCPreboot": {
                    "device_path": "/dev/disk1s1",  # in iboot system container (disk0s1)
                    "used_blocks": 0,
                    "total_blocks": 0,
                },
                "/System/Volumes/Data": {
                    "device_path": "/dev/disk3s5",  # in apfs container (disk0s2)
                    "used_blocks": 0,
                    "total_blocks": 0,
                },
                "/System/Volumes/Update/SFR/mnt1": {
                    "device_path": "/dev/disk2s1",  # in recovery container (disk0s3)
                    "used_blocks": 0,
                    "total_blocks": 0,
                },
            }
            # We should end up with the 3 container device paths
            self.assertDictEqual(
                Disk._replace_apfs_volumes_by_their_containers(  # pylint: disable=protected-access
                    self.disk_instance_mock
                ),
                {
                    "disk3": {
                        "device_path": "/dev/disk0s2",
                        "used_blocks": 0,
                        "total_blocks": 0,
                    },
                    "disk1": {
                        "device_path": "/dev/disk0s1",
                        "used_blocks": 0,
                        "total_blocks": 0,
                    },
                    "disk2": {
                        "device_path": "/dev/disk0s3",
                        "used_blocks": 0,
                        "total_blocks": 0,
                    },
                },
            )

        with self.subTest("Adding usage of ignored APFS volumes on macOS"):
            # As above test, but checking for correct usage and total figures once combined
            self.disk_instance_mock._disk_dict = {  # pylint: disable=protected-access
                "/": {
                    "device_path": "/dev/disk3s1s1",  # in apfs container (disk0s2)
                    "used_blocks": 23068672,
                    "total_blocks": 970981376,
                },
                "/System/Volumes/VM": {
                    "device_path": "/dev/disk3s6",  # in apfs container (disk0s2)
                    "used_blocks": 1048576,
                    "total_blocks": 970981376,
                },
                "/System/Volumes/xarts": {
                    "device_path": "/dev/disk1s2",  # in iboot system container (disk0s1)
                    "used_blocks": 6144,
                    "total_blocks": 512000,
                },
                "/System/Volumes/iSCPreboot": {
                    "device_path": "/dev/disk1s1",  # in iboot system container (disk0s1)
                    "used_blocks": 7578,
                    "total_blocks": 512000,
                },
                "/System/Volumes/Data": {
                    "device_path": "/dev/disk3s5",  # in apfs container (disk0s2)
                    "used_blocks": 266338304,
                    "total_blocks": 970981376,
                },
                "/System/Volumes/Update/SFR/mnt1": {
                    "device_path": "/dev/disk2s1",  # in recovery container (disk0s3)
                    "used_blocks": 1677722,
                    "total_blocks": 5242880,
                },
            }
            # We should end up with the 3 container device paths
            self.assertDictEqual(
                Disk._replace_apfs_volumes_by_their_containers(  # pylint: disable=protected-access
                    self.disk_instance_mock
                ),
                {
                    "disk3": {
                        "device_path": "/dev/disk0s2",
                        "used_blocks": 290455552,
                        "total_blocks": 970981376,
                    },
                    "disk1": {
                        "device_path": "/dev/disk0s1",
                        "used_blocks": 13722,
                        "total_blocks": 512000,
                    },
                    "disk2": {
                        "device_path": "/dev/disk0s3",
                        "used_blocks": 1677722,
                        "total_blocks": 5242880,
                    },
                },
            )

    def test_disk_get_specified_filesystems(self):
        """Tests `Disk._get_specified_filesystems`."""
        # This minimal `_disk_dict` contains everything this method touches.
        self.disk_instance_mock._disk_dict = {  # pylint: disable=protected-access
            "/very/good/mountpoint": {
                "device_path": "/dev/sda1",
            },
            "/mounted/here/too": {
                "device_path": "/dev/sda1",
            },
            "/less/good/mountpoint": {
                "device_path": "/dev/sda2",
            },
            "/a/samba/share": {
                "device_path": "//server.local/cool_share",
            },
        }

        with self.subTest("Get all filesystems with mount points."):
            # pylint: disable=protected-access
            self.assertDictEqual(
                Disk._get_specified_filesystems(
                    self.disk_instance_mock,
                    self.disk_instance_mock._disk_dict,  # recall dicts are iterables of their keys.
                ),
                self.disk_instance_mock._disk_dict,
            )
            # pylint: enable=protected-access

        with self.subTest("Get only `/dev/sda1` filesystems."):
            self.assertDictEqual(
                Disk._get_specified_filesystems(  # pylint: disable=protected-access
                    self.disk_instance_mock, ("/dev/sda1",)
                ),
                {
                    "/very/good/mountpoint": {
                        "device_path": "/dev/sda1",
                    }
                },
            )

    @patch("archey.entries.disk.run")
    def test_disk_df_output_dict(self, run_mock):
        """Test method to get `df` output as a dict by mocking calls to `subprocess.run`"""
        with self.subTest("`df` regular output."):
            run_mock.return_value.stdout = "\n".join(
                [
                    # pylint: disable=line-too-long
                    "Filesystem               1024-blocks      Used     Available Capacity Mounted on",
                    "/dev/nvme0n1p2             499581952 427458276      67779164      87% /",
                    "tmpfs                        8127236       292       8126944       1% /tmp",
                    "/dev/nvme0n1p1                523248     35908        487340       7% /boot",
                    "/dev/sda1                       1624        42          1582       1% /what is  this",
                    "map auto_home                      0         0             0     100% /System/Volumes/Data/home",
                    "/Applications/Among Us.app/Wrapper 0         0             0     100% /System/Volumes/Data/game",
                    "",
                    # pylint: enable=line-too-long
                ]
            )
            self.assertDictEqual(
                Disk._get_df_output_dict(),  # pylint: disable=protected-access
                {
                    "/": {
                        "device_path": "/dev/nvme0n1p2",
                        "used_blocks": 427458276,
                        "total_blocks": 499581952,
                    },
                    "/tmp": {"device_path": "tmpfs", "used_blocks": 292, "total_blocks": 8127236},
                    "/boot": {
                        "device_path": "/dev/nvme0n1p1",
                        "used_blocks": 35908,
                        "total_blocks": 523248,
                    },
                    "/what is  this": {
                        "device_path": "/dev/sda1",
                        "used_blocks": 42,
                        "total_blocks": 1624,
                    },
                },
            )

        with self.subTest("`df` missing from system."):
            run_mock.side_effect = FileNotFoundError()
            self.assertDictEqual(Disk._get_df_output_dict(), {})  # pylint: disable=protected-access

    def test_disk_blocks_to_human_readable(self):
        """Test method to convert 1024-byte blocks to a human readable format."""
        # Each tuple is a number of blocks followed by the expected output.
        test_cases = (
            (1, "1.0 KiB"),
            (1024, "1.0 MiB"),
            (2048, "2.0 MiB"),
            (95604, "93.4 MiB"),
            (1048576, "1.0 GiB"),
            (2097152, "2.0 GiB"),
            (92156042, "87.9 GiB"),
            (1073742000, "1.0 TiB"),
            (2147484000, "2.0 TiB"),
            (458028916298, "426.6 TiB"),
            (1099512000000, "1.0 PiB"),
            (2199023000000, "2.0 PiB"),  # I think we can safely stop here :)
        )
        for test_case in test_cases:
            with self.subTest(test_case[1]):
                self.assertEqual(
                    Disk._blocks_to_human_readable(  # pylint: disable=protected-access
                        test_case[0]
                    ),
                    test_case[1],
                )

    def test_disk_output_colors(self):
        """Test `output` disk level coloring."""
        # This dict's values are tuples of used blocks, and the level's corresponding color.
        # For reference, this test uses a disk whose total block count is 100.
        levels = {
            "normal": (45.0, Colors.GREEN_NORMAL),
            "warning": (70.0, Colors.YELLOW_NORMAL),
            "danger": (95.0, Colors.RED_NORMAL),
        }
        for level, blocks_color_tuple in levels.items():
            with self.subTest(level):
                self.disk_instance_mock.value = {
                    "mount_point": {
                        "device_path": "/dev/my-cool-disk",
                        "used_blocks": blocks_color_tuple[0],
                        "total_blocks": 100,
                    }
                }
                Disk.output(self.disk_instance_mock, self.output_mock)
                self.output_mock.append.assert_called_with(
                    "Disk",
                    f"{blocks_color_tuple[1]}{blocks_color_tuple[0]} KiB{Colors.CLEAR} / 100.0 KiB",
                )

    def test_disk_multiline_output(self):
        """Test `output`'s multi-line capability."""
        self.disk_instance_mock.value = {
            "first_mount_point": {
                "device_path": "/dev/my-cool-disk",
                "used_blocks": 10,
                "total_blocks": 10,
            },
            "second_mount_point": {
                "device_path": "/dev/my-cooler-disk",
                "used_blocks": 10,
                "total_blocks": 30,
            },
        }

        with self.subTest("Single-line combined output."):
            Disk.output(self.disk_instance_mock, self.output_mock)
            self.output_mock.append.assert_called_once_with(
                "Disk", f"{Colors.YELLOW_NORMAL}20.0 KiB{Colors.CLEAR} / 40.0 KiB"
            )

        self.output_mock.reset_mock()

        with self.subTest("Multi-line output"):
            self.disk_instance_mock.options["combine_total"] = False
            Disk.output(self.disk_instance_mock, self.output_mock)
            self.assertEqual(self.output_mock.append.call_count, 2)
            self.output_mock.append.assert_has_calls(
                [
                    call("Disk", f"{Colors.RED_NORMAL}10.0 KiB{Colors.CLEAR} / 10.0 KiB"),
                    call("Disk", f"{Colors.GREEN_NORMAL}10.0 KiB{Colors.CLEAR} / 30.0 KiB"),
                ]
            )

        self.output_mock.reset_mock()

        with self.subTest("Entry name labeling (device path with entry name)"):
            self.disk_instance_mock.options = {
                "combine_total": False,
                "disk_labels": "device_paths",
            }

            Disk.output(self.disk_instance_mock, self.output_mock)
            self.assertEqual(self.output_mock.append.call_count, 2)
            self.output_mock.append.assert_has_calls(
                [
                    call(
                        "Disk (/dev/my-cool-disk)",
                        f"{Colors.RED_NORMAL}10.0 KiB{Colors.CLEAR} / 10.0 KiB",
                    ),
                    call(
                        "Disk (/dev/my-cooler-disk)",
                        f"{Colors.GREEN_NORMAL}10.0 KiB{Colors.CLEAR} / 30.0 KiB",
                    ),
                ]
            )

        self.output_mock.reset_mock()

        with self.subTest("Entry name labeling (mount points without entry name)"):
            self.disk_instance_mock.options = {
                "combine_total": False,
                "disk_labels": "mount_points",
                "hide_entry_name": True,
            }

            Disk.output(self.disk_instance_mock, self.output_mock)
            self.assertEqual(self.output_mock.append.call_count, 2)
            self.output_mock.append.assert_has_calls(
                [
                    call(
                        "(first_mount_point)",
                        f"{Colors.RED_NORMAL}10.0 KiB{Colors.CLEAR} / 10.0 KiB",
                    ),
                    call(
                        "(second_mount_point)",
                        f"{Colors.GREEN_NORMAL}10.0 KiB{Colors.CLEAR} / 30.0 KiB",
                    ),
                ]
            )

        self.output_mock.reset_mock()

        with self.subTest("Entry name labeling (without disk label nor entry name)"):
            self.disk_instance_mock.options = {
                "combine_total": False,
                "disk_labels": False,
                # `hide_entry_name` is being ignored as `disk_labels` evaluates to "falsy" too.
                "hide_entry_name": True,
            }

            Disk.output(self.disk_instance_mock, self.output_mock)
            self.assertEqual(self.output_mock.append.call_count, 2)
            self.output_mock.append.assert_has_calls(
                [
                    call("Disk", f"{Colors.RED_NORMAL}10.0 KiB{Colors.CLEAR} / 10.0 KiB"),
                    call("Disk", f"{Colors.GREEN_NORMAL}10.0 KiB{Colors.CLEAR} / 30.0 KiB"),
                ]
            )


if __name__ == "__main__":
    unittest.main()
