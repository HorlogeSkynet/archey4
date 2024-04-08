"""Test module for Archey's session user name detection module"""

import unittest
from unittest.mock import patch

from archey.entries.user import User


class TestUserEntry(unittest.TestCase):
    """
    For this entry, we'll simply mock `getpass.getuser` call.
    If internals happen to fail, `ImportError` might be raised.
    """

    @patch(
        "archey.entries.user.getpass.getuser",
        side_effect=[
            "USERNAME",
            ImportError("pwd", "Sure, you got a good reason..."),
        ],
    )
    def test_getenv(self, _):
        """Simple mock, simple test"""
        self.assertEqual(User().value, "USERNAME")
        self.assertIsNone(User().value)


if __name__ == "__main__":
    unittest.main()
