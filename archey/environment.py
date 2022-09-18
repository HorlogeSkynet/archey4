"""
Simple class (acting as a singleton) dealing with environment variables.
Variables that should alter Archey _global_ behavior may be DRY-ed here.
"""

import os
import platform

from archey.singleton import Singleton


class Environment(metaclass=Singleton):
    """
    At startup, instantiate this class and set up some attributes
      according to their respective environment variable value.
    """

    # See <https://no-color.org/>.
    NO_COLOR = "NO_COLOR" in os.environ

    # See <https://bixense.com/clicolors/>.
    CLICOLOR = os.getenv("CLICOLOR") != "0"
    CLICOLOR_FORCE = os.getenv("CLICOLOR_FORCE", "0") != "0"

    # See <https://consoledonottrack.com/>.
    DO_NOT_TRACK = os.getenv("DO_NOT_TRACK") == "1"

    def __init__(self):
        if platform.system() == "Darwin":
            # Makes future `platform.mac_ver` calls not being _trolled_ by Darwin's kernel
            #   when opening `/System/Library/CoreServices/SystemVersion.plist` file.
            # "Fortunately" for us, `platform` module does not cache these very results.
            # See `platform._mac_ver_xml` function and
            #   <https://eclecticlight.co/2020/08/13/macos-version-numbering-isnt-so-simple/>.
            os.environ["SYSTEM_VERSION_COMPAT"] = "0"
