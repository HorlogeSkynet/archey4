"""Kernel information detection class"""

import json
import platform
from socket import timeout as SocketTimeoutError
from typing import Optional
from urllib.error import URLError
from urllib.request import urlopen

from archey.entry import Entry
from archey.environment import Environment
from archey.utility import Utility


class Kernel(Entry):
    """
    Retrieve kernel identity.
    [GNU/LINUX] If user-enabled, implement a version comparison against upstream data.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.value = {
            "name": platform.system(),
            "release": platform.release(),
            "latest": None,
            "is_outdated": None,
        }

        # On GNU/Linux systems, if `check_version` has been enabled and `DO_NOT_TRACK` isn't set,
        #  retrieve the latest kernel release in order to compare the current one against it.
        if (
            not self.options.get("check_version")
            or self.value["name"] != "Linux"
            or Environment.DO_NOT_TRACK
        ):
            return

        self.value["latest"] = self._fetch_latest_linux_release()
        if self.value["latest"]:
            self.value["is_outdated"] = Utility.version_to_semver_segments(
                self.value["release"]
            ) < Utility.version_to_semver_segments(self.value["latest"])

    @staticmethod
    def _fetch_latest_linux_release() -> Optional[str]:
        try:
            with urlopen("https://www.kernel.org/releases.json") as http_request:
                try:
                    kernel_releases = json.load(http_request)
                except json.JSONDecodeError:
                    return None
        except (URLError, SocketTimeoutError):
            return None

        return kernel_releases.get("latest_stable", {}).get("version")

    def output(self, output) -> None:
        """Display running kernel and latest kernel if possible"""
        text_output = " ".join((self.value["name"], self.value["release"]))

        if self.value["latest"]:
            if self.value["is_outdated"]:
                text_output += f" ({self.value['latest']} {self._default_strings.get('available')})"
            else:
                text_output += f" ({self._default_strings.get('latest')})"

        output.append(self.name, text_output)
