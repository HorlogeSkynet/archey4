
import unittest
from subprocess import TimeoutExpired

from archey.entries.wan_ip import WanIp


class TestWanIpEntry(unittest.TestCase):
    """
    Here, we mock the `check_output` call to `dig` or `wget`.
    """
    @unittest.mock.patch(
        'archey.archey.check_output',
        side_effect=[
            '0123::4567:89a:dead:beef\n',
            'XXX.YY.ZZ.TTT\n'
        ]
    )
    @unittest.mock.patch.dict(
        'archey.archey.CONFIG.config',
        {'ip_settings': {'wan_ip_v6_support': True}}
    )
    def test_ipv6_and_ipv4(self, check_output_mock):
        self.assertEqual(
            WanIp().value,
            'XXX.YY.ZZ.TTT, 0123::4567:89a:dead:beef'
        )

    @unittest.mock.patch(
        'archey.archey.check_output',
        return_value='XXX.YY.ZZ.TTT'
    )
    @unittest.mock.patch.dict(
        'archey.archey.CONFIG.config',
        {'ip_settings': {'wan_ip_v6_support': False}}
    )
    def test_ipv4_only(self, check_output_mock):
        self.assertEqual(
            WanIp().value,
            'XXX.YY.ZZ.TTT'
        )

    @unittest.mock.patch(
        'archey.archey.check_output',
        side_effect=[
            TimeoutExpired('dig', 1),     # First `check_output` call will fail
            '0123::4567:89a:dead:beef',  # `wget` will "work"
            'XXX.YY.ZZ.TTT'              # The IPv4 address is detected
        ]
    )
    @unittest.mock.patch.dict(
        'archey.archey.CONFIG.config',
        {'ip_settings': {'wan_ip_v6_support': True}}
    )
    def test_ipv6_timeout(self, check_output_mock):
        self.assertEqual(
            WanIp().value,
            'XXX.YY.ZZ.TTT, 0123::4567:89a:dead:beef'
        )

    @unittest.mock.patch(
        'archey.archey.check_output',
        side_effect=[
            TimeoutExpired('dig', 1),   # First `check_output` call will fail
            TimeoutExpired('wget', 1),  # Second one too
        ]
    )
    @unittest.mock.patch.dict(
        'archey.archey.CONFIG.config',
        {
            'ip_settings': {'wan_ip_v6_support': False},
            'default_strings': {'no_address': 'No Address'}
        }
    )
    def test_ipv4_timeout_twice(self, check_output_mock):
        self.assertEqual(WanIp().value, 'No Address')

    @unittest.mock.patch(
        'archey.archey.check_output',
        side_effect=[
            '',  # No address will be returned
            ''
        ]
    )
    @unittest.mock.patch.dict(
        'archey.archey.CONFIG.config',
        {
            'ip_settings': {'wan_ip_v6_support': True},
            'default_strings': {'no_address': 'No Address'}
        }
    )
    def test_no_address(self, check_output_mock):
        self.assertEqual(WanIp().value, 'No Address')


if __name__ == '__main__':
    unittest.main()
