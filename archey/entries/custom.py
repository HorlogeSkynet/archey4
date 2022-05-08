"""Custom entry class"""

from contextlib import suppress
from subprocess import CalledProcessError, DEVNULL, PIPE, run
from typing import List

from archey.entry import Entry


class Custom(Entry):
    """Custom entry gathering info based on configuration options"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        shell = self.options.get("shell", False)
        if shell:
            command: str = self.options["command"]
        else:
            command: List[str] = self.options["command"]

        log_stderr = self.options.get("log_stderr", True)

        with suppress(CalledProcessError):
            proc = run(
                command,
                stdout=PIPE,
                stderr=PIPE if log_stderr else DEVNULL,
                shell=shell,
                check=self.options.get("check", True),
                universal_newlines=True,
            )
            if proc.stdout:
                self.value = proc.stdout.rstrip().splitlines()

            if log_stderr and proc.stderr:
                self._logger.warning("%s", proc.stderr.rstrip())

    def output(self, output):
        if not self.value:
            output.append(self.name, self._default_strings.get("not_detected"))
            return

        # Join the results only if `one_line` option is enabled.
        if self.options.get("one_line", True):
            output.append(self.name, ", ".join(self.value))
        else:
            for element in self.value:
                output.append(self.name, element)
