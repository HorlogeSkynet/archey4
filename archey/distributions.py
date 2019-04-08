"""Distributions enumeration"""

from enum import Enum


class Distributions(Enum):
    """
    This enumeration lists supported operating systems (keys).
    Values contain their not-yet-compiled REGEXP format string.
    """
    ARCH_LINUX = 'Arch.*'
    BUNSENLABS = 'BunsenLabs'
    CRUNCHBANG = 'CrunchBang'
    DEBIAN = '(Rasp|De)bian'
    FEDORA = 'Fedora'
    GENTOO = 'Gentoo'
    KALI_LINUX = 'Kali'
    MANJARO_LINUX = 'Manjaro ?Linux'
    LINUX = 'Linux'
    LINUX_MINT = 'Linux ?Mint'
    OPENSUSE = 'openSUSE'
    RED_HAT = '(Red ?Hat|RHEL)'
    SLACKWARE = 'Slackware'
    UBUNTU = 'Ubuntu'
    WINDOWS = 'Windows'
