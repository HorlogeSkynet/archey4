"""Test module for Archey's GPU detection module"""

import unittest
from unittest.mock import patch

from archey.entries.gpu import GPU
from archey.configuration import Configuration
from archey.singleton import Singleton
import archey.default_configuration as DefaultConfig


class TestGPUEntry(unittest.TestCase):
    """Here, we mock the `check_output` call to `lspci` to test the logic"""

    def setUp(self):
        """Runs when each test begins"""
        # Set up a default configuration instance.
        config = Configuration()
        config._config = DefaultConfig.CONFIGURATION # pylint: disable=protected-access

    def tearDown(self):
        """Runs when each test finishes testing"""
        # Destroy the singleton configuration instance (if created)
        try:
            del Singleton._instances[Configuration] # pylint: disable=protected-access
        except KeyError:
            pass

    @patch(
        'archey.entries.gpu.check_output',
        return_value="""\
XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H VGA compatible controller: GPU-MODEL-NAME
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
""")
    def test_match_vga(self, _):
        """[Entry] [GPU] Simple "VGA" device type matching"""
        self.assertEqual(GPU().value, 'GPU-MODEL-NAME')

    @patch(
        'archey.entries.gpu.check_output',
        return_value="""\
XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
XX:YY.H Display controller: GPU-MODEL-NAME VERY LONG WITH SPACES TO BE CUT OFF
""")
    def test_match_display_too_long(self, _):
        """[Entry] [GPU] Test output truncation, when the graphical candidate is too long"""
        self.assertEqual(
            GPU().value,
            'GPU-MODEL-NAME VERY LONG WITH SPACES TO BE...'
        )

    @patch(
        'archey.entries.gpu.check_output',
        return_value="""\
XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
XX:YY.H VGA compatible controller: GPU-MODEL-NAME VERY LONG WITH SPACES TO BE (CUT OFF)
""")
    def test_match_display_long_special(self, _):
        """[Entry] [GPU] Same test as above with a very particular pattern"""
        self.assertEqual(
            GPU().value,
            'GPU-MODEL-NAME VERY LONG WITH SPACES TO BE...'
        )

    @patch(
        'archey.entries.gpu.check_output',
        return_value="""\
XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H Display controller: ANOTHER MATCHING VIDEO CONTROLLER IGNORED
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
XX:YY.H 3D controller: 3D GPU-MODEL-NAME TAKES ADVANTAGE
""")
    def test_multi_matches(self, _):
        """[Entry] [GPU] Test detection when there are multiple graphical candidates"""
        self.assertEqual(
            GPU().value,
            '3D GPU-MODEL-NAME TAKES ADVANTAGE'
        )

    @patch(
        'archey.entries.gpu.check_output',
        return_value="""\
XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
""")
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'default_strings': {
                'not_detected': 'Not detected'
            }
        }
    )
    def test_no_match(self, _):
        """[Entry] [GPU] Test (non-)detection when there is not any graphical candidate"""
        self.assertEqual(GPU().value, 'Not detected')


if __name__ == '__main__':
    unittest.main()
