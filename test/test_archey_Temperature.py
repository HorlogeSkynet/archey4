
import os
import tempfile
import unittest
from unittest.mock import patch

from archey.archey import Temperature


class TestUserEntry(unittest.TestCase):
    """
    For this entry, we'll just verify that the output is non-null.
    """

    # def __init__(self):
    #     # We'll store there filenames of some temp files mocking those under
    #     #  `/sys/class/thermal/thermal_zone*/temp`
    #     self.tempfiles = None

    def setUp(self):
        self.tempfiles = []
        for temperature in [  # Fake temperatures
                    b'50000',
                    b'0',
                    b'40000',
                    b'50000'
                ]:
            file = tempfile.NamedTemporaryFile(delete=False)
            file.write(temperature)
            self.tempfiles.append(file.name)

    def tearDown(self):
        for file in self.tempfiles:
            os.remove(file)

    @patch(
        'archey.archey.check_output',
        return_value=b'temp=42.8\'C\n'
    )
    @patch(
        'archey.archey.glob',
        return_value=[]  # No temperature from file will be retrieved
    )
    def test_vcgencmd_only(self, glob_mock, check_output_mock):
        self.assertRegex(Temperature().value, '42\.8.?.? \(Max\. 42\.8.?.?\)')

    @patch(
        'archey.archey.check_output',
        return_value=b'temp=40.0\'C\n'
    )
    @patch('archey.archey.glob')
    def test_vcgencmd_and_files(self, glob_mock, check_output_mock):
        glob_mock.return_value = self.tempfiles
        self.assertRegex(Temperature().value, '45\.0.?.? \(Max\. 50\.0.?.?\)')

    @patch(
        'archey.archey.check_output',
        side_effect=FileNotFoundError()
    )
    @patch('archey.archey.glob')
    @patch('archey.archey.config.config', {
            'temperature': {
                'char_before_unit': ' ',
                'use_fahrenheit': True
            }
        }
    )
    def test_files_only_plus_fahrenheit(self, glob_mock, check_output_mock):
        glob_mock.return_value = self.tempfiles
        self.assertRegex(
            Temperature().value,
            '116\.0.?.? \(Max\. 122\.0.?.?\)'  # 46.6 converted into Fahrenheit
        )


if __name__ == '__main__':
    unittest.main()
