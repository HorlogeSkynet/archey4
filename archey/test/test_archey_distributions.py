"""Test module for `archey.distributions`"""

import unittest
from unittest.mock import patch

from archey.distributions import Distributions


class TestDistributionsUtil(unittest.TestCase):
    """
    Test cases for the `Distributions` (enumeration / utility) class.
    """
    def test_constant_values(self):
        """Test enumeration member instantiation from value"""
        self.assertEqual(Distributions('debian'), Distributions.DEBIAN)
        self.assertRaises(ValueError, Distributions, 'unknown')

        # Check `get_distribution_identifiers` consistency.
        distribution_identifiers = Distributions.get_distribution_identifiers()
        self.assertTrue(isinstance(distribution_identifiers, list))
        self.assertTrue(all(isinstance(i, str) for i in distribution_identifiers))

    @patch(
        'archey.distributions.sys.platform',
        'win32'
    )
    def test_run_detection_windows(self):
        """Test output for Windows"""
        self.assertEqual(
            Distributions.run_detection(),
            Distributions.WINDOWS
        )

    @patch(
        'archey.distributions.sys.platform',
        'linux'
    )
    @patch(
        'archey.distributions.check_output',
        return_value=b'X.Y.Z-R-Microsoft\n'
    )
    def test_run_detection_windows_subsystem(self, _):
        """Test output for Windows Subsystem Linux"""
        self.assertEqual(
            Distributions.run_detection(),
            Distributions.WINDOWS
        )

    @patch(
        'archey.distributions.sys.platform',
        'linux'
    )
    @patch(
        'archey.distributions.check_output',
        return_value=b'X.Y.Z-R-ARCH\n'
    )
    @patch(
        'archey.distributions.distro.id',
        return_value='debian'
    )
    @patch(
        'archey.distributions.os.path.isfile',  # Emulate a "regular" Debian file-system.
        return_value=False                      # Any additional check will fail.
    )
    def test_run_detection_known_distro_id(self, _, __, ___):
        """Test known distribution output"""
        self.assertEqual(
            Distributions.run_detection(),
            Distributions.DEBIAN
        )

    @patch(
        'archey.distributions.sys.platform',
        'linux'
    )
    @patch(
        'archey.distributions.check_output',
        return_value=b'X.Y.Z-R-ARCH\n'
    )
    @patch(
        'archey.distributions.distro.id',
        return_value='an-unknown-distro-id'
    )
    @patch(
        'archey.distributions.distro.like',
        return_value=''  # No `ID_LIKE` specified.
    )
    @patch(
        'archey.distributions.os.path.isdir',  # Make Android detection fails.
        return_value=False
    )
    def test_run_detection_unknown_distro_id(self, _, __, ___, ____):
        """Test unknown distribution output"""
        self.assertEqual(
            Distributions.run_detection(),
            Distributions.LINUX
        )

    @patch(
        'archey.distributions.sys.platform',
        'linux'
    )
    @patch(
        'archey.distributions.check_output',
        return_value=b'X.Y.Z-R-ARCH\n'
    )
    @patch(
        'archey.distributions.distro.id',
        return_value=''  # Unknown distribution.
    )
    @patch(
        'archey.distributions.distro.like',
        return_value='ubuntu'  # Oh, it's actually an Ubuntu-based one !
    )
    def test_run_detection_known_distro_like(self, _, __, ___):
        """Test distribution matching from the `os-release`'s `ID_LIKE` option"""
        self.assertEqual(
            Distributions.run_detection(),
            Distributions.UBUNTU
        )

    @patch(
        'archey.distributions.sys.platform',
        'linux'
    )
    @patch(
        'archey.distributions.check_output',
        return_value=b'X.Y.Z-R-ARCH\n'
    )
    @patch(
        'archey.distributions.distro.id',
        return_value=''  # Unknown distribution.
    )
    @patch(
        'archey.distributions.distro.like',
        return_value='an-unknown-distro-id arch'  # Hmmm, an unknown Arch-based...
    )
    def test_run_detection_distro_like_second(self, _, __, ___):
        """Test distribution matching from the `os-release`'s `ID_LIKE` option (second candidate)"""
        self.assertEqual(
            Distributions.run_detection(),
            Distributions.ARCH_LINUX
        )

    @patch(
        'archey.distributions.sys.platform',
        'linux'
    )
    @patch(
        'archey.distributions.check_output',
        return_value=b'X.Y.Z-R-ARCH\n'
    )
    @patch(
        'archey.distributions.distro.id',
        return_value=''  # Unknown distribution.
    )
    @patch(
        'archey.distributions.distro.like',
        return_value=''  # No `ID_LIKE` either...
    )
    @patch(
        'archey.distributions.os.path.isdir',  # Make Android detection fails.
        return_value=False
    )
    def test_run_detection_both_distro_calls_fail(self, _, __, ___, ____):
        """Test distribution fall-back when `distro` soft-fail two times"""
        self.assertEqual(
            Distributions.run_detection(),
            Distributions.LINUX
        )

    @patch(
        'archey.distributions.sys.platform',
        'linux'
    )
    @patch(
        'archey.distributions.check_output',
        return_value=b'X.Y.Z-R-ARCH\n'
    )
    @patch(
        'archey.distributions.distro.id',
        return_value='debian'
    )
    @patch(
        'archey.distributions.os.path.isfile',  # Emulate a CrunchBang file-system.
        side_effect=(
            lambda file_path: file_path == '/etc/lsb-release-crunchbang'
        )
    )
    def test_run_detection_specific_crunchbang(self, _, __, ___):
        """Test CrunchBang specific detection"""
        self.assertEqual(
            Distributions.run_detection(),
            Distributions.CRUNCHBANG
        )

    @patch(
        'archey.distributions.Distributions._detection_logic',
        return_value=None  # Base detection logic soft-fails...
    )
    @patch(
        'archey.distributions.os.path.isdir',  # Emulate an Android file-system.
        side_effect=(
            lambda dir_path: dir_path.startswith('/system/') and dir_path.endswith('app')
        )
    )
    def test_run_detection_specific_android(self, _, __):
        """Test Android specific detection"""
        self.assertEqual(
            Distributions.run_detection(),
            Distributions.ANDROID
        )

    @patch(
        'archey.distributions.distro.name',
        side_effect=[
            'Debian GNU/Linux 10 (buster)',
            ''  # Second call will (soft-)fail.
        ]
    )
    def test_get_distro_name(self, _):
        """Very basic test cases for `get_distro_name` static method"""
        self.assertEqual(
            Distributions.get_distro_name(),
            'Debian GNU/Linux 10 (buster)'
        )
        self.assertIsNone(Distributions.get_distro_name())

    @patch(
        'archey.distributions.distro.os_release_attr',
        side_effect=[
            '33;1',
            ''  # Second call will (soft-)fail.
        ]
    )
    def test_get_ansi_color(self, _):
        """Very basic test cases for `get_ansi_color` static method"""
        self.assertEqual(
            Distributions.get_ansi_color(),
            '33;1'
        )
        self.assertIsNone(Distributions.get_ansi_color())
