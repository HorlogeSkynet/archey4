"""Distribution and architecture detection class"""

from subprocess import check_output

import distro


class Distro:
    """Relies on the `distro` module and `uname` system program"""
    def __init__(self):
        self.value = '{0} [{1}]'.format(
            distro.name(pretty=True),
            check_output(
                ['uname', '-m'],
                universal_newlines=True
            ).rstrip()
        )
