"""Test module for `archey.logos`"""

import pkgutil
import unittest

from archey import logos
from archey.colors import Colors
from archey.distributions import Distributions
from archey.logos import get_logo_width, lazy_load_logo_module


class TestLogos(unittest.TestCase):
    """Simple tests checking logos consistency and utility function logic"""
    def test_distribution_logos_consistency(self):
        """
        Verify each distribution identifier got a logo module.
        Verify each distribution logo module contain `LOGO` & `COLORS` ("truthy") attributes.
        Also check they got _consistent_ widths across their respective lines.
        Additionally verify they don't contain any (useless) empty line.

        This test also indirectly checks `lazy_load_logo_module` behavior!
        """
        distributions_identifiers = Distributions.get_distribution_identifiers()

        for i, logo_module_info in enumerate(pkgutil.iter_modules(logos.__path__), start=1):

            # Check each logo module name corresponds to a distribution identifier.
            self.assertIn(
                logo_module_info.name,
                distributions_identifiers,
                msg='No distribution identifier for [{0}]'.format(logo_module_info.name)
            )

            logo_module = lazy_load_logo_module(logo_module_info.name)

            # Attributes checks.
            self.assertTrue(
                getattr(logo_module, 'LOGO', []),
                msg='[{0}] logo module missing `LOGO` attribute'.format(
                    logo_module_info.name
                )
            )
            self.assertTrue(
                getattr(logo_module, 'COLORS', []),
                msg='[{0}] logo module missing `COLORS` attribute'.format(
                    logo_module_info.name
                )
            )

            # Make Archey compute the logo width.
            logo_width = get_logo_width(logo_module.LOGO)

            # Then, check that each logo line got the same effective width.
            for j, line in enumerate(logo_module.LOGO[1:], start=1):
                # Here we gotta trick the `get_logo_width` call.
                # We actually pass each logo line as if it was a "complete" logo.
                line_width = get_logo_width([line])

                # Width check.
                self.assertEqual(
                    line_width,
                    logo_width,
                    msg='[{0}] line index {1}, got an unexpected width {2} (expected {3})'.format(
                        logo_module_info.name, j, line_width, logo_width
                    )
                )

                # Non-empty line check.
                self.assertTrue(
                    Colors.remove_colors(line).strip(),
                    msg='[{0}] line index {1}, got an useless empty line'.format(
                        logo_module_info.name, j
                    )
                )

        # Finally, check each distributions identifier got a logo!
        # pylint: disable=undefined-loop-variable
        self.assertEqual(
            i,
            len(distributions_identifiers),
            msg='[{0}] Expected {1} logo modules, got {2}'.format(
                logo_module_info.name, len(distributions_identifiers), i
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
