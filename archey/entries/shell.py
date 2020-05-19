"""Shell detection class"""

import os

from subprocess import CalledProcessError, check_output

from archey.entry import Entry


class Shell(Entry):
    """
    Simple shell path detection based either on the `SHELL` environment variable or
    the local administrative database.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.value = os.getenv('SHELL')
        if not self.value:
            try:
                self.value = check_output(
                    ['getent', 'passwd', str(os.getuid())],
                    universal_newlines=True
                ).rstrip().split(':')[-1]
            except CalledProcessError:
                # Where does this user come from ?
                pass
