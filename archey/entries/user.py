"""User session detection class"""

import os

from subprocess import CalledProcessError, check_output

from archey.configuration import Configuration


class User:
    """Retrieves the session name of the current logged in user"""
    def __init__(self):
        user = os.getenv('USER')
        if not user:
            try:
                user = check_output(
                    ['id', '-u', '-n'],
                    universal_newlines=True
                ).rstrip()
            except CalledProcessError:
                # Should not occur, but who knows ?
                user = Configuration().get('default_strings')['not_detected']

        self.value = user
