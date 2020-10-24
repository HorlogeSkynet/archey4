"""CPU information detection class"""

import re

from subprocess import check_output

from archey.entry import Entry


class CPU(Entry):
    """
    Parse `/proc/cpuinfo` file to retrieve model names.
    If no information could be retrieved, call `lscpu`.

    `value` attribute is populated as a `list` of `dict`.
    Each `dict` **SHOULD** contain only one entry (CPU model name as key and cores count as value).
    """
    _MODEL_NAME_REGEXP = re.compile(
        r'^model name\s*:\s*(.*)$',
        flags=re.IGNORECASE | re.MULTILINE
    )
    _PHYSICAL_ID_REGEXP = re.compile(
        r'^physical id\s*:\s*(\d+)$',
        flags=re.IGNORECASE | re.MULTILINE
    )
    _THREADS_PER_CORE_REGEXP = re.compile(
        r'^Thread\(s\) per core\s*:\s*(\d+)$',
        flags=re.IGNORECASE | re.MULTILINE
    )
    _CORES_PER_SOCKET_REGEXP = re.compile(
        r'^Core\(s\) per socket\s*:\s*(\d+)$',
        flags=re.IGNORECASE | re.MULTILINE
    )
    _SOCKETS_REGEXP = re.compile(
        r'^Socket\(s\)\s*:\s*(\d+)$',
        flags=re.IGNORECASE | re.MULTILINE
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.value = self._parse_proc_cpuinfo()
        if not self.value:
            # This test case has been built for some ARM architectures (see #29).
            # Sometimes, `model name` info is not present within `/proc/cpuinfo`.
            # We use the output of `lscpu` program (util-linux-ng) to retrieve it.
            self.value = self._parse_lscpu_output()


    @classmethod
    def _parse_proc_cpuinfo(cls):
        """Read `/proc/cpuinfo` and search for CPU model names occurrences"""
        try:
            with open('/proc/cpuinfo') as f_cpu_info:
                cpu_info = f_cpu_info.read()
        except (PermissionError, FileNotFoundError):
            return []

        model_names = cls._MODEL_NAME_REGEXP.findall(cpu_info)
        physical_ids = cls._PHYSICAL_ID_REGEXP.findall(cpu_info)

        cpus_list = []

        # Manually de-duplicates CPUs count.
        for model_name, physical_id in zip(model_names, physical_ids):
            # Sometimes CPU model names contain extra ugly white-spaces.
            model_name = re.sub(r'\s+', ' ', model_name)

            try:
                cpus_list[int(physical_id)][model_name] += 1
            except KeyError:
                # Different CPUs with same physical ids ? Shouldn't happen.
                cpus_list[int(physical_id)][model_name] = 1
            except IndexError:
                cpus_list.append({model_name: 1})

        return cpus_list

    @classmethod
    def _parse_lscpu_output(cls):
        """Same operation but from `lscpu` output"""
        cpu_info = check_output(
            ['lscpu'],
            env={'LANG': 'C'}, universal_newlines=True
        )

        nb_threads = cls._THREADS_PER_CORE_REGEXP.findall(cpu_info)
        nb_cores = cls._CORES_PER_SOCKET_REGEXP.findall(cpu_info)
        nb_sockets = cls._SOCKETS_REGEXP.findall(cpu_info)
        model_names = cls._MODEL_NAME_REGEXP.findall(cpu_info)

        cpus_list = []

        for threads, cores, sockets, model_name in zip(
                nb_threads, nb_cores, nb_sockets, model_names
            ):
            for _ in range(int(sockets)):
                # Sometimes CPU model names contain extra ugly white-spaces.
                cpus_list.append(
                    {re.sub(r'\s+', ' ', model_name): int(threads) * int(cores)}
                )

        return cpus_list

    def output(self, output):
        """Writes CPUs to `output` based on preferences"""
        # No CPU could be detected.
        if not self.value:
            output.append(self.name, self._default_strings.get('not_detected'))
            return

        entries = []
        for cpus in self.value:
            for model_name, cpu_count in cpus.items():
                if cpu_count > 1 and self.options.get('show_cores', True):
                    entries.append('{} x {}'.format(cpu_count, model_name))
                else:
                    entries.append(model_name)

        if self.options.get('one_line'):
            # One-line output is enabled : Join the results !
            output.append(self.name, ', '.join(entries))
        else:
            # One-line output has been disabled, add one entry per item.
            for entry in entries:
                output.append(self.name, entry)
