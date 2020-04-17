"""Test module for Archey's RAM usage detection module"""

import unittest
from unittest.mock import mock_open, patch

from archey.entries.ram import RAM
from archey.configuration import Configuration


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
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'entries': {
                'RAM': {
                    'display_text': 'RAM', # Required KV pair
                    'usage_warnings': {
                        'warning': 25,
                        'danger': 45
                    }
                }
            }
        }
    )
    def test_free_dash_m(self, _):
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
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'entries': {
                'RAM': {
                    'display_text': 'RAM', # Required KV pair
                    'usage_warnings': {
                        'warning': 33.3,
                        'danger': 66.7
                    }
                }
            }
        }
    )
    def test_free_dash_m_warning(self, _):
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
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'entries': {
                'RAM': {
                    'display_text': 'RAM', # Required KV pair
                    'usage_warnings': {
                        'warning': 33.3,
                        'danger': 66.7
                    }
                }
            }
        }
    )
    def test_free_dash_m_danger(self, _):
        """Test `free -m` output parsing for danger RAM use case"""
        ram = RAM().value
        self.assertTrue(all(i in ram for i in ['\x1b[0;31m', '12341', '15658']))

    @patch(
        'archey.entries.ram.check_output',
        side_effect=IndexError()  # `free` call will fail
    )
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'entries': {
                'RAM': {
                    'display_text': 'RAM', # Required KV pair
                    'usage_warnings': {
                        'warning': 33.3,
                        'danger': 66.7
                    }
                }
            }
        }
    )
    @patch(
        'archey.entries.ram.open',
        mock_open(
            read_data="""\
MemTotal:        7581000 kB
MemFree:          716668 kB
MemAvailable:    3632244 kB
Buffers:          478524 kB
Cached:          2807032 kB
SwapCached:        67092 kB
Active:          3947284 kB
Inactive:        2447708 kB
Active(anon):    2268724 kB
Inactive(anon):  1106220 kB
Active(file):    1678560 kB
Inactive(file):  1341488 kB
Unevictable:         128 kB
Mlocked:             128 kB
SwapTotal:       7811068 kB
SwapFree:        7277708 kB
Dirty:               144 kB
Writeback:             0 kB
AnonPages:       3067204 kB
Mapped:           852272 kB
Shmem:            451056 kB
Slab:             314100 kB
SReclaimable:     200792 kB
SUnreclaim:       113308 kB
"""),  # Some lines have been ignored as they are useless for computations.
        create=True
    )
    def test_proc_meminfo(self, _):
        """Test `/proc/meminfo` parsing (when `free` is not available)"""
        ram = RAM().value
        self.assertTrue(all(i in ram for i in ['\x1b[0;33m', '3739', '7403']))


if __name__ == '__main__':
    unittest.main()
