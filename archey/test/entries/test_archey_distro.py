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
        return_value="""\
NAME VERSION (CODENAME)\
""")
    @patch(
        'archey.entries.distro.check_output',  # `uname` output
        return_value="""\
ARCHITECTURE
""")
    def test_ok(self, _, __):
        """Test for `distro` and `uname` retrievals"""
        self.assertDictEqual(
            Distro().value,
            {
                'name': 'NAME VERSION (CODENAME)',
                'arch': 'ARCHITECTURE'
            }
        )

    @patch(
        'archey.entries.distro.Distributions.get_distro_name',
        return_value=None  # Soft-failing : No _pretty_ distribution name found...
    )
    @patch(
        'archey.entries.distro.check_output',
        side_effect=[
            '10\n',           # Imitate Android 10 output for `getprop` execution.
            'ARCHITECTURE\n'  # `uname` output.
        ]
    )
    def test_android_device(self, _, __):
        """Test `value` format on Android devices"""
        self.assertEqual(
            Distro().value,
            {
                'name': 'Android 10',
                'arch': 'ARCHITECTURE'
            }
        )

    @patch(
        'archey.entries.distro.Distributions.get_distro_name',
        return_value=None  # Soft-failing : No _pretty_ distribution name found...
    )
    @patch(
        'archey.entries.distro.Distro._fetch_android_release',
        return_value=None  # Not an Android device either...
    )
    @patch(
        'archey.entries.distro.check_output',
        return_value='ARCHITECTURE\n'  # `uname` output.
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
