"""User session detection class"""

import os

from archey.configuration import Configuration


class User:
    """Retrieves the session name of the current logged in user"""
    def __init__(self):
        self.value = os.getenv(
            'USER',
            Configuration().get('default_strings')['not_detected']
        )
