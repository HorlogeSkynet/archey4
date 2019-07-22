"""CPU information detection class"""

import re

from subprocess import check_output


class CPU:
    """
    Parse `/proc/cpuinfo` file to retrieve the model name.
    If no information could be retrieved, calls `lscpu`.
    """
    def __init__(self):
        model_name_regex = re.compile(
            r'^model name\s*:\s*(.*)$',
            flags=re.IGNORECASE | re.MULTILINE
        )

        with open('/proc/cpuinfo') as file:
            cpuinfo = re.search(model_name_regex, file.read())

        # This test case has been built for some ARM architectures (see #29).
        # Sometimes, `model name` info is not present within `/proc/cpuinfo`.
        # We use the output of `lscpu` program (util-linux-ng) to retrieve it.
        if not cpuinfo:
            cpuinfo = re.search(
                model_name_regex,
                check_output(
                    ['lscpu'],
                    env={'LANG': 'C'}, universal_newlines=True
                )
            )

        # Sometimes CPU model name contains extra ugly white-spaces.
        self.value = re.sub(r'\s+', ' ', cpuinfo.group(1))
