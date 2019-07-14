"""Shell detection class"""

import os

from archey.configuration import Configuration


class Shell:
    """Simple shell detection based on the `SHELL` environment variable"""
    def __init__(self):
        self.value = os.getenv(
            'SHELL',
            Configuration().get('default_strings')['not_detected']
        )
