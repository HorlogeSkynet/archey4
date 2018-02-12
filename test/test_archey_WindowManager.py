
import unittest
from unittest.mock import patch

from archey.archey import WindowManager


class TestHostnameEntry(unittest.TestCase):
    """
    Here, we mock the `check_output` call and check afterwards
      that the output is correct.
    We've to test the case where `wmctrl` is not installed too.
    """
    @patch(
        'archey.archey.check_output',
        return_value=b'Name: WINDOW MANAGER\nClass: N/A\nPID: N/A\n'
    )
    def test_wmctrl(self, check_output_mock):
        self.assertEqual(WindowManager().value, 'WINDOW MANAGER')

    @patch(
        'archey.archey.check_output',
        side_effect=FileNotFoundError()  # `wmctrl` call will fail
    )
    @patch('archey.archey.PROCESSES', [  # Fake running processes list
        'some',
        'awesome',  # Match !
        'programs',
        'running',
        'here'
    ])
    def test_no_wmctrl_match(self, check_output_mock):
        self.assertEqual(WindowManager().value, 'Awesome')

    @patch(
        'archey.archey.check_output',
        side_effect=FileNotFoundError()  # `wmctrl` call will fail
    )
    @patch('archey.archey.PROCESSES', [  # Fake running processes list
        'some',
        'weird',  # Mismatch !
        'programs',
        'running',
        'here'
    ])
    def test_no_wmctrl_mismatch(self, check_output_mock):
        self.assertEqual(WindowManager().value, 'Not detected')


if __name__ == '__main__':
    unittest.main()