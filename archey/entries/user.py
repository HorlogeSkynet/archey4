"""User session detection class"""

import os


class User:
    """Retrieves the session name of the current logged in user"""
    def __init__(self, not_detected=None):
        self.value = os.getenv(
            'USER',
            not_detected
        )
