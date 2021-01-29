"""Kernel information detection class"""

import json
import platform
import sys

from socket import timeout as SocketTimeoutError
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from typing import Optional

from archey.entry import Entry
from archey.environment import Environment
from archey.utility import Utility


class Kernel(Entry):
    """
    Retrieve kernel release.
    [GNU/LINUX] If user-enabled, implement a version comparison against upstream data.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.value = {
            'release': platform.release(),
            'latest': None,
            'is_outdated': None
        }

        # On GNU/Linux systems, if `check_version` has been enabled and `DO_NOT_TRACK` isn't set,
        #  retrieve the latest Linux kernel release in order to compare the current one against it.
        if not self.options.get('check_version') \
            or sys.platform != 'linux' \
            or Environment.DO_NOT_TRACK:
            return

        self.value['latest'] = self._fetch_latest_linux_release()
        if self.value['latest']:
            self.value['is_outdated'] = (
                Utility.version_to_semver_segments(self.value['release'])
                < Utility.version_to_semver_segments(self.value['latest'])
            )

    @staticmethod
    def _fetch_latest_linux_release() -> Optional[str]:
        try:
            http_request = urlopen('https://www.kernel.org/releases.json')
        except (HTTPError, URLError, SocketTimeoutError):
            return None

        try:
            kernel_releases = json.load(http_request)
        except json.JSONDecodeError:
            return None

        return kernel_releases.get('latest_stable', {}).get('version')

    def output(self, output):
        """Display running kernel and latest kernel if possible"""
        text_output = self.value['release']

        if self.value['latest']:
            if self.value['is_outdated']:
                text_output += ' ({} {})'.format(
                    self.value['latest'],
                    self._default_strings.get('available')
                )
            else:
                text_output += ' ({})'.format(self._default_strings.get('latest'))

        output.append(self.name, text_output)
