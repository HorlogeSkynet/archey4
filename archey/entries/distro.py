"""Distribution and architecture detection class"""

from subprocess import check_output

from archey.distributions import Distributions
from archey.entry import Entry


class Distro(Entry):
    """Uses `distro` module and `uname` system program to format `${DISTRO} [${ARCH}]` string"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        distro_name = Distributions.get_distro_name()
        if not distro_name:
            distro_name = self._fetch_android_release()

        self.value = {
            'name': distro_name,
            'arch': self._fetch_architecture()
        }

    @staticmethod
    def _fetch_architecture():
        """Simple wrapper to `uname -m` returning the current system architecture"""
        return check_output(
            ['uname', '-m'],
            universal_newlines=True
        ).rstrip()

    @staticmethod
    def _fetch_android_release():
        """Simple method to fetch current release on Android systems"""
        try:
            release = check_output(
                ['getprop', 'ro.build.version.release'],
                universal_newlines=True
            ).rstrip()
        except FileNotFoundError:
            return None

        return 'Android {0}'.format(release)


    def output(self, output):
        output.append(
            self.name,
            '{0} [{1}]'.format(
                (self.value['name'] or self._default_strings.get('not_detected')),
                self.value['arch']
            )
        )
