"""Windows manager detection class"""

import os
import platform
import re
from subprocess import DEVNULL, CalledProcessError, check_output

from archey.entry import Entry
from archey.processes import Processes

WM_DICT = {
    "Amethyst": "Amethyst",
    "awesome": "Awesome",
    "beryl": "Beryl",
    "blackbox": "Blackbox",
    "bspwm": "bspwm",
    "cinnamon": "Cinnamon",
    "chunkwm": "ChunkWM",
    "compiz": "Compiz",
    "deepin-wm": "Deepin WM",
    "dwm": "DWM",
    "enlightenment": "Enlightenment",
    "herbstluftwm": "herbstluftwm",
    "fluxbox": "Fluxbox",
    "fvwm": "FVWM",
    "i3": "i3",
    "icewm": "IceWM",
    "kwin_x11": "KWin",
    "kwin_wayland": "KWin",
    "metacity": "Metacity",
    "musca": "Musca",
    "openbox": "Openbox",
    "pekwm": "PekWM",
    "qtile": "QTile",
    "ratpoison": "RatPoison",
    "Rectangle": "Rectangle",
    "scrotwm": "ScrotWM",
    "Spectacle": "Spectacle",
    "stumpwm": "StumpWM",
    "subtle": "Subtle",
    "monsterwm": "MonsterWM",
    "wingo": "Wingo",
    "wmaker": "Window Maker",
    "wmfs": "Wmfs",
    "wmii": "wmii",
    "xfwm4": "Xfwm",
    "xmonad": "Xmonad",
    "yabai": "Yabai",
}

DSP_DICT = {
    "x11": "X11",
    "wayland": "Wayland",
}


class WindowManager(Entry):
    """
    Uses `wmctrl` to retrieve some information about the window manager.
    If not available, fall back on a simple iteration over the processes.
    """

    _ICON = "\ueae4"  # cod_empty_window
    _PRETTY_NAME = "Window Manager"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        name = None
        try:
            name = re.search(  # type: ignore
                r"(?<=Name: ).*",
                check_output(["wmctrl", "-m"], stderr=DEVNULL, universal_newlines=True),
            ).group(0)
        except (FileNotFoundError, CalledProcessError):
            processes = Processes().list
            for wm_id, wm_name in WM_DICT.items():
                if wm_id in processes:
                    name = wm_name
                    break
            else:
                if platform.system() == "Darwin":
                    name = "Quartz Compositor"

        display_server_protocol = DSP_DICT.get(os.getenv("XDG_SESSION_TYPE", ""))

        self.value = {
            "name": name,
            "display_server_protocol": display_server_protocol,
        }

    def __str__(self) -> str:
        # No WM could be detected.
        if self.value["name"] is None:
            return self._default_strings.get("not_detected")

        text_output = self.value["name"]
        if self.value["display_server_protocol"] is not None:
            text_output += f" ({self.value['display_server_protocol']})"

        return text_output
