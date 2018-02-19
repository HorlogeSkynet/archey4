
import unittest
from unittest.mock import patch

from archey.archey import LAN_IP


class TestLAN_IPEntry(unittest.TestCase):
    """
    Here, we mock the `check_output` call to `hostname`.
    Same thing with `ip` during the manual workaround.
    """
    @patch(
        'archey.archey.check_output',
        return_value='192.168.0.1 192.168.0.11 172.34.56.78\n'
    )
    @patch.dict(
        'archey.archey.config.config',
        {'ip_settings': {'lan_ip_max_count': False}}
    )
    def test_hostname_without_limit(self, check_output_mock):
        self.assertEqual(
            LAN_IP().value,
            '192.168.0.1, 192.168.0.11, 172.34.56.78'
        )

    def test_manual_workaround_with_limit(self):
        raise unittest.SkipTest('TO DO')

    @patch(
        'archey.archey.check_output',
        return_value='\n'
    )
    @patch.dict(
        'archey.archey.config.config',
        {
            'ip_settings': {'lan_ip_max_count': False},
            'default_strings': {'no_address': 'No Address'}
        }
    )
    def test_no_address(self, check_output_mock):
        self.assertEqual(LAN_IP().value, 'No Address')


if __name__ == '__main__':
    unittest.main()
