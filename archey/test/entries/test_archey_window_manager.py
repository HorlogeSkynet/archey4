"""Test module for Archey's window manager detection module"""

import unittest
from unittest.mock import patch

from archey.configuration import DEFAULT_CONFIG
from archey.entries.window_manager import WindowManager
from archey.test.entries import HelperMethods


@patch(
    "archey.entries.desktop_environment.platform.system",
    return_value="Linux",
)
class TestWindowManagerEntry(unittest.TestCase):
    """
    Here, we mock the `check_output` call and check afterwards
      that the output is correct.
    We've to test the case where `wmctrl` is not installed too.
    """

    @patch(
        "archey.entries.window_manager.check_output",
        return_value="""\
Name: WINDOW MANAGER
Class: N/A
PID: N/A
Window manager's "showing the desktop" mode: OFF
""",
    )
    def test_wmctrl(self, _, __):
        """Test `wmctrl` output parsing"""
        self.assertEqual(WindowManager().value["name"], "WINDOW MANAGER")

    @patch(
        "archey.entries.window_manager.check_output",
        side_effect=FileNotFoundError(),  # `wmctrl` call will fail
    )
    @patch(
        "archey.entries.window_manager.Processes.list",
        (  # Fake running processes list
            "some",
            "awesome",  # Match !
            "programs",
            "running",
            "here",
        ),
    )
    @patch(
        "archey.entries.desktop_environment.os.getenv",
        return_value="wayland",
    )
    def test_no_wmctrl_match(self, _, __, ___):
        """Test basic detection based on a (fake) processes list"""
        window_manager = WindowManager()
        self.assertEqual(window_manager.value["name"], "Awesome")
        self.assertEqual(window_manager.value["display_server_protocol"], "Wayland")

    @patch(
        "archey.entries.window_manager.check_output",
        side_effect=FileNotFoundError(),  # `wmctrl` call will fail
    )
    @patch(
        "archey.entries.window_manager.Processes.list",
        (  # Fake running processes list
            "some",
            "weird",  # Mismatch !
            "programs",
            "running",
            "here",
        ),
    )
    @HelperMethods.patch_clean_configuration
    def test_no_wmctrl_mismatch(self, _, __):
        """Test (non-detection) when processes list do not contain any known value"""
        window_manager = WindowManager()
        self.assertIsNone(window_manager.value["name"])
        self.assertEqual(
            str(window_manager),
            DEFAULT_CONFIG["default_strings"]["not_detected"],
        )


if __name__ == "__main__":
    unittest.main()
