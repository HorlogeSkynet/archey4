
import unittest
from unittest.mock import patch

from archey.entries.hostname import Hostname


class TestHostnameEntry(unittest.TestCase):
    """
    Here, we mock the `check_output` call and check afterwards
      that the output is correct.
    """
    @patch(
        'archey.archey.check_output',
        return_value='MY-COOL-LAPTOP\n'
    )
    def test(self, check_output_mock):
        self.assertEqual(Hostname().value, 'MY-COOL-LAPTOP')


if __name__ == '__main__':
    unittest.main()
