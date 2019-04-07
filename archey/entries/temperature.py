import re
from glob import glob
from subprocess import check_output, DEVNULL, CalledProcessError


class Temperature:
    def __init__(self,
                 use_fahrenheit=False,
                 char_before_unit=' ',
                 not_detected=None):
        temps = []

        try:
            # Let's try to retrieve a value from the Broadcom chip on Raspberry
            temp = float(
                re.search(
                    r'\d+\.\d+',
                    check_output(
                        ['/opt/vc/bin/vcgencmd', 'measure_temp'],
                        stderr=DEVNULL, universal_newlines=True
                    )
                ).group(0)
            )

            temps.append(
                self._convert_to_fahrenheit(temp)
                if use_fahrenheit else temp
            )

        except (FileNotFoundError, CalledProcessError):
            pass

        # Now we just check for values within files present in the path below
        for thermal_file in glob('/sys/class/thermal/thermal_zone*/temp'):
            with open(thermal_file) as file:
                try:
                    temp = float(file.read().strip()) / 1000

                except OSError:
                    continue

                if temp != 0.0:
                    temps.append(
                        self._convert_to_fahrenheit(temp)
                        if use_fahrenheit
                        else temp
                    )

        if temps:
            self.value = '{0}{1}{2}'.format(
                str(round(sum(temps) / len(temps), 1)),
                char_before_unit,
                'F' if use_fahrenheit else 'C'
            )

            if len(temps) > 1:
                self.value += ' (Max. {0}{1}{2})'.format(
                    str(round(max(temps), 1)),
                    char_before_unit,
                    'F' if use_fahrenheit else 'C'
                )

        else:
            self.value = not_detected

    @staticmethod
    def _convert_to_fahrenheit(temp):
        """
        Simple Celsius to Fahrenheit conversion method
        """
        return temp * (9 / 5) + 32

