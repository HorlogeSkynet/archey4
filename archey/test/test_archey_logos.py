"""Test module for `archey.logos`"""

import pkgutil
import unittest

from archey.colors import Colors
from archey import logos
from archey.logos import get_logo_width, lazy_load_logo_module


class TestLogosModule(unittest.TestCase):
    """Simple tests checking logos consistency and utility function logic"""
    def test_distribution_logos_consistency(self):
        """
        Verify each distribution logo module contain `LOGO` & `COLORS` ("truthy") attributes.
        Also check they got _consistent_ widths across their respective lines.
        Additionally verify they don't contain any (useless) empty line.

        This test also indirectly checks `lazy_load_logo_module` behavior!
        """
        for logo_module_info in pkgutil.iter_modules(logos.__path__):
            # `iter_modules` yields `pkgutil.ModuleInfo` named tuple starting with Python 3.6.
            # So we manually extract the module name from `(module_finder, name, ispkg)` tuple.
            logo_module_name = logo_module_info[1]

            logo_module = lazy_load_logo_module(logo_module_name)

            # Attributes checks.
            self.assertTrue(
                getattr(logo_module, 'LOGO', []),
                msg='[{0}] logo module missing `LOGO` attribute'.format(logo_module_name)
            )
            self.assertTrue(
                getattr(logo_module, 'COLORS', []),
                msg='[{0}] logo module missing `COLORS` attribute'.format(logo_module_name)
            )

            # Make Archey compute the logo width.
            logo_width = get_logo_width(logo_module.LOGO)

            # Then, check that each logo line got the same effective width.
            for i, line in enumerate(logo_module.LOGO[1:], start=1):
                # Here we gotta trick the `get_logo_width` call.
                # We actually pass each logo line as if it was a "complete" logo.
                line_width = get_logo_width([line])

                # Width check.
                self.assertEqual(
                    line_width,
                    logo_width,
                    msg='[{0}] line index {1}, got an unexpected width {2} (expected {3})'.format(
                        logo_module_name, i, line_width, logo_width
                    )
                )

                # Non-empty line check.
                self.assertTrue(
                    Colors.remove_colors(line).strip(),
                    msg='[{0}] line index {1}, got an useless empty line'.format(
                        logo_module_name, i
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
