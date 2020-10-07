"""Test module for Archey's temperature detection module"""

import os
import tempfile

from subprocess import CalledProcessError

import unittest
from unittest.mock import MagicMock, patch


from archey.entries.temperature import Temperature


class TestTemperatureEntry(unittest.TestCase):
    """
    Based on `sensors`, `vcgencmd` and thermal files, this module verifies temperature computations.
    """

    def setUp(self):
        # We'll store there filenames of some temp files mocking those under
        #  `/sys/class/thermal/thermal_zone*/temp`
        self._temp_files = []
        for temperature in [  # Fake temperatures
                b'50000',
                b'0',
                b'40000',
                b'50000'
            ]:
            file = tempfile.NamedTemporaryFile(delete=False)
            file.write(temperature)
            file.seek(0)
            self._temp_files.append(file)

    def tearDown(self):
        for file in self._temp_files:
            file.close()
            os.remove(file.name)

    @patch(
        'archey.entries.temperature.check_output',
        side_effect=[
            FileNotFoundError(),
            'temp=42.8\'C\n'
        ]
    )
    @patch(
        'archey.entries.temperature.iglob',
        return_value=[]  # No temperature from file will be retrieved
    )
    def test_vcgencmd_only_no_max(self, _, __):
        """
        Test for `vcgencmd` output only (no sensor files).
        Only one value is retrieved, so no maximum should be displayed (see #39).
        """
        temperature = Temperature(options={
            'sensors_chipsets': [],
            'use_fahrenheit': False,
            'char_before_unit': ' '
        })

        output_mock = MagicMock()
        temperature.output(output_mock)

        self.assertDictEqual(
            temperature.value,
            {
                'temperature': 42.8,
                'max_temperature': 42.8,
                'char_before_unit': ' ',
                'unit': 'C'
            }
        )
        self.assertEqual(
            output_mock.append.call_args[0][1],
            '42.8 C'
        )

    @patch(
        'archey.entries.temperature.check_output',
        side_effect=[
            FileNotFoundError(),
            'temp=40.0\'C\n'
        ]
    )
    @patch('archey.entries.temperature.iglob')
    def test_vcgencmd_and_files(self, iglob_mock, _):
        """Tests `vcgencmd` output AND sensor files"""
        iglob_mock.return_value = iter([file.name for file in self._temp_files])
        self.assertDictEqual(
            Temperature(options={
                'sensors_chipsets': [],
                'use_fahrenheit': False,
                'char_before_unit': ' '
            }).value,
            {
                'temperature': 45.0,
                'max_temperature': 50.0,
                'char_before_unit': ' ',
                'unit': 'C'
            }
        )

    @patch(
        'archey.entries.temperature.check_output',
        side_effect=[
            FileNotFoundError(),  # No temperature from `sensors` call
            FileNotFoundError()   # No temperature from `vcgencmd` call
        ]
    )
    @patch('archey.entries.temperature.iglob')
    def test_files_only_in_fahrenheit(self, iglob_mock, _):
        """Test sensor files only, Fahrenheit (naive) conversion and special degree character"""
        iglob_mock.return_value = iter([file.name for file in self._temp_files])
        self.assertDictEqual(
            Temperature(options={
                'sensors_chipsets': [],
                'use_fahrenheit': True,
                'char_before_unit': '@'
            }).value,
            {
                'temperature': 116.0,      # 46.7 degrees C in Fahrenheit.
                'max_temperature': 122.0,  # 50 degrees C in Fahrenheit
                'char_before_unit': '@',
                'unit': 'F'
            }
        )

    @patch(
        'archey.entries.temperature.check_output',
        side_effect=[
            FileNotFoundError(),  # No temperature from `sensors` call.
            FileNotFoundError()   # No temperature from `vcgencmd` call.
        ]
    )
    @patch(
        'archey.entries.temperature.iglob',
        return_value=[]  # No temperature from file will be retrieved.
    )
    def test_no_output(self, _, __):
        """Test when no value could be retrieved (anyhow)"""
        self.assertIsNone(Temperature(options={
            'sensors_chipsets': []
        }).value)

    @patch(
        'archey.entries.temperature.check_output',  # Mock the `sensors` call.
        side_effect=[
            """\
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
""",
            FileNotFoundError()  # No temperature from `vcgencmd` call.
        ]
    )
    def test_sensors_only_in_fahrenheit(self, _):
        """Test computations around `sensors` output and Fahrenheit (naive) conversion"""
        self.assertDictEqual(
            Temperature(options={
                'sensors_chipsets': [],
                'use_fahrenheit': True,
                'char_before_unit': ' '
            }).value,
            {
                'temperature': 126.6,      # (52.6 C in F)
                'max_temperature': 237.2,  # (114.0 C in F)
                'char_before_unit': ' ',
                'unit': 'F'
            }
        )

    @patch(
        'archey.entries.temperature.check_output',
        side_effect=[
            CalledProcessError(1, 'sensors'),  # `sensors` will hard fail.
            FileNotFoundError()                # No temperature from `vcgencmd` call
        ]
    )
    @patch('archey.entries.temperature.iglob')
    def test_sensors_error_1(self, iglob_mock, _):
        """Test `sensors` (hard) failure handling and polling from files in Celsius"""
        iglob_mock.return_value = iter([file.name for file in self._temp_files])

        temperature = Temperature(options={
            'sensors_chipsets': [],
            'use_fahrenheit': False,
            'char_before_unit': 'o'
        })

        output_mock = MagicMock()
        temperature.output(output_mock)

        self.assertDictEqual(
            temperature.value,
            {
                'temperature': 46.7,
                'max_temperature': 50.0,
                'char_before_unit': 'o',
                'unit': 'C'
            }
        )
        self.assertEqual(
            output_mock.append.call_args[0][1],
            '46.7oC (Max. 50.0oC)'
        )

    @patch(
        'archey.entries.temperature.check_output',
        side_effect=[  # JSON decoding from `sensors` will fail..
            """\
{
    "Is this JSON valid ?": [
        "You", "should", "look", "twice.",
    ]
}
""",
            FileNotFoundError()  # No temperature from `vcgencmd` call
        ]
    )
    @patch('archey.entries.temperature.iglob')
    def test_sensors_error_2(self, iglob_mock, _):
        """Test `sensors` (hard) failure handling and polling from files in Celsius"""
        iglob_mock.return_value = iter([file.name for file in self._temp_files])
        self.assertDictEqual(
            Temperature(options={
                'sensors_chipsets': [],
                'use_fahrenheit': False,
                'char_before_unit': 'o'
            }).value,
            {
                'temperature': 46.7,
                'max_temperature': 50.0,
                'char_before_unit': 'o',
                'unit': 'C'
            }
        )

    @patch(
        'archey.entries.temperature.check_output',
        side_effect=[
            FileNotFoundError(),  # No temperature from `sensors` call.
            FileNotFoundError()   # No temperature from `vcgencmd` call.
        ]
    )
    @patch(
        'archey.entries.temperature.iglob',
        return_value=[]  # No temperature from file will be retrieved.
    )
    def test_celsius_to_fahrenheit_conversion(self, _, __):
        """Simple tests for the `_convert_to_fahrenheit` static method"""
        test_conversion_cases = [
            (-273.15, -459.67),
            (0.0, 32.0),
            (21.0, 69.8),
            (37.0, 98.6),
            (100.0, 212.0)
        ]

        for celsius_value, expected_fahrenheit in test_conversion_cases:
            self.assertAlmostEqual(
                Temperature._convert_to_fahrenheit(celsius_value),  # pylint: disable=protected-access
                expected_fahrenheit
            )


if __name__ == '__main__':
    unittest.main()
