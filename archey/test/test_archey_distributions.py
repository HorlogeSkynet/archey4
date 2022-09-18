"""Test module for `archey.distributions`"""

import unittest
from unittest.mock import patch

from archey.distributions import Distributions


class TestDistributions(unittest.TestCase):
    """
    Test cases for the `Distributions` (enumeration / utility) class.
    """

    def setUp(self):
        # Clear cache filled by `functools.lru_cache` decorator.
        Distributions.get_local.cache_clear()

    def test_constant_values(self):
        """Test enumeration member instantiation from value"""
        self.assertEqual(Distributions("debian"), Distributions.DEBIAN)
        self.assertRaises(ValueError, Distributions, "unknown")

        # Check `get_identifiers` consistency.
        distributions_identifiers = Distributions.get_identifiers()
        self.assertTrue(isinstance(distributions_identifiers, list))
        self.assertTrue(all(isinstance(i, str) for i in distributions_identifiers))

    @patch("archey.distributions.platform.system", return_value="Windows")
    def test_get_local_windows(self, _):
        """Test output for Windows"""
        self.assertEqual(Distributions.get_local(), Distributions.WINDOWS)

    @patch("archey.distributions.platform.system", return_value="Linux")
    @patch("archey.distributions.distro.id", return_value="debian")
    @patch(
        "archey.distributions.os.path.isfile",  # Emulate a "regular" Debian file-system.
        return_value=False,  # Any additional check will fail.
    )
    def test_get_local_known_distro_id(self, _, __, ___):
        """Test known distribution output"""
        self.assertEqual(Distributions.get_local(), Distributions.DEBIAN)

    @patch("archey.distributions.platform.system", return_value="Linux")
    @patch("archey.distributions.distro.id", return_value="an-unknown-distro-id")
    @patch("archey.distributions.distro.like", return_value="")  # No `ID_LIKE` specified.
    @patch(
        "archey.distributions.os.path.isdir", return_value=False  # Make Android detection fails.
    )
    def test_get_local_unknown_distro_id(self, _, __, ___, ____):
        """Test unknown distribution output"""
        self.assertEqual(Distributions.get_local(), Distributions.LINUX)

    @patch("archey.distributions.platform.system", return_value="Linux")
    @patch("archey.distributions.distro.id", return_value="")  # Unknown distribution.
    @patch(
        "archey.distributions.distro.like",
        return_value="ubuntu",  # Oh, it's actually an Ubuntu-based one !
    )
    def test_get_local_known_distro_like(self, _, __, ___):
        """Test distribution matching from the `os-release`'s `ID_LIKE` option"""
        self.assertEqual(Distributions.get_local(), Distributions.UBUNTU)

    @patch("archey.distributions.platform.system", return_value="Linux")
    @patch("archey.distributions.distro.id", return_value="")  # Unknown distribution.
    @patch(
        "archey.distributions.distro.like",
        return_value="an-unknown-distro-id arch",  # Hmmm, an unknown Arch-based...
    )
    def test_get_local_distro_like_second(self, _, __, ___):
        """Test distribution matching from the `os-release`'s `ID_LIKE` option (second candidate)"""
        self.assertEqual(Distributions.get_local(), Distributions.ARCH)

    @patch(
        "archey.distributions.platform.system",
        return_value="Darwin",  # Mostly used by our second run.
    )
    @patch(
        "archey.distributions.distro.id",
        side_effect=[
            "darwin",  # First detection will succeed.
            "",  # Second detection will fail.
        ],
    )
    @patch("archey.distributions.distro.like", return_value="")  # No `ID_LIKE` here.
    def test_darwin_detection(self, _, __, ___):
        """Test OS detection for Darwin"""
        # Detection based on `distro`.
        self.assertEqual(Distributions.get_local(), Distributions.DARWIN)

        # Detection based on `platform`.
        self.assertEqual(Distributions.get_local(), Distributions.DARWIN)

    @patch(
        "archey.distributions.distro.name",
        side_effect=[
            "Debian GNU/Linux 10 (buster)",
            "",  # Second call will (soft-)fail.
        ],
    )
    def test_get_distro_name(self, _):
        """Very basic test cases for `get_distro_name` static method"""
        self.assertEqual(Distributions.get_distro_name(), "Debian GNU/Linux 10 (buster)")
        self.assertIsNone(Distributions.get_distro_name())

    @patch(
        "archey.distributions.distro.os_release_attr",
        side_effect=[
            "33;1",
            "",
        ],  # Second call will (soft-)fail.
    )
    def test_get_ansi_color(self, _):
        """Very basic test cases for `get_ansi_color` static method"""
        self.assertEqual(Distributions.get_ansi_color(), "33;1")
        self.assertIsNone(Distributions.get_ansi_color())
