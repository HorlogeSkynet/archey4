"""Terminal detection class"""

import os

from archey.colors import Colors
from archey.entry import Entry


# This dictionary contains environment variables used to detect terminal emulators...
#   which do not propagate `TERM_PROGRAM`.
# When a key is found in environment, a normalization is performed with its corresponding value.
TERM_DICT = {
    'ALACRITTY_LOG_ENV': 'Alacritty',
    'GNOME_TERMINAL_SCREEN': 'GNOME Terminal',
    'GUAKE_TAB_UUID': 'Guake',
    'KONSOLE_VERSION': 'Konsole',
    'MLTERM': 'MLTERM',
    'TERMINATOR_UUID': 'Terminator'
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
        """Build and return a 8-color palette, with Unicode characters if allowed"""
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
        """Try to detect current terminal emulator based on various environment variables"""
        # At first, try to honor `TERM_PROGRAM` environment variable.
        # See <https://github.com/Maximus5/ConEmu/issues/1837#issuecomment-469199525>.
        env_term_program = os.getenv('TERM_PROGRAM')
        if env_term_program:
            return env_term_program

        # Secondly, if `TERM` is set to "something special", honor it.
        env_term = os.getenv('TERM')
        if env_term and not env_term.startswith('xterm'):
            return env_term

        # If not, try to find a "known identifier" and perform name normalization...
        for env_var, normalized_name in TERM_DICT.items():
            if env_var in os.environ:
                return normalized_name

        # When nothing of the above matched, falls-back on the regular `TERM` environment variable.
        # Note : It _might_ be `None` in very specific environments.
        return env_term
