"""Number of installed packages detection class"""

from subprocess import check_output, DEVNULL, CalledProcessError

from archey.configuration import Configuration
from archey.entry import Entry


PACKAGES_TOOLS = (
    {'cmd': ['apt', 'list', '-qq', '--installed']},
    {'cmd': ['dnf', 'list', 'installed'], 'skew': 1},
    {'cmd': ['dpkg', '--get-selections']},
    {'cmd': ['emerge', '-ep', 'world'], 'skew': 5},
    {'cmd': ['pacman', '-Q']},
    {'cmd': ['rpm', '-qa']},
    {'cmd': ['yum', 'list', 'installed'], 'skew': 2},
    {'cmd': ['zypper', 'search', '-i'], 'skew': 5}
)


class Packages(Entry):
    """Relies on the first found packages manager to list the installed packages"""
    def __init__(self):
        super().__init__()

        for packages_tool in PACKAGES_TOOLS:
            try:
                results = check_output(
                    packages_tool['cmd'],
                    stderr=DEVNULL,
                    env={'LANG': 'C'},
                    universal_newlines=True
                )
            except (FileNotFoundError, CalledProcessError):
                continue

            packages = results.count('\n')

            # If any, deduct any skew present due to the packages tool output.
            if 'skew' in packages_tool:
                packages -= packages_tool['skew']

            # For DPKG only, remove any not purged package.
            if packages_tool['cmd'][0] == 'dpkg':
                packages -= results.count('deinstall')

            # At this step, we may break the loop.
            break

        else:
            packages = Configuration()['default_strings']['not_detected']

        self.value = packages
