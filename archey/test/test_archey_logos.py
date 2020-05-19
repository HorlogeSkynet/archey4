"""Test module for `archey.logos`"""

import unittest

from archey.colors import Colors
from archey.distributions import Distributions
from archey.constants import LOGOS_DICT
from archey.logos import get_logo_width


class TestLogosModule(unittest.TestCase):
    """Simple tests checking logos consistency and utility function logic"""
    def test_distribution_logos_width(self):
        """
        Check that each distribution logo got a _consistent_ width across its lines.

        For this test, we have to trick the `get_logo_width` call.
        We actually pass each logos line as if they were a "complete" logo.
        """
        for distribution in Distributions:
            # Make Archey compute the logo width.
            logo_width = get_logo_width(LOGOS_DICT[distribution])
            # Then, check that each logo line got the same effective width.
            for i, line in enumerate(LOGOS_DICT[distribution][1:], start=1):
                line_width = get_logo_width([line])
                self.assertEqual(
                    line_width,
                    logo_width,
                    msg='[{0}] line index {1}, got an unexpected width {2} (expected {3})'.format(
                        distribution, i, line_width, logo_width
                    )
                )

    def test_distribution_logos_no_empty_lines(self):
        """Check that distribution logos do not contain (useless) empty lines"""
        for distribution in Distributions:
            for i, line in enumerate(LOGOS_DICT[distribution]):
                self.assertTrue(
                    Colors.remove_colors(line).strip(),
                    msg='[{0}] line index {1}, got a forbidden empty line'.format(
                        distribution, i
                    )
                )

    def test_get_logo_width(self):
        """Test `logos.get_logo_width` behavior"""
        self.assertEqual(
            get_logo_width(['{c[0]}   {c[1]}'], 2),
            3
        )
        self.assertEqual(
            get_logo_width(['{c[0]} {{ {c[1]}']),
            3
        )
        self.assertEqual(
            get_logo_width(
                [
                    '{c[0]}   {c[1]}>>>>{c[2]}<<<<{c[3]}',
                    '{c[0]}   {c[1]}>>>>{c[2]}<<<<<{c[3]}'  # Ignored from computation...
                ]
            ),
            11
        )
