"""Test module for Archey's GPU detection module"""

import unittest
from unittest.mock import patch

from subprocess import CalledProcessError

from archey.entries.gpu import GPU


class TestGPUEntry(unittest.TestCase):
    """Here, we mock the `check_output` call to `lspci` to test the logic"""
    @patch(
        'archey.configuration.Configuration.get',
        side_effect=[
            {'max_count': None}
        ]
    )
    @patch(
        'archey.entries.gpu.check_output',
        return_value="""\
XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H VGA compatible controller: GPU-MODEL-NAME
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
""")
    def test_match_vga(self, _, __):
        """Simple 'VGA' device type matching"""
        self.assertListEqual(GPU().gpu_devices, ['GPU-MODEL-NAME'])

    @patch(
        'archey.configuration.Configuration.get',
        side_effect=[
            {'max_count': 2},
            {'one_line': True}
        ]
    )
    @patch(
        'archey.entries.gpu.check_output',
        return_value="""\
XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H VGA compatible controller: GPU-MODEL-NAME
XX:YY.H Display controller: ANOTHER-MATCHING-VIDEO-CONTROLLER
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
XX:YY.H 3D controller: 3D GPU-MODEL-NAME TAKES ADVANTAGE
""")
    def test_multi_matches_capped_one_line(self, _, __):
        """
        Test detection when there are multiple graphical device candidates.
        Check that `max_count` and `one_line` are honored too, including on `output` overriding.
        """
        gpu_entry = GPU()
        output = []
        gpu_entry.output(output)

        self.assertListEqual(
            gpu_entry.gpu_devices,
            ['3D GPU-MODEL-NAME TAKES ADVANTAGE', 'GPU-MODEL-NAME']
        )
        self.assertEqual(
            output[0][1],
            '3D GPU-MODEL-NAME TAKES ADVANTAGE, GPU-MODEL-NAME'
        )

    @patch(
        'archey.configuration.Configuration.get',
        side_effect=[
            {'max_count': False},
            {'one_line': False}
        ]
    )
    @patch(
        'archey.entries.gpu.check_output',
        return_value="""\
XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H Display controller: ANOTHER-MATCHING-VIDEO-CONTROLLER
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
XX:YY.H 3D controller: 3D GPU-MODEL-NAME TAKES ADVANTAGE
""")
    def test_multi_matches_uncapped_multiple_lines(self, _, __):
        """
        Test detection when there are multiple graphical device candidates.
        Check that `max_count` and `one_line` are honored too, including on `output` overriding.
        """
        gpu_entry = GPU()
        output = []
        gpu_entry.output(output)

        self.assertListEqual(
            gpu_entry.gpu_devices,
            ['3D GPU-MODEL-NAME TAKES ADVANTAGE', 'ANOTHER-MATCHING-VIDEO-CONTROLLER']
        )
        self.assertEqual(
            output[0][1],
            '3D GPU-MODEL-NAME TAKES ADVANTAGE'
        )
        self.assertEqual(
            output[1][1],
            'ANOTHER-MATCHING-VIDEO-CONTROLLER'
        )

    @patch(
        'archey.configuration.Configuration.get',
        side_effect=[
            {'max_count': None},
            {'one_line': True}
        ]
    )
    @patch(
        'archey.entries.gpu.check_output',
        return_value="""\
XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
""")
    def test_no_match(self, _, __):
        """Test (non-)detection when there is not any graphical candidate"""
        gpu_entry = GPU()
        output = []
        gpu_entry.output(output)

        self.assertFalse(gpu_entry.gpu_devices)
        self.assertFalse(output[0][1])

    @patch(
        'archey.configuration.Configuration.get',
        side_effect=[
            {'max_count': None},
            {'one_line': False}
        ]
    )
    @patch(
        'archey.entries.gpu.check_output',
        side_effect=CalledProcessError(1, 'lspci')
    )
    def test_lspci_crash(self, _, __):
        """Test (non-)detection due to a crashing `lspci` program"""
        gpu_entry = GPU()
        output = []
        gpu_entry.output(output)

        self.assertFalse(gpu_entry.gpu_devices)
        self.assertFalse(output[0][1])


if __name__ == '__main__':
    unittest.main()
