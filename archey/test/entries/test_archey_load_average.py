"""Test module for Archey LoadAverage detection module"""

import unittest
from unittest.mock import MagicMock

from archey.colors import Colors
from archey.entries.load_average import LoadAverage
from archey.test.entries import HelperMethods


class TestLoadAverageEntry(unittest.TestCase):
    """LoadAverage `output` configuration-based coloration test class"""

    def setUp(self):
        """Define mocked entry before each test"""
        self.load_average_mock = HelperMethods.entry_mock(LoadAverage)
        self.output_mock = MagicMock()

    @HelperMethods.patch_clean_configuration
    def test_output_coloration(self):
        """Test `output` coloration based on user preferences"""
        self.load_average_mock.value = (0.5, 1.25, 2.5)
        self.load_average_mock.options = {
            "warning_threshold": 0.75,
            "danger_threshold": 2.25,
        }

        LoadAverage.output(self.load_average_mock, self.output_mock)
        self.assertEqual(
            self.output_mock.append.call_args[0][1],
            f"{Colors.GREEN_NORMAL}0.5{Colors.CLEAR} "
            f"{Colors.YELLOW_NORMAL}1.25{Colors.CLEAR} "
            f"{Colors.RED_NORMAL}2.5{Colors.CLEAR}",
        )

    @HelperMethods.patch_clean_configuration
    def test_output_rounding(self):
        """Test `output` rounding based on user preferences"""
        self.load_average_mock.value = (0.33333, 1.25, 2.0)

        with self.subTest("No decimal places"):
            self.load_average_mock.options = {
                "decimal_places": 0,
                "warning_threshold": 5,
                "danger_threshold": 5,
            }
            LoadAverage.output(self.load_average_mock, self.output_mock)
            self.assertEqual(
                self.output_mock.append.call_args[0][1],
                f"{Colors.GREEN_NORMAL}0.0{Colors.CLEAR} "
                f"{Colors.GREEN_NORMAL}1.0{Colors.CLEAR} "
                f"{Colors.GREEN_NORMAL}2.0{Colors.CLEAR}",
            )

        with self.subTest("1 decimal place"):
            self.load_average_mock.options = {
                "decimal_places": 1,
                "warning_threshold": 5,
                "danger_threshold": 5,
            }
            LoadAverage.output(self.load_average_mock, self.output_mock)
            self.assertEqual(
                self.output_mock.append.call_args[0][1],
                f"{Colors.GREEN_NORMAL}0.3{Colors.CLEAR} "
                f"{Colors.GREEN_NORMAL}1.2{Colors.CLEAR} "
                f"{Colors.GREEN_NORMAL}2.0{Colors.CLEAR}",
            )

        with self.subTest("2 decimal places"):
            self.load_average_mock.options = {
                "decimal_places": 2,
                "warning_threshold": 5,
                "danger_threshold": 5,
            }
            LoadAverage.output(self.load_average_mock, self.output_mock)
            self.assertEqual(
                self.output_mock.append.call_args[0][1],
                f"{Colors.GREEN_NORMAL}0.33{Colors.CLEAR} "
                f"{Colors.GREEN_NORMAL}1.25{Colors.CLEAR} "
                f"{Colors.GREEN_NORMAL}2.0{Colors.CLEAR}",
            )


if __name__ == "__main__":
    unittest.main()
