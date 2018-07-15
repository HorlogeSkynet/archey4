
import unittest
from unittest.mock import patch

from archey.archey import LanIp


class TestLanIpEntryAutomatic(unittest.TestCase):
    """
    Here, we mock the `check_output` call to `hostname`.
    Same thing with `ip` during the manual workaround.
    """
    @patch(
        'archey.archey.check_output',
        return_value='192.168.0.1 192.168.0.11 172.34.56.78\n'
    )
    @patch.dict(
        'archey.archey.CONFIG.config',
        {'ip_settings': {'lan_ip_max_count': False}}
    )
    def test_hostname_without_limit(self, check_output_mock):
        self.assertEqual(
            LanIp().value,
            '192.168.0.1, 192.168.0.11, 172.34.56.78'
        )

    @patch(
        'archey.archey.check_output',
        return_value='\n'
    )
    @patch.dict(
        'archey.archey.CONFIG.config',
        {
            'ip_settings': {'lan_ip_max_count': False},
            'default_strings': {'no_address': 'No Address'}
        }
    )
    def test_no_address(self, check_output_mock):
        self.assertEqual(LanIp().value, 'No Address')


if __name__ == '__main__':
    unittest.main()
