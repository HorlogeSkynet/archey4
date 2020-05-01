"""Kernel information detection class"""

from subprocess import check_output

from archey.entry import Entry


class Kernel(Entry):
    """Another call to `uname` to retrieve kernel release information"""
    def __init__(self):
        super().__init__()

        self.value = check_output(
            ['uname', '-r'],
            universal_newlines=True
        ).rstrip()
