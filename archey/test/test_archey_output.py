"""Test module for `archey.output`"""

import unittest
from unittest.mock import patch

from archey.colors import Colors
from archey.constants import COLOR_DICT
from archey.output import Output
from archey.distributions import Distributions


class TestOutputUtil(unittest.TestCase):
    """
    Simple test cases to check the behavior of `Output` main class.
    """
    @patch(
        'archey.output.check_output',
        return_value='X.Y.Z-R-ARCH\n'
    )
    @patch(
        'archey.output.distro.id',
        return_value='debian'
    )
    @patch(
        'archey.output.distro.os_release_attr',
        return_value=''
    )
    def test_init_known_distro(self, _, __, ___):
        """Test known distribution output"""
        output = Output()

        self.assertEqual(
            output._distribution,  # pylint: disable=protected-access
            Distributions.DEBIAN
        )

    @patch(
        'archey.output.check_output',
        return_value='X.Y.Z-R-ARCH\n'
    )
    @patch(
        'archey.output.distro.id',
        return_value='an-unknown-distro-id'
    )
    @patch(
        'archey.output.distro.like',
        return_value=''  # No `ID_LIKE` specified.
    )
    @patch(
        'archey.output.distro.os_release_attr',
        return_value=''
    )
    def test_init_unknown_distro(self, _, __, ___, ____):
        """Test unknown distribution output"""
        output = Output()

        self.assertEqual(
            output._distribution,  # pylint: disable=protected-access
            Distributions.LINUX
        )

    @patch(
        'archey.output.check_output',
        return_value='X.Y.Z-R-ARCH\n'
    )
    @patch(
        'archey.output.distro.id',
        return_value=''  # Unknown distribution.
    )
    @patch(
        'archey.output.distro.like',
        return_value='ubuntu'  # Oh, it's actually an Ubuntu-based one !
    )
    @patch(
        'archey.output.distro.os_release_attr',
        return_value=''
    )
    def test_init_distro_like(self, _, __, ___, ____):
        """Test distribution matching from the `os-release`'s `ID_LIKE` option"""
        output = Output()

        self.assertEqual(
            output._distribution,  # pylint: disable=protected-access
            Distributions.UBUNTU
        )

    @patch(
        'archey.output.check_output',
        return_value='X.Y.Z-R-ARCH\n'
    )
    @patch(
        'archey.output.distro.id',
        return_value=''  # Unknown distribution.
    )
    @patch(
        'archey.output.distro.like',
        return_value='linuxmint debian'  # Oh, what do we got there ?!
    )
    @patch(
        'archey.output.distro.os_release_attr',
        return_value=''
    )
    def test_init_distro_like_multiple(self, _, __, ___, ____):
        """Test distribution matching from the `os-release`'s `ID_LIKE` option (multiple entries)"""
        output = Output()

        self.assertEqual(
            output._distribution,  # pylint: disable=protected-access
            Distributions.LINUX_MINT
        )

    @patch(
        'archey.output.check_output',
        return_value='X.Y.Z-R-ARCH\n'
    )
    @patch(
        'archey.output.distro.id',
        return_value=''  # Unknown distribution.
    )
    @patch(
        'archey.output.distro.like',
        return_value=''  # No `ID_LIKE` either...
    )
    @patch(
        'archey.output.distro.os_release_attr',
        return_value=''
    )
    def test_init_both_distro_calls_fail(self, _, __, ___, ____):
        """Test distribution fall-back when `distro` soft-fail two times"""
        output = Output()

        self.assertEqual(
            output._distribution,  # pylint: disable=protected-access
            Distributions.LINUX
        )

    @patch(
        'archey.output.check_output',
        return_value='X.Y.Z-R-Microsoft\n'
    )
    @patch(
        'archey.output.distro.os_release_attr',
        return_value=''
    )
    def test_init_windows_subsystem(self, _, __):
        """Test output for Windows Subsystem Linux"""
        output = Output()

        self.assertEqual(
            output._distribution,  # pylint: disable=protected-access
            Distributions.WINDOWS
        )

    @patch(
        'archey.output.check_output',
        return_value='X.Y.Z-R-ARCH\n'
    )
    @patch(
        'archey.output.distro.id',
        return_value='debian'  # Make Debian being selected.
    )
    @patch.dict(
        'archey.output.COLOR_DICT',
        {Distributions.DEBIAN: ['COLOR_0']}
    )
    @patch(
        'archey.output.Configuration.get',
        return_value={'honor_ansi_color': False}
    )
    def test_append_regular(self, _, __, ___):
        """Test the `append` method, for new entries"""
        output = Output()
        output.append('KEY', 'VALUE')

        self.assertListEqual(
            output._results,  # pylint: disable=protected-access
            ['COLOR_0KEY:{clear} VALUE'.format(clear=Colors.CLEAR)]
        )

    @patch(
        'archey.output.check_output',
        return_value='X.Y.Z-R-ARCH\n'
    )
    @patch(
        'archey.output.distro.id',
        return_value='slackware'  # Make Slackware being selected.
    )
    @patch(
        'archey.output.distro.os_release_attr',
        return_value='ANSI_COLOR'
    )
    @patch(
        'archey.output.Configuration.get',
        return_value={'honor_ansi_color': True}
    )
    def test_append_ansi_color(self, _, __, ___, ____):
        """Check that `Output` honor `ANSI_COLOR` as required"""
        output = Output()

        # Slackware logo got three colors, so let's check they have been correctly replaced.
        self.assertTrue(
            all('ANSI_COLOR' in str(color) for color in output._colors_palette)  # pylint: disable=protected-access
        )
        self.assertEqual(
            len(output._colors_palette),  # pylint: disable=protected-access
            len(COLOR_DICT[Distributions.SLACKWARE])
        )

    @patch(
        'archey.output.check_output',
        return_value='X.Y.Z-R-Microsoft\n'  # Make WSL detection pass.
    )
    @patch(
        'archey.output.distro.os_release_attr',
        return_value='ANSI_COLOR'
    )
    @patch(
        'archey.output.Configuration.get',
        return_value={'honor_ansi_color': False}
    )
    def test_append_no_ansi_color(self, _, __, ___):
        """Check that `Output` DOES NOT honor `ANSI_COLOR` when specified"""
        output = Output()

        # Check that NO colors have been replaced (actually, that the list is the same as before).
        self.assertFalse(
            any('ANSI_COLOR' in str(color) for color in output._colors_palette)  # pylint: disable=protected-access
        )
        self.assertListEqual(
            output._colors_palette,  # pylint: disable=protected-access
            COLOR_DICT[Distributions.WINDOWS]
        )

    @patch(
        'archey.output.check_output',
        return_value='X.Y.Z-R-ARCH\n'
    )
    @patch(
        'archey.output.distro.id',
        return_value='debian'  # Make Debian being selected.
    )
    @patch(
        'archey.output.distro.os_release_attr',
        return_value=''
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
{c[0]} {r[17]} {c[1]}\
"""
        }
    )
    @patch(
        'archey.output.print',
        return_value=None,  # Let's nastily mute class' outputs.
        create=True
    )
    def test_centered_output(self, _, __, ___, ____):
        """Test how the `output` method handles centering operations"""
        output = Output()

        # # ODD ENTRIES NUMBER # #
        output._results = [  # pylint: disable=protected-access
            '1',
            '2',
            '3'
        ]
        # Let's run the algorithm !
        output.output()
        self.assertListEqual(
            output._results,  # pylint: disable=protected-access
            [
                '', '', '', '', '', '', '',
                '1', '2', '3',
                '', '', '', '', '', '', '', ''
            ]
        )

        # # EVEN ENTRIES NUMBER # #
        output._results = [  # pylint: disable=protected-access
            '1',
            '2',
            '3',
            '4'
        ]
        output.output()
        self.assertListEqual(
            output._results,  # pylint: disable=protected-access
            [
                '', '', '', '', '', '', '',
                '1', '2', '3', '4',
                '', '', '', '', '', '', ''
            ]
        )

        # # FULL ENTRIES # #
        output._results = [  # pylint: disable=protected-access
            '1', '2', '3', '4', '5', '6',
            '7', '8', '9', '10', '11', '12',
            '13', '14', '15', '16', '17', '18'
        ]
        output.output()
        self.assertListEqual(
            output._results,  # pylint: disable=protected-access
            [
                '1', '2', '3', '4', '5', '6',
                '7', '8', '9', '10', '11', '12',
                '13', '14', '15', '16', '17', '18'
            ]
        )

        # # NO ENTRY # #
        output._results = []  # pylint: disable=protected-access
        output.output()
        self.assertListEqual(
            output._results,  # pylint: disable=protected-access
            [
                '', '', '', '', '', '',
                '', '', '', '', '', '',
                '', '', '', '', '', '',
            ]
        )


if __name__ == '__main__':
    unittest.main()
