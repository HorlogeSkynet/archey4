"""Shell detection class"""

import os
from subprocess import CalledProcessError, check_output
from typing import Optional

from archey.entry import Entry


class Shell(Entry):
    """
    Simple shell path detection based either on the `SHELL` environment variable or
    the local administrative database.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.value = os.getenv("SHELL") or self._query_name_service_switch()

    @staticmethod
    def _query_name_service_switch() -> Optional[str]:
        try:
            user_id = os.getuid()
        except AttributeError:
            # Not UNIX...
            return None

        try:
            shell = (
                check_output(["getent", "passwd", str(user_id)], universal_newlines=True)
                .rstrip()
                .rsplit(":", maxsplit=1)[-1]
            )
        except CalledProcessError:
            # Ghost user...
            return None

        return shell
