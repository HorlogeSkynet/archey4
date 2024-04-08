"""Test module for Archey's distribution detection module"""

import unittest
from unittest.mock import patch

from archey.entries.distro import Distro


class TestDistroEntry(unittest.TestCase):
    """`Distro` entry simple test cases"""

    @patch(
        "archey.entries.distro.check_output",
        return_value="10\n",  # Imitate `getprop` output on Android 10.
    )
    def test_fetch_android_release(self, _):
        """Test `_fetch_android_release` static method"""
        self.assertEqual(
            Distro._fetch_android_release(),  # pylint: disable=protected-access
            "Android 10",
        )

    @patch(
        "archey.entries.distro.platform.mac_ver",
        side_effect=[
            ("", ("", "", ""), ""),  # Darwin case.
            ("11.1", ("foo", "bar", "baz"), "x86_64"),  # macOS case.
        ],
    )
    @patch(
        "archey.entries.distro.platform.release",
        return_value="20.2.0",  # Darwin release.
    )
    def test_fetch_darwin_release(self, _, __):
        """Test `_fetch_darwin_release` static method"""
        self.assertEqual(
            Distro._fetch_darwin_release(),  # pylint: disable=protected-access
            "Darwin 20.2.0",
        )
        self.assertEqual(
            Distro._fetch_darwin_release(),  # pylint: disable=protected-access
            "macOS 11.1",
        )


if __name__ == "__main__":
    unittest.main()
