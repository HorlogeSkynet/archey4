"""Logos colors and distributions / logos matching"""

import archey.logos as logos

from archey.colors import Colors
from archey.distributions import Distributions


# This dictionary contains which colors should be used for each supported distribution.
# The first element (`[0]`) of each list will be used to display text entries.
COLOR_DICT = {
    Distributions.ARCH_LINUX: [Colors.CYAN_BRIGHT, Colors.CYAN_NORMAL],
    Distributions.ALPINE_LINUX: [Colors.BLUE_BRIGHT],
    Distributions.BUNSENLABS: [Colors.WHITE_BRIGHT, Colors.YELLOW_BRIGHT, Colors.YELLOW_NORMAL],
    Distributions.CENTOS: [
        Colors.WHITE_BRIGHT,
        Colors.YELLOW_NORMAL, Colors.GREEN_BRIGHT, Colors.BLUE_NORMAL, Colors.MAGENTA_BRIGHT
    ],
    Distributions.CRUNCHBANG: [Colors.WHITE_BRIGHT],
    Distributions.DEBIAN: [Colors.RED_BRIGHT, Colors.RED_NORMAL],
    Distributions.FEDORA: [Colors.BLUE_NORMAL, Colors.WHITE_BRIGHT],
    Distributions.GENTOO: [Colors.MAGENTA_BRIGHT, Colors.WHITE_BRIGHT],
    Distributions.KALI_LINUX: [Colors.BLUE_BRIGHT, Colors.WHITE_BRIGHT],
    Distributions.MANJARO_LINUX: [Colors.GREEN_BRIGHT],
    Distributions.LINUX: [Colors.WHITE_BRIGHT, Colors.YELLOW_BRIGHT],
    Distributions.LINUX_MINT: [Colors.GREEN_BRIGHT, Colors.WHITE_BRIGHT],
    Distributions.OPENSUSE: [Colors.GREEN_NORMAL, Colors.WHITE_BRIGHT],
    Distributions.RASPBIAN: [Colors.RED_BRIGHT, Colors.RED_NORMAL],
    Distributions.RED_HAT: [Colors.RED_BRIGHT, Colors.WHITE_BRIGHT, Colors.RED_NORMAL],
    Distributions.SLACKWARE: [Colors.BLUE_NORMAL, Colors.BLUE_BRIGHT, Colors.CLEAR],
    Distributions.UBUNTU: [Colors.RED_BRIGHT, Colors.RED_NORMAL, Colors.YELLOW_BRIGHT],
    Distributions.WINDOWS: [
        Colors.BLUE_BRIGHT, Colors.RED_BRIGHT, Colors.GREEN_BRIGHT, Colors.YELLOW_NORMAL
    ]
}


# This dictionary contains which logo should be used for each supported distribution.
LOGOS_DICT = {
    Distributions.ALPINE_LINUX: logos.ALPINE_LINUX,
    Distributions.ARCH_LINUX: logos.ARCH_LINUX,
    Distributions.BUNSENLABS: logos.BUNSENLABS,
    Distributions.CENTOS: logos.CENTOS,
    Distributions.CRUNCHBANG: logos.CRUNCHBANG,
    Distributions.DEBIAN: logos.DEBIAN,
    Distributions.FEDORA: logos.FEDORA,
    Distributions.GENTOO: logos.GENTOO,
    Distributions.KALI_LINUX: logos.KALI_LINUX,
    Distributions.MANJARO_LINUX: logos.MANJARO,
    Distributions.LINUX: logos.LINUX,
    Distributions.LINUX_MINT: logos.LINUX_MINT,
    Distributions.OPENSUSE: logos.OPENSUSE,
    Distributions.RASPBIAN: logos.DEBIAN,  # Force the Debian logo for Raspbian.
    Distributions.RED_HAT: logos.RED_HAT,
    Distributions.SLACKWARE: logos.SLACKWARE,
    Distributions.UBUNTU: logos.UBUNTU,
    Distributions.WINDOWS: logos.WINDOWS
}
