"""Shell detection class"""

import os

from archey.configuration import Configuration
from archey.module import Module


class Shell(Module):
    """Simple shell detection based on the `SHELL` environment variable"""
    def __init__(self):
        self.name = Configuration().get("entry_names")["Shell"]
        self.value = os.getenv(
            'SHELL',
            Configuration().get('default_strings')['not_detected']
        )
