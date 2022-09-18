"""Test module for Archey's desktop environment detection module"""

import unittest
from unittest.mock import patch

from archey.entries.desktop_environment import DesktopEnvironment


@patch("archey.entries.desktop_environment.platform.system", return_value="Linux")
class TestDesktopEnvironmentEntry(unittest.TestCase):
    """
    With the help of a fake running processes list, we test the DE matching.
    """

    @patch(
        "archey.entries.desktop_environment.Processes.list",
        (
            "do",
            "you",
            "like",
            "cinnamon",
            "tea",
        ),  # Fake running processes list  # Match !
    )
    def test_match(self, _):
        """Simple list matching"""
        self.assertEqual(DesktopEnvironment().value, "Cinnamon")

    @patch(
        "archey.entries.desktop_environment.Processes.list",
        (  # Fake running processes list
            "do",
            "you",
            "like",
            "unsweetened",  # Mismatch...
            "coffee",
        ),
    )
    @patch("archey.entries.desktop_environment.os.getenv", return_value="DESKTOP ENVIRONMENT")
    def test_mismatch(self, _, __):
        """Simple list (mis-)-matching"""
        self.assertEqual(DesktopEnvironment().value, "DESKTOP ENVIRONMENT")

    @patch("archey.entries.desktop_environment.platform.system")
    def test_darwin_aqua_deduction(self, _, platform_system_mock):
        """Test "Aqua" deduction on Darwin systems"""
        platform_system_mock.return_value = "Darwin"  # Override module-wide mocked value.

        self.assertEqual(DesktopEnvironment().value, "Aqua")

    @patch(
        "archey.entries.desktop_environment.Processes.list",
        (  # Fake running processes list
            "do",
            "you",
            "like",
            "unsweetened",  # Mismatch...
            "coffee",
        ),
    )
    @patch(
        "archey.entries.desktop_environment.os.getenv",
        return_value=None,  # The environment variable is empty...
    )
    def test_non_detection(self, _, __):
        """Simple global non-detection"""
        self.assertIsNone(DesktopEnvironment().value)


if __name__ == "__main__":
    unittest.main()
