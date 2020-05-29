"""Test module for Archey's disks usage detection module"""

import unittest
from unittest.mock import patch, MagicMock
from os import linesep

from archey.colors import Colors
from archey.entries.disk import Disk


class TestDiskEntry(unittest.TestCase):
    """
    Here, we mock `check_output` calls to disk utility tools.
    """
    def setUp(self):
        """Some useful setup tasks to do before each test, to help us DRY."""
        self.disk_instance_mock = MagicMock(spec=Disk, wraps=Disk)
        self.output_mock = MagicMock()
        # Let's set `Disk` instance mock's attributes to sensible defaults.
        self.disk_instance_mock.name = 'Disk'
        self.disk_instance_mock.value = None
        # We can always change this configuration in tests if need be.
        self.disk_instance_mock._configuration = {  # pylint: disable=protected-access
            'disk': {
                'show_filesystems': ['local'],
                'combine_total': True,
                'disk_labels': None,
                'hide_entry_name': None
            },
            'limits': {
                'disk': {
                    'warning': 50,
                    'danger': 75
                }
            },
            # Required by all entries:
            'default_strings': {'not_detected': 'Not detected'}
        }

    def test_disk_get_local_filesystems(self):
        """Tests `Disk._get_local_filesystems`."""
        # This minimal `_disk_dict` contains everything this method touches.
        self.disk_instance_mock._disk_dict = {  # pylint: disable=protected-access
            '/very/good/mountpoint': {
                'device_path': '/dev/sda1'
            },
            '/mounted/here/too': {
                'device_path': '/dev/sda1'
            },
            '/other/acceptable/device/paths': {
                'device_path': '/dev/anything-really'
            },
            '/a/samba/share': {
                'device_path': '//server.local/cool_share'  # ignored - not `/dev/...`
            },
            '/linux/loop/device/one': {
                'device_path': '/dev/loop0'  # ignored - loop device
            },
            '/linux/loop/device/two': {
                'device_path': '/dev/blah/loop0'  # ignored - loop device
            },
            '/bsd/s/loop/device/one': {
                'device_path': '/dev/svnd'  # ignored - loop device
            },
            '/bsd/s/loop/device/two': {
                'device_path': '/dev/blah/svnd1'  # ignored - loop device
            },
            '/bsd/r/loop/device/one': {
                'device_path': '/dev/rvnd'  # ignored - loop device
            },
            '/bsd/r/loop/device/two': {
                'device_path': '/dev/blah/rvnd1'  # ignored - loop device
            },
            '/solaris/loop/device/one': {
                'device_path': '/dev/lofi1'  # ignored - loop device
            },
            '/solaris/loop/device/two': {
                'device_path': '/dev/blah/lofi'  # ignored - loop device
            },
            '/linux/device/mapper': {
                'device_path': '/dev/dm-1'  # ignored - device mapper
            }
        }

        result_disk_dict = Disk._get_local_filesystems(self.disk_instance_mock) # pylint: disable=protected-access
        # Python < 3.6 doesn't guarantee dict ordering,
        # so we can't know which `/dev/sda1` mount point was used.
        self.assertEqual(
            len(result_disk_dict),
            2  # (/dev/sda1 is de-duplicated)
        )
        self.assertIn(
            '/other/acceptable/device/paths',
            result_disk_dict
        )
        # If we can now find `/dev/sda1`, then we logically must have the correct result.
        seen_sda1_device = False
        for disk_data in result_disk_dict.values():
            if disk_data['device_path'] == '/dev/sda1':
                seen_sda1_device = True
                break
        if not seen_sda1_device:
            self.fail('`/dev/sda1` missing from results dict.')

    def test_disk_get_specified_filesystems(self):
        """Tests `Disk._get_specified_filesystems`."""
        # This minimal `_disk_dict` contains everything this method touches.
        self.disk_instance_mock._disk_dict = {  # pylint: disable=protected-access
            '/very/good/mountpoint': {
                'device_path': '/dev/sda1'
            },
            '/mounted/here/too': {
                'device_path': '/dev/sda1'
            },
            '/less/good/mountpoint': {
                'device_path': '/dev/sda2'
            },
            '/a/samba/share': {
                'device_path': '//server.local/cool_share'
            }
        }

        with self.subTest('Get all filesystems with mount points.'):
            # pylint: disable=protected-access
            self.assertDictEqual(
                Disk._get_specified_filesystems(
                    self.disk_instance_mock,
                    self.disk_instance_mock._disk_dict  # recall dicts are iterables of their keys.
                ),
                self.disk_instance_mock._disk_dict
            )
            # pylint: enable=protected-access

        with self.subTest('Get only `/dev/sda1` filesystems.'):
            result_disk_dict = Disk._get_specified_filesystems(  # pylint: disable=protected-access
                self.disk_instance_mock,
                ('/dev/sda1',)
            )
            # With Python < 3.6, dict ordering isn't guaranteed,
            # so we don't know which disk will be selected.
            self.assertEqual(len(result_disk_dict), 1)
            # As long as `device_path` is also correct, this passes.
            self.assertEqual(
                result_disk_dict[list(result_disk_dict.keys())[0]]['device_path'],
                '/dev/sda1'
            )


    @patch(
        'archey.entries.disk.check_output',
        side_effect=[
            # First `df` call succeeds.
            linesep.join((
                "Filesystem               1024-blocks      Used     Available Capacity Mounted on",
                "/dev/nvme0n1p2             499581952 427458276      67779164      87% /",
                "tmpfs                        8127236       292       8126944       1% /tmp",
                "/dev/nvme0n1p1                523248     35908        487340       7% /boot",
                ""
            )),
            # Second `df` call fails (emulating it not being present).
            FileNotFoundError
        ]
    )
    def test_disk_df_output_dict(self, _):
        """Test method to get `df` output as a dict by mocking calls to `check_output`."""
        self.assertDictEqual(
            Disk.get_df_output_dict(),
            {
                '/': {
                    'device_path': '/dev/nvme0n1p2',
                    'used_blocks': 427458276,
                    'total_blocks': 499581952
                },
                '/tmp': {
                    'device_path': 'tmpfs',
                    'used_blocks': 292,
                    'total_blocks': 8127236
                },
                '/boot': {
                    'device_path': '/dev/nvme0n1p1',
                    'used_blocks': 35908,
                    'total_blocks': 523248
                }
            }
        )

        with self.subTest('Missing `df` from system.'):
            self.assertDictEqual(
                Disk.get_df_output_dict(),
                {}
            )

    def test_disk_blocks_to_human_readable(self):
        """Test method to convert 1024-byte blocks to a human readable format."""
        # Each tuple is a number of blocks followed by the expected output.
        tests = (
            (1, '1.0 KiB'),
            (1024, '1.0 MiB'),
            (2048, '2.0 MiB'),
            (95604, '93.4 MiB'),
            (1048576, '1.0 GiB'),
            (2097152, '2.0 GiB'),
            (92156042, '87.9 GiB'),
            (1073742000, '1.0 TiB'),
            (2147484000, '2.0 TiB'),
            (458028916298, '426.6 TiB'),
            (1099512000000, '1.0 PiB'),
            (2199023000000, '2.0 PiB')  # I think we can safely stop here :)
        )
        for test in tests:
            with self.subTest(test[1]):
                self.assertEqual(
                    Disk._blocks_to_human_readable(test[0]),  # pylint: disable=protected-access
                    test[1]
                )

    def test_disk_output_colors(self):
        """Test `output` disk level coloring."""
        # This dict's values are tuples of used blocks, and the level's corresponding color.
        # For reference, this test uses a disk whose total block count is 100.
        levels = {
            'normal': (45, Colors.GREEN_NORMAL),
            'warning': (70, Colors.YELLOW_NORMAL),
            'danger': (95, Colors.RED_NORMAL)
        }
        for level, blocks_color_tuple in levels.items():
            with self.subTest(level):
                self.disk_instance_mock.value = {
                    'mount_point': {
                        'device_path': '/dev/my-cool-disk',
                        'used_blocks': blocks_color_tuple[0],
                        'total_blocks': 100
                    }
                }
                Disk.output(self.disk_instance_mock, self.output_mock)
                self.output_mock.append.assert_called_with(
                    'Disk',
                    '{color}{used}.0 KiB{clear} / 100.0 KiB'.format(
                        color=blocks_color_tuple[1],
                        used=blocks_color_tuple[0],
                        clear=Colors.CLEAR
                    )
                )


if __name__ == '__main__':
    unittest.main()
