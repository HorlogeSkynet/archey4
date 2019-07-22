"""Kernel information detection class"""

from subprocess import check_output


class Kernel:
    """Another call to `uname` to retrieve kernel release information"""
    def __init__(self):
        self.value = check_output(
            ['uname', '-r'],
            universal_newlines=True
        ).rstrip()
