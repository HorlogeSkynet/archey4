"""Test module for Archey's kernel information detection module"""

import unittest
from unittest.mock import MagicMock, Mock, patch

from archey.configuration import DEFAULT_CONFIG
from archey.entries.kernel import Kernel
from archey.test.entries import HelperMethods


class TestKernelEntry(unittest.TestCase):
    """
    Here, we mock the `platform` module calls and check afterwards
      that the output is correct.
    """

    @patch(
        "archey.entries.kernel.platform.system",
        return_value="Linux",
    )
    @patch(
        "archey.entries.kernel.platform.release",
        return_value="X.Y.Z-R-arch",
    )
    def test_fetch_kernel_release(self, _, __):
        """Verify `platform` module mocking"""
        self.assertEqual(Kernel().value["name"], "Linux")
        self.assertEqual(Kernel().value["release"], "X.Y.Z-R-arch")

    @patch("archey.entries.kernel.urlopen")
    def test_fetch_latest_linux_release(self, urlopen_mock):
        """Check proper JSON decoding and value gathering"""
        urlopen_mock.return_value.__enter__.return_value.read.return_value = b"""\
{
    "latest_stable": {
        "version": "5.10.1"
    },
    "releases": [
        {
            "iseol": false,
            "version": "5.10",
            "moniker": "mainline",
            "source": "https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.10.tar.xz",
            "pgp": "https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.10.tar.sign",
            "released": {
                "timestamp": 1607899290,
                "isodate": "2020-12-13"
            },
            "gitweb": "https://git.kernel.org/torvalds/h/v5.10",
            "changelog": null,
            "diffview": "https://git.kernel.org/torvalds/ds/v5.10/v5.9",
            "patch": {
                "full": "https://cdn.kernel.org/pub/linux/kernel/v5.x/patch-5.10.xz",
                "incremental": null
            }
        },
        {
            "iseol": false,
            "version": "5.10.1",
            "moniker": "stable",
            "source": "https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.10.1.tar.xz",
            "pgp": "https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.10.1.tar.sign",
            "released": {
                "timestamp": 1607970794,
                "isodate": "2020-12-14"
            },
            "gitweb": "https://git.kernel.org/stable/h/v5.10.1",
            "changelog": "https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.10.1",
            "diffview": "https://git.kernel.org/stable/ds/v5.10.1/v5.10",
            "patch": {
                "full": "https://cdn.kernel.org/pub/linux/kernel/v5.x/patch-5.10.1.xz",
                "incremental": null
            }
        }
    ]
}"""
        self.assertEqual(
            Kernel._fetch_latest_linux_release(), "5.10.1"  # pylint: disable=protected-access
        )

    @patch(
        "archey.entries.kernel.platform.system",
        return_value="Java",
    )
    @patch(
        "archey.entries.kernel.platform.release",
        return_value="X.Y.Z-R-arch",
    )
    @patch(
        "archey.entries.kernel.Environment",
        Mock(DO_NOT_TRACK=False),
    )
    def test_non_linux_platform(self, _, __):
        """Check behavior on non-Linux platforms"""
        kernel = Kernel(options={"check_version": True})

        self.assertIsNone(kernel.value["latest"])
        self.assertIsNone(kernel.value["is_outdated"])

    @patch(
        "archey.entries.kernel.platform.release",
        return_value="X.Y.Z-R-arch",
    )
    @patch(
        "archey.entries.kernel.Environment",
        Mock(DO_NOT_TRACK=True),
    )
    def test_do_not_track(self, _):
        """Check `DO_NOT_TRACK` is correctly honored"""
        kernel = Kernel(options={"check_version": True})

        self.assertIsNone(kernel.value["latest"])
        self.assertIsNone(kernel.value["is_outdated"])

    @patch(
        "archey.entries.kernel.platform.release",
        return_value="1.2.3-4-arch",
    )
    @patch(
        "archey.entries.kernel.Kernel._fetch_latest_linux_release",
        side_effect=["1.2.3", "1.3.2"],
    )
    @patch(
        "archey.entries.kernel.platform.system",
        return_value="Linux",
    )
    @patch(
        "archey.entries.kernel.Environment",
        Mock(DO_NOT_TRACK=False),
    )
    @HelperMethods.patch_clean_configuration
    def test_kernel_comparison(self, _, __, ___):
        """Check kernel releases comparison and output templates"""
        output_mock = MagicMock()

        # Only current release (`check_version` disabled by default).
        kernel = Kernel()
        kernel.output(output_mock)
        self.assertEqual(output_mock.append.call_args[0][1], "Linux 1.2.3-4-arch")

        # Current = latest (up to date !).
        kernel = Kernel(options={"check_version": True})
        kernel.output(output_mock)

        self.assertTrue(kernel.value["latest"])
        self.assertIs(kernel.value["is_outdated"], False)
        self.assertEqual(
            output_mock.append.call_args[0][1],
            f"Linux 1.2.3-4-arch ({DEFAULT_CONFIG['default_strings']['latest']})",
        )

        # Current < latest (outdated).
        kernel = Kernel(options={"check_version": True})
        kernel.output(output_mock)

        self.assertTrue(kernel.value["latest"])
        self.assertIs(kernel.value["is_outdated"], True)
        self.assertEqual(
            output_mock.append.call_args[0][1],
            f"Linux 1.2.3-4-arch (1.3.2 {DEFAULT_CONFIG['default_strings']['available']})",
        )


if __name__ == "__main__":
    unittest.main()
