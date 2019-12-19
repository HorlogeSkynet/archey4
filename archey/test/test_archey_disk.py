"""Test module for Archey's disks usage detection module"""

import unittest
from unittest.mock import patch

from archey.entries.disk import Disk


class TestDiskEntry(unittest.TestCase):
    """
    Here, we mock the `check_output` call to `df` using all three cases of available space.
    """
    @patch(
        'archey.entries.disk.check_output',
        return_value="""\
Filesystem       Type 1GB-blocks  Used Available Use% Mounted on
/dev/mapper/root ext4      512GB  14GB     498GB   2% /
/dev/mapper/home ext3      512GB  47GB     465GB   9% /home
total            -        1024GB  61GB     963GB  11% -
""")
    @patch(
        'archey.entries.disk.Configuration.get',
        side_effect=[
            {'low': 50},
            {'medium': 75}
        ]
    )
    def test(self, _, __):
        """Test computations around `df` output at disk normal level"""
        disk = Disk().value
        self.assertIn('\x1b[0;32m', disk)
        self.assertIn('61', disk)
        self.assertIn('1024', disk)

    @patch(
        'archey.entries.disk.check_output',
        return_value="""\
Filesystem       Type 1GB-blocks  Used Available Use% Mounted on
/dev/mapper/root ext4      512GB 314GB     198GB  61% /
/dev/mapper/home ext3      512GB 347GB     165GB  68% /home
total            -        1024GB 661GB     363GB  65% -
""")
    @patch(
        'archey.entries.disk.Configuration.get',
        side_effect=[
            {'low': 50},
            {'medium': 75}
        ]
    )
    def test_warning(self, _, __):
        """Test computations around `df` output at disk warning level"""
        disk = Disk().value
        self.assertIn('\x1b[0;33m', disk)
        self.assertIn('661', disk)
        self.assertIn('1024', disk)

    @patch(
        'archey.entries.disk.check_output',
        return_value="""\
Filesystem       Type 1GB-blocks  Used Available Use% Mounted on
/dev/mapper/root ext4      512GB 414GB      98GB  81% /
/dev/mapper/home ext3      512GB 447GB      65GB  87% /home
total            -        1024GB 861GB     163GB  84% -
""")
    @patch(
        'archey.entries.disk.Configuration.get',
        side_effect=[
            {'low': 50},
            {'medium': 75}
        ]
    )
    def test_danger(self, _, __):
        """Test computations around `df` output at disk danger level"""
        disk = Disk().value
        self.assertIn('\x1b[0;31m', disk)
        self.assertIn('861', disk)
        self.assertIn('1024', disk)


if __name__ == '__main__':
    unittest.main()
