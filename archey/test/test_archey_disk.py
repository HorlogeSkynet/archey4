"""Test module for Archey's disks usage detection module"""

import unittest
from unittest.mock import patch

from archey.entries.disk import Disk


class TestDiskEntry(unittest.TestCase):
    """
    Here, we mock `check_output` calls to disk utility tools.
    """
    @patch(
        'archey.entries.disk.check_output',
        side_effect=[
            """\
Filesystem       1000000000-blocks  Used Available Capacity Mounted on
/dev/mapper/root             512GB  14GB     498GB       2% /
/dev/mapper/home             512GB  47GB     465GB       9% /home
total                       1024GB  61GB     963GB      11% -
""",
            FileNotFoundError()  # `btrfs` call will fail.
        ]
    )
    @patch(
        'archey.entries.disk.Configuration.get',
        return_value={
            'disk': {
                'warning': 50,
                'danger': 75
            }
        }
    )
    def test_df_only(self, _, __):
        """Test computations around `df` output at disk normal level"""
        disk = Disk().value
        self.assertTrue(all(i in disk for i in ['\x1b[0;32m', '61', '1024']))

    @patch(
        'archey.entries.disk.check_output',
        side_effect=[
            """\
Filesystem       1000000000-blocks  Used Available Capacity Mounted on
/dev/mapper/root             512GB 314GB     198GB      61% /
/dev/mapper/home             512GB 347GB     165GB      68% /home
total                       1024GB 661GB     363GB      65% -
""",
            FileNotFoundError()  # `btrfs` call will fail.
        ]
    )
    @patch(
        'archey.entries.disk.Configuration.get',
        return_value={
            'disk': {
                'warning': 50,
                'danger': 75
            }
        }
    )
    def test_df_only_warning(self, _, __):
        """Test computations around `df` output at disk warning level"""
        disk = Disk().value
        self.assertTrue(all(i in disk for i in ['\x1b[0;33m', '661', '1024']))

    @patch(
        'archey.entries.disk.check_output',
        side_effect=[
            """\
Filesystem       1GB-blocks  Used Available Use% Mounted on
/dev/mapper/root      512GB  14GB     498GB   2% /
/dev/mapper/home      512GB  47GB     465GB   9% /home
total                1024GB  61GB     963GB  11% -
""",
            """\
Label: none  uuid: ac1d4ab8-6ea1-11ea-bc55-0242ac130003
	Total devices 1 FS bytes used 6.23GiB
	devid    1 size 55.97GiB used 17.12GiB path /dev/vda1

Label: none  uuid: b749f0c6-6ea1-11ea-bc55-0242ac130003
	Total devices 1 FS bytes used 0.00GiB
	devid    1 size 3.15GiB used 0.99GiB path /dev/vda8

Label: none  uuid: bb675216-6ea1-11ea-bc55-0242ac130003
	Total devices 1 FS bytes used 0.52GiB
	devid    1 size 9.37GiB used 2.12GiB path /dev/vda6

Label: none  uuid: c168c2e4-6ea1-11ea-bc55-0242ac130003
	Total devices 1 FS bytes used 0.00GiB
	devid    1 size 9.36GiB used 1.24GiB path /dev/vda7

"""
        ]
    )
    @patch(
        'archey.entries.disk.Configuration.get',
        return_value={
            'disk': {
                'warning': 50,
                'danger': 75
            }
        }
    )
    def test_df_and_btrfs(self, _, __):
        """Test computations around `df` and `btrfs` outputs"""
        disk = Disk().value
        self.assertTrue(all(i in disk for i in ['\x1b[0;32m', '82.5', '1101.8']))

if __name__ == '__main__':
    unittest.main()
