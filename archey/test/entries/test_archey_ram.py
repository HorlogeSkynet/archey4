"""Test module for Archey's RAM usage detection module"""

import unittest
from unittest.mock import MagicMock, mock_open, patch

from archey.colors import Colors
from archey.configuration import DEFAULT_CONFIG
from archey.entries.ram import RAM
from archey.test.entries import HelperMethods


class TestRAMEntry(unittest.TestCase):
    """
    Here, we mock the `check_output` call to `free` using all three levels of available ram.
    In the last test, mock with `/proc/meminfo` file opening during the manual way.
    """

    @patch(
        "archey.entries.ram.check_output",
        return_value="""\
              total        used        free      shared  buff/cache   available
Mem:          15658        2043       10232          12        3382       13268
Swap:          4095          39        4056
""",
    )
    def test_run_free_dash_m(self, _):
        """Test `_run_free_dash_m` output parsing"""
        self.assertTupleEqual(
            RAM._run_free_dash_m(),  # pylint: disable=protected-access
            (2043.0, 15658.0),
        )

    @patch(
        "archey.entries.ram.open",
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
"""
        ),
    )  # Some lines have been ignored as they are useless for computations.
    def test_read_proc_meminfo(self):
        """Test `_read_proc_meminfo` content parsing"""
        self.assertTupleEqual(
            RAM._read_proc_meminfo(),  # pylint: disable=protected-access
            (3739.296875, 7403.3203125),
        )

    @patch(
        "archey.entries.ram.check_output",
        side_effect=[
            "8589934592\n",
            """\
Mach Virtual Memory Statistics: (page size of 4096 bytes)
Pages free:                               55114.
Pages active:                            511198.
Pages inactive:                          488363.
Pages speculative:                        22646.
Pages throttled:                              0.
Pages wired down:                        666080.
Pages purgeable:                          56530.
"Translation faults":                 170435998.
Pages copy-on-write:                    3496023.
Pages zero filled:                     96454484.
Pages reactivated:                     12101726.
Pages purged:                           6728288.
File-backed pages:                       445114.
Anonymous pages:                         577093.
Pages stored in compressor:             2019211.
Pages occupied by compressor:            353431.
Decompressions:                        10535599.
Compressions:                          19723567.
Pageins:                                7586286.
Pageouts:                                388644.
Swapins:                                2879182.
Swapouts:                               3456015.
""",
        ],
    )
    def test_run_sysctl_and_vmstat(self, _):
        """Check `sysctl` and `vm_stat` parsing logic"""
        self.assertTupleEqual(
            RAM._run_sysctl_and_vmstat(),  # pylint: disable=protected-access
            (1685.58984375, 8192.0),
        )

    @patch(
        "archey.entries.ram.check_output",
        side_effect=[
            """\
3992309
3050620
297854
"""
        ],
    )
    def test_run_sysctl_mem(self, _):
        """Test _run_sysctl_mem()"""
        self.assertTupleEqual(
            RAM._run_sysctl_mem(),  # pylint: disable=protected-access
            (2514.98046875, 15594.95703125),
        )

    @HelperMethods.patch_clean_configuration
    def test_various_output_configuration(self):
        """Test `output` overloading based on user preferences"""
        ram_instance_mock = HelperMethods.entry_mock(RAM)
        output_mock = MagicMock()

        with self.subTest("Output in case of non-detection."):
            RAM.output(ram_instance_mock, output_mock)
            self.assertEqual(
                output_mock.append.call_args[0][1],
                DEFAULT_CONFIG["default_strings"]["not_detected"],
            )

        output_mock.reset_mock()

        with self.subTest('"Normal" output (green).'):
            ram_instance_mock.value = {
                "used": 2043.0,
                "total": 15658.0,
                "unit": "MiB",
            }
            ram_instance_mock.options = {
                "warning_use_percent": 33.3,
                "danger_use_percent": 66.7,
            }

            RAM.output(ram_instance_mock, output_mock)
            self.assertEqual(
                output_mock.append.call_args[0][1],
                f"{Colors.GREEN_NORMAL}2043 MiB{Colors.CLEAR} / 15658 MiB",
            )

        output_mock.reset_mock()

        with self.subTest('"Danger" output (red).'):
            ram_instance_mock.value = {
                "used": 7830.0,
                "total": 15658.0,
                "unit": "MiB",
            }
            ram_instance_mock.options = {
                "warning_use_percent": 25,
                "danger_use_percent": 50,
            }

            RAM.output(ram_instance_mock, output_mock)
            self.assertEqual(
                output_mock.append.call_args[0][1],
                f"{Colors.RED_NORMAL}7830 MiB{Colors.CLEAR} / 15658 MiB",
            )


if __name__ == "__main__":
    unittest.main()
