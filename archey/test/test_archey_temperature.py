
import os
import tempfile
import unittest
from unittest.mock import patch

from archey.entries.temperature import Temperature


class TestTemperatureEntry(unittest.TestCase):
    """
    For this entry, we'll just verify that the output is non-null.
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
        'archey.archey.check_output',
        return_value='temp=42.8\'C\n'
    )
    @patch(
        'archey.archey.glob',
        return_value=[]  # No temperature from file will be retrieved
    )
    def test_vcgencmd_only_no_max(self, glob_mock, check_output_mock):
        self.assertRegex(Temperature().value, r'42\.8.?.?')

    @patch(
        'archey.archey.check_output',
        return_value='temp=40.0\'C\n'
    )
    @patch('archey.archey.glob')
    def test_vcgencmd_and_files(self, glob_mock, check_output_mock):
        glob_mock.return_value = [file.name for file in self.tempfiles]
        self.assertRegex(Temperature().value, r'45\.0.?.? \(Max\. 50\.0.?.?\)')

    @patch(
        'archey.archey.check_output',
        side_effect=FileNotFoundError()  # No temperature from `vcgencmd` call
    )
    @patch('archey.archey.glob')
    @patch.dict('archey.archey.CONFIG.config', {
        'temperature': {
            'char_before_unit': ' ',
            'use_fahrenheit': True
        }
    })
    def test_files_only_plus_fahrenheit(self, glob_mock, check_output_mock):
        glob_mock.return_value = [file.name for file in self.tempfiles]
        self.assertRegex(
            Temperature().value,
            r'116\.0.?.? \(Max\. 122\.0.?.?\)'  # 46.6 converted into Fahrenheit
        )

    @patch(
        'archey.archey.check_output',
        side_effect=FileNotFoundError()  # No temperature from `vcgencmd` call
    )
    @patch(
        'archey.archey.glob',
        return_value=[]  # No temperature from file will be retrieved
    )
    @patch.dict('archey.archey.CONFIG.config', {
        'default_strings': {
            'not_detected': 'Not detected'
        }
    })
    def test_no_output(self, glob_mock, check_output_mock):
        self.assertEqual(Temperature().value, 'Not detected')


if __name__ == '__main__':
    unittest.main()
