"""Terminal detection class"""

import os

from archey.colors import Colors
from archey.configuration import Configuration
from archey.entry import Entry


class Terminal(Entry):
    """
    Simple terminal detection based on the `TERM` environment variable.
    It also displays the colors palette afterwards.
    """
    def __init__(self):
        super().__init__()

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
            '{normal}{character}{bright}{character}{clear}'.format(
                normal=Colors((0, i)),
                bright=Colors((1, i)),
                character=('\u2588' if use_unicode else '#'),
                clear=Colors.CLEAR
            ) for i in range(37, 30, -1)
        ])

        self.value = '{0} {1}'.format(terminal, colors)
