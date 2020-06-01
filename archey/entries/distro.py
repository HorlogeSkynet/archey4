"""Distribution and architecture detection class"""

from subprocess import check_output

from archey.distributions import Distributions
from archey.entry import Entry


class Distro(Entry):
    """Uses `distro` module and `uname` system program to format `${DISTRO} [${ARCH}]` string"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.value = {
            'name': Distributions.get_distro_name(),
            'arch': check_output(
                ['uname', '-m'],
                universal_newlines=True
            ).rstrip()
        }


    def output(self, output):
        output.append(
            self.name,
            '{0} [{1}]'.format(
                (self.value['name'] or self._configuration.get('default_strings')['not_detected']),
                self.value['arch']
            )
        )
