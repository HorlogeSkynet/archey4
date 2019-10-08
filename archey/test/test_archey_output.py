"""Test module for `archey.output`"""

import unittest
from unittest.mock import patch

from archey.output import Output
from archey.distributions import Distributions


class TestOutputUtil(unittest.TestCase):
    """
    Simple test cases to check the behavior of `Output` main class.
    """
    @patch(
        'archey.output.check_output',
        return_value="""\
'X.Y.Z-R-ARCH'
""")
    @patch(
        'archey.output.distro.id',
        return_value="""\
debian\
""")
    def test_init_known_distro(self, _, __):
        """Test known distribution output"""
        output = Output()

        self.assertEqual(
            output.distribution,
            Distributions.DEBIAN
        )

    @patch(
        'archey.output.check_output',
        return_value="""\
X.Y.Z-R-ARCH
""")
    @patch(
        'archey.output.distro.id',
        return_value="""\
an-unknown-distro-id\
""")
    def test_init_unknown_distro(self, _, __):
        """Test unknown distribution output"""
        output = Output()

        self.assertEqual(
            output.distribution,
            Distributions.LINUX
        )

    @patch(
        'archey.output.check_output',
        return_value="""\
X.Y.Z-R-Microsoft
""")
    @patch(
        'archey.output.distro.id',
        return_value="""\
opensuse\
""")
    def test_init_windows_subsystem(self, _, __):
        """Test output for Windows Subsystem Linux"""
        output = Output()

        self.assertEqual(
            output.distribution,
            Distributions.WINDOWS
        )

    @patch.dict(
        'archey.output.COLOR_DICT',
        {
            Distributions.DEBIAN: ['COLOR_0', 'COLOR_1'],
            'clear': 'CLEAR'
        }
    )
    def test_append(self):
        """Test the `append` method, for new entries"""
        output = Output()

        # Let's manually set the distribution for the test case...
        output.distribution = Distributions.DEBIAN

        output.append('KEY', 'VALUE')

        self.assertEqual(
            output.results,
            ['COLOR_1KEY:CLEAR VALUE']
        )

    @patch.dict(
        'archey.output.COLOR_DICT',
        {
            Distributions.DEBIAN: ['COLOR_0', 'COLOR_1'],
            'clear': 'CLEAR'
        }
    )
    @patch.dict(
        'archey.output.LOGOS_DICT',
        {
            Distributions.DEBIAN: """\
{c[0]} {r[0]} {c[1]}
{c[0]} {r[1]} {c[1]}
{c[0]} {r[2]} {c[1]}
{c[0]} {r[3]} {c[1]}
{c[0]} {r[4]} {c[1]}
{c[0]} {r[5]} {c[1]}
{c[0]} {r[6]} {c[1]}
{c[0]} {r[7]} {c[1]}
{c[0]} {r[8]} {c[1]}
{c[0]} {r[9]} {c[1]}
{c[0]} {r[10]} {c[1]}
{c[0]} {r[11]} {c[1]}
{c[0]} {r[12]} {c[1]}
{c[0]} {r[13]} {c[1]}
{c[0]} {r[14]} {c[1]}
{c[0]} {r[15]} {c[1]}
{c[0]} {r[16]} {c[1]}
{c[0]} {r[17]} {c[1]}
""",
            'clear': 'CLEAR'
        }
    )
    @patch(
        'archey.output.print',
        return_value=None,  # Let's badly mute the class outputs
        create=True
    )
    def test_centered_output(self, _):
        """Test how the `output` method handle centering operations"""
        output = Output()

        # Let's manually set the distribution for the test case...
        output.distribution = Distributions.DEBIAN

        # # ODD ENTRIES NUMBER # #
        output.results = [
            '1',
            '2',
            '3'
        ]
        # Let's run the algorithm !
        output.output()
        self.assertListEqual(
            output.results,
            [
                '', '', '', '', '', '', '',
                '1', '2', '3',
                '', '', '', '', '', '', '', ''
            ]
        )

        # # EVEN ENTRIES NUMBER # #
        output.results = [
            '1',
            '2',
            '3',
            '4'
        ]
        output.output()
        self.assertListEqual(
            output.results,
            [
                '', '', '', '', '', '', '',
                '1', '2', '3', '4',
                '', '', '', '', '', '', ''
            ]
        )

        # # FULL ENTRIES # #
        output.results = [
            '1', '2', '3', '4', '5', '6',
            '7', '8', '9', '10', '11', '12',
            '13', '14', '15', '16', '17', '18'
        ]
        output.output()
        self.assertListEqual(
            output.results,
            [
                '1', '2', '3', '4', '5', '6',
                '7', '8', '9', '10', '11', '12',
                '13', '14', '15', '16', '17', '18'
            ]
        )

        # # NO ENTRY # #
        output.results = []
        output.output()
        self.assertListEqual(
            output.results,
            [
                '', '', '', '', '', '',
                '', '', '', '', '', '',
                '', '', '', '', '', '',
            ]
        )


if __name__ == '__main__':
    unittest.main()
