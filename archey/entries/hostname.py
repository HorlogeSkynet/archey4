"""Host name detection class"""

from subprocess import check_output


class Hostname:
    """Simple call to `uname` to retrieve the host name"""
    def __init__(self):
        self.value = check_output(
            ['uname', '-n'],
            universal_newlines=True
        ).rstrip()
