import os

from ._constants import DE_DICT


class DesktopEnvironment:
    def __init__(self, processes=[], not_detected=None):
        for key, value in DE_DICT.items():
            if key in processes:
                desktop_environment = value
                break

        else:
            # Let's rely on an environment var if the loop above didn't `break`
            desktop_environment = os.getenv(
                'XDG_CURRENT_DESKTOP',
                not_detected
            )

        self.value = desktop_environment
