"""Test module for `archey.output`"""

import json
import unittest
from unittest.mock import patch, Mock
from collections import namedtuple

from archey.colors import Colors
from archey.constants import COLORS_DICT
from archey.output import Output
from archey.distributions import Distributions


@patch(
    'archey.colors.NO_COLOR',
    False  # By default, colors won't be disabled.
)
class TestOutputUtil(unittest.TestCase):
    """
    Simple test cases to check the behavior of the `Output` class.
    """
    @patch(
        'archey.output.Distributions.run_detection',
        return_value=Distributions.DEBIAN  # Make Debian being selected.
    )
    @patch.dict(
        'archey.output.COLORS_DICT',
        {Distributions.DEBIAN: ['COLOR_0']}
    )
    @patch(
        'archey.output.Configuration.get',  # Disable `honor_ansi_color` option.
        side_effect=(
            lambda config_key: not (config_key == 'honor_ansi_color')
        )
    )
    def test_append_regular(self, _, __):
        """Test the `append` method, for new entries"""
        output = Output()
        output.append('KEY', 'VALUE')

        self.assertListEqual(
            output._results,  # pylint: disable=protected-access
            ['COLOR_0KEY:{clear} VALUE'.format(clear=Colors.CLEAR)]
        )

    @patch(
        'archey.output.Distributions.run_detection',
        return_value=Distributions.SLACKWARE  # Make Slackware being selected.
    )
    @patch(
        'archey.output.Distributions.get_ansi_color',
        return_value='ANSI_COLOR'
    )
    @patch(
        'archey.output.Configuration.get',  # Enable `honor_ansi_color` option.
        side_effect=(
            lambda config_key: config_key == 'honor_ansi_color'
        )
    )
    def test_append_ansi_color(self, _, __, ___):
        """Check that `Output` honor `ANSI_COLOR` as required"""
        output = Output()

        # Slackware logo got three colors, so let's check they have been correctly replaced.
        self.assertTrue(
            all('ANSI_COLOR' in str(color) for color in output._colors_palette)  # pylint: disable=protected-access
        )
        self.assertEqual(
            len(output._colors_palette),  # pylint: disable=protected-access
            len(COLORS_DICT[Distributions.SLACKWARE])
        )

    @patch(
        'archey.output.Distributions.run_detection',
        return_value=Distributions.WINDOWS  # Make WSL detection pass.
    )
    @patch(
        'archey.output.Distributions.get_ansi_color',
        return_value='ANSI_COLOR'
    )
    @patch(
        'archey.output.Configuration.get',  # Disable `honor_ansi_color` option.
        side_effect=(
            lambda config_key: not (config_key == 'honor_ansi_color')
        )
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
            COLORS_DICT[Distributions.WINDOWS]
        )

    @patch(
        'archey.output.Distributions.run_detection',
        return_value=Distributions.DEBIAN  # Make Debian being selected.
    )
    @patch(
        'archey.output.Distributions.get_ansi_color',
        return_value=None
    )
    @patch.dict(
        'archey.output.LOGOS_DICT',
        {
            Distributions.DEBIAN: [
                ' ',
                ' ',
                ' ',
                ' ',
                ' ',
                ' ',
                ' ',
                ' ',
                ' ',
                ' ',
                ' ',
                ' ',
                ' ',
                ' ',
                ' ',
                ' ',
                ' ',
                ' '
            ]
        }
    )
    @patch.dict(
        'archey.constants.COLORS_DICT',
        {
            Distributions.DEBIAN: ['FAKE_COLOR']
        }
    )
    @patch(
        'archey.output.print',
        return_value=None  # Let's nastily mute class' outputs.
    )
    def test_centered_output(self, print_mock, _, __):
        """Test how the `output` method handles centering operations"""
        output = Output()

        # # ODD ENTRIES NUMBER # #
        # Entries smaller than logo
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

        # Entries bigger than logo
        output._results = [  # pylint: disable=protected-access
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11',
            '12', '13', '14', '15', '16', '17', '18', '19', '20', '21'
        ]
        output.output()
        print_mock.assert_called_with("""\
FAKE_COLOR 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13
 14
 15
 16
 17
 18
 19
FAKE_COLOR 20
FAKE_COLOR 21\x1b[0m\
""")

        # # EVEN ENTRIES NUMBER # #
        # Entries smaller than logo
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

        # Entries bigger than logo
        output._results = [  # pylint: disable=protected-access
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
            '13', '14', '15', '16', '17', '18', '19', '20', '21', '22'
        ]
        output.output()
        print_mock.assert_called_with("""\
FAKE_COLOR 1
FAKE_COLOR 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13
 14
 15
 16
 17
 18
 19
 20
FAKE_COLOR 21
FAKE_COLOR 22\x1b[0m\
""")

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
                '', '', '', '', '', ''
            ]
        )

    @patch(
        'archey.output.Distributions.run_detection',
        return_value=Distributions.DEBIAN  # Make Debian being selected.
    )
    @patch(
        'archey.output.Distributions.get_ansi_color',
        return_value=None
    )
    @patch.dict(
        'archey.output.LOGOS_DICT',
        {
            Distributions.DEBIAN: [
                'W ',
                'O ',
                'O ',
                'O ',
                'O '
            ]
        }
    )
    @patch('archey.output.get_terminal_size')
    @patch(
        'archey.output.print',
        return_value=None  # Let's nastily mute class' outputs.
    )
    def test_line_wrapping(self, print_mock, termsize_mock, _, __):
        """Test how the `output` method handles wrapping lines that are too long"""
        output = Output()

        # We only need a column value for the terminal size
        termsize_tuple = namedtuple('termsize_tuple', 'columns')
        termsize_mock.return_value = termsize_tuple(10)

        output._results = [ # pylint: disable=protected-access
            'short',                       # no truncation - too short
            'looooooong',                  # truncation - too long
            'tenchars',                    # no truncation - exactly the right width
            '\x1b[0;31mshort\x1b[0m',      # no truncation - too short
            '\x1b[0;31mlooooooong\x1b[0m'  # truncation - too long, long word truncated
        ]
        output.output()

        print_mock.assert_called_with("""\
W short
O \x1b[0m...
O tenchars
O \x1b[0;31mshort\x1b[0m
O \x1b[0;31m\x1b[0m...\x1b[0m\
""")
        # Check that `print` has been called only once.
        # `unittest.mock.Mock.assert_called_once` is not available against Python < 3.6.
        self.assertEqual(print_mock.call_count, 1)

    @patch('archey.output.Distributions.run_detection')
    @patch(
        'archey.output.Distributions.get_ansi_color',
        return_value=None
    )
    def test_preferred_distribution(self, _, run_detection_mock):
        """Simple test checking behavior when `preferred_distribution` is passed at instantiation"""
        output = Output(preferred_distribution='rhel')

        self.assertEqual(
            output._distribution,  # pylint: disable=protected-access
            Distributions.RED_HAT
        )
        # Check `Distributions.run_detection` method has not been called at all.
        self.assertFalse(run_detection_mock.called)

    @patch(
        'archey.output.Distributions.run_detection',
        return_value=Distributions.DEBIAN  # Make Debian being selected.
    )
    @patch(
        'archey.output.Configuration.get',  # Disable `honor_ansi_color` option.
        side_effect=(
            lambda config_key: not (config_key == 'honor_ansi_color')
        )
    )
    @patch(
        'archey.output.print',
        return_value=None  # Let's nastily mute class' outputs.
    )
    def test_format_to_json(self, print_mock, _, __):
        """Test how the `output` method handles JSON preferred formatting of entries"""
        output = Output(format_to_json=True)
        # We can't set the `name` attribute of a mock on its creation,
        # so this is a little bit messy...
        mocked_entries = [
            Mock(value='test'),
            Mock(value=0xDEAD)
        ]
        mocked_entries[0].name = 'test'
        mocked_entries[1].name = 'name'

        output._entries = mocked_entries  # pylint: disable=protected-access
        output.output()

        # Check that `print` output is properly formatted as JSON, with expected results.
        output_json_data = json.loads(print_mock.call_args[0][0])['data']
        self.assertEqual(
            output_json_data['test'],
            'test'
        )
        self.assertEqual(
            output_json_data['name'],
            0xDEAD
        )


if __name__ == '__main__':
    unittest.main()
