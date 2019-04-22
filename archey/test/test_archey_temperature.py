"""Test module for Archey's temperature detection module"""

import os
import tempfile
import unittest
from unittest.mock import patch

from archey.entries.temperature import Temperature


class TestTemperatureEntry(unittest.TestCase):
    """
    Based on `vcgencmd` and some sensor files, this module verifies temperature computations.
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
        return_value='temp=42.8\'C\n'
    )
    @patch(
        'archey.entries.temperature.glob',
        return_value=[]  # No temperature from file will be retrieved
    )
    def test_vcgencmd_only_no_max(self, _, __):
        """
        Test for `vcgencmd` output only (no sensor files).
        Only one value is retrieved, so no maximum is displayed (see #39).
        """
        self.assertRegex(Temperature().value, r'42\.8.?.?')

    @patch(
        'archey.entries.temperature.check_output',
        return_value='temp=40.0\'C\n'
    )
    @patch('archey.entries.temperature.glob')
    def test_vcgencmd_and_files(self, glob_mock, _):
        """Tests `vcgencmd` output AND sensor files"""
        glob_mock.return_value = [file.name for file in self.tempfiles]
        self.assertRegex(Temperature().value, r'45\.0.?.? \(Max\. 50\.0.?.?\)')

    @patch(
        'archey.entries.temperature.check_output',
        side_effect=FileNotFoundError()  # No temperature from `vcgencmd` call
    )
    @patch('archey.entries.temperature.glob')
    def test_files_only_plus_fahrenheit(self, glob_mock, _):
        """Test sensor files only, Fahrenheit (naive) conversion and special degree character"""
        glob_mock.return_value = [file.name for file in self.tempfiles]
        self.assertRegex(
            Temperature(use_fahrenheit=True, char_before_unit='@').value,
            r'116\.0@F \(Max\. 122\.0@F\)'  # 46.6 converted into Fahrenheit
        )

    @patch(
        'archey.entries.temperature.check_output',
        side_effect=FileNotFoundError()  # No temperature from `vcgencmd` call
    )
    @patch(
        'archey.entries.temperature.glob',
        return_value=[]  # No temperature from file will be retrieved
    )
    def test_no_output(self, _, __):
        """Test when no value could be retrieved (anyhow)"""
        self.assertEqual(
            Temperature(not_detected='Not detected').value,
            'Not detected'
        )


if __name__ == '__main__':
    unittest.main()
