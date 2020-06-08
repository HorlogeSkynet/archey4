"""
Distributions enumeration module.
Operating Systems detection logic.
Interface to `os-release` (through `distro` module).
"""

import sys

from enum import Enum
from subprocess import check_output

import distro


class Distributions(Enum):
    """
    This enumeration lists supported operating systems (keys).
    Values contain their respective `distro` identifier.
    See <https://distro.readthedocs.io/en/latest/#distro.id>.
    """
    ALPINE_LINUX = 'alpine'
    ARCH_LINUX = 'arch'
    BUNSENLABS = 'bunsenlabs'
    CENTOS = 'centos'
    CRUNCHBANG = 'crunchbang'
    DEBIAN = 'debian'
    FEDORA = 'fedora'
    FREEBSD = 'freebsd'
    GENTOO = 'gentoo'
    KALI_LINUX = 'kali'
    MANJARO_LINUX = 'manjaro'
    LINUX = 'linux'
    LINUX_MINT = 'linuxmint'
    OPENBSD = 'openbsd'
    OPENSUSE = 'opensuse'
    RASPBIAN = 'raspbian'
    RED_HAT = 'rhel'
    SLACKWARE = 'slackware'
    UBUNTU = 'ubuntu'
    WINDOWS = 'windows'


    @staticmethod
    def get_distribution_identifiers():
        """Simple getter returning current supported distributions identifiers"""
        return [d.value for d in Distributions.__members__.values()]

    @staticmethod
    def run_detection():
        """Entry point of Archey distribution detection logic"""
        # Are we running on Windows ?
        if sys.platform in ('win32', 'cygwin'):
            return Distributions.WINDOWS

        # Is it a Windows Sub-system Linux (WSL) distribution ?
        # If so, kernel release identifier should keep a trace of it.
        if b'microsoft' in check_output(['uname', '-r']).lower():
            return Distributions.WINDOWS

        # Is `ID` (from `os-release`) well-known and supported ?
        try:
            return Distributions(distro.id())
        except ValueError:
            pass

        # Is any of `ID_LIKE` (from `os-release`) well-known and supported ?
        # See <https://www.freedesktop.org/software/systemd/man/os-release.html#ID_LIKE=>.
        for id_like in distro.like().split(' '):
            try:
                return Distributions(id_like)
            except ValueError:
                continue

        # At the moment, fall-back to default `Linux` if nothing of the above matched.
        return Distributions.LINUX

    @staticmethod
    def get_distro_name():
        """Simple wrapper to `distro` to return the current distribution _pretty_ name"""
        return distro.name(pretty=True) or None

    @staticmethod
    def get_ansi_color():
        """
        Simple wrapper to `distro` to return the distribution preferred ANSI color.
        See <https://www.freedesktop.org/software/systemd/man/os-release.html#ANSI_COLOR=>.
        """
        return distro.os_release_attr('ansi_color') or None
