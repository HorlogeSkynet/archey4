"""Test module for Archey's disks usage detection module"""

import os
import unittest
from unittest.mock import call, patch, MagicMock

from archey.colors import Colors
from archey.entries.disk import Disk
from archey.test.entries import HelperMethods


class TestDiskEntry(unittest.TestCase):
    """
    Here, we mock `check_output` calls to disk utility tools.
    """
    def setUp(self):
        """We use these mocks so often, it's worth defining them here."""
        self.disk_instance_mock = HelperMethods.entry_mock(Disk)
        self.output_mock = MagicMock()

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

        result_disk_dict = Disk._get_local_filesystems(self.disk_instance_mock)  # pylint: disable=protected-access
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
        self.assertTrue(
            any(
                disk_data['device_path'] == '/dev/sda1'
                for disk_data in result_disk_dict.values()
            ),
            msg='`/dev/sda1` missing from results dict'
        )

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
            os.linesep.join((
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
        test_cases = (
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
        for test_case in test_cases:
            with self.subTest(test_case[1]):
                self.assertEqual(
                    Disk._blocks_to_human_readable(test_case[0]),  # pylint: disable=protected-access
                    test_case[1]
                )

    def test_disk_output_colors(self):
        """Test `output` disk level coloring."""
        # This dict's values are tuples of used blocks, and the level's corresponding color.
        # For reference, this test uses a disk whose total block count is 100.
        levels = {
            'normal': (45.0, Colors.GREEN_NORMAL),
            'warning': (70.0, Colors.YELLOW_NORMAL),
            'danger': (95.0, Colors.RED_NORMAL)
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
                    '{color}{used} KiB{clear} / 100.0 KiB'.format(
                        color=blocks_color_tuple[1],
                        used=blocks_color_tuple[0],
                        clear=Colors.CLEAR
                    )
                )

    def test_disk_multiline_output(self):
        """Test `output`'s multi-line capability."""
        self.disk_instance_mock.value = {
            'first_mount_point': {
                'device_path': '/dev/my-cool-disk',
                'used_blocks': 10,
                'total_blocks': 10
            },
            'second_mount_point': {
                'device_path': '/dev/my-cooler-disk',
                'used_blocks': 10,
                'total_blocks': 30
            }
        }

        with self.subTest('Single-line combined output.'):
            Disk.output(self.disk_instance_mock, self.output_mock)
            self.output_mock.append.assert_called_once_with(
                'Disk',
                '{0}20.0 KiB{1} / 40.0 KiB'.format(Colors.YELLOW_NORMAL, Colors.CLEAR)
            )

        self.output_mock.reset_mock()

        with self.subTest('Multi-line output'):
            self.disk_instance_mock._configuration['disk']['combine_total'] = False  # pylint: disable=protected-access
            Disk.output(self.disk_instance_mock, self.output_mock)
            self.assertEqual(self.output_mock.append.call_count, 2)
            self.output_mock.append.assert_has_calls(
                [
                    call(
                        'Disk',
                        '{0}10.0 KiB{1} / 10.0 KiB'.format(Colors.RED_NORMAL, Colors.CLEAR)
                    ),
                    call(
                        'Disk',
                        '{0}10.0 KiB{1} / 30.0 KiB'.format(Colors.GREEN_NORMAL, Colors.CLEAR)
                    )
                ],
                any_order=True  # Since Python < 3.6 doesn't have definite `dict` ordering.
            )

        self.output_mock.reset_mock()

        with self.subTest('Entry name labeling (device path with entry name)'):
            self.disk_instance_mock._configuration['disk']['combine_total'] = False  # pylint: disable=protected-access
            self.disk_instance_mock._configuration['disk']['disk_labels'] = 'device_paths'  # pylint: disable=protected-access

            Disk.output(self.disk_instance_mock, self.output_mock)
            self.assertEqual(self.output_mock.append.call_count, 2)
            self.output_mock.append.assert_has_calls(
                [
                    call(
                        'Disk (/dev/my-cool-disk)',
                        '{0}10.0 KiB{1} / 10.0 KiB'.format(Colors.RED_NORMAL, Colors.CLEAR)
                    ),
                    call(
                        'Disk (/dev/my-cooler-disk)',
                        '{0}10.0 KiB{1} / 30.0 KiB'.format(Colors.GREEN_NORMAL, Colors.CLEAR)
                    )
                ],
                any_order=True  # Since Python < 3.6 doesn't have definite `dict` ordering.
            )

        self.output_mock.reset_mock()

        with self.subTest('Entry name labeling (mount points without entry name)'):
            self.disk_instance_mock._configuration['disk']['combine_total'] = False  # pylint: disable=protected-access
            self.disk_instance_mock._configuration['disk']['disk_labels'] = 'mount_points'  # pylint: disable=protected-access
            self.disk_instance_mock._configuration['disk']['hide_entry_name'] = True  # pylint: disable=protected-access

            Disk.output(self.disk_instance_mock, self.output_mock)
            self.assertEqual(self.output_mock.append.call_count, 2)
            self.output_mock.append.assert_has_calls(
                [
                    call(
                        '(first_mount_point)',
                        '{0}10.0 KiB{1} / 10.0 KiB'.format(Colors.RED_NORMAL, Colors.CLEAR)
                    ),
                    call(
                        '(second_mount_point)',
                        '{0}10.0 KiB{1} / 30.0 KiB'.format(Colors.GREEN_NORMAL, Colors.CLEAR)
                    )
                ],
                any_order=True  # Since Python < 3.6 doesn't have definite `dict` ordering.
            )

        self.output_mock.reset_mock()

        with self.subTest('Entry name labeling (without disk label nor entry name)'):
            self.disk_instance_mock._configuration['disk']['combine_total'] = False  # pylint: disable=protected-access
            self.disk_instance_mock._configuration['disk']['disk_labels'] = False  # pylint: disable=protected-access
            # `hide_entry_name` is being ignored as `disk_labels` evaluates to "falsy" too.
            self.disk_instance_mock._configuration['disk']['hide_entry_name'] = True  # pylint: disable=protected-access

            Disk.output(self.disk_instance_mock, self.output_mock)
            self.assertEqual(self.output_mock.append.call_count, 2)
            self.output_mock.append.assert_has_calls(
                [
                    call(
                        'Disk',
                        '{0}10.0 KiB{1} / 10.0 KiB'.format(Colors.RED_NORMAL, Colors.CLEAR)
                    ),
                    call(
                        'Disk',
                        '{0}10.0 KiB{1} / 30.0 KiB'.format(Colors.GREEN_NORMAL, Colors.CLEAR)
                    )
                ],
                any_order=True  # Since Python < 3.6 doesn't have definite `dict` ordering.
            )


if __name__ == '__main__':
    unittest.main()
