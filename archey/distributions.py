from enum import Enum

# ----- Distributions fingerprints ---- #


class Distributions(Enum):
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

