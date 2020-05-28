"""Test module for Archey's distribution detection module"""

import unittest
from unittest.mock import MagicMock, patch

from archey.entries.distro import Distro


class TestDistroEntry(unittest.TestCase):
    """`Distro` entry simple test cases"""
    @patch(
        'archey.entries.distro.check_output',  # `uname` output
        return_value="""\
ARCHITECTURE
""")
    @patch(
        'archey.entries.distro.Distributions.get_distro_name',
        return_value="""\
NAME VERSION (CODENAME)\
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
        'archey.entries.distro.check_output',  # `uname` output
        return_value="""\
ARCHITECTURE
""")
    @patch(
        'archey.entries.distro.Distributions.get_distro_name',
        return_value=None  # Soft-failing : No _pretty_ distribution name found...
    )
    @patch(
        'archey.configuration.Configuration.get',
        return_value={'not_detected': 'Not detected'}
    )
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
            'Not detected [ARCHITECTURE]'
        )


if __name__ == '__main__':
    unittest.main()
