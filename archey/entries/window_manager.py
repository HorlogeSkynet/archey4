import re
from subprocess import (
    check_output,
    DEVNULL,
    CalledProcessError
)

from ._constants import WM_DICT


class WindowManager:
    def __init__(self, processes=[], not_detected=None):
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

