"""Terminal detection class"""

import os

from archey.constants import COLOR_DICT
from archey.configuration import Configuration


class Terminal:
    """
    Simple terminal detection based on the `TERM` environment variable.
    It also displays the colors palette afterwards.
    """
    def __init__(self):
        # The configuration object is needed to retrieve some settings below.
        configuration = Configuration()

        terminal = os.getenv(
            'TERM',
            configuration.get('default_strings')['not_detected']
        )

        # On systems with non-Unicode locales, we imitate '\u2588' character
        # ... with '#' to display the terminal colors palette.
        # This is the default option for backward compatibility.
        use_unicode = configuration.get('colors_palette')['use_unicode']
        colors = ' '.join([
            '\x1b[0;3{0}m{1}\x1b[1;3{0}m{1}{2}'.format(
                i,
                '\u2588' if use_unicode else '#',
                COLOR_DICT['clear']
            ) for i in range(7, 0, -1)
        ])

        self.value = '{0} {1}'.format(terminal, colors)
