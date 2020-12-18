"""Kernel information detection class"""

import json
import sys

from socket import timeout as SocketTimeoutError
from subprocess import check_output
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from typing import Optional

from archey.entry import Entry
from archey.environment import Environment
from archey.utility import Utility


class Kernel(Entry):
    """Another call to `uname` to retrieve kernel release information"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.value = {
            'release': self._fetch_kernel_release(),
            'latest': None,
            'is_outdated': None
        }

        # On GNU/Linux systems, if `check_version` has been enabled and `DO_NOT_TRACK` isn't set,
        #  retrieve the latest Linux kernel release in order to compare the current one against it.
        if not self.options.get('check_version') \
            or sys.platform != 'linux' \
            or Environment.DO_NOT_TRACK:
            return

        self.value['latest'] = self._fetch_latest_kernel_release()
        if self.value['latest']:
            self.value['is_outdated'] = (
                Utility.version_to_semver_segments(self.value['release'])
                < Utility.version_to_semver_segments(self.value['latest'])
            )

    @staticmethod
    def _fetch_kernel_release() -> str:
        return check_output(
            ['uname', '-r'],
            universal_newlines=True
        ).rstrip()

    @staticmethod
    def _fetch_latest_kernel_release() -> Optional[str]:
        try:
            http_request = urlopen('https://www.kernel.org/releases.json')
        except (HTTPError, URLError, SocketTimeoutError):
            return None

        try:
            # `json.load` does not accept binary file before Python 3.6.
            # We have to manually read and decode the HTTP body before passing it to `json`.
            kernel_releases = json.loads(http_request.read().decode())
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
