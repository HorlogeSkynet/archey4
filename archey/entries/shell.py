"""Shell detection class"""

import os


class Shell:
    """Simple shell detection based on the `SHELL` environment variable"""
    def __init__(self, not_detected=None):
        self.value = os.getenv(
            'SHELL',
            not_detected
        )
