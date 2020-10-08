"""
Logos colors definition.
Distributions / logos correspondences.
Default configuration.
"""

import archey.logos as logos

from archey.colors import Colors
from archey.distributions import Distributions


# This dictionary contains which colors should be used for each supported distribution.
# The first element (`[0]`) of each list will be used to display text entries.
COLORS_DICT = {
    Distributions.ARCH_LINUX: [Colors.CYAN_BRIGHT, Colors.CYAN_NORMAL],
    Distributions.ANDROID: [Colors.GREEN_BRIGHT, Colors.WHITE_BRIGHT],
    Distributions.ALPINE_LINUX: [Colors.BLUE_BRIGHT],
    Distributions.BUNSENLABS: [Colors.WHITE_BRIGHT, Colors.YELLOW_BRIGHT, Colors.YELLOW_NORMAL],
    Distributions.CENTOS: [
        Colors.WHITE_BRIGHT,
        Colors.YELLOW_NORMAL, Colors.GREEN_BRIGHT, Colors.BLUE_NORMAL, Colors.MAGENTA_BRIGHT
    ],
    Distributions.CRUNCHBANG: [Colors.WHITE_BRIGHT],
    Distributions.DEBIAN: [Colors.RED_BRIGHT, Colors.RED_NORMAL],
    Distributions.ELEMENTARY: [Colors.WHITE_BRIGHT],
    Distributions.FEDORA: [Colors.BLUE_BRIGHT, Colors.BLUE_NORMAL, Colors.WHITE_BRIGHT],
    Distributions.FREEBSD: [Colors.RED_BRIGHT, Colors.RED_NORMAL],
    Distributions.GENTOO: [Colors.MAGENTA_BRIGHT, Colors.WHITE_BRIGHT],
    Distributions.KALI_LINUX: [Colors.BLUE_BRIGHT, Colors.WHITE_BRIGHT],
    Distributions.MANJARO_LINUX: [Colors.GREEN_BRIGHT],
    Distributions.NIXOS: [Colors.BLUE_NORMAL, Colors.CYAN_NORMAL],
    Distributions.LINUX: [Colors.WHITE_BRIGHT, Colors.YELLOW_BRIGHT],
    Distributions.LINUX_MINT: [Colors.GREEN_BRIGHT, Colors.WHITE_BRIGHT],
    Distributions.POP: [Colors.CYAN_BRIGHT, Colors.WHITE_BRIGHT],
    Distributions.OPENBSD: [Colors.YELLOW_BRIGHT, Colors.WHITE_BRIGHT],
    Distributions.OPENSUSE: [Colors.GREEN_NORMAL, Colors.WHITE_BRIGHT],
    Distributions.RASPBIAN: [Colors.RED_BRIGHT, Colors.GREEN_NORMAL],
    Distributions.RED_HAT: [Colors.RED_BRIGHT, Colors.WHITE_BRIGHT, Colors.RED_NORMAL],
    Distributions.SLACKWARE: [Colors.BLUE_NORMAL, Colors.BLUE_BRIGHT, Colors.CLEAR],
    Distributions.UBUNTU: [Colors.RED_BRIGHT, Colors.WHITE_BRIGHT],
    Distributions.WINDOWS: [
        Colors.BLUE_BRIGHT, Colors.RED_BRIGHT, Colors.GREEN_BRIGHT, Colors.YELLOW_NORMAL
    ]
}


# This dictionary contains which logo should be used for each supported distribution.
LOGOS_DICT = {
    Distributions.ALPINE_LINUX: logos.ALPINE_LINUX,
    Distributions.ANDROID: logos.ANDROID,
    Distributions.ARCH_LINUX: logos.ARCH_LINUX,
    Distributions.BUNSENLABS: logos.BUNSENLABS,
    Distributions.CENTOS: logos.CENTOS,
    Distributions.CRUNCHBANG: logos.CRUNCHBANG,
    Distributions.DEBIAN: logos.DEBIAN,
    Distributions.ELEMENTARY: logos.ELEMENTARY,
    Distributions.FEDORA: logos.FEDORA,
    Distributions.FREEBSD: logos.FREEBSD,
    Distributions.GENTOO: logos.GENTOO,
    Distributions.KALI_LINUX: logos.KALI_LINUX,
    Distributions.MANJARO_LINUX: logos.MANJARO,
    Distributions.NIXOS: logos.NIXOS,
    Distributions.LINUX: logos.LINUX,
    Distributions.LINUX_MINT: logos.LINUX_MINT,
    Distributions.POP: logos.POP,
    Distributions.OPENBSD: logos.OPENBSD,
    Distributions.OPENSUSE: logos.OPENSUSE,
    Distributions.RASPBIAN: logos.RASPBIAN,
    Distributions.RED_HAT: logos.RED_HAT,
    Distributions.SLACKWARE: logos.SLACKWARE,
    Distributions.UBUNTU: logos.UBUNTU,
    Distributions.WINDOWS: logos.WINDOWS
}


# The default needed configuration which will be used by Archey is present below.
DEFAULT_CONFIG = {
    'allow_overriding': True,
    'parallel_loading': True,
    'suppress_warnings': False,
    'colors_palette': {
        'use_unicode': True,
        'honor_ansi_color': True
    },
    'disk': {
        'show_filesystems': ['local'],
        'combine_total': True,
        'disk_labels': None,
        'hide_entry_name': None
    },
    'default_strings': {
        'no_address': 'No Address',
        'not_detected': 'Not detected',
        'virtual_environment': 'Virtual Environment'
    },
    'gpu': {
        'one_line': True,
        'max_count': 2
    },
    'ip_settings': {
        'lan_ip_max_count': 2,
        'lan_ip_v6_support': True,
        'wan_ip_v6_support': True
    },
    'limits': {
        'ram': {
            'warning': 33.3,
            'danger': 66.7
        },
        'disk': {
            'warning': 50,
            'danger': 75
        }
    },
    'temperature': {
        'char_before_unit': ' ',
        'sensors_chipsets': [],
        'use_fahrenheit': False
    },
    'timeout': {
        'ipv4_detection': 1,
        'ipv6_detection': 1
    }
}
