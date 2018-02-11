
import unittest
from unittest.mock import patch

from archey.archey import Shell


class TestUserEntry(unittest.TestCase):
    """
    For this entry, we'll just verify that the output is non-null.
    """
    @patch(
        'archey.archey.getenv',
        return_value='SHELL'
    )
    def test(self, getenv_mock):
        self.assertEqual(Shell().value, 'SHELL')


if __name__ == '__main__':
    unittest.main()
