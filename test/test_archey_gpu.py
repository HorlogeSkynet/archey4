
import unittest
from unittest.mock import patch

from archey.archey import GPU


class TestGPUEntry(unittest.TestCase):
    """
    Here, we mock the `check_output` call to `lspci` to test the logic.
    """

    @patch(
        'archey.archey.check_output',
        return_value="""\
XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H VGA compatible controller: GPU-MODEL-NAME
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
""")
    def test_match_vga(self, check_output_mock):
        self.assertEqual(GPU().value, 'GPU-MODEL-NAME')

    @patch(
        'archey.archey.check_output',
        return_value="""\
XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
XX:YY.H Display controller: GPU-MODEL-NAME VERY LONG WITH SPACES TO BE CUT OFF
""")
    def test_match_display_too_long(self, check_output_mock):
        self.assertEqual(
            GPU().value,
            'GPU-MODEL-NAME VERY LONG WITH SPACES TO BE...'
        )

    @patch(
        'archey.archey.check_output',
        return_value="""\
XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
XX:YY.H VGA compatible controller: GPU-MODEL-NAME VERY LONG WITH SPACES TO BE (CUT OFF)
""")
    def test_match_display_long_special(self, check_output_mock):
        self.assertEqual(
            GPU().value,
            'GPU-MODEL-NAME VERY LONG WITH SPACES TO BE...'
        )

    @patch(
        'archey.archey.check_output',
        return_value="""\
XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H Display controller: ANOTHER MATCHING VIDEO CONTROLLER IGNORED
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
XX:YY.H 3D controller: 3D GPU-MODEL-NAME TAKES ADVANTAGE
""")
    def test_multi_matches(self, check_output_mock):
        self.assertEqual(
            GPU().value,
            '3D GPU-MODEL-NAME TAKES ADVANTAGE'
        )

    @patch(
        'archey.archey.check_output',
        return_value="""\
XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
""")
    @patch.dict(
        'archey.archey.CONFIG.config',
        {'default_strings': {'not_detected': 'Not detected'}}
    )
    def test_no_match(self, check_output_mock):
        self.assertEqual(GPU().value, 'Not detected')


if __name__ == '__main__':
    unittest.main()
