"""Simple `__init__` file for the `logos` module, to load each distribution logo"""

from archey.logos.alpine_linux import ALPINE_LINUX
from archey.logos.android import ANDROID
from archey.logos.arch_linux import ARCH_LINUX
from archey.logos.bunsenlabs import BUNSENLABS
from archey.logos.centos import CENTOS
from archey.logos.crunchbang import CRUNCHBANG
from archey.logos.debian import DEBIAN
from archey.logos.elementary import ELEMENTARY
from archey.logos.fedora import FEDORA
from archey.logos.freebsd import FREEBSD
from archey.logos.gentoo import GENTOO
from archey.logos.kali_linux import KALI_LINUX
from archey.logos.manjaro import MANJARO
from archey.logos.nixos import NIXOS
from archey.logos.linux import LINUX
from archey.logos.linux_mint import LINUX_MINT
from archey.logos.pop import POP
from archey.logos.openbsd import OPENBSD
from archey.logos.opensuse import OPENSUSE
from archey.logos.raspbian import RASPBIAN
from archey.logos.red_hat import RED_HAT
from archey.logos.slackware import SLACKWARE
from archey.logos.ubuntu import UBUNTU
from archey.logos.windows import WINDOWS


def get_logo_width(logo, nb_colors=8):
    """
    Utility function computing the real width of a distribution logo.
    Rationale : We use placeholders to dynamically set ANSI colors.
                Although, they **DO NOT** take width space once the text as been printed.

    For performance purposes we compute the logo length based on its first line.
    See `archey.test.test_archey_logos` unit tests for further logos consistency verifications.

    `logo` is supposed to be one of the constants declared above.
    `nb_colors` must be greater than or equal to the number of colors used by the logo.
    """
    # We replace each placeholder by a 0-character string.
    return len(logo[0].format(c=[''] * nb_colors))
