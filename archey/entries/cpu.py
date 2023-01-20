"""CPU information detection class"""

import json
import platform
import re
from subprocess import DEVNULL, CalledProcessError, check_output
from typing import Dict, List

from archey.distributions import Distributions
from archey.entry import Entry


class CPU(Entry):
    """
    Parse `/proc/cpuinfo` file to retrieve model names.
    If no information could be retrieved, call `lscpu`.

    `value` attribute is populated as a `list` of `dict`.
    Each `dict` **SHOULD** contain only one entry (CPU model name as key and cores count as value).
    """

    _MODEL_NAME_REGEXP = re.compile(
        r"^model name\s*:\s*(.*)$",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    _PHYSICAL_ID_REGEXP = re.compile(
        r"^physical id\s*:\s*(\d+)$",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    _THREADS_PER_CORE_REGEXP = re.compile(
        r"^Thread\(s\) per core\s*:\s*(\d+)$",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    _CORES_PER_SOCKET_REGEXP = re.compile(
        r"^Core\(s\) per socket\s*:\s*(\d+)$",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    _SOCKETS_REGEXP = re.compile(
        r"^Socket\(s\)\s*:\s*(\d+)$",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    _CLUSTERS_REGEXP = re.compile(
        r"^Cluster\(s\)\s*:\s*(\d+)$",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    _CORES_PER_CLUSTER_REGEXP = re.compile(
        r"^Core\(s\) per cluster\s*:\s*(\d+)$",
        flags=re.IGNORECASE | re.MULTILINE,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if platform.system() == "Linux":
            self.value = self._parse_proc_cpuinfo()
        elif Distributions.get_local() == Distributions.FREEBSD:
            self._parse_sysctl_cpu_model()
        else:
            # Darwin or any other BSD-based system.
            self.value = self._parse_system_profiler() or self._parse_sysctl_machdep()

        if not self.value:
            # This test case has been built for some ARM architectures (see #29 and #127).
            # Sometimes, model name and physical id info are missing from `/proc/cpuinfo`.
            # We use the output of `lscpu` program (util-linux-ng) to properly detect logical cores.
            self.value = self._parse_lscpu_output()

    @classmethod
    def _parse_proc_cpuinfo(cls) -> List[Dict[str, int]]:
        """Read `/proc/cpuinfo` and search for CPU model names occurrences"""
        try:
            with open("/proc/cpuinfo", encoding="ASCII") as f_cpu_info:
                cpu_info = f_cpu_info.read()
        except OSError:
            return []

        model_names = cls._MODEL_NAME_REGEXP.findall(cpu_info)
        physical_ids = cls._PHYSICAL_ID_REGEXP.findall(cpu_info)

        cpus_list: List[Dict[str, int]] = []

        # Manually de-duplicates CPUs count.
        for model_name, physical_id in zip(model_names, physical_ids):
            # Sometimes CPU model names contain extra ugly white-spaces.
            model_name = re.sub(r"\s+", " ", model_name)

            try:
                cpus_list[int(physical_id)][model_name] += 1
            except KeyError:
                # Different CPUs with same physical ids ? Shouldn't happen.
                cpus_list[int(physical_id)][model_name] = 1
            except IndexError:
                cpus_list.append({model_name: 1})

        return cpus_list

    @classmethod
    def _parse_lscpu_output(cls) -> List[Dict[str, int]]:
        """Same operation but from `lscpu` output"""
        try:
            cpu_info = check_output("lscpu", env={"LANG": "C"}, universal_newlines=True)
        except FileNotFoundError:
            return []

        nb_threads = cls._THREADS_PER_CORE_REGEXP.findall(cpu_info)
        nb_cores = cls._CORES_PER_SOCKET_REGEXP.findall(
            cpu_info
        ) or cls._CORES_PER_CLUSTER_REGEXP.findall(cpu_info)
        nb_slots = cls._SOCKETS_REGEXP.findall(cpu_info) or cls._CLUSTERS_REGEXP.findall(cpu_info)
        model_names = cls._MODEL_NAME_REGEXP.findall(cpu_info)

        cpus_list = []

        for threads, cores, slots, model_name in zip(nb_threads, nb_cores, nb_slots, model_names):
            for _ in range(int(slots)):
                # Sometimes CPU model names contain extra ugly white-spaces.
                cpus_list.append({re.sub(r"\s+", " ", model_name): int(threads) * int(cores)})

        return cpus_list

    @staticmethod
    def _parse_system_profiler() -> List[Dict[str, int]]:
        # Parse JSON output from Darwin's `system_profiler` binary.
        try:
            profiler_output = check_output(
                ["system_profiler", "-json", "SPHardwareDataType"],
                stderr=DEVNULL,
                universal_newlines=True,
            )
        except (FileNotFoundError, CalledProcessError):
            # `-json` is not available before Catalina.
            return []

        cpus_list = []

        for hw_overview in json.loads(profiler_output).get("SPHardwareDataType", []):
            model_name = hw_overview.get("cpu_type")
            nb_cores = hw_overview.get("number_processors")
            nb_sockets = hw_overview.get("packages")
            if not model_name or not nb_cores or not nb_sockets:
                continue

            # Add processor speed (if available).
            proc_speed = hw_overview.get("current_processor_speed")
            if proc_speed:
                model_name += f" @ {proc_speed.replace(',', '.')}"

            # Intel hyper-threading.
            if hw_overview.get("platform_cpu_htt") == "htt_enabled":
                nb_cores *= 2

            for _ in range(nb_sockets):
                cpus_list.append({model_name: nb_cores})

        return cpus_list

    @staticmethod
    def _parse_sysctl_machdep() -> List[Dict[str, int]]:
        # Runs `sysctl` to fetch some `machdep.cpu.*` keys.
        try:
            sysctl_output = check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string", "machdep.cpu.core_count"],
                stderr=DEVNULL,
                universal_newlines=True,
            )
        except (FileNotFoundError, CalledProcessError):
            return []

        # `sysctl_output` should exactly contains two lines.
        model_name, nb_cores = sysctl_output.splitlines()
        return [{model_name: int(nb_cores)}]

    @staticmethod
    def _parse_sysctl_cpu_model() -> List[Dict[str, int]]:
        # Runs `sysctl` to fetch `hw.model` and `hw.ncpu` keys.
        try:
            sysctl_output = check_output(
                ["sysctl", "-n", "hw.model", "hw.ncpu"], stderr=DEVNULL, universal_newlines=True
            )
        except (FileNotFoundError, CalledProcessError):
            return []

        # `sysctl_output` should exactly contains two lines.
        model_name, nb_cores = sysctl_output.splitlines()
        return [{model_name: int(nb_cores)}]

    def output(self, output) -> None:
        """Writes CPUs to `output` based on preferences"""
        # No CPU could be detected.
        if not self.value:
            output.append(self.name, self._default_strings.get("not_detected"))
            return

        entries = []
        for cpus in self.value:
            for model_name, cpu_count in cpus.items():
                if cpu_count > 1 and self.options.get("show_cores", True):
                    entries.append(f"{cpu_count} x {model_name}")
                else:
                    entries.append(model_name)

        if self.options.get("one_line"):
            # One-line output is enabled : Join the results !
            output.append(self.name, ", ".join(entries))
        else:
            # One-line output has been disabled, add one entry per item.
            for entry in entries:
                output.append(self.name, entry)
