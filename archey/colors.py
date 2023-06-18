"""Colors enumeration definition"""

import re
import sys
from bisect import bisect
from enum import Enum
from functools import lru_cache

from archey.environment import Environment

# REGEXP compiled pattern matching ANSI/ECMA-48 color escape codes.
ANSI_ECMA_REGEXP = re.compile(r"\x1b\[\d+(?:(?:;\d+)+)?m")


class Style:
    """
    Style base-class supporting terminal escape sequences for bold, colour, etc.
    Supports an arbitrary number of display attributes.
    """

    def __str__(self):
        if self.should_color_output():
            return self.escape_code_from_attrs(";".join(map(str, self.value)))  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
        return ""

    @staticmethod
    @lru_cache(maxsize=None)  # Python < 3.9, `functools.cache` is not yet available.
    def should_color_output() -> bool:
        """
        Returns whether or not output should be colored, according to runtime environment.
        Current implementation is specific to Archey as it's not standardized (see jcs/no_color#28).
        """
        if Environment.CLICOLOR_FORCE:
            return True

        if Environment.NO_COLOR:
            return False

        return sys.stdout.isatty() and Environment.CLICOLOR

    @staticmethod
    def remove_colors(string: str) -> str:
        """Simple DRY method to remove any ANSI/ECMA-48 color escape code from passed `string`"""
        return ANSI_ECMA_REGEXP.sub("", string)

    @classmethod
    def escape_code_from_attrs(cls, display_attrs: str) -> str:
        """
        Build and return an ANSI/ECMA-48 escape code string from passed display attributes.
        """
        return f"\x1b[{display_attrs}m"


class Colors(Style, Enum):
    """
    ANSI terminal colors enumeration.

    See <https://web.archive.org/web/20200627145120/http://www.termsys.demon.co.uk/vtansi.htm>
      or <https://en.wikipedia.org/wiki/ANSI_escape_code>.
    """

    CLEAR = (0,)
    RED_NORMAL = (0, 31)
    RED_BRIGHT = (1, 31)
    GREEN_NORMAL = (0, 32)
    GREEN_BRIGHT = (1, 32)
    YELLOW_NORMAL = (0, 33)
    YELLOW_BRIGHT = (1, 33)
    BLUE_NORMAL = (0, 34)
    BLUE_BRIGHT = (1, 34)
    MAGENTA_NORMAL = (0, 35)
    MAGENTA_BRIGHT = (1, 35)
    CYAN_NORMAL = (0, 36)
    CYAN_BRIGHT = (1, 36)
    WHITE_NORMAL = (0, 37)
    WHITE_BRIGHT = (1, 37)

    # Python 3.6 compatibility (bug in enum overriding __str__ from mixin?)
    def __str__(self):  # pylint: disable=useless-parent-delegation
        return super().__str__()

    # Python 3.6 compatibility due to string format changes, see
    # <https://docs.python.org/3/whatsnew/3.7.html#other-language-changes> (bpo-28794)
    def __format__(self, _):
        return super().__str__()

    @staticmethod
    def get_level_color(value: float, yellow_bpt: float, red_bpt: float) -> "Colors":
        """Returns the best level color according to `value` compared to `{yellow,red}_bpt`"""
        level_colors = (Colors.GREEN_NORMAL, Colors.YELLOW_NORMAL, Colors.RED_NORMAL)
        return level_colors[bisect((yellow_bpt, red_bpt), value)]


class Colors8Bit(Style):
    """
    ANSI Terminal colors using 8-bit values (256 available)
    Instantiated using a `bright` int and `value` int, similar to a `Colors` tuple.
    See <https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit>.
    """

    def __init__(self, bright: int, value: int):
        if bright not in (0, 1) or value not in range(0, 255):
            raise ValueError("Supplied color is outside the allowed range.")
        # `ESC[38;5` selects 8-bit foreground colour
        self.value = (bright, 38, 5, value)
