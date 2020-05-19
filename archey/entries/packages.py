"""Number of installed packages detection class"""

import os

from subprocess import check_output, DEVNULL, CalledProcessError

from archey.entry import Entry


PACKAGES_TOOLS = (
    {'cmd': ('apk', 'list', '--installed')},
    # As of 2020, `apt` is _very_ slow compared to `dpkg` on Debian-based distributions.
    # Additional note : `apt`'s CLI is currently not "stable" in Debian terms.
    #{'cmd': ('apt', 'list', '-qq', '--installed')},
    {'cmd': ('dnf', 'list', 'installed'), 'skew': 1},
    {'cmd': ('dpkg', '--get-selections')},
    {'cmd': ('emerge', '-ep', 'world'), 'skew': 5},
    {'cmd': ('pacman', '-Q')},
    {'cmd': ('rpm', '-qa')},
    {'cmd': ('yum', 'list', 'installed'), 'skew': 2},
    {'cmd': ('zypper', 'search', '-i'), 'skew': 5}
)


class Packages(Entry):
    """Relies on the first found packages manager to list the installed packages"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for packages_tool in PACKAGES_TOOLS:
            try:
                results = check_output(
                    packages_tool['cmd'],
                    stderr=DEVNULL,
                    env={
                        'LANG': 'C',
                        # Alpine Linux: We have to manually propagate `PATH`.
                        #               `apk` wouldn't be found otherwise.
                        'PATH': os.getenv('PATH')
                    },
                    universal_newlines=True
                )
            except (FileNotFoundError, CalledProcessError):
                continue

            self.value = results.count(os.linesep)

            # If any, deduct output skew present due to the packages tool.
            if 'skew' in packages_tool:
                self.value -= packages_tool['skew']

            # For DPKG only, remove any not purged package.
            if packages_tool['cmd'][0] == 'dpkg':
                self.value -= results.count('deinstall')

            # At this step, we may break the loop.
            break
