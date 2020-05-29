"""Test module for Archey's disks usage detection module"""

from subprocess import CalledProcessError

import unittest
from unittest.mock import patch, MagicMock

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
