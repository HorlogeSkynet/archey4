"""Test module for Archey's device host-name detection module"""

import unittest
from unittest.mock import mock_open, patch

from archey.entries.hostname import Hostname


class TestHostnameEntry(unittest.TestCase):
    """Test cases mocking `/etc/hostname` or `check_output` call to `hostname`"""
    @patch(
        'archey.entries.hostname.open',
        mock_open(
            read_data="""\
MY-COOL-LAPTOP
"""))
    def test_etc_hostname(self):
        """Mock reading from `/etc/hostname`"""
        self.assertEqual(Hostname().value, 'MY-COOL-LAPTOP')

    @patch(
        'archey.entries.hostname.open',
        side_effect=FileNotFoundError()
    )
    @patch(
        'archey.entries.hostname.check_output',
        return_value="""\
MY-COOL-LAPTOP
""")
    def test_hostname(self, _, __):
        """Mock call to `hostname`"""
        self.assertEqual(Hostname().value, 'MY-COOL-LAPTOP')


if __name__ == '__main__':
    unittest.main()
