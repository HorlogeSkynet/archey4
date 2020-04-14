"""User session detection class"""

import os

from archey.configuration import Configuration
from archey.module import Module


class User(Module):
    """Retrieves the session name of the current logged in user"""
    def __init__(self):
        self.name = Configuration().get("entry_names")["User"]
        self.value = os.getenv(
            'USER',
            Configuration().get('default_strings')['not_detected']
        )
