"""GPU information detection class"""

import platform
import re
from subprocess import DEVNULL, CalledProcessError, check_output
from typing import List

from archey.entry import Entry


class GPU(Entry):
    """Relies on `lspci` or `pciconf` to retrieve graphical device(s) information"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if platform.system() == "Linux":
            self.value = self._parse_lspci_output()
        else:
            # Darwin or any other BSD-based system.
            self.value = self._parse_system_profiler() or self._parse_pciconf_output()

        max_count = self.options.get("max_count", 2)
        # Consistency with other entries' configuration: Infinite count if false.
        if max_count is not False:
            self.value = self.value[:max_count]

    @staticmethod
    def _parse_lspci_output() -> List[str]:
        """Based on `lspci` output, return a list of video controllers names"""
        try:
            lspci_output = check_output("lspci", universal_newlines=True).splitlines()
        except (FileNotFoundError, CalledProcessError):
            return []

        gpus_list = []

        # We'll be looking for specific video controllers (in the below keys order).
        for video_key in ("3D", "VGA", "Display"):
            for pci_device in lspci_output:
                # If a controller type match...
                if video_key in pci_device:
                    # ... adds its name to the final list.
                    gpus_list.append(pci_device.partition(": ")[2])

        return gpus_list

    @staticmethod
    def _parse_system_profiler() -> List[str]:
        """Based on `system_profiler` output, return a list of video chipsets model names"""
        # Parse output from Darwin's `system_profiler` binary.
        # We do not use JSON output (more than 10 times longer for nothing).
        try:
            profiler_output = check_output(
                ["system_profiler", "SPDisplaysDataType"], stderr=DEVNULL, universal_newlines=True
            )
        except FileNotFoundError:
            return []

        return re.findall(r"Chipset Model: (.*)", profiler_output, re.MULTILINE)

    @staticmethod
    def _parse_pciconf_output() -> List[str]:
        """Based on `pciconf` output, return a list of video devices as long as their vendor"""
        try:
            pciconf_output = check_output(
                ["pciconf", "-lv"], stderr=DEVNULL, universal_newlines=True
            )
        except (FileNotFoundError, CalledProcessError):
            return []

        gpus_list = []

        for vendor, device in re.findall(
            r"vendor\s*=\s*\'(.*)\'\s*device\s*=\s*\'(.*)\'\s*class\s*=\s*display",
            pciconf_output,
            re.MULTILINE,
        ):
            gpus_list.append(f"{vendor} {device}")

        return gpus_list

    def output(self, output) -> None:
        """Writes GPUs to `output` based on preferences"""
        # No GPU could be detected.
        if not self.value:
            output.append(self.name, self._default_strings.get("not_detected"))
            return

        # Join the results only if `one_line` option is enabled.
        if self.options.get("one_line"):
            output.append(self.name, ", ".join(self.value))
        else:
            for gpu_device in self.value:
                output.append(self.name, gpu_device)
