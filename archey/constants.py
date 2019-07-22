"""Logos colors and distributions / logos matching"""

import archey.logos as logos
from archey.distributions import Distributions


COLOR_DICT = {
    Distributions.ARCH_LINUX: ['\x1b[0;34m', '\x1b[1;34m'],
    Distributions.BUNSENLABS: ['\x1b[1;37m', '\x1b[1;33m', '\x1b[0;33m'],
    Distributions.CRUNCHBANG: ['\x1b[1;37m', '\x1b[1;37m'],
    Distributions.DEBIAN: ['\x1b[0;31m', '\x1b[1;31m'],
    Distributions.FEDORA: ['\x1b[1;37m', '\x1b[0;34m'],
    Distributions.GENTOO: ['\x1b[1;37m', '\x1b[1;35m'],
    Distributions.KALI_LINUX: ['\x1b[1;37m', '\x1b[1;34m'],
    Distributions.MANJARO_LINUX: ['\x1b[0;32m', '\x1b[1;32m'],
    Distributions.LINUX: ['\x1b[1;33m', '\x1b[1;37m'],
    Distributions.LINUX_MINT: ['\x1b[1;37m', '\x1b[1;32m'],
    Distributions.OPENSUSE: ['\x1b[1;37m', '\x1b[1;32m'],
    Distributions.RED_HAT: ['\x1b[1;37m', '\x1b[1;31m', '\x1b[0;31m'],
    Distributions.SLACKWARE: ['\x1b[0;34m', '\x1b[1;34m', '\x1b[1;0m'],
    Distributions.UBUNTU: ['\x1b[0;31m', '\x1b[1;31m', '\x1b[0;33m'],
    Distributions.WINDOWS: ['\x1b[1;31m', '\x1b[1;34m',
                            '\x1b[1;32m', '\x1b[0;33m'],
    'sensors': ['\x1b[0;32m', '\x1b[0;33m', '\x1b[0;31m'],
    'clear': '\x1b[0m'
}

LOGOS_DICT = {
    Distributions.ARCH_LINUX: logos.ARCH_LINUX,
    Distributions.BUNSENLABS: logos.BUNSENLABS,
    Distributions.CRUNCHBANG: logos.CRUNCHBANG,
    Distributions.DEBIAN: logos.DEBIAN,
    Distributions.FEDORA: logos.FEDORA,
    Distributions.GENTOO: logos.GENTOO,
    Distributions.KALI_LINUX: logos.KALI_LINUX,
    Distributions.MANJARO_LINUX: logos.MANJARO,
    Distributions.LINUX: logos.LINUX,
    Distributions.LINUX_MINT: logos.LINUX_MINT,
    Distributions.OPENSUSE: logos.OPENSUSE,
    Distributions.RED_HAT: logos.RED_HAT,
    Distributions.SLACKWARE: logos.SLACKWARE,
    Distributions.UBUNTU: logos.UBUNTU,
    Distributions.WINDOWS: logos.WINDOWS
}
