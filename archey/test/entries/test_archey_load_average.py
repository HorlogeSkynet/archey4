"""Test module for Archey LoadAverage detection module"""

import unittest
from unittest.mock import MagicMock

from archey.colors import Colors
from archey.entries.load_average import LoadAverage
from archey.test.entries import HelperMethods


class TestLoadAverageEntry(unittest.TestCase):
    """LoadAverage `output` configuration-based coloration test class"""

    @HelperMethods.patch_clean_configuration
    def test_output_coloration(self):
        """Test `output` coloration based on user preferences"""
        load_average_mock = HelperMethods.entry_mock(LoadAverage)
        output_mock = MagicMock()

        load_average_mock.value = (0.5, 1.25, 2.5)
        load_average_mock.options = {
            "warning_threshold": 0.75,
            "danger_threshold": 2.25,
        }

        LoadAverage.output(load_average_mock, output_mock)
        self.assertEqual(
            output_mock.append.call_args[0][1],
            f"{Colors.GREEN_NORMAL}0.5{Colors.CLEAR} "
            f"{Colors.YELLOW_NORMAL}1.25{Colors.CLEAR} "
            f"{Colors.RED_NORMAL}2.5{Colors.CLEAR}",
        )


if __name__ == "__main__":
    unittest.main()
