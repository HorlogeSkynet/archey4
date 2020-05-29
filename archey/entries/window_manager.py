"""Windows manager detection class"""

import re

from subprocess import check_output, DEVNULL, CalledProcessError

from archey.entry import Entry
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


class WindowManager(Entry):
    """
    Uses `wmctrl` to retrieve some information about the window manager.
    If not available, fall back on a simple iteration over the processes.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.value = re.search(
                '(?<=Name: ).*',
                check_output(
                    ['wmctrl', '-m'],
                    stderr=DEVNULL, universal_newlines=True
                )
            ).group(0)
        except (FileNotFoundError, CalledProcessError):
            processes = Processes().list
            for wm_id, wm_name in WM_DICT.items():
                if wm_id in processes:
                    self.value = wm_name
                    break
