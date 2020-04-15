"""Distribution and architecture detection class"""

from subprocess import check_output

import distro

from archey.entry import Entry


class Distro(Entry):
    """Relies on the `distro` module and `uname` system program"""
    def __init__(self):
        super().__init__()

        self.value = '{0} [{1}]'.format(
            distro.name(pretty=True),
            check_output(
                ['uname', '-m'],
                universal_newlines=True
            ).rstrip()
        )
