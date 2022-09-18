"""Distribution and architecture detection class"""

import platform
from subprocess import check_output
from typing import Optional

from archey.distributions import Distributions
from archey.entry import Entry


class Distro(Entry):
    """Uses `distro` and `platform` modules to retrieve distribution and architecture information"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if platform.system() == "Darwin":
            distro_name = self._fetch_darwin_release()
        else:
            distro_name = Distributions.get_distro_name() or self._fetch_android_release()

        self.value = {"name": distro_name, "arch": platform.machine()}

    @staticmethod
    def _fetch_android_release() -> Optional[str]:
        """Simple method to fetch current release on Android systems"""
        try:
            release = check_output(
                ["getprop", "ro.build.version.release"], universal_newlines=True
            ).rstrip()
        except FileNotFoundError:
            return None

        return f"Android {release}"

    @staticmethod
    def _fetch_darwin_release() -> Optional[str]:
        """Simple method to fetch current release on Darwin systems"""
        # For macOS, let's mimic Python's `platform.platform` internal behavior here.
        macos_release = platform.mac_ver()[0]
        if macos_release:
            return f"macOS {macos_release}"

        return f"Darwin {platform.release()}"

    def output(self, output) -> None:
        output.append(
            self.name,
            f"{{}} {self.value['arch']}".format(
                self.value["name"] or self._default_strings.get("not_detected")
            ),
        )
