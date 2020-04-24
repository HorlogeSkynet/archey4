"""Temperature detection class"""

import json
import re

from glob import iglob
from subprocess import check_output, DEVNULL, CalledProcessError

from archey.configuration import Configuration


class Temperature:
    """
    Tries to compute an average temperature from `sensors` (LM-Sensors).
    If not available, falls back on system thermal zones files.
    On Raspberry devices, retrieves temperature from the `vcgencmd` binary.
    """
    def __init__(self):
        # The configuration object is needed to retrieve some settings below.
        configuration = Configuration()

        self._temps = []

        # Tries `sensors` at first.
        self._run_sensors(configuration.get('temperature')['sensors_chipsets'])

        # On error (list still empty), checks for system thermal zones files.
        if not self._temps:
            self._poll_thermal_zones()

        # Tries `vcgencmd` for Raspberry devices.
        self._run_vcgencmd()

        # No value could be fetched...
        if not self._temps:
            self.value = configuration.get('default_strings')['not_detected']
            return

        # Let's DRY some constants once.
        use_fahrenheit = configuration.get('temperature')['use_fahrenheit']
        char_before_unit = configuration.get('temperature')['char_before_unit']

        # Conversion to Fahrenheit if needed.
        if use_fahrenheit:
            for i in range(len(self._temps)):
                self._temps[i] = self._convert_to_fahrenheit(self._temps[i])

        # Final average computation.
        self.value = '{0}{1}{2}'.format(
            str(round(sum(self._temps) / len(self._temps), 1)),
            char_before_unit,
            'F' if use_fahrenheit else 'C'
        )

        # Multiple values ? Show the hottest.
        if len(self._temps) > 1:
            self.value += ' (Max. {0}{1}{2})'.format(
                str(round(max(self._temps), 1)),
                char_before_unit,
                'F' if use_fahrenheit else 'C'
            )

    def _run_sensors(self, whitelisted_chips):
        # Uses the `sensors` program (from LM-Sensors) to interrogate thermal chip-sets.
        try:
            sensors_output = check_output(
                ['sensors', '-A', '-j'] + whitelisted_chips,
                universal_newlines=True
            )
        except (FileNotFoundError, CalledProcessError):
            return

        try:
            sensors_data = json.loads(sensors_output)
        # For backward compatibility with Python versions prior to 3.5.0
        #   we use `ValueError` instead of `json.JSONDecodeError`.
        except ValueError:
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
        for thermal_file in iglob('/sys/class/thermal/thermal_zone*/temp'):
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
    def _convert_to_fahrenheit(temp):
        """
        Simple Celsius to Fahrenheit conversion method
        """
        return temp * (9 / 5) + 32
