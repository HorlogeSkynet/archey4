"""Test module for Archey's desktop environment detection module"""

import unittest
from unittest.mock import mock_open, patch

from archey.entries.desktop_environment import DesktopEnvironment


class TestDesktopEnvironmentEntry(unittest.TestCase):
    """DesktopEnvironment test cases"""

    @patch(
        "archey.entries.desktop_environment.platform.system",
        return_value="Windows",
    )
    @patch(
        "archey.entries.desktop_environment.platform.win32_ver",
        return_value=("10", "10.0.19042", "SP0", "0", "0", "Workstation"),
    )
    def test_platform_detection(self, _, __) -> None:
        """_platform_detection simple test"""
        self.assertEqual(
            DesktopEnvironment._platform_detection(),  # pylint: disable=protected-access
            "Metro",
        )

    @patch(
        "archey.entries.desktop_environment.os.getenv",
        side_effect=[
            "GNOME-Flashback:GNOME",  # XDG_CURRENT_DESKTOP
        ],
    )
    def test_environment_detection_1(self, _) -> None:
        """_environment_detection XDG_CURRENT_DESKTOP (normalization) test"""
        self.assertEqual(
            DesktopEnvironment._environment_detection(),  # pylint: disable=protected-access
            "GNOME Flashback",
        )

    @patch(
        "archey.entries.desktop_environment.os.getenv",
        side_effect=[
            "",  # XDG_CURRENT_DESKTOP
        ],
    )
    @patch.dict(
        "archey.entries.desktop_environment.os.environ",
        {
            "GNOME_DESKTOP_SESSION_ID": "this-is-deprecated",
        },
        clear=True,
    )
    def test_environment_detection_2(self, _) -> None:
        """_environment_detection against environment-specific variables"""
        self.assertEqual(
            DesktopEnvironment._environment_detection(),  # pylint: disable=protected-access
            "GNOME",
        )

    @patch(
        "archey.entries.desktop_environment.os.getenv",
        side_effect=[
            "",  # XDG_CURRENT_DESKTOP
            "Xfce Session",  # DE
        ],
    )
    @patch.dict(
        "archey.entries.desktop_environment.os.environ",
        {},
        clear=True,
    )
    def test_environment_detection_3(self, _) -> None:
        """_environment_detection against legacy `DE` environment variable"""
        self.assertEqual(
            DesktopEnvironment._environment_detection(),  # pylint: disable=protected-access
            "Xfce",
        )

    @patch(
        "archey.entries.desktop_environment.os.getenv",
        side_effect=[
            "",  # XDG_CURRENT_DESKTOP
            "",  # DE
            "lumina",  # SESSION_DESKTOP
        ],
    )
    @patch.dict(
        "archey.entries.desktop_environment.os.environ",
        {},
        clear=True,
    )
    def test_environment_detection_4(self, _) -> None:
        """_environment_detection against legacy `SESSION_DESKTOP` environment variable"""
        self.assertEqual(
            DesktopEnvironment._environment_detection(),  # pylint: disable=protected-access
            "Lumina",
        )

    @patch(
        "archey.entries.desktop_environment.os.getenv",
        side_effect=[
            "",  # XDG_CURRENT_DESKTOP
            "",  # DE
            "/usr/share/xsessions/retro-home.desktop",  # SESSION_DESKTOP
        ],
    )
    @patch.dict(
        "archey.entries.desktop_environment.os.environ",
        {},
        clear=True,
    )
    @patch(
        "archey.entries.desktop_environment.open",
        mock_open(
            read_data="""\
[Desktop Entry]
Name=Retro Home
Comment=Your home for retro gaming
Exec=/usr/local/bin/retro-home
TryExec=ludo
Type=Application
DesktopNames=Retro-Home;Ludo;

no-value-option
"""
        ),
    )
    def test_environment_detection_4_desktop_file(self, _) -> None:
        """_environment_detection against legacy `SESSION_DESKTOP` pointing to a desktop file"""
        self.assertEqual(
            DesktopEnvironment._environment_detection(),  # pylint: disable=protected-access
            "Retro-Home",
        )

    @patch(
        "archey.entries.desktop_environment.os.getenv",
        side_effect=[
            "",  # XDG_CURRENT_DESKTOP
            "",  # DE
            "/usr/share/xsessions/emacsdesktop.desktop",  # SESSION_DESKTOP
        ],
    )
    @patch.dict(
        "archey.entries.desktop_environment.os.environ",
        {},
        clear=True,
    )
    @patch(
        "archey.entries.desktop_environment.open",
        mock_open(
            read_data="""\
[Desktop Entry]
Name=EmacsDesktop
Comment=EmacsDesktop
Exec=/usr/share/xsessions/emacsdesktop.sh
TryExec=emacs
Type=Application
X-LightDM-DesktopName=EmacsDesktop

[Desktop Entry]
Comment="Just messing with ConfigParser by adding section and option duplicates"
"""
        ),
    )
    def test_environment_detection_4_desktop_file_fallback(self, _) -> None:
        """_environment_detection against legacy `SESSION_DESKTOP` pointing to a desktop file"""
        self.assertEqual(
            DesktopEnvironment._environment_detection(),  # pylint: disable=protected-access
            "EmacsDesktop",
        )

    @patch(
        "archey.entries.desktop_environment.os.getenv",
        side_effect=[
            "",  # XDG_CURRENT_DESKTOP
            "",  # DE
            "/usr/share/xsessions/foo.desktop",  # SESSION_DESKTOP
        ],
    )
    @patch.dict(
        "archey.entries.desktop_environment.os.environ",
        {},
        clear=True,
    )
    @patch(
        "archey.entries.desktop_environment.open",
        mock_open(
            read_data="""\
[Desktop Entry]
Name=FooDesktop
"""
        ),
    )
    def test_environment_detection_4_bad_desktop_file(self, _) -> None:
        """_environment_detection against legacy `SESSION_DESKTOP` pointing to a desktop file"""
        self.assertIsNone(
            DesktopEnvironment._environment_detection(),  # pylint: disable=protected-access
        )

    @patch(
        "archey.entries.desktop_environment.Processes.list",
        (
            "do",
            "you",
            "like",
            "cinnamon",
            "tea",
        ),
    )
    def test_process_detection(self) -> None:
        """_process_detection simple test"""
        self.assertEqual(
            DesktopEnvironment._process_detection(),  # pylint: disable=protected-access
            "Cinnamon",
        )


if __name__ == "__main__":
    unittest.main()
