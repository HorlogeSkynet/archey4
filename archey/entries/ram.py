"""RAM usage detection class"""

import os
import platform
import re
from contextlib import suppress
from subprocess import check_output
from typing import Tuple

from archey.colors import Colors
from archey.entry import Entry
from archey.exceptions import ArcheyException


class RAM(Entry):
    """
    First tries to use the `free` command to retrieve RAM usage.
    If not available, falls back on the parsing of `/proc/meminfo` file.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        used, total = self._get_used_total_values()
        if not total:
            return

        self.value = {
            "used": used,
            "total": total,
            "unit": "MiB",
        }

    def _get_used_total_values(self) -> Tuple[float, float]:
        """
        Returns a tuple containing used and total RAM values.
        Tries a variety of methods, increasing compatibility for a wide range of systems.
        """
        if platform.system() == "Linux":
            with suppress(IndexError, FileNotFoundError):
                return self._run_free_dash_m()
        elif platform.system() == "FreeBSD":
            with suppress(FileNotFoundError):
                return self._run_sysctl_mem()
        else:
            # Darwin or any other BSD-based system.
            with suppress(FileNotFoundError):
                return self._run_sysctl_and_vmstat()

        with suppress(OSError):
            return self._read_proc_meminfo()

        return 0, 0

    @staticmethod
    def _run_free_dash_m() -> Tuple[float, float]:
        """Call `free -m` and parse its output to retrieve current used and total RAM"""
        memory_usage = "".join(
            filter(
                re.compile(r"Mem").search,
                check_output(
                    ["free", "-m"], env={"LANG": "C"}, universal_newlines=True
                ).splitlines(),
            )
        ).split()

        return float(memory_usage[2]), float(memory_usage[1])

    @staticmethod
    def _read_proc_meminfo() -> Tuple[float, float]:
        """Same behavior but by reading from `/proc/meminfo` directly"""
        with open("/proc/meminfo", encoding="ASCII") as f_mem_info:
            mem_info_lines = f_mem_info.read().splitlines()

        # Store memory information into a dictionary.
        mem_info = {}
        for line in filter(None, mem_info_lines):
            key, value = line.split(":", maxsplit=1)
            mem_info[key] = float(value.strip(" kB")) / 1024

        total = mem_info["MemTotal"]
        # Here, let's imitate Neofetch's behavior.
        # See <https://github.com/dylanaraps/neofetch/wiki/Frequently-Asked-Questions>.
        used = (
            total
            + mem_info["Shmem"]
            - (
                mem_info["MemFree"]
                + mem_info["Cached"]
                + mem_info["SReclaimable"]
                + mem_info["Buffers"]
            )
        )
        # Imitates what `free` does when the obtained value happens to be incorrect.
        # See <https://gitlab.com/procps-ng/procps/blob/master/proc/sysinfo.c#L790>.
        if used < 0:
            used = total - mem_info["MemFree"]

        return used, total

    @staticmethod
    def _run_sysctl_and_vmstat() -> Tuple[float, float]:
        """From `sysctl` and `vm_stat` calls, compute used and total system RAM values"""
        total = float(check_output(["sysctl", "-n", "hw.memsize"], universal_newlines=True))

        vm_stat_lines = check_output("vm_stat", universal_newlines=True).splitlines()

        # From first heading line, fetch system page size.
        page_size_match = re.match(
            r"^Mach Virtual Memory Statistics: \(page size of (\d+) bytes\)$", vm_stat_lines[0]
        )
        if not page_size_match:
            raise ArcheyException("Couldn't parse `vm_stat` output, please open an issue.")
        page_size = int(page_size_match.group(1))

        # Store memory information into a dictionary.
        mem_info = {}
        for line in vm_stat_lines[1:]:  # We ignore the first heading line.
            key, value = line.split(":", maxsplit=1)
            mem_info[key] = int(value.lstrip().rstrip("."))

        # Here we imitate Ansible behavior to compute used RAM.
        used = (
            total
            - (mem_info["Pages wired down"] + mem_info["Pages active"] + mem_info["Pages inactive"])
            * page_size
        )

        return (used / 1024**2), (total / 1024**2)

    @staticmethod
    def _run_sysctl_mem() -> Tuple[float, float]:
        """
        Return used and total memory on FreeBSD
        """
        output = check_output(
            [
                "sysctl",
                "-n",
                "vm.stats.vm.v_page_count",
                "vm.stats.vm.v_free_count",
                "vm.stats.vm.v_inactive_count",
            ],
            universal_newlines=True,
        )
        total, free, inactive = [float(x) for x in output.splitlines()]

        page_size = os.sysconf(os.sysconf_names["SC_PAGESIZE"])

        mem_total = total * (page_size >> 10)
        mem_used = (total - free - inactive) * (page_size >> 10)

        return (mem_used / 1024), (mem_total / 1024)

    def output(self, output) -> None:
        """
        Adds the entry to `output` after pretty-formatting the RAM usage with color and units.
        """
        if not self.value:
            # Fall back on the default behavior if no RAM usage could be detected.
            super().output(output)
            return

        # DRY some constants
        used = self.value["used"]
        total = self.value["total"]
        unit = self.value["unit"]

        # Based on the RAM percentage usage, select the corresponding level color.
        level_color = Colors.get_level_color(
            (used / total) * 100,
            self.options.get("warning_use_percent", 33.3),
            self.options.get("danger_use_percent", 66.7),
        )

        output.append(
            self.name, f"{level_color}{int(used)} {unit}{Colors.CLEAR} / {int(total)} {unit}"
        )
