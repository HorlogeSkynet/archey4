"""Desktop environment detection class"""

import os

from archey.configuration import Configuration
from archey.processes import Processes
from archey.module import Module


DE_DICT = {
    'cinnamon': 'Cinnamon',
    'dde-dock': 'Deepin',
    'gnome-session': 'GNOME',
    'gnome-shell': 'GNOME',
    'mate-session': 'MATE',
    'ksmserver': 'KDE',
    'xfce4-session': 'Xfce',
    'fur-box-session': 'Fur Box',
    'lxsession': 'LXDE',
    'lxqt-session': 'LXQt'
}


class DesktopEnvironment(Module):
    """
    Just iterate over running processes to find a known-entry.
    If not, rely on the `XDG_CURRENT_DESKTOP` environment variable.
    """
    def __init__(self):
        self.name = Configuration().get("entry_names")["DesktopEnvironment"]
        
        processes = Processes().get()
        for key, value in DE_DICT.items():
            if key in processes:
                desktop_environment = value
                break

        else:
            # Let's rely on an environment var if the loop above didn't `break`
            desktop_environment = os.getenv(
                'XDG_CURRENT_DESKTOP',
                Configuration().get('default_strings')['not_detected']
            )

        self.value = desktop_environment
