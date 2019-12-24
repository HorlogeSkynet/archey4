"""Test module for Archey's RAM usage detection module"""

import unittest
from unittest.mock import mock_open, patch

from archey.entries.ram import RAM


class TestRAMEntry(unittest.TestCase):
    """
    Here, we mock the `check_output` call to `free` using all three levels of available ram.
    In the last test, mock with `/proc/meminfo` file opening during the manual way.
    """
    @patch(
        'archey.entries.ram.check_output',
        return_value="""\
          total     used    free    shared  buff/cache   available
Mem:       7412     3341    1503       761        2567        3011
Swap:      7607        5    7602
""")
    @patch(
        'archey.entries.ram.Configuration.get',
        return_value={
            'ram': {
                'warning': 25,
                'danger': 45
            },
        }
    )
    def test_free_dash_m(self, _, __):
        """Test `free -m` output parsing for low RAM use case and tweaked limits"""
        ram = RAM().value
        self.assertTrue(all(i in ram for i in ['\x1b[0;31m', '3341', '7412']))

    @patch(
        'archey.entries.ram.check_output',
        return_value="""\
              total        used        free      shared  buff/cache   available
Mem:          15658        2043       10232          12        3382       13268
Swap:          4095          39        4056
""")
    @patch(
        'archey.entries.ram.Configuration.get',
        return_value={
            'ram': {
                'warning': 33.3,
                'danger': 66.7
            },
        }
    )
    def test_free_dash_m_warning(self, _, __):
        """Test `free -m` output parsing for warning RAM use case"""
        ram = RAM().value
        self.assertTrue(all(i in ram for i in ['\x1b[0;32m', '2043', '15658']))

    @patch(
        'archey.entries.ram.check_output',
        return_value="""\
              total        used        free      shared  buff/cache   available
Mem:          15658       12341         624         203        2692        2807
Swap:          4095         160        3935
""")
    @patch(
        'archey.entries.ram.Configuration.get',
        return_value={
            'ram': {
                'warning': 33.3,
                'danger': 66.7
            },
        }
    )
    def test_free_dash_m_danger(self, _, __):
        """Test `free -m` output parsing for danger RAM use case"""
        ram = RAM().value
        self.assertTrue(all(i in ram for i in ['\x1b[0;31m', '12341', '15658']))

    @patch(
        'archey.entries.ram.check_output',
        side_effect=IndexError()  # `free` call will fail
    )
    @patch(
        'archey.entries.ram.Configuration.get',
        return_value={
            'ram': {
                'warning': 33.3,
                'danger': 66.7
            },
        }
    )
    @patch(
        'archey.entries.ram.open',
        mock_open(
            read_data="""\
MemTotal:        7590580 kB
MemFree:         1502940 kB
MemAvailable:    3173804 kB
Buffers:          156976 kB
Cached:          2289164 kB
SwapCached:          220 kB
Active:          3426704 kB
Inactive:        2254292 kB
Active(anon):    2221228 kB
Inactive(anon):  1725868 kB
Active(file):    1205476 kB
Inactive(file):   528424 kB
Unevictable:          32 kB
Mlocked:              32 kB
SwapTotal:       7790588 kB
SwapFree:        7785396 kB
Dirty:               200 kB
"""),  # Some content have been truncated (because the following is useless)
        create=True
    )
    def test_proc_meminfo(self, _, __):
        """Test `/proc/meminfo` parsing (when `free` is not available)"""
        ram = RAM().value
        self.assertTrue(all(i in ram for i in ['\x1b[0;33m', '3556', '7412']))


if __name__ == '__main__':
    unittest.main()
