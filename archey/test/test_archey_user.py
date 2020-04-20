"""Test module for Archey's session user name detection module"""

from subprocess import CalledProcessError

import unittest
from unittest.mock import patch

from archey.entries.user import User


class TestUserEntry(unittest.TestCase):
    """
    For this entry, we'll check the output by mocking the `getenv` call.
    If the environment variable happens to be empty, we fall-back to a fake `id` call.
    """
    @patch(
        'archey.entries.user.os.getenv',
        return_value='USERNAME'
    )
    @patch(
        'archey.entries.user.Configuration.get',
        return_value={'not_detected': 'Not detected'}
    )
    def test_getenv(self, _, __):
        """Simple mock, simple test"""
        self.assertEqual(User().value, 'USERNAME')

    @patch(
        'archey.entries.user.os.getenv',
        return_value=''
    )
    @patch(
        'archey.entries.user.check_output',
        return_value='USERNAME\n'
    )
    @patch(
        'archey.entries.user.Configuration.get',
        return_value={'not_detected': 'Not detected'}
    )
    def test_id_call(self, _, __, ___):
        """Mock `id` return value and check the correct assignment"""
        self.assertEqual(User().value, 'USERNAME')

    @patch(
        'archey.entries.user.os.getenv',
        return_value=''
    )
    @patch(
        'archey.entries.user.check_output',
        side_effect=CalledProcessError(1, 'id: ’1000’: no such user')
    )
    @patch(
        'archey.entries.user.Configuration.get',
        return_value={'not_detected': 'Not detected'}
    )
    def test_config_fall_back(self, _, __, ___):
        """`id` fails, but Archey must not !"""
        self.assertEqual(User().value, 'Not detected')


if __name__ == '__main__':
    unittest.main()
