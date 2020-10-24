"""Test module for Archey's GPU detection module"""

import unittest
from unittest.mock import MagicMock, patch

from subprocess import CalledProcessError

from archey.entries.gpu import GPU
from archey.test import CustomAssertions
from archey.test.entries import HelperMethods
from archey.constants import DEFAULT_CONFIG


class TestGPUEntry(unittest.TestCase, CustomAssertions):
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
        self.assertListEqual(GPU().value, ['GPU-MODEL-NAME'])

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
    def test_multi_matches_capped_one_line(self, _):
        """
        Test detection when there are multiple graphical device candidates.
        Check that `max_count` and `one_line` are honored too, including on `output` overriding.
        """
        gpu = GPU(options={
            'one_line': True,
            'max_count': 2
        })

        output_mock = MagicMock()
        gpu.output(output_mock)

        self.assertListEqual(
            gpu.value,
            ['3D GPU-MODEL-NAME TAKES ADVANTAGE', 'GPU-MODEL-NAME']
        )
        self.assertEqual(
            output_mock.append.call_args[0][1],
            '3D GPU-MODEL-NAME TAKES ADVANTAGE, GPU-MODEL-NAME'
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
    def test_multi_matches_uncapped_multiple_lines(self, _):
        """
        Test detection when there are multiple graphical device candidates.
        Check that `max_count` and `one_line` are honored too, including on `output` overriding.
        """
        gpu = GPU(options={
            'one_line': False,
            'max_count': False
        })

        output_mock = MagicMock()
        gpu.output(output_mock)

        self.assertListEqual(
            gpu.value,
            ['3D GPU-MODEL-NAME TAKES ADVANTAGE', 'ANOTHER-MATCHING-VIDEO-CONTROLLER']
        )
        self.assertEqual(
            output_mock.append.call_args_list[0][0][1],
            '3D GPU-MODEL-NAME TAKES ADVANTAGE'
        )
        self.assertEqual(
            output_mock.append.call_args_list[1][0][1],
            'ANOTHER-MATCHING-VIDEO-CONTROLLER'
        )

    @patch(
        'archey.entries.gpu.check_output',
        return_value="""\
XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
""")
    @HelperMethods.patch_clean_configuration
    def test_no_match(self, _):
        """Test (non-)detection when there is not any graphical candidate"""
        gpu = GPU()

        output_mock = MagicMock()
        gpu.output(output_mock)

        self.assertListEmpty(gpu.value)
        self.assertEqual(
            output_mock.append.call_args[0][1],
            DEFAULT_CONFIG['default_strings']['not_detected']
        )

    @patch(
        'archey.entries.gpu.check_output',
        side_effect=CalledProcessError(1, 'lspci')
    )
    @HelperMethods.patch_clean_configuration
    def test_lspci_crash(self, _):
        """Test (non-)detection due to a crashing `lspci` program"""
        gpu = GPU()

        output_mock = MagicMock()
        gpu.output(output_mock)

        self.assertListEmpty(gpu.value)
        self.assertEqual(
            output_mock.append.call_args[0][1],
            DEFAULT_CONFIG['default_strings']['not_detected']
        )


if __name__ == '__main__':
    unittest.main()
