"""Test module for Archey's session user name detection module"""

import unittest
from unittest.mock import patch

from archey.configuration import DEFAULT_CONFIG
from archey.entries.user import User
from archey.test.entries import HelperMethods


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

    @HelperMethods.patch_clean_configuration
    def test_pretty_value(self):
        """Simple test for `pretty_value` base property"""
        user_instance_mock = HelperMethods.entry_mock(User)
        self.assertListEqual(
            User.pretty_value.__get__(user_instance_mock),
            [(user_instance_mock.name, DEFAULT_CONFIG["default_strings"]["not_detected"])],
        )


if __name__ == "__main__":
    unittest.main()
