"""Shell detection class"""

import os

from subprocess import CalledProcessError, check_output

from archey.configuration import Configuration


class Shell:
    """
    Simple shell path detection based either on the `SHELL` environment variable or
    the local administrative database.
    """
    def __init__(self):
        shell = os.getenv('SHELL')
        if not shell:
            try:
                shell = check_output(
                    ['getent', 'passwd', str(os.getuid())],
                    universal_newlines=True
                ).rstrip().split(':')[-1]
            except CalledProcessError:
                # Where does this user come from ?
                shell = Configuration().get('default_strings')['not_detected']

        self.value = shell
