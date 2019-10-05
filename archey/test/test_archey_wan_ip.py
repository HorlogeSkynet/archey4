"""Test module for Archey's public IP address detection module"""

import unittest
from unittest.mock import patch

from subprocess import TimeoutExpired
from urllib.error import URLError

from archey.entries.wan_ip import WanIp


class TestWanIpEntry(unittest.TestCase):
    """
    Here, we mock calls to `dig` or `urlopen`.
    """
    @patch(
        'archey.entries.wan_ip.check_output',
        side_effect=[
            '0123::4567:89a:dead:beef\n',
            'XXX.YY.ZZ.TTT\n'
        ]
    )
    @patch(
        'archey.entries.wan_ip.Configuration.get',
        side_effect=[
            {'wan_ip_v6_support': True},
            {'ipv6_detection': None},  # Needed key.
            {'ipv4_detection': None}   # Needed key.
        ]
    )
    def test_ipv6_and_ipv4(self, _, __):
        """Test the regular case : Both IPv4 and IPv6 are retrieved"""
        self.assertEqual(
            WanIp().value,
            'XXX.YY.ZZ.TTT, 0123::4567:89a:dead:beef'
        )

    @patch(
        'archey.entries.wan_ip.check_output',
        return_value='XXX.YY.ZZ.TTT'
    )
    @patch(
        'archey.entries.wan_ip.Configuration.get',
        side_effect=[
            {'wan_ip_v6_support': False},
            {'ipv4_detection': None}  # Needed key.
        ]
    )
    def test_ipv4_only(self, _, __):
        """Test only public IPv4 detection"""
        self.assertEqual(
            WanIp().value,
            'XXX.YY.ZZ.TTT'
        )

    @patch(
        'archey.entries.wan_ip.check_output',
        side_effect=[
            TimeoutExpired('dig', 1),  # `check_output` call will fail
            'XXX.YY.ZZ.TTT'            # The IPv4 address is detected
        ]
    )
    @patch(
        'archey.entries.wan_ip.urlopen',  # `urlopen`'s `getcode` & `read` special mocking.
        **{
            'return_value.getcode.return_value': 200,
            'return_value.read.return_value': b'0123::4567:89a:dead:beef\n'
        }
    )
    @patch(
        'archey.entries.wan_ip.Configuration.get',
        side_effect=[
            {'wan_ip_v6_support': True},
            {'ipv6_detection': None},  # Needed key.
            {'ipv6_detection': None},  # Needed key.
            {'ipv4_detection': None}   # Needed key.
        ]
    )
    def test_ipv6_timeout(self, _, __, ___):
        """Test when `dig` call timeout for the IPv6 detection"""
        self.assertEqual(
            WanIp().value,
            'XXX.YY.ZZ.TTT, 0123::4567:89a:dead:beef'
        )

    @patch(
        'archey.entries.wan_ip.check_output',
        side_effect=TimeoutExpired('dig', 1)  # `check_output` call will fail
    )
    @patch(
        'archey.entries.wan_ip.urlopen',
        side_effect=URLError('<urlopen error timed out>')  # `urlopen` call will fail
    )
    @patch(
        'archey.entries.wan_ip.Configuration.get',
        side_effect=[
            {'wan_ip_v6_support': False},
            {'ipv4_detection': None},  # Needed key.
            {'ipv4_detection': None},  # Needed key.
            {'no_address': 'No Address'}
        ]
    )
    def test_ipv4_timeout_twice(self, _, __, ___):
        """Test when both `dig` and `wget` trigger timeouts..."""
        self.assertEqual(WanIp().value, 'No Address')

    @patch(
        'archey.entries.wan_ip.check_output',
        return_value=''  # No address will be returned
    )
    @patch(
        'urllib.request.urlopen',
        return_value=None  # No object will be returned
    )
    @patch(
        'archey.entries.wan_ip.Configuration.get',
        side_effect=[
            {'wan_ip_v6_support': False},
            {'ipv4_detection': None},  # Needed key.
            {'no_address': 'No Address'}
        ]
    )
    def test_no_address(self, _, __, ___):
        """Test when no address could be retrieved"""
        self.assertEqual(WanIp().value, 'No Address')


if __name__ == '__main__':
    unittest.main()
