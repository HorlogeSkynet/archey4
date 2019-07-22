"""Windows manager detection class"""

import re

from subprocess import check_output, DEVNULL, CalledProcessError

from archey.configuration import Configuration
from archey.processes import Processes


WM_DICT = {
    'awesome': 'Awesome',
    'beryl': 'Beryl',
    'blackbox': 'Blackbox',
    'bspwm': 'bspwm',
    'cinnamon': 'Cinnamon',
    'compiz': 'Compiz',
    'deepin-wm': 'Deepin WM',
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


class WindowManager:
    """
    Uses `wmctrl` to retrieve some information about the window manager.
    If not available, fall back on a simple iteration over the processes.
    """
    def __init__(self):
        try:
            window_manager = re.search(
                '(?<=Name: ).*',
                check_output(
                    ['wmctrl', '-m'],
                    stderr=DEVNULL, universal_newlines=True
                )
            ).group(0)

        except (FileNotFoundError, CalledProcessError):
            processes = Processes().get()
            for key, value in WM_DICT.items():
                if key in processes:
                    window_manager = value
                    break

            else:
                window_manager = Configuration().get('default_strings')['not_detected']

        self.value = window_manager
