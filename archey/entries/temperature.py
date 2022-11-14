"""Temperature detection class"""

import json
import os
import platform
import re
from glob import iglob
from subprocess import DEVNULL, PIPE, CalledProcessError, check_output, run
from typing import List, Optional

from archey.entry import Entry


class Temperature(Entry):
    """
    Tries to compute an average temperature from `sensors` (LM-Sensors).
    If not available, falls back on system thermal zones files (GNU/Linux)
      or `sysctl` output for BSD and derivatives systems.
    On Raspberry devices, retrieves temperature from the `vcgencmd` binary.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._temps: List[float] = []

        # Tries `sensors` at first.
        self._run_sensors(
            self.options.get("sensors_chipsets"), self.options.get("sensors_excluded_subfeatures")
        )

        # On error (list still empty)...
        if not self._temps:
            if platform.system() == "Linux":
                # ... checks for system thermal zones files on GNU/Linux.
                self._poll_thermal_zones()
            elif platform.system() == "Darwin":
                self._run_istats_or_osxcputemp()
            else:
                # ... or tries `sysctl` calls (available on BSD and derivatives).
                self._run_sysctl_dev_cpu()

        # Tries `vcgencmd` for Raspberry devices.
        self._run_vcgencmd()

        # No value could be fetched, leave `self.value` to `None`.
        if not self._temps:
            return

        # Let's DRY some constants once.
        use_fahrenheit = self.options.get("use_fahrenheit")
        char_before_unit = self.options.get("char_before_unit", " ")

        # Conversion to Fahrenheit if needed.
        if use_fahrenheit:
            self._temps = list(map(self._convert_to_fahrenheit, self._temps))

        # Final average and maximum computations.
        self.value = {
            "temperature": float(round(sum(self._temps) / len(self._temps), 1)),
            "max_temperature": float(round(max(self._temps), 1)),
            "char_before_unit": char_before_unit,
            "unit": ("F" if use_fahrenheit else "C"),
        }

    def _run_sensors(
        self,
        whitelisted_chips: Optional[List[str]] = None,
        excluded_subfeatures: Optional[List[str]] = None,
    ):
        def _get_sensors_output(whitelisted_chip: Optional[str]) -> Optional[str]:
            sensors_args = ["sensors", "-A", "-j"]
            if whitelisted_chip is not None:
                sensors_args.append(whitelisted_chip)

            # Uses the `sensors` program (from lm-sensors) to query thermal chipsets.
            error_message = None
            try:
                sensors_output = run(
                    sensors_args, universal_newlines=True, stdout=PIPE, stderr=PIPE, check=True
                )
            except FileNotFoundError:
                return None
            except CalledProcessError as called_process_error:
                error_message = called_process_error.stderr
                return None
            else:
                error_message = sensors_output.stderr
            finally:
                # Log any `sensors` error messages at warning level.
                if error_message:
                    for line in error_message.splitlines():
                        self._logger.warning("[lm-sensors]: %s", line)

            return sensors_output.stdout

        sensors_outputs = []
        if whitelisted_chips:
            # Iterate over each whitelisted chipset and store JSON outputs.
            for whitelisted_chip in whitelisted_chips:
                sensors_outputs.append(_get_sensors_output(whitelisted_chip))
        else:
            sensors_outputs.append(_get_sensors_output(None))

        # Loop over output(s) and parse JSON documents.
        for sensors_output in sensors_outputs:
            if sensors_output is None:
                continue

            try:
                sensors_data = json.loads(sensors_output)
            except json.JSONDecodeError as json_decode_error:
                self._logger.warning(
                    "Couldn't decode JSON from sensors output : %s", json_decode_error
                )
                continue

            # Iterate over the chipsets outputs to retrieve interesting values.
            for features in sensors_data.values():
                for subfeature_name, subfeature_value in features.items():
                    # Has this subfeature been explicitly excluded in configuration ?
                    if excluded_subfeatures and subfeature_name in excluded_subfeatures:
                        continue

                    for name, value in subfeature_value.items():
                        # These conditions check whether this sub-feature value is a correct
                        #  temperature, as :
                        # * It might be an input fan speed (from a control chip) ;
                        # * Some chips/adapters might return null temperatures.
                        if value != 0.0 and re.match(r"temp\d_input", name):
                            self._temps.append(value)
                            # As there is only one `temp*_input` field per item,
                            #  we may stop the current sub-feature iteration now.
                            break

    def _poll_thermal_zones(self) -> None:
        # We just check for values within files present in the path below.
        for thermal_file in iglob(r"/sys/class/thermal/thermal_zone*/temp"):
            try:
                with open(thermal_file, encoding="ASCII") as file:
                    temp = float(file.read())
            except OSError:
                continue

            if temp != 0.0:
                self._temps.append(temp / 1000)

    def _run_istats_or_osxcputemp(self) -> None:
        """
        For Darwin systems, let's rely on `iStats` or `OSX CPU Temp` third-party programs.
        System's `powermetrics` program is **very** slow to run
          and requires administrator privileges.
        """
        # Run iStats binary (<https://github.com/Chris911/iStats>).
        try:
            istats_output = check_output(
                ["istats", "cpu", "temperature", "--value-only"], universal_newlines=True
            )
        except OSError:
            pass
        else:
            self._temps.append(float(istats_output))
            return

        # Run OSX CPU Temp binary (<https://github.com/lavoiesl/osx-cpu-temp>).
        try:
            osxcputemp_output = check_output("osx-cpu-temp", universal_newlines=True)
        except OSError:
            pass
        else:
            # Parse output across <= 1.1.0 versions and above.
            temp_match = re.search(r"\d+\.\d", osxcputemp_output)
            if temp_match is None:
                return
            temp = float(temp_match.group(0))
            if temp != 0.0:  # (Apple) System Management Control read _may_ fail.
                self._temps.append(temp)

    def _run_sysctl_dev_cpu(self) -> None:
        # Tries to get temperatures from each CPU core sensor.
        try:
            sysctl_output = check_output(
                ["sysctl", "-n"] + [f"dev.cpu.{i}.temperature" for i in range(os.cpu_count() or 1)],
                stderr=PIPE,
                universal_newlines=True,
            )
        except FileNotFoundError:
            # `sysctl` does not seem to be available on this system.
            return
        except CalledProcessError as error_message:
            self._logger.warning(
                "[sysctl]: Couldn't fetch temperature from CPU sensors (%s). "
                "Please be sure to load the corresponding kernel driver beforehand "
                "(`kldload coretemp` for Intel or `kldload amdtemp` for AMD`).",
                (error_message.stderr or "unknown error").rstrip(),
            )
            return

        for temp_output in sysctl_output.splitlines():
            # Strip any temperature unit from output (some drivers may add it).
            temp = float(temp_output.rstrip("C"))
            if temp != 0.0:
                self._temps.append(temp)

    def _run_vcgencmd(self) -> None:
        # Let's try to retrieve a value from the Broadcom chip on Raspberry.
        try:
            vcgencmd_output = check_output(
                ["/opt/vc/bin/vcgencmd", "measure_temp"], stderr=DEVNULL, universal_newlines=True
            )
        except (FileNotFoundError, CalledProcessError):
            return

        temp_match = re.search(r"\d+\.\d+", vcgencmd_output)
        if temp_match is not None:
            self._temps.append(float(temp_match.group(0)))

    @staticmethod
    def _convert_to_fahrenheit(temp: float) -> float:
        """Simple Celsius to Fahrenheit conversion method"""
        return temp * (9 / 5) + 32

    def output(self, output) -> None:
        """Adds the entry to `output` after pretty-formatting with units."""
        if not self.value:
            # Fall back on the default behavior if no temperatures were detected.
            super().output(output)
            return

        # DRY some constants
        char_before_unit = self.value["char_before_unit"]
        unit = self.value["unit"]

        entry_text = f"{self.value['temperature']}{char_before_unit}{unit}"
        # When there are multiple input sources, show the hottest value.
        if len(self._temps) > 1:
            entry_text += f" (Max. {self.value['max_temperature']}{char_before_unit}{unit})"

        output.append(self.name, entry_text)
