"""Terminal detection class"""

import os
import re

from archey.colors import Colors, NO_COLOR
from archey.entry import Entry


# We detect a terminal by using the following three constants in the order below:
# First, we try using the value in the `TERM_PROGRAM` environment variable.
# Then, we use `COLORTERM_DICT` to try matching a value with the `COLORTERM` one.
# Third, we use `TERM_DICT` to try matching a value with the `TERM` one.
# Finally, we fall back to custom environment variables defined in `ENV_DICT`.
# If none of the above tests find a value, we use whichever value was defined in `$TERM`.

# All of the keys in `COLORTERM_DICT` and `TERM_DICT` are matched as regular expressions...
#   (using `re.match`, i.e. attempting to match once at the beginning of the string), so be careful!


# This dictionary contains values for the `COLORTERM` environment variable for terminal emulators
#   which do not propagate any other usable environment variable.
# If `COLORTERM` matches one of these values, a normalization is performed with its corresponding
#   value (i.e. the respective terminal emulator).
# If the variable does not match any keys in this dictionary, it is ignored.
COLORTERM_DICT = {
    r'kmscon': 'KMSCON',
    r'rxvt': 'rxvt',
}

# This dictionary contains values for the `TERM` environment variable for terminal emulators
#   which do not propagate any other usable environment variable.
# If `TERM` matches one of these values, a normalization is performed with its corresponding
#   value (i.e. the respective terminal emulator).
# If the variable does not match any keys in this dictionary, it is ignored,
#   UNLESS it does not begin with `xterm`, at which point its value is taken as the terminal in use.
#   This behavior can be overridden by specifying its exact match here.
TERM_DICT = {
    r'xterm-termite': 'Termite',
}

# This dictionary contains environment variables used to detect terminal emulators...
#   which do not propagate any usable `COLORTERM`, `TERM`, or `TERM_PROGRAM`.
# When a key is found in environment, a normalization is performed with its corresponding value.
ENV_DICT = {
    'ALACRITTY_LOG': 'Alacritty',
    'GNOME_TERMINAL_SCREEN': 'GNOME Terminal',
    'GUAKE_TAB_UUID': 'Guake',
    'KITTY_WINDOW_ID': 'Kitty',
    'KONSOLE_VERSION': 'Konsole',
    'MLTERM': 'MLTERM',
    'TERMINATOR_UUID': 'Terminator',
}


class Terminal(Entry):
    """
    Simple terminal detection based on the `TERM` environment variable.
    It also displays the colors palette afterwards.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.value = self._detect_terminal_emulator()

    def _get_colors_palette(self):
        """Build and return a 8-color palette, with Unicode characters if allowed"""
        # On systems with non-Unicode locales, we imitate '\u2588' character
        # ... with '#' to display the terminal colors palette.
        # Archey >= v4.8.0, Unicode is enabled by default.
        use_unicode = self.options.get('use_unicode', True)

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

        # Second, check if we have any matches as defined in our `COLORTERM` constant dict.
        env_colorterm = os.getenv('COLORTERM')
        if env_colorterm:
            for env_value_re, normalized_name in COLORTERM_DICT.items():
                if re.match(env_value_re, env_colorterm):
                    return normalized_name

        # Third, check if we have any matches defined in our `TERM` constant dict.
        env_term = os.getenv('TERM')
        if env_term:
            for env_value_re, normalized_name in TERM_DICT.items():
                if re.match(env_value_re, env_term):
                    return normalized_name

            # If we didn't find any match and `TERM` is set to "something special", honor it.
            if not env_term.startswith('xterm'):
                return env_term

        # If not, try to find a "known identifier" and perform name normalization...
        for env_var, normalized_name in ENV_DICT.items():
            if env_var in os.environ:
                return normalized_name

        # When nothing of the above matched, falls-back on the regular `TERM` environment variable.
        # Note : It _might_ be `None` in very specific environments.
        return env_term


    def output(self, output):
        """Adds the entry to `output` after pretty-formatting with colors palette"""
        text_output = (self.value or self._default_strings.get('not_detected'))
        if not NO_COLOR:
            text_output += ' ' + self._get_colors_palette()

        output.append(self.name, text_output)
