"""Test module for `archey.colors`"""

import unittest
from unittest.mock import patch

from archey.colors import ANSI_ECMA_REGEXP, Colors, Colors8Bit, Style


class TestColors(unittest.TestCase):
    """Test cases for the `Style` and `Colors` (enumeration / utility) classes"""

    def setUp(self):
        # Skip `Style.should_color_output` patching for its own testing method.
        if self.id().endswith("should_color_output"):
            return

        # By default, colors won't be disabled.
        self._should_color_output_patch = patch(
            "archey.colors.Style.should_color_output",
            return_value=True,
        )
        self._should_color_output_patch.start()

    def tearDown(self):
        # Skip `Style.should_color_output` patching for its own testing method.
        if self.id().endswith("should_color_output"):
            return

        self._should_color_output_patch.stop()

    def test_constant_values(self):
        """Test `Colors` enumeration member instantiation from value"""
        self.assertEqual(Colors((1, 31)), Colors.RED_BRIGHT)
        self.assertRaises(ValueError, Colors, (-1,))

    def test_string_representation(self):
        """Test cases for `__str__` implementations"""
        with self.subTest("`Colors` class"):
            self.assertEqual(str(Colors.CLEAR), "\x1b[0m")
            self.assertEqual(str(Colors.CYAN_BRIGHT), "\x1b[1;36m")

        with self.subTest("`Colors8Bit` class"):
            self.assertEqual(str(Colors8Bit(0, 0)), "\x1b[0;38;5;0m")
            self.assertEqual(str(Colors8Bit(0, 127)), "\x1b[0;38;5;127m")
            self.assertEqual(str(Colors8Bit(1, 202)), "\x1b[1;38;5;202m")

    def test_8_bit_out_of_range(self):
        """Test for exception on colors outside the defined range in `Colors8Bit`"""
        for test_values in [(0, 256), (2, 0), (0, -1), (-1, 0)]:
            with self.assertRaises(ValueError):
                Colors8Bit(*test_values)

    def test_should_color_output(self):
        """Test for `Style.should_color_output`"""
        # Clear cache filled by `functools.lru_cache` decorator.
        Style.should_color_output.cache_clear()

        with patch("archey.colors.Environment.CLICOLOR_FORCE", True):
            self.assertTrue(Style.should_color_output())

        Style.should_color_output.cache_clear()

        with patch("archey.colors.Environment.CLICOLOR_FORCE", False), patch(
            "archey.colors.Environment.NO_COLOR", True
        ):
            self.assertFalse(Style.should_color_output())

        Style.should_color_output.cache_clear()

        with patch("archey.colors.Environment.CLICOLOR_FORCE", False), patch(
            "archey.colors.Environment.NO_COLOR", False
        ):
            with patch("archey.colors.sys.stdout.isatty", return_value=False):
                with patch("archey.colors.Environment.CLICOLOR", True):
                    self.assertFalse(Style.should_color_output())

                Style.should_color_output.cache_clear()

                with patch("archey.colors.Environment.CLICOLOR", False):
                    self.assertFalse(Style.should_color_output())

                Style.should_color_output.cache_clear()

            with patch("archey.colors.sys.stdout.isatty", return_value=True):
                # Default case : STDOUT is a TTY and `CLICOLOR` is (by default) set.
                with patch("archey.colors.Environment.CLICOLOR", True):
                    self.assertTrue(Style.should_color_output())

                Style.should_color_output.cache_clear()

                with patch("archey.colors.Environment.CLICOLOR", False):
                    self.assertFalse(Style.should_color_output())

                Style.should_color_output.cache_clear()

    def test_escape_code_from_attrs(self):
        """Test for `Style.escape_code_from_attrs`"""
        self.assertEqual(Style.escape_code_from_attrs("0;31"), "\x1b[0;31m")
        self.assertEqual(Style.escape_code_from_attrs("0;31;45"), "\x1b[0;31;45m")

    def test_get_level_color(self):
        """Test for `Colors.get_level_color`"""
        # [25] (GREEN) < 50 < 75
        self.assertEqual(Colors.get_level_color(25, 50, 75), Colors.GREEN_NORMAL)
        # 33 < [34] (YELLOW) < 66
        self.assertEqual(Colors.get_level_color(34, 33, 66), Colors.YELLOW_NORMAL)
        # 33 < 66 < [90] (RED)
        self.assertEqual(Colors.get_level_color(90, 33, 66), Colors.RED_NORMAL)

    def test_ansi_ecma_regexp(self):
        """Test our ANSI/ECMA REGEXP compiled pattern"""
        self.assertTrue(ANSI_ECMA_REGEXP.match(str(Colors.CLEAR)))
        self.assertTrue(ANSI_ECMA_REGEXP.match(str(Colors.RED_NORMAL)))
        self.assertTrue(ANSI_ECMA_REGEXP.match(str(Colors8Bit(0, 127))))
        self.assertTrue(ANSI_ECMA_REGEXP.match(Colors.escape_code_from_attrs("0;31;45")))
        self.assertFalse(ANSI_ECMA_REGEXP.match(""))
        self.assertFalse(ANSI_ECMA_REGEXP.match("\x1b[m"))
        self.assertFalse(ANSI_ECMA_REGEXP.match("\x1b[0M"))
        # Check that matched groups contain the whole code (no capturing groups).
        self.assertEqual(
            len(
                "".join(
                    ANSI_ECMA_REGEXP.findall(
                        str(Colors.GREEN_NORMAL) + "NOT_A_COLOR" + str(Colors.CLEAR)
                    )
                )
            ),
            len(str(Colors.GREEN_NORMAL) + str(Colors.CLEAR)),
        )

    def test_remove_colors(self):
        """Test our ANSI/ECMA REGEXP colors removal method"""
        self.assertFalse(Style.remove_colors(str(Colors.CLEAR)))
        self.assertEqual(Style.remove_colors("\x1b[0;31mTEST\x1b[0;0m"), "TEST")  # 4-bit
        self.assertEqual(Style.remove_colors("\x1b[0;38;5;127mTEST\x1b[0;0m"), "TEST")  # 8-bit
        self.assertEqual(
            Style.remove_colors("\x1b[0nTEST\xde\xad\xbe\xaf"), "\x1b[0nTEST\xde\xad\xbe\xaf"
        )

    def test_color_disabling(self):
        """Test `Colors` internal behavior when coloration is disabled"""
        with patch("archey.colors.Style.should_color_output", return_value=False):
            self.assertFalse(str(Colors.CYAN_NORMAL))
            self.assertFalse(str(Colors8Bit(0, 127)))


if __name__ == "__main__":
    unittest.main()
