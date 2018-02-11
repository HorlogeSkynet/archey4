
import unittest
from unittest.mock import patch

from archey.archey import User


class TestUserEntry(unittest.TestCase):
    """
    For this entry, we'll just verify that the output is non-null.
    """
    @patch(
        'archey.archey.getenv',
        return_value='USERNAME'
    )
    def test(self, getenv_mock):
        self.assertEqual(User().value, 'USERNAME')


if __name__ == '__main__':
    unittest.main()
