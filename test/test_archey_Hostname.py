
import unittest
from unittest.mock import patch

from archey.archey import Hostname


class TestHostnameEntry(unittest.TestCase):
    @patch(
        'archey.archey.check_output',
        return_value=b'MY-COOL-LAPTOP\n'
    )
    def test(self, check_output_mock):
        self.assertEqual(Hostname().value, 'MY-COOL-LAPTOP')


if __name__ == '__main__':
    unittest.main()
