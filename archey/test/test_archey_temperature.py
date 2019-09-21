"""Test module for Archey's temperature detection module"""

import os
import tempfile

from subprocess import CalledProcessError

import unittest
from unittest.mock import patch


from archey.entries.temperature import Temperature


class TestTemperatureEntry(unittest.TestCase):
    """
    Based on `sensors`, `vcgencmd` and thermal files, this module verifies temperature computations.
    """

    def setUp(self):
        # We'll store there filenames of some temp files mocking those under
        #  `/sys/class/thermal/thermal_zone*/temp`
        self.tempfiles = []
        for temperature in [  # Fake temperatures
                b'50000',
                b'0',
                b'40000',
                b'50000'
            ]:
            file = tempfile.NamedTemporaryFile(delete=False)
            file.write(temperature)
            file.seek(0)
            self.tempfiles.append(file)

    def tearDown(self):
        for file in self.tempfiles:
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
        'archey.entries.temperature.glob',
        return_value=[]  # No temperature from file will be retrieved
    )
    @patch(
        'archey.entries.temperature.Configuration.get',
        side_effect=[
            {'use_fahrenheit': False},
            {'char_before_unit': ' '}
        ]
    )
    def test_vcgencmd_only_no_max(self, _, __, ___):
        """
        Test for `vcgencmd` output only (no sensor files).
        Only one value is retrieved, so no maximum is displayed (see #39).
        """
        self.assertEqual(Temperature().value, '42.8 C')

    @patch(
        'archey.entries.temperature.check_output',
        side_effect=[
            FileNotFoundError(),
            'temp=40.0\'C\n'
        ]
    )
    @patch('archey.entries.temperature.glob')
    @patch(
        'archey.entries.temperature.Configuration.get',
        side_effect=[
            {'use_fahrenheit': False},
            {'char_before_unit': ' '}
        ]
    )
    def test_vcgencmd_and_files(self, _, glob_mock, __):
        """Tests `vcgencmd` output AND sensor files"""
        glob_mock.return_value = [file.name for file in self.tempfiles]
        self.assertEqual(Temperature().value, '45.0 C (Max. 50.0 C)')

    @patch(
        'archey.entries.temperature.check_output',
        side_effect=[
            FileNotFoundError(),  # No temperature from `sensors` call
            FileNotFoundError()   # No temperature from `vcgencmd` call
        ]
    )
    @patch('archey.entries.temperature.glob')
    @patch(
        'archey.entries.temperature.Configuration.get',
        side_effect=[
            {'use_fahrenheit': True},
            {'char_before_unit': '@'}
        ]
    )
    def test_files_only_in_fahrenheit(self, _, glob_mock, __):
        """Test sensor files only, Fahrenheit (naive) conversion and special degree character"""
        glob_mock.return_value = [file.name for file in self.tempfiles]
        self.assertEqual(
            Temperature().value,
            '116.0@F (Max. 122.0@F)'  # 46.7 and 50.0 converted into Fahrenheit.
        )

    @patch(
        'archey.entries.temperature.check_output',
        side_effect=[
            FileNotFoundError(),  # No temperature from `sensors` call.
            FileNotFoundError()   # No temperature from `vcgencmd` call.
        ]
    )
    @patch(
        'archey.entries.temperature.glob',
        return_value=[]  # No temperature from file will be retrieved.
    )
    @patch(
        'archey.entries.temperature.Configuration.get',
        return_value={'not_detected': 'Not detected'}
    )
    def test_no_output(self, _, __, ___):
        """Test when no value could be retrieved (anyhow)"""
        self.assertEqual(Temperature().value, 'Not detected')

    @patch(
        'archey.entries.temperature.check_output',  # Mock the `sensors` call.
        side_effect=[
            """\
{
   "who-care-about":{
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
   }
}
""",
            FileNotFoundError()  # No temperature from `vcgencmd` call.
        ]
    )
    @patch(
        'archey.entries.temperature.Configuration.get',
        side_effect=[
            {'use_fahrenheit': True},
            {'char_before_unit': ' '}
        ]
    )
    def test_sensors_only_in_fahrenheit(self, _, __):
        """Test computations around `sensors` output and Fahrenheit (naive) conversion"""
        self.assertEqual(
            Temperature().value,
            '126.6 F (Max. 237.2 F)'  # 52.6 and 114.0 converted into Fahrenheit.
        )

    @patch(
        'archey.entries.temperature.check_output',
        side_effect=[
            CalledProcessError(1, 'sensors'),  # `sensors` will hard fail.
            FileNotFoundError()                # No temperature from `vcgencmd` call
        ]
    )
    @patch('archey.entries.temperature.glob')
    @patch(
        'archey.entries.temperature.Configuration.get',
        side_effect=[
            {'use_fahrenheit': False},
            {'char_before_unit': 'o'}
        ]
    )
    def test_sensors_error_1(self, _, glob_mock, ___):
        """Test `sensors` (hard) failure handling and polling from files in Celsius"""
        glob_mock.return_value = [file.name for file in self.tempfiles]
        self.assertEqual(
            Temperature().value,
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
    @patch('archey.entries.temperature.glob')
    @patch(
        'archey.entries.temperature.Configuration.get',
        side_effect=[
            {'use_fahrenheit': False},
            {'char_before_unit': 'o'}
        ]
    )
    def test_sensors_error_2(self, _, glob_mock, ___):
        """Test `sensors` (hard) failure handling and polling from files in Celsius"""
        glob_mock.return_value = [file.name for file in self.tempfiles]
        self.assertEqual(
            Temperature().value,
            '46.7oC (Max. 50.0oC)'
        )

    @patch(
        'archey.entries.temperature.check_output',
        side_effect=[
            FileNotFoundError(),  # No temperature from `sensors` call.
            FileNotFoundError()   # No temperature from `vcgencmd` call.
        ]
    )
    @patch(
        'archey.entries.temperature.glob',
        return_value=[]  # No temperature from file will be retrieved.
    )
    @patch(
        'archey.entries.temperature.Configuration.get',
        side_effect=[
            {'not_detected': "Not detected"}  # Needed key.
        ]
    )
    def test_celsius_to_fahrenheit_conversion(self, _, __, ___):
        """Simple tests for the `_convert_to_fahrenheit` static method"""
        temperature = Temperature()
        # pylint: disable=protected-access
        self.assertAlmostEqual(temperature._convert_to_fahrenheit(-273.15), -459.67)
        self.assertAlmostEqual(temperature._convert_to_fahrenheit(0.0), 32.0)
        self.assertAlmostEqual(temperature._convert_to_fahrenheit(21.0), 69.8)
        self.assertAlmostEqual(temperature._convert_to_fahrenheit(37.0), 98.6)
        self.assertAlmostEqual(temperature._convert_to_fahrenheit(100.0), 212.0)
        # pylint: enable=protected-access


if __name__ == '__main__':
    unittest.main()
