
import unittest
from subprocess import TimeoutExpired
from unittest.mock import patch

from archey.archey import WAN_IP


class TestWAN_IPEntry(unittest.TestCase):
    """
    Here, we mock the `check_output` call to `dig` or `wget`.
    """
    @patch(
        'archey.archey.check_output',
        side_effect=[
            b'0123::4567:89a:dead:beef\n',
            b'XXX.YY.ZZ.TTT\n'
        ]
    )
    @patch.dict(
        'archey.archey.config.config',
        {'ip_settings': {'wan_ip_v6_support': True}}
    )
    def test_ipv6_and_ipv4(self, check_output_mock):
        self.assertEqual(
            WAN_IP().value,
            'XXX.YY.ZZ.TTT, 0123::4567:89a:dead:beef'
        )

    @patch(
        'archey.archey.check_output',
        return_value=b'XXX.YY.ZZ.TTT'
    )
    @patch.dict(
        'archey.archey.config.config',
        {'ip_settings': {'wan_ip_v6_support': False}}
    )
    def test_ipv4_only(self, check_output_mock):
        self.assertEqual(
            WAN_IP().value,
            'XXX.YY.ZZ.TTT'
        )

    @patch(
        'archey.archey.check_output',
        side_effect=[
            TimeoutExpired('dig', 1),     # First `check_output` call will fail
            b'0123::4567:89a:dead:beef',  # `wget` will "work"
            b'XXX.YY.ZZ.TTT'              # The IPv4 address is detected
        ]
    )
    @patch.dict(
        'archey.archey.config.config',
        {'ip_settings': {'wan_ip_v6_support': True}}
    )
    def test_ipv6_timeout(self, check_output_mock):
        self.assertEqual(
            WAN_IP().value,
            'XXX.YY.ZZ.TTT, 0123::4567:89a:dead:beef'
        )

    @patch(
        'archey.archey.check_output',
        side_effect=[
            TimeoutExpired('dig', 1),   # First `check_output` call will fail
            TimeoutExpired('wget', 1),  # Second one too
        ]
    )
    @patch.dict(
        'archey.archey.config.config',
        {
            'ip_settings': {'wan_ip_v6_support': False},
            'default_strings': {'no_address': 'No Address'}
        }
    )
    def test_ipv4_timeout_twice(self, check_output_mock):
        self.assertEqual(WAN_IP().value, 'No Address')

    @patch(
        'archey.archey.check_output',
        side_effect=[
            b'',  # No address will be returned
            b''
        ]
    )
    @patch.dict(
        'archey.archey.config.config',
        {
            'ip_settings': {'wan_ip_v6_support': True},
            'default_strings': {'no_address': 'No Address'}
        }
    )
    def test_no_address(self, check_output_mock):
        self.assertEqual(WAN_IP().value, 'No Address')


if __name__ == '__main__':
    unittest.main()
