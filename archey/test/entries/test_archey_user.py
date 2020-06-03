"""Test module for Archey's session user name detection module"""

from subprocess import CalledProcessError

import unittest
from unittest.mock import MagicMock, patch

from archey.entries.user import User
from archey.test.entries import HelperMethods
from archey.constants import DEFAULT_CONFIG


class TestUserEntry(unittest.TestCase):
    """
    For this entry, we'll check the output by mocking the `getenv` call.
    If the environment variable happens to be empty, we fall-back to a fake `id` call.
    """
    @patch(
        'archey.entries.user.os.getenv',
        return_value='USERNAME'
    )
    def test_getenv(self, _):
        """Simple mock, simple test"""
        self.assertEqual(User().value, 'USERNAME')

    @patch(
        'archey.entries.user.os.getenv',
        return_value=None
    )
    @patch(
        'archey.entries.user.check_output',
        return_value='USERNAME\n'
    )
    def test_id_call(self, _, __):
        """Mock `id` returned value and check the correct assignment"""
        self.assertEqual(User().value, 'USERNAME')

    @patch(
        'archey.entries.user.os.getenv',
        return_value=None
    )
    @patch(
        'archey.entries.user.check_output',
        side_effect=CalledProcessError(1, 'id', "id: ’1000’: no such user\n")
    )
    @HelperMethods.patch_clean_configuration
    def test_config_fall_back(self, _, __):
        """`id` fails, but Archey must not !"""
        user = User()

        output_mock = MagicMock()
        user.output(output_mock)

        self.assertIsNone(user.value)
        self.assertEqual(
            output_mock.append.call_args[0][1],
            DEFAULT_CONFIG['default_strings']['not_detected']
        )


if __name__ == '__main__':
    unittest.main()
