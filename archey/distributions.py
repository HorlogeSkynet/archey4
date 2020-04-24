"""Distributions enumeration"""

from enum import Enum


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
    GENTOO = 'gentoo'
    KALI_LINUX = 'kali'
    MANJARO_LINUX = 'manjaro'
    LINUX = 'linux'
    LINUX_MINT = 'linuxmint'
    OPENSUSE = 'opensuse'
    RASPBIAN = 'raspbian'
    RED_HAT = 'rhel'
    SLACKWARE = 'slackware'
    UBUNTU = 'ubuntu'
    WINDOWS = 'windows'
