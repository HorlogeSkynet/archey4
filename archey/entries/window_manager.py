"""Windows manager detection class"""

import re

from subprocess import (
    check_output,
    DEVNULL,
    CalledProcessError
)

from .constants import WM_DICT


class WindowManager:
    """
    Uses `wmctrl` to retrieve some information about the window manager.
    If not available, fall back on a simple iteration over the processes.
    """
    def __init__(self, processes, not_detected=None):
        try:
            window_manager = re.search(
                '(?<=Name: ).*',
                check_output(
                    ['wmctrl', '-m'],
                    stderr=DEVNULL, universal_newlines=True
                )
            ).group(0)

        except (FileNotFoundError, CalledProcessError):
            for key, value in WM_DICT.items():
                if key in processes:
                    window_manager = value
                    break

            else:
                window_manager = not_detected

        self.value = window_manager
