"""Temperature detection class"""

import json
import logging
import re

from glob import iglob
from subprocess import CalledProcessError, DEVNULL, PIPE, check_output, run
from typing import List

from archey.entry import Entry


class Temperature(Entry):
    """
    Tries to compute an average temperature from `sensors` (LM-Sensors).
    If not available, falls back on system thermal zones files.
    On Raspberry devices, retrieves temperature from the `vcgencmd` binary.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._temps = []

        # Tries `sensors` at first.
        self._run_sensors(self.options.get('sensors_chipsets', []))

        # On error (list still empty), checks for system thermal zones files.
        if not self._temps:
            self._poll_thermal_zones()

        # Tries `vcgencmd` for Raspberry devices.
        self._run_vcgencmd()

        # No value could be fetched...
        if not self._temps:
            return

        # Let's DRY some constants once.
        use_fahrenheit = self.options.get('use_fahrenheit')
        char_before_unit = self.options.get('char_before_unit', ' ')

        # Conversion to Fahrenheit if needed.
        if use_fahrenheit:
            self._temps = list(map(self._convert_to_fahrenheit, self._temps))

        # Final average and maximum computations.
        self.value = {
            'temperature': float(round(sum(self._temps) / len(self._temps), 1)),
            'max_temperature': float(round(max(self._temps), 1)),
            'char_before_unit': char_before_unit,
            'unit': ('F' if use_fahrenheit else 'C')
        }


    def _run_sensors(self, whitelisted_chips: List[str]):
        # Uses the `sensors` program (from lm-sensors) to interrogate thermal chip-sets.
        try:
            sensors_output = run(
                ['sensors', '-A', '-j'] + whitelisted_chips,
                universal_newlines=True,
                stdout=PIPE, stderr=PIPE,
                check=True
            )
        except FileNotFoundError:
            error_message = None
            return
        except CalledProcessError as called_process_error:
            error_message = called_process_error.stderr
            return
        else:
            error_message = sensors_output.stderr
        finally:
            # Log any `sensors` error messages at warning level.
            if error_message:
                logging.warning('[lm-sensors]: %s', error_message.rstrip())

        try:
            sensors_data = json.loads(sensors_output.stdout)
        except json.JSONDecodeError:
            return

        # Iterates over the chip-sets outputs to filter interesting values.
        for features in sensors_data.values():
            for subfeatures in features.values():
                for name, value in subfeatures.items():
                    # These conditions check whether this sub-feature value is a correct
                    #  temperature, as :
                    # * It might be an input fan speed (from a control chip) ;
                    # * Some chips/adapters might return null temperatures.
                    if value != 0.0 and re.match(r"temp\d_input", name):
                        self._temps.append(value)
                        # There is only one `temp*_input` field, let's stop the current iteration.
                        break

    def _poll_thermal_zones(self):
        # We just check for values within files present in the path below.
        for thermal_file in iglob(r'/sys/class/thermal/thermal_zone*/temp'):
            with open(thermal_file) as file:
                try:
                    temp = float(file.read().strip()) / 1000
                except OSError:
                    continue

                if temp != 0.0:
                    self._temps.append(temp)

    def _run_vcgencmd(self):
        # Let's try to retrieve a value from the Broadcom chip on Raspberry.
        try:
            vcgencmd_output = check_output(
                ['/opt/vc/bin/vcgencmd', 'measure_temp'],
                stderr=DEVNULL, universal_newlines=True
            )
        except (FileNotFoundError, CalledProcessError):
            return

        self._temps.append(
            float(
                re.search(
                    r'\d+\.\d+',
                    vcgencmd_output
                ).group(0)
            )
        )

    @staticmethod
    def _convert_to_fahrenheit(temp: float) -> float:
        """Simple Celsius to Fahrenheit conversion method"""
        return temp * (9 / 5) + 32


    def output(self, output):
        """Adds the entry to `output` after pretty-formatting with units."""
        if not self.value:
            # Fall back on the default behavior if no temperatures were detected.
            super().output(output)
            return

        # DRY some constants
        char_before_unit = self.value['char_before_unit']
        unit = self.value['unit']

        entry_text = f"{self.value['temperature']}{char_before_unit}{unit}"
        # When there are multiple input sources, show the hottest value.
        if len(self._temps) > 1:
            entry_text += f" (Max. {self.value['max_temperature']}{char_before_unit}{unit})"

        output.append(self.name, entry_text)
