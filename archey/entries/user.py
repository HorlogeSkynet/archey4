"""User session detection class"""

import os

from subprocess import CalledProcessError, check_output

from archey.entry import Entry


class User(Entry):
    """Retrieves the session name of the current logged in user"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.value = os.getenv('USER')
        if not self.value:
            try:
                self.value = check_output(
                    ['id', '-u', '-n'],
                    universal_newlines=True
                ).rstrip()
            except CalledProcessError:
                # Should not occur, but who knows ?
                pass
