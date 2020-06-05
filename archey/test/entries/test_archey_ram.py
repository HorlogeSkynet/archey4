"""Test module for Archey's RAM usage detection module"""

import unittest
from unittest.mock import mock_open, patch, MagicMock

from archey.colors import Colors
from archey.entries.ram import RAM
from archey.test.entries import HelperMethods
from archey.constants import DEFAULT_CONFIG


class TestRAMEntry(unittest.TestCase):
    """
    Here, we mock the `check_output` call to `free` using all three levels of available ram.
    In the last test, mock with `/proc/meminfo` file opening during the manual way.
    """
    @patch(
        'archey.entries.ram.check_output',
        return_value="""\
              total        used        free      shared  buff/cache   available
Mem:          15658        2043       10232          12        3382       13268
Swap:          4095          39        4056
""")
    @HelperMethods.patch_clean_configuration(
        configuration={
            'limits': {
                'ram': {
                    'warning': 25,
                    'danger': 45
                }
            }
        }
    )
    def test_free_dash_m(self, _):
        """Test `free -m` output parsing for low RAM use case"""
        output_mock = MagicMock()
        RAM().output(output_mock)
        self.assertEqual(
            output_mock.append.call_args[0][1],
            '{0}2043 MiB{1} / 15658 MiB'.format(
                Colors.GREEN_NORMAL,
                Colors.CLEAR
            )
        )

    @patch(
        'archey.entries.ram.check_output',
        return_value="""\
          total     used    free    shared  buff/cache   available
Mem:       7412     3341    1503       761        2567        3011
Swap:      7607        5    7602
""")
    @HelperMethods.patch_clean_configuration(
        configuration={
            'limits': {
                'ram': {
                    'warning': 33.3,
                    'danger': 66.7
                }
            }
        }
    )
    def test_free_dash_m_warning(self, _):
        """Test `free -m` output parsing for warning RAM use case"""
        output_mock = MagicMock()
        RAM().output(output_mock)
        self.assertEqual(
            output_mock.append.call_args[0][1],
            '{0}3341 MiB{1} / 7412 MiB'.format(
                Colors.YELLOW_NORMAL,
                Colors.CLEAR
            )
        )

    @patch(
        'archey.entries.ram.check_output',
        return_value="""\
              total        used        free      shared  buff/cache   available
Mem:          15658       12341         624         203        2692        2807
Swap:          4095         160        3935
""")
    @HelperMethods.patch_clean_configuration(
        configuration={
            'limits': {
                'ram': {
                    'warning': 33.3,
                    'danger': 66.7
                }
            }
        }
    )
    def test_free_dash_m_danger(self, _):
        """Test `free -m` output parsing for danger RAM use case"""
        output_mock = MagicMock()
        RAM().output(output_mock)
        self.assertEqual(
            output_mock.append.call_args[0][1],
            '{0}12341 MiB{1} / 15658 MiB'.format(
                Colors.RED_NORMAL,
                Colors.CLEAR
            )
        )

    @patch(
        'archey.entries.ram.check_output',
        side_effect=IndexError()  # `free` call will fail
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
        self.assertDictEqual(
            RAM().value,
            {
                'used': 3739.296875,
                'total': 7403.3203125,
                'unit': 'MiB'
            }
        )

    @patch(
        'archey.entries.ram.check_output',
        side_effect=IndexError()  # `free` call will fail
    )
    @patch(
        'archey.entries.ram.open',
        side_effect=PermissionError(),
        create=True
    )
    @HelperMethods.patch_clean_configuration
    def test_not_detected(self, _, __):
        """Check Archey does not crash when `/proc/meminfo` is not readable"""
        ram = RAM()

        output_mock = MagicMock()
        ram.output(output_mock)

        self.assertIsNone(ram.value)
        self.assertEqual(
            output_mock.append.call_args[0][1],
            DEFAULT_CONFIG['default_strings']['not_detected']
        )


if __name__ == '__main__':
    unittest.main()
