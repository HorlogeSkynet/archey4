import distro

from subprocess import check_output


class Distro:
    def __init__(self):
        self.value = '{0} [{1}]'.format(
            distro.name(pretty=True),
            check_output(
                ['uname', '-m'],
                universal_newlines=True
            ).rstrip()
        )

