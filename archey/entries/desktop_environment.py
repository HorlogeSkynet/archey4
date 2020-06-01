"""Desktop environment detection class"""

import os

from archey.entry import Entry
from archey.processes import Processes


DE_DICT = {
    'cinnamon': 'Cinnamon',
    'dde-dock': 'Deepin',
    'fur-box-session': 'Fur Box',
    'gnome-session': 'GNOME',
    'gnome-shell': 'GNOME',
    'ksmserver': 'KDE',
    'lxqt-session': 'LXQt',
    'lxsession': 'LXDE',
    'mate-session': 'MATE',
    'xfce4-session': 'Xfce'
}


class DesktopEnvironment(Entry):
    """
    Just iterate over running processes to find a known-entry.
    If not, rely on the `XDG_CURRENT_DESKTOP` environment variable.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        processes = Processes().list
        for de_id, de_name in DE_DICT.items():
            if de_id in processes:
                self.value = de_name
                break
        else:
            # Let's rely on an environment variable if the loop above didn't `break`.
            self.value = os.getenv('XDG_CURRENT_DESKTOP')
