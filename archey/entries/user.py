"""User session detection class"""

import os

from archey.configuration import Configuration
from archey.entry import Entry


class User(Entry):
    """Retrieves the session name of the current logged in user"""
    def __init__(self):
        super().__init__()

        self.value = os.getenv(
            'USER',
            Configuration()['default_strings']['not_detected']
        )
