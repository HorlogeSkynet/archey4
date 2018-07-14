
import unittest
from unittest.mock import patch

from archey.archey import User


class TestUserEntry(unittest.TestCase):
    """
    For this entry, we'll check the output by mocking the `getenv` call.
    """
    @patch(
        'archey.archey.os.getenv',
        return_value='USERNAME'
    )
    def test(self, getenv_mock):
        self.assertEqual(User().value, 'USERNAME')


if __name__ == '__main__':
    unittest.main()
