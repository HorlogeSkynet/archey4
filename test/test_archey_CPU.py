
import unittest
from unittest.mock import mock_open, patch

from archey.archey import CPU


class TestCPUEntry(unittest.TestCase):
    """
    Here, we mock the `open` call on `/proc/cpuinfo` with fake content.
    """
    @patch(
        'archey.archey.open',
        mock_open(
            read_data="""\
processor\t: 0
vendor_id\t: CPU-VENDOR-NAME
cpu family\t: X
model\t\t: YY
model name\t: CPU-MODEL-NAME
"""),
        create=True
    )
    def test_model_name_match(self):
        self.assertEqual(CPU().value, 'CPU-MODEL-NAME')

    @patch(
        'archey.archey.open',
        mock_open(
            read_data="""\
processor\t: 0
vendor_id\t: CPU-VENDOR-NAME
cpu family\t: X
model\t\t: YY
model name\t: CPU  MODEL\t  NAME
"""),
        create=True
    )
    def test_spaces_squeezing(self):
        self.assertEqual(CPU().value, 'CPU MODEL NAME')


if __name__ == '__main__':
    unittest.main()
