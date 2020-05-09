"""Terminal detection class"""

import os

from archey.colors import Colors
from archey.entry import Entry


# This dictionary contains environment variables used to detect terminal emulators.
# Such an identification is _still_ not standardized.
# See <https://github.com/Maximus5/ConEmu/issues/1837#issuecomment-469199525>.
TERM_DICT = {
    # On its way for normalization ?
    'TERM_PROGRAM': None,
    # Manual name overriding per-emulator.
    'ALACRITTY_LOG_ENV': 'Alacritty',
    'GNOME_TERMINAL_SCREEN': 'GNOME Terminal',
    'GUAKE_TAB_UUID': 'Guake',
    'KONSOLE_VERSION': 'Konsole',
    'MLTERM': 'MLTERM',
    'TERMINATOR_UUID': 'Terminator',
    # Regular fallback.
    'TERM': None
}


class Terminal(Entry):
    """
    Simple terminal detection based on the `TERM` environment variable.
    It also displays the colors palette afterwards.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        terminal_emulator = self._detect_terminal_emulator() or \
            self._configuration.get('default_strings')['not_detected']
        colors_palette = self._get_colors_palette()

        self.value = '{0} {1}'.format(terminal_emulator, colors_palette)

    def _get_colors_palette(self):
        # On systems with non-Unicode locales, we imitate '\u2588' character
        # ... with '#' to display the terminal colors palette.
        # This is the default option for backward compatibility.
        use_unicode = self._configuration.get('colors_palette')['use_unicode']

        return ' '.join([
            '{normal}{character}{bright}{character}{clear}'.format(
                normal=Colors((0, i)),
                bright=Colors((1, i)),
                character=('\u2588' if use_unicode else '#'),
                clear=Colors.CLEAR
            ) for i in range(37, 30, -1)
        ])

    @staticmethod
    def _detect_terminal_emulator():
        for env_var, override_value in TERM_DICT.items():
            if env_var in os.environ:
                if override_value:
                    return override_value

                return os.getenv(env_var)

        return None
