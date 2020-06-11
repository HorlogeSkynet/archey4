"""Test module for Archey's distribution detection module"""

import unittest
from unittest.mock import MagicMock, patch

from archey.entries.distro import Distro
from archey.test.entries import HelperMethods
from archey.constants import DEFAULT_CONFIG


class TestDistroEntry(unittest.TestCase):
    """`Distro` entry simple test cases"""
    @patch(
        'archey.entries.distro.Distributions.get_distro_name',
        return_value='NAME VERSION (CODENAME)'
    )
    @patch(
        'archey.entries.distro.Distro._fetch_architecture',
        return_value='ARCHITECTURE'
    )
    def test_init(self, _, __):
        """Test `Distro` instantiation"""
        self.assertDictEqual(
            Distro().value,
            {
                'name': 'NAME VERSION (CODENAME)',
                'arch': 'ARCHITECTURE'
            }
        )

    @patch(
        'archey.entries.distro.check_output',
        return_value='x86_64\n'  # Imitate `uname` output on AMD64.
    )
    def test_fetch_architecture(self, _):
        """Test `_fetch_architecture` static method"""
        self.assertEqual(
            Distro._fetch_architecture(),  # pylint: disable=protected-access
            'x86_64'
        )

    @patch(
        'archey.entries.distro.check_output',
        return_value='10\n'  # Imitate `getprop` output on Android 10.
    )
    def test_fetch_android_release(self, _):
        """Test `_fetch_android_release` static method"""
        self.assertEqual(
            Distro._fetch_android_release(),  # pylint: disable=protected-access
            'Android 10'
        )

    @patch(
        'archey.entries.distro.Distributions.get_distro_name',
        return_value=None  # Soft-failing : No _pretty_ distribution name found...
    )
    @patch(
        'archey.entries.distro.Distro._fetch_architecture',
        return_value='ARCHITECTURE'
    )
    @patch(
        'archey.entries.distro.Distro._fetch_android_release',
        return_value=None  # Not an Android device either...
    )
    @HelperMethods.patch_clean_configuration
    def test_unknown_distro_output(self, _, __, ___):
        """Test for `distro` and `uname` outputs concatenation"""
        distro = Distro()

        output_mock = MagicMock()
        distro.output(output_mock)

        self.assertDictEqual(
            distro.value,
            {
                'name': None,
                'arch': 'ARCHITECTURE'
            }
        )
        self.assertEqual(
            output_mock.append.call_args[0][1],
            DEFAULT_CONFIG['default_strings']['not_detected'] + ' [ARCHITECTURE]'
        )


if __name__ == '__main__':
    unittest.main()
