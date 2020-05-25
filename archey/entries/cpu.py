"""CPU information detection class"""

import re

from subprocess import check_output

from archey.entry import Entry


class CPU(Entry):
    """
    Parse `/proc/cpuinfo` file to retrieve the model name.
    If no information could be retrieved, calls `lscpu`.
    """
    _MODEL_NAME_REGEXP = re.compile(
        r'^model name\s*:\s*(.*)$',
        flags=re.IGNORECASE | re.MULTILINE
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        cpuinfo_match = self._read_proc_cpuinfo()
        if not cpuinfo_match:
            # This test case has been built for some ARM architectures (see #29).
            # Sometimes, `model name` info is not present within `/proc/cpuinfo`.
            # We use the output of `lscpu` program (util-linux-ng) to retrieve it.
            cpuinfo_match = self._run_lscpu()

        # Sometimes CPU model name contains extra ugly white-spaces.
        self.value = re.sub(r'\s+', ' ', cpuinfo_match.group(1))

    def _read_proc_cpuinfo(self):
        """Read `/proc/cpuinfo` and search for our model name pattern"""
        try:
            with open('/proc/cpuinfo') as f_cpu_info:
                return self._MODEL_NAME_REGEXP.search(f_cpu_info.read())
        except (PermissionError, FileNotFoundError):
            return None

    def _run_lscpu(self):
        """Same operation but from `lscpu` output"""
        return self._MODEL_NAME_REGEXP.search(
            check_output(
                ['lscpu'],
                env={'LANG': 'C'}, universal_newlines=True
            )
        )
