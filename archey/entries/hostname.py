"""Host name detection class"""

from subprocess import check_output

from archey.entry import Entry


class Hostname(Entry):
    """Simple call to `uname` to retrieve the host name"""
    def __init__(self):
        super().__init__()
        self.value = check_output(
            ['uname', '-n'],
            universal_newlines=True
        ).rstrip()
