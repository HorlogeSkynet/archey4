"""Host name detection class"""

from subprocess import check_output

from archey.configuration import Configuration
from archey.module import Module


class Hostname(Module):
    """Simple call to `uname` to retrieve the host name"""
    def __init__(self):
        self.name = Configuration().get("entry_names")["Hostname"]
        self.value = check_output(
            ['uname', '-n'],
            universal_newlines=True
        ).rstrip()
