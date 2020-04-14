"""Kernel information detection class"""

from subprocess import check_output

from archey.configuration import Configuration
from archey.module import Module


class Kernel(Module):
    """Another call to `uname` to retrieve kernel release information"""
    def __init__(self):
        self.name = Configuration().get("entry_names")["Kernel"]
        self.value = check_output(
            ['uname', '-r'],
            universal_newlines=True
        ).rstrip()
