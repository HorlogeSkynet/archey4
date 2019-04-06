import logos
from distributions import Distributions

# ------------ Dictionaries ----------- #

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

DE_DICT = {
    'cinnamon': 'Cinnamon',
    'gnome-session': 'GNOME',
    'gnome-shell': 'GNOME',
    'mate-session': 'MATE',
    'ksmserver': 'KDE',
    'xfce4-session': 'Xfce',
    'fur-box-session': 'Fur Box',
    'lxsession': 'LXDE',
    'lxqt-session': 'LXQt'
}

WM_DICT = {
    'awesome': 'Awesome',
    'beryl': 'Beryl',
    'blackbox': 'Blackbox',
    'bspwm': 'bspwm',
    'cinnamon': 'Cinnamon',
    'compiz': 'Compiz',
    'dwm': 'DWM',
    'enlightenment': 'Enlightenment',
    'herbstluftwm': 'herbstluftwm',
    'fluxbox': 'Fluxbox',
    'fvwm': 'FVWM',
    'i3': 'i3',
    'icewm': 'IceWM',
    'kwin_x11': 'KWin',
    'metacity': 'Metacity',
    'musca': 'Musca',
    'openbox': 'Openbox',
    'pekwm': 'PekWM',
    'qtile': 'QTile',
    'ratpoison': 'ratpoison',
    'scrotwm': 'ScrotWM',
    'stumpwm': 'StumpWM',
    'subtle': 'Subtle',
    'monsterwm': 'MonsterWM',
    'wingo': 'Wingo',
    'wmaker': 'Window Maker',
    'wmfs': 'Wmfs',
    'wmii': 'wmii',
    'xfwm4': 'Xfwm',
    'xmonad': 'xmonad'
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
    Distributions.OPENSUSE: logos.OPENUSE,
    Distributions.RED_HAT: logos.RED_HAT,
    Distributions.SLACKWARE: logos.SLACKWARE,
    Distributions.UBUNTU: logos.UBUNTU,
    Distributions.WINDOWS: logos.WINDOWS
}
