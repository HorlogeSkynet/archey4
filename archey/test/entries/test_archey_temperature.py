"""Test module for Archey's temperature detection module"""

import os
import tempfile
import unittest
from subprocess import CalledProcessError
from unittest.mock import MagicMock, Mock, patch

from archey.configuration import DEFAULT_CONFIG
from archey.entries.temperature import Temperature
from archey.test import CustomAssertions
from archey.test.entries import HelperMethods


class TestTemperatureEntry(unittest.TestCase, CustomAssertions):
    """This module verifies Archey temperature detection"""

    def setUp(self):
        self.temperature_mock = HelperMethods.entry_mock(Temperature)
        self.temperature_mock._temps = []  # pylint: disable=protected-access

    @patch("archey.entries.temperature.run")  # Mock the `sensors` call.
    def test_run_sensors_ok(self, run_mock):
        """Test computations around `sensors` output"""
        run_mock.return_value.stdout = """\
{
   "who-cares-about":{
      "temp1":{
         "temp1_input": 45.000,
         "temp1_crit": 128.000
      },
      "temp2":{
         "temp2_input": 0.000,
         "temp2_crit": 128.000
      },
      "temp3":{
         "temp3_input": 38.000,
         "temp3_crit": 128.000
      },
      "temp4":{
         "temp4_input": 39.000,
         "temp4_crit": 128.000
      },
      "temp5":{
         "temp5_input": 0.000,
         "temp5_crit": 128.000
      },
      "temp6":{
         "temp6_input": 114.000,
         "temp6_crit": 128.000
      }
   },
   "the-chipsets-names":{
      "what-are":{
         "temp1_input": 45.000,
         "temp1_max": 100.000,
         "temp1_crit": 100.000,
         "temp1_crit_alarm": 0.000
      },
      "those":{
         "temp2_input": 43.000,
         "temp2_max": 100.000,
         "temp2_crit": 100.000,
         "temp2_crit_alarm": 0.000
      },
      "identifiers":{
         "temp3_input": 44.000,
         "temp3_max": 100.000,
         "temp3_crit": 100.000,
         "temp3_crit_alarm": 0.000
      }
   },
   "crap-a-fan-chip":{
      "fan1":{
         "fan1_input": 3386.000
      }
   }
}
"""
        # pylint: disable=protected-access
        Temperature._run_sensors(self.temperature_mock)
        self.assertListEqual(
            self.temperature_mock._temps, [45.0, 38.0, 39.0, 114.0, 45.0, 43.0, 44.0]
        )
        # pylint: enable=protected-access

    @patch("archey.entries.temperature.run")
    def test_run_sensors_ok_multiple_chipsets(self, run_mock):
        """Test `sensors` when multiple chipsets names have been passed"""
        run_mock.side_effect = [
            Mock(
                stdout="""\
{
   "who-cares-about":{
      "temp1":{
         "temp1_input": 45.000,
         "temp1_crit": 128.000
      },
      "temp2":{
         "temp2_input": 0.000,
         "temp2_crit": 128.000
      },
      "temp3":{
         "temp3_input": 38.000,
         "temp3_crit": 128.000
      }
   }
}
""",
                stderr=None,
            ),
            Mock(
                stdout="""\
{
   "the-chipsets-names":{
      "what-are":{
         "temp1_input": 45.000,
         "temp1_max": 100.000,
         "temp1_crit": 100.000,
         "temp1_crit_alarm": 0.000
      }
    }
}
""",
                stderr=None,
            ),
        ]

        sensors_chipsets = ["who-cares-about", "the-chipsets-names"]

        # pylint: disable=protected-access
        Temperature._run_sensors(self.temperature_mock, sensors_chipsets)
        self.assertListEqual(self.temperature_mock._temps, [45.0, 38.0, 45.0])
        # pylint: enable=protected-access

        # Check that our `run` mock has been called up to the number of passed chipsets.
        self.assertEqual(run_mock.call_count, len(sensors_chipsets))

    @patch("archey.entries.temperature.run")
    def test_run_sensors_ok_excluded_subfeatures(self, run_mock):
        """Test `sensors` when chipset subfeatures have been excluded"""
        run_mock.side_effect = [
            Mock(
                stdout="""\
{
   "k10temp-pci-00c3":{
      "Tctl":{
         "temp1_input": 42.000
      },
      "Tdie":{
         "temp2_input": 32.000
      }
   }
}
""",
                stderr=None,
            )
        ]

        # pylint: disable=protected-access
        Temperature._run_sensors(self.temperature_mock, excluded_subfeatures=["Tctl"])
        self.assertListEqual(self.temperature_mock._temps, [32.0])
        # pylint: enable=protected-access

    @patch(
        "archey.entries.temperature.run",
        side_effect=[
            CalledProcessError(1, "sensors"),  # `sensors` will hard fail.
            FileNotFoundError(),  # `sensors` won't be available.
        ],
    )
    def test_run_sensors_ko_exec(self, _):
        """Test `sensors` (hard) failure handling"""
        # pylint: disable=protected-access
        Temperature._run_sensors(self.temperature_mock)
        self.assertListEmpty(self.temperature_mock._temps)

        Temperature._run_sensors(self.temperature_mock)
        self.assertListEmpty(self.temperature_mock._temps)
        # pylint: enable=protected-access

    @patch("archey.entries.temperature.run")
    def test_run_sensors_ko_output(self, run_mock):
        """Test `sensors` (soft) failure handling"""
        # JSON decoding from `sensors` will fail...
        run_mock.return_value.stdout = """\
{
    "Is this JSON valid ?": [
        "You", "should", "look", "twice.",
    ]
}
"""
        # pylint: disable=protected-access
        Temperature._run_sensors(self.temperature_mock)
        self.assertListEmpty(self.temperature_mock._temps)
        # pylint: enable=protected-access

    @patch("archey.entries.temperature.iglob")
    def test_poll_thermal_zones(self, iglob_mock):
        """Tests sensor files handling"""

        ## BEGIN PRELUDE ##
        # We'll store there filenames of some temp files mocking those under
        #  `/sys/class/thermal/thermal_zone*/temp`
        tmp_files = []
        for temperature in (b"50000", b"0", b"40000", b"50000"):  # Fake temperatures
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(temperature)
                temp_file.seek(0)
                tmp_files.append(temp_file)
        ## END PRELUDE ##

        iglob_mock.return_value = iter([file.name for file in tmp_files])

        # pylint: disable=protected-access
        Temperature._poll_thermal_zones(self.temperature_mock)
        self.assertListEqual(self.temperature_mock._temps, [50.0, 40.0, 50.0])
        # pylint: enable=protected-access

        ## BEGIN POSTLUDE ##
        for tmp_file in tmp_files:
            tmp_file.close()
            os.remove(tmp_file.name)
        ## END POSTLUDE ##

    @patch(
        "archey.entries.temperature.check_output",
        side_effect=[
            # First case (`iStats` nor `OSX CPU Temp` won't be available).
            FileNotFoundError(),
            FileNotFoundError(),
            # Second case (`iStats` OK).
            "41.125\n",
            # Third case (`iStats` KO, `OSX CPU Temp` OK).
            FileNotFoundError(),
            "61.8 °C\n",
            # Fourth case (`OSX CPU Temp` KO, but with <= 1.1.0 output).
            # See lavoiesl/osx-cpu-temp#22.
            FileNotFoundError(),
            "0.0°C\n",
        ],
    )
    def test_run_istats_or_osxcputemp(self, _):
        """Test for `iStats` and `OSX CPU Temp` third-party programs outputs"""
        # pylint: disable=protected-access
        # First case.
        Temperature._run_istats_or_osxcputemp(self.temperature_mock)
        self.assertListEmpty(self.temperature_mock._temps)

        # Second case.
        Temperature._run_istats_or_osxcputemp(self.temperature_mock)
        self.assertListEqual(self.temperature_mock._temps, [41.125])

        # Reset internal object here.
        self.temperature_mock._temps = []

        # Third case.
        Temperature._run_istats_or_osxcputemp(self.temperature_mock)
        self.assertListEqual(self.temperature_mock._temps, [61.8])

        # Reset internal object here.
        self.temperature_mock._temps = []

        # Fourth case.
        Temperature._run_istats_or_osxcputemp(self.temperature_mock)
        self.assertListEmpty(self.temperature_mock._temps)
        # pylint: enable=protected-access

    @patch(
        "archey.entries.temperature.os.cpu_count", return_value=4  # Mocks a quad-cores CPU system.
    )
    @patch(
        "archey.entries.temperature.check_output",
        side_effect=[
            # First case (`sysctl` won't be available).
            FileNotFoundError(),
            # Second case (`sysctl` will fail).
            CalledProcessError(1, "sysctl"),
            # Third case (OK).
            """\
42C
42C
45C
45C
""",
            # Fourth case (partially-OK).
            """\
42
40
0
38
""",
        ],
    )
    def test_run_sysctl_dev_cpu(self, _, __):
        """Test for `sysctl` output only"""
        # pylint: disable=protected-access
        # First case.
        Temperature._run_sysctl_dev_cpu(self.temperature_mock)
        self.assertListEmpty(self.temperature_mock._temps)

        # Second case.
        Temperature._run_sysctl_dev_cpu(self.temperature_mock)
        self.assertListEmpty(self.temperature_mock._temps)

        # Third case.
        Temperature._run_sysctl_dev_cpu(self.temperature_mock)
        self.assertListEqual(self.temperature_mock._temps, [42.0, 42.0, 45.0, 45.0])

        # Reset internal object here.
        self.temperature_mock._temps = []

        # Fourth case.
        Temperature._run_sysctl_dev_cpu(self.temperature_mock)
        self.assertListEqual(self.temperature_mock._temps, [42.0, 40.0, 38.0])
        # pylint: enable=protected-access

    @patch(
        "archey.entries.temperature.check_output",
        side_effect=[
            FileNotFoundError(),
            "temp=42.8'C\n",
        ],
    )
    def test_run_vcgencmd(self, _):
        """Test for `vcgencmd` output only"""
        # pylint: disable=protected-access
        Temperature._run_vcgencmd(self.temperature_mock)
        self.assertListEmpty(self.temperature_mock._temps)

        Temperature._run_vcgencmd(self.temperature_mock)
        self.assertListEqual(self.temperature_mock._temps, [42.8])
        # pylint: enable=protected-access

    @HelperMethods.patch_clean_configuration
    def test_output(self):
        """Test `output` method"""
        output_mock = MagicMock()

        # No value --> not detected.
        Temperature.output(self.temperature_mock, output_mock)
        self.assertEqual(
            output_mock.append.call_args[0][1], DEFAULT_CONFIG["default_strings"]["not_detected"]
        )

        output_mock.reset_mock()

        # Values --> normal behavior.
        self.temperature_mock._temps = [50.0, 40.0, 50.0]  # pylint: disable=protected-access
        self.temperature_mock.value = {
            "temperature": 46.7,
            "max_temperature": 50.0,
            "char_before_unit": "o",
            "unit": "C",
        }
        Temperature.output(self.temperature_mock, output_mock)
        self.assertEqual(output_mock.append.call_args[0][1], "46.7oC (Max. 50.0oC)")

        # Only one value --> no maximum.
        self.temperature_mock._temps = [42.8]  # pylint: disable=protected-access
        self.temperature_mock.value = {
            "temperature": 42.8,
            "max_temperature": 42.8,
            "char_before_unit": " ",
            "unit": "C",
        }
        Temperature.output(self.temperature_mock, output_mock)
        self.assertEqual(output_mock.append.call_args[0][1], "42.8 C")

    def test_convert_to_fahrenheit(self):
        """Simple tests for the `_convert_to_fahrenheit` static method"""
        test_conversion_cases = (
            (-273.15, -459.67),
            (0.0, 32.0),
            (21.0, 69.8),
            (37.0, 98.6),
            (100.0, 212.0),
        )
        for celsius_value, expected_fahrenheit_value in test_conversion_cases:
            self.assertAlmostEqual(
                Temperature._convert_to_fahrenheit(  # pylint: disable=protected-access
                    celsius_value
                ),
                expected_fahrenheit_value,
            )


if __name__ == "__main__":
    unittest.main()
