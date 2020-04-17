"""Test module for Archey's disks usage detection module"""

from subprocess import CalledProcessError

import unittest
from unittest.mock import patch

from archey.entries.disk import Disk
from archey.configuration import Configuration

class TestDiskEntry(unittest.TestCase):
    """
    Here, we mock `check_output` calls to disk utility tools.
    """
    @patch(
        'archey.entries.disk.check_output',
        side_effect=[
            """\
Filesystem       1000000-blocks    Used Available Capacity Mounted on
/dev/mapper/root        39101MB 14216MB   22870MB      39% /
/dev/sda1                 967MB    91MB     810MB      11% /boot
/dev/mapper/home       265741MB 32700MB  219471MB      13% /home
total                  305809MB 47006MB  243149MB      17% -
""",
            FileNotFoundError()  # `btrfs` call will fail.
        ]
    )
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'entries': {
                'Disk': {
                    'display_text': 'Disk', # Required KV pair
                    'usage_warnings': {
                        'warning': 50,
                        'danger': 75
                    }
                }
            }
        }
    )
    def test_df_only(self, _):
        """Test computations around `df` output at disk regular level"""
        disk = Disk().value
        self.assertTrue(all(i in disk for i in ['\x1b[0;32m', '45.9', '298.6']))

    @patch(
        'archey.entries.disk.check_output',
        side_effect=[
            """\
Filesystem       1000000-blocks     Used Available Capacity Mounted on
/dev/mapper/root        39101MB  14216MB   22870MB      39% /
/dev/sda1                 967MB     91MB     810MB      11% /boot
/dev/mapper/home       265741MB 243291MB   22450MB      92% /home
total                  305809MB 257598MB   46130MB      84% -
""",
            FileNotFoundError()  # `btrfs` call will fail.
        ]
    )
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'entries': {
                'Disk': {
                    'display_text': 'Disk', # Required KV pair
                    'usage_warnings': {
                        'warning': 80,
                        'danger': 90
                    }
                }
            }
        }
    )
    def test_df_only_warning(self, _):
        """Test computations around `df` output at disk warning level"""
        disk = Disk().value
        self.assertTrue(all(i in disk for i in ['\x1b[0;33m', '251.6', '298.6']))

    @patch(
        'archey.entries.disk.check_output',
        side_effect=[
            """\
Filesystem       1000000-blocks    Used Available Capacity Mounted on
/dev/mapper/root        39101MB 14216MB   22870MB      39% /
/dev/sda1                 967MB    91MB     810MB      11% /boot
/dev/mapper/home       265741MB 32700MB  219471MB      13% /home
total                  305809MB 47006MB  243149MB      17% -
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
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'entries': {
                'Disk': {
                    'display_text': 'Disk', # Required KV pair
                    'usage_warnings': {
                        'warning': 50,
                        'danger': 75
                    }
                }
            }
        }
    )
    def test_df_and_btrfs(self, _):
        """Test computations around `df` and `btrfs` outputs"""
        disk = Disk().value
        self.assertTrue(all(i in disk for i in ['\x1b[0;32m', '67.4', '376.5']))

    @patch(
        'archey.entries.disk.check_output',
        side_effect=[
            CalledProcessError(1, "df: no file systems processed"),
            '\n'
        ]
    )
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        return_value={
            'entries': {
                'Disk': {
                    'display_text': 'Disk', # Required KV pair
                    'usage_warnings': {
                        'warning': 50,
                        'danger': 75
                    }
                }
            }
        }
    )
    def test_failing_df_and_empty_btrfs(self, _):
        """Test computations around `df` and `btrfs` outputs"""
        disk = Disk().value
        self.assertTrue(all(i in disk for i in ['\x1b[0;32m', '0.0']))

if __name__ == '__main__':
    unittest.main()
