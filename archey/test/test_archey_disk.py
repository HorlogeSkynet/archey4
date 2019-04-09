
import unittest
from unittest.mock import patch

from archey.entries.disk import Disk


class TestDiskEntry(unittest.TestCase):
    """
    Here, we mock the `check_output` call to `df`.
    """
    @patch(
        'archey.archey.check_output',
        return_value="""\
Filesystem       Type 1GB-blocks  Used Available Use% Mounted on
/dev/mapper/root ext4      512GB  14GB     498GB   2% /
/dev/mapper/home ext3      512GB  47GB     465GB   9% /home
total            -        1024GB  61GB     963GB  11% -
""")
    def test(self, check_output_mock):
        self.assertIn('61', Disk().value)
        self.assertIn('1024', Disk().value)


if __name__ == '__main__':
    unittest.main()
