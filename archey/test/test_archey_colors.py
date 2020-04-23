"""Test module for `archey.colors`"""

import unittest

from archey.colors import Colors


class TestColorsUtil(unittest.TestCase):
    """Test cases for the `Colors` (enumeration / utility) class."""

    def test_string_representation(self):
        """Simple test case for `__str__` implementation"""
        self.assertEqual(str(Colors.CLEAR), '\x1b[0m')
        self.assertEqual(str(Colors.CYAN_BRIGHT), '\x1b[1;36m')

    def test_escape_code_from_attrs(self):
        """Test for `Colors.escape_code_from_attrs`"""
        self.assertEqual(Colors.escape_code_from_attrs('0;31'), '\x1b[0;31m')
        self.assertEqual(Colors.escape_code_from_attrs('0;31;45'), '\x1b[0;31;45m')

    def test_get_level_color(self):
        """Test for `Colors.get_level_color`"""
        # [25] (GREEN) < 50 < 75
        self.assertEqual(Colors.get_level_color(25, 50, 75), Colors.GREEN_NORMAL)
        # 33 < [34] (YELLOW) < 66
        self.assertEqual(Colors.get_level_color(34, 33, 66), Colors.YELLOW_NORMAL)
        # 33 < 66 < [90] (RED)
        self.assertEqual(Colors.get_level_color(90, 33, 66), Colors.RED_NORMAL)


if __name__ == '__main__':
    unittest.main()
