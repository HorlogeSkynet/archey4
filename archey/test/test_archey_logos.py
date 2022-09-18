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
        distributions_identifiers = Distributions.get_identifiers()

        for i, logo_module_info in enumerate(pkgutil.iter_modules(logos.__path__), start=1):

            # Check each logo module name corresponds to a distribution identifier.
            self.assertIn(
                logo_module_info.name,
                distributions_identifiers,
                msg=f"No distribution identifier for [{logo_module_info.name}]",
            )

            logo_module = lazy_load_logo_module(logo_module_info.name)

            # Attributes checks.
            self.assertTrue(
                getattr(logo_module, "LOGO", []),
                msg=f"[{logo_module_info.name}] logo module missing `LOGO` attribute",
            )
            self.assertTrue(
                getattr(logo_module, "COLORS", []),
                msg=f"[{logo_module_info.name}] logo module missing `COLORS` attribute",
            )

            # Compute once and for all the number of defined colors for this logo.
            nb_colors = len(logo_module.COLORS)

            # Make Archey compute the logo (effective) width.
            logo_width = get_logo_width(logo_module.LOGO, nb_colors)

            # Then, check that each logo line got the same effective width.
            for j, line in enumerate(logo_module.LOGO[1:], start=1):
                # Here we gotta trick the `get_logo_width` call.
                # We actually pass each logo line as if it was a "complete" logo.
                line_width = get_logo_width([line], nb_colors)

                # Width check.
                self.assertEqual(
                    line_width,
                    logo_width,
                    msg=(
                        f"[{logo_module_info.name}] line index {j}, "
                        f"got an unexpected width {line_width} (expected {logo_width})"
                    ),
                )

                # Non-empty line check.
                self.assertTrue(
                    Colors.remove_colors(line.format(c=[""] * nb_colors)).strip(),
                    msg=f"[{logo_module_info.name}] line index {j}, got an useless empty line",
                )

        # Finally, check each distributions identifier got a logo!
        # pylint: disable=undefined-loop-variable
        self.assertEqual(
            i,
            len(distributions_identifiers),
            msg=(
                f"[{logo_module_info.name}] Expected {len(distributions_identifiers)} "
                f"logo modules, got {i}"
            ),
        )

    def test_get_logo_width(self):
        """Test `logos.get_logo_width` behavior"""
        self.assertEqual(get_logo_width(["{c[0]}   {c[1]}"], 2), 3)
        self.assertEqual(get_logo_width(["{c[0]} {{ {c[1]}"]), 3)
        self.assertEqual(
            get_logo_width(
                [
                    "{c[0]}   {c[1]}>>>>{c[2]}<<<<{c[3]}",
                    "{c[0]}   {c[1]}>>>>{c[2]}<<<<<{c[3]}",  # Ignored from computation...
                ]
            ),
            11,
        )
