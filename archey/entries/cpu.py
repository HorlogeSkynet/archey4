"""CPU information detection class"""

import re

from subprocess import check_output

from archey.entry import Entry


class CPU(Entry):
    """
    Parse `/proc/cpuinfo` file to retrieve model names.
    If no information could be retrieved, call `lscpu`.

    `value` attribute is populated as a `dict`.
    It means that for Python < 3.6, "physical" CPU order **MAY** be lost.
    """
    _MODEL_NAME_REGEXP = re.compile(
        r'^model name\s*:\s*(.*)$',
        flags=re.IGNORECASE | re.MULTILINE
    )
    _CPUS_COUNT_REGEXP = re.compile(
        r'^CPU\(s\)\s*:\s*(\d+)$',
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
                cpu_models = cls._MODEL_NAME_REGEXP.findall(f_cpu_info.read())
        except (PermissionError, FileNotFoundError):
            return {}

        # Manually de-duplicates CPUs count.
        cpu_info = {}
        for cpu_model in cpu_models:
            # Sometimes CPU model names contain extra ugly white-spaces.
            cpu_model = re.sub(r'\s+', ' ', cpu_model)

            if cpu_model not in cpu_info:
                cpu_info[cpu_model] = 1
            else:
                cpu_info[cpu_model] += 1

        return cpu_info

    @classmethod
    def _parse_lscpu_output(cls):
        """Same operation but from `lscpu` output"""
        cpu_info = check_output(
            ['lscpu'],
            env={'LANG': 'C'}, universal_newlines=True
        )

        cpu_models = cls._MODEL_NAME_REGEXP.findall(cpu_info)
        cpu_counts = cls._CPUS_COUNT_REGEXP.findall(cpu_info)

        return {
            # Sometimes CPU model names contain extra ugly white-spaces.
            re.sub(r'\s+', ' ', cpu_model): int(cpu_count)
            for cpu_model, cpu_count in zip(cpu_models, cpu_counts)
        }


    def output(self, output):
        """Writes CPUs to `output` based on preferences"""
        def _pre_format(cpu_model, cpu_count):
            """Simple closure to format our CPU final entry content"""
            if cpu_count > 1 and self.options.get('show_count', True):
                return '{} x {}'.format(cpu_count, cpu_model)

            return cpu_model

        # No CPU could be detected.
        if not self.value:
            output.append(self.name, self._default_strings.get('not_detected'))
        # One-line output is enabled : Join the results !
        elif self.options.get('one_line', True):
            output.append(
                self.name,
                ', '.join([
                    _pre_format(cpu_model, cpu_count)
                    for cpu_model, cpu_count in self.value.items()
                ])
            )
        # One-line output has been disabled, add one entry per item.
        else:
            for cpu_model, cpu_count in self.value.items():
                output.append(self.name, _pre_format(cpu_model, cpu_count))
