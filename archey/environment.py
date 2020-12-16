"""
Simple class (acting as a singleton) dealing with environment variables.
Variables that should alter Archey _global_ behavior may be DRY-ed here.
"""

import os

from archey.singleton import Singleton


class Environment(metaclass=Singleton):
    """
    At startup, instantiate this class and set up some attributes
      according to their respective environment variable value.
    """
    # See <https://no-color.org/>.
    NO_COLOR = ('NO_COLOR' in os.environ)

    # See <https://consoledonottrack.com/>.
    DO_NOT_TRACK = (os.getenv('DO_NOT_TRACK') == '1')
