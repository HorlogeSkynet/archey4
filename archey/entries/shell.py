"""Shell detection class"""

import os

from archey.configuration import Configuration
from archey.entry import Entry


class Shell(Entry):
    """Simple shell detection based on the `SHELL` environment variable"""
    def __init__(self):
        super().__init__()

        self.value = os.getenv(
            'SHELL',
            Configuration()['default_strings']['not_detected']
        )
