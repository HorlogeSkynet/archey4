"""`__init__` file for the `logos` submodule, containing dedicated utility methods"""

from importlib import import_module
from types import ModuleType
from typing import List


def lazy_load_logo_module(logo_name: str) -> ModuleType:
    """
    Utility function returning a logo (as a Python module) lazily-loaded.
    It allows us to only load to RAM the distribution logo object that will actually be used.
    """
    return import_module(f"{__name__}.{logo_name}")


def get_logo_width(logo: List[str], nb_colors: int = 8) -> int:
    """
    Utility function computing the real width of a distribution logo.
    Rationale : We use placeholders to dynamically set ANSI colors.
                Although, they **DO NOT** take width space once the text as been printed.

    For performance purposes we compute the logo length based on its first line.
    See `archey.test.test_archey_logos` unit tests for further logos consistency verifications.

    `logo` is supposed to be one of the constants declared above.
    `nb_colors` must be greater than or equal to the number of colors used by the logo.
    """
    # We replace each placeholder by a 0-character string.
    return len(logo[0].format(c=[""] * nb_colors))
