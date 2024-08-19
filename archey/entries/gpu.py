"""GPU information detection class"""

import contextlib
import os
import platform
import re
from pathlib import Path
from shlex import split
from subprocess import DEVNULL, CalledProcessError, check_output
from typing import List

from archey.entry import Entry

LINUX_DRI_DEBUGFS_PATH = Path("/sys/kernel/debug/dri")

# See <https://unix.stackexchange.com/a/725968>
LINUX_DRM_DEV_MAJOR = 226
LINUX_MAX_DRM_MINOR_PRIMARY = 63

# From <https://www.lambda-v.com/texts/programming/gpu/gpu_raspi.html#id_sec_vcdisasm_examples>
V3D_REV_TO_VC_VERSION = {
    "1": "VideoCore IV",  # Raspberry Pi 1 -> 3
    "4.2": "VideoCore VI",  # Raspberry Pi 4
    "7.1": "VideoCore VII",  # Raspberry Pi 5
}


class GPU(Entry):
    """Relies on `lspci` or `pciconf` to retrieve graphical device(s) information"""

    _ICON = "\ue735"  # dev_html5_3d_effects

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if platform.system() == "Linux":
            self.value = self._parse_lspci_output() + self._videocore_chipsets()
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
            lspci_output = check_output(["lspci", "-m"], universal_newlines=True).splitlines()
        except (FileNotFoundError, CalledProcessError):
            return []

        gpus_list = []

        # We'll be looking for specific video controllers (in the below keys order).
        for video_key in ("3D", "VGA", "Display"):
            for pci_device in lspci_output:
                pci_class, pci_vendor, pci_device = split(pci_device)[1:4]
                # If a controller type matches the class...
                if video_key in pci_class:
                    # ... adds its name to the final list.
                    gpus_list.append(f"{pci_vendor} {pci_device}")

        return gpus_list

    def _videocore_chipsets(self) -> List[str]:
        """
        Browse /dev/dri/card* to look for devices managed by vc4/v3d driver. From there, infer
        VideoCore chipset version from v3d driver revision (through kernel debugfs).

        See <https://unix.stackexchange.com/a/393324>.
        """
        videocore_chipsets = []

        for device in Path("/dev/dri").glob("card*"):
            # safety checks to make sure DRI cards are primary interface node devices
            # Python < 3.10, can't use `follow_symlinks=False` with `stat`
            st_rdev = device.stat().st_rdev
            if (
                os.major(st_rdev) != LINUX_DRM_DEV_MAJOR
                or os.minor(st_rdev) > LINUX_MAX_DRM_MINOR_PRIMARY
            ):
                continue

            with contextlib.suppress(OSError):
                # assert device card driver is vc4 or v3d
                if (LINUX_DRI_DEBUGFS_PATH / str(os.minor(st_rdev)) / "name").read_text().split()[
                    0
                ] not in ("vc4", "v3d"):
                    continue

                # retrieve driver (major.minor SemVer segments) revision from v3d_ident file
                # Note : there seems to be multiple "Revision" fields for v3d driver (1 global + 1
                #        per core). `re.search` will return the first match.
                v3d_revision = re.search(
                    r"Revision:\s*(\d(?:\.\d)?)",
                    (LINUX_DRI_DEBUGFS_PATH / str(os.minor(st_rdev)) / "v3d_ident").read_text(),
                )
                if v3d_revision is None:
                    self._logger.warning("could not find v3d driver revision for %s", device)
                    continue

                try:
                    videocore_chipsets.append(V3D_REV_TO_VC_VERSION[v3d_revision.group(1)])
                except KeyError:
                    self._logger.warning(
                        "could not infer VideoCore version from %s driver version %s",
                        device,
                        v3d_revision.group(1),
                    )

        return videocore_chipsets

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
