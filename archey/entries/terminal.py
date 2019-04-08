"""Terminal detection class"""

import os


class Terminal:
    """
    Simple terminal detection based on the `TERM` environment variable.
    It also displays the colors palette afterwards.
    """
    def __init__(self,
                 not_detected=None,
                 use_unicode=False,
                 clear_color='\x1b[0m'):
        terminal = os.getenv(
            'TERM',
            not_detected
        )

        # On systems with non-Unicode locales, we imitate '\u2588' character
        # ... with '#' to display the terminal colors palette.
        # This is the default option for backward compatibility.
        colors = ' '.join([
            '\x1b[0;3{0}m{1}\x1b[1;3{0}m{1}{2}'.format(
                i,
                '\u2588' if use_unicode
                else '#',
                clear_color
            ) for i in range(7, 0, -1)
        ])

        self.value = '{0} {1}'.format(terminal, colors)
