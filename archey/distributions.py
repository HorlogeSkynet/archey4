"""
Distributions enumeration module.
Operating Systems detection logic.
Interface to `os-release` (through `distro` module).
"""

import os
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
    ANDROID = 'android'
    ARCH_LINUX = 'arch'
    BUNSENLABS = 'bunsenlabs'
    CENTOS = 'centos'
    CRUNCHBANG = 'crunchbang'
    DEBIAN = 'debian'
    ELEMENTARY = 'elementary'
    FEDORA = 'fedora'
    FREEBSD = 'freebsd'
    GENTOO = 'gentoo'
    KALI_LINUX = 'kali'
    MANJARO_LINUX = 'manjaro'
    NIXOS = 'nixos'
    LINUX = 'linux'
    LINUX_MINT = 'linuxmint'
    OPENBSD = 'openbsd'
    OPENSUSE = 'opensuse'
    POP = 'pop'
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
        distribution = Distributions._detection_logic()

        # In case nothing got detected the "regular" way, fall-back on the Linux logo.
        if not distribution:
            # Android systems are currently not being handled by `distro`.
            # We imitate Neofetch behavior to manually "detect" them.
            # See <https://github.com/nir0s/distro/issues/253>.
            if os.path.isdir('/system/app') and os.path.isdir('/system/priv-app'):
                return Distributions.ANDROID

            return Distributions.LINUX

        # Below are brain-dead cases for distributions not properly handled by `distro`.
        # One _may_ want to add its own logic to add support for such undetectable systems.
        if distribution == Distributions.DEBIAN:
            # CrunchBang is tagged as _regular_ Debian by `distro`.
            # Below conditions are here to work-around this issue.
            # First condition : CrunchBang-Linux and CrunchBang-Monara.
            # Second condition : CrunchBang++ (CBPP).
            if os.path.isfile('/etc/lsb-release-crunchbang') \
                or os.path.isfile('/usr/bin/cbpp-exit'):
                return Distributions.CRUNCHBANG

        elif distribution == Distributions.UBUNTU:
            # Older Pop!_OS releases (< 20.*) didn't ship their own `ID` (from `os-release`).
            # Thus, they are detected as "regular" Ubuntu distributions.
            # We may here rely on their `NAME` (from `os-release`), which is sufficient.
            if Distributions.get_distro_name(pretty=False) == 'Pop!_OS':
                return Distributions.POP

        return distribution

    @staticmethod
    def _detection_logic():
        """Main distribution detection logic, relying on `distro`, handling _common_ cases"""
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
                pass

        # Nothing of the above matched, let's return `None` and let the caller handle it.
        return None

    @staticmethod
    def get_distro_name(pretty=True):
        """Simple wrapper to `distro` to return the current distribution _pretty_ name"""
        return distro.name(pretty=pretty) or None

    @staticmethod
    def get_ansi_color():
        """
        Simple wrapper to `distro` to return the distribution preferred ANSI color.
        See <https://www.freedesktop.org/software/systemd/man/os-release.html#ANSI_COLOR=>.
        """
        return distro.os_release_attr('ansi_color') or None
