
import unittest
from unittest.mock import mock_open, patch

from archey.archey import RAM


class TestRAMEntry(unittest.TestCase):
    """
    Here, we mock the `check_output` call to `free`.
    Same thing with `/proc/meminfo` file opening during the manual way.
    """

    @patch(
        'archey.archey.check_output',
        return_value="""\
          total     used    free    shared  buff/cache   available
Mem:       7412     3341    1503       761        2567        3011
Swap:      7607        5    7602
""")
    def test_free_dash_m(self, check_output_mock):
        self.assertIn('3341', RAM().value)
        self.assertIn('7412', RAM().value)

    @patch(
        'archey.archey.check_output',
        side_effect=IndexError()  # `free` call will fail
    )
    @patch(
        'archey.archey.open',
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
""")  # Some content have been truncated (because the following is useless)
    )
    def test_proc_meminfo(self, check_output_mock):
        self.assertIn('3556', RAM().value)
        self.assertIn('7412', RAM().value)


if __name__ == '__main__':
    unittest.main()
