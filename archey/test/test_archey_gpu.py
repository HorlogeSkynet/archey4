"""Test module for Archey's GPU detection module"""

import unittest
from unittest.mock import patch

from subprocess import CalledProcessError

from archey.entries.gpu import GPU


class TestGPUEntry(unittest.TestCase):
    """Here, we mock the `check_output` call to `lspci` to test the logic"""
    @patch(
        'archey.entries.gpu.check_output',
        return_value="""\
XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H VGA compatible controller: GPU-MODEL-NAME
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
""")
    def test_match_vga(self, _):
        """Simple 'VGA' device type matching"""
        self.assertEqual(GPU().value, 'GPU-MODEL-NAME')

    @patch(
        'archey.entries.gpu.check_output',
        return_value="""\
XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H Display controller: ANOTHER-MATCHING-VIDEO-CONTROLLER
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
XX:YY.H 3D controller: 3D GPU-MODEL-NAME TAKES ADVANTAGE
""")
    def test_multi_matches(self, _):
        """Test detection when there are multiple graphical candidates"""
        self.assertEqual(
            GPU().value,
            '3D GPU-MODEL-NAME TAKES ADVANTAGE, ANOTHER-MATCHING-VIDEO-CONTROLLER'
        )

    @patch(
        'archey.entries.gpu.check_output',
        return_value="""\
XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
""")
    @patch(
        'archey.configuration.Configuration.get',
        return_value={'not_detected': 'Not detected'}
    )
    def test_no_match(self, _, __):
        """Test (non-)detection when there is not any graphical candidate"""
        self.assertEqual(GPU().value, 'Not detected')

    @patch(
        'archey.entries.gpu.check_output',
        side_effect=CalledProcessError(1, 'lspci')
    )
    @patch(
        'archey.configuration.Configuration.get',
        return_value={'not_detected': 'Not detected'}
    )
    def test_lspsci_crash(self, _, __):
        """Test (non-)detection due to a crashing `lspci` program"""
        self.assertEqual(GPU().value, 'Not detected')


if __name__ == '__main__':
    unittest.main()
