"""Test module for Archey's session user name detection module"""

import unittest
from unittest.mock import patch

from archey.entries.user import User


class TestUserEntry(unittest.TestCase):
    """
    For this entry, we'll check the output by mocking the `getenv` call.
    """
    @patch(
        'archey.entries.user.os.getenv',
        return_value='USERNAME'
    )
    def test(self, _):
        """Simple mock, simple test"""
        self.assertEqual(User().value, 'USERNAME')


if __name__ == '__main__':
    unittest.main()
