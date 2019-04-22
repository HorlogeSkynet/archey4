"""Test module for Archey's public IP address detection module"""

import unittest
from unittest.mock import patch

from subprocess import TimeoutExpired

from archey.entries.wan_ip import WanIp


class TestWanIpEntry(unittest.TestCase):
    """
    Here, we mock the `check_output` call to `dig` or `wget`.
    """
    @patch(
        'archey.entries.wan_ip.check_output',
        side_effect=[
            '0123::4567:89a:dead:beef\n',
            'XXX.YY.ZZ.TTT\n'
        ]
    )
    def test_ipv6_and_ipv4(self, _):
        """Test the regular case : Both IPv4 and IPv6 are retrieved"""
        self.assertEqual(
            WanIp().value,
            'XXX.YY.ZZ.TTT, 0123::4567:89a:dead:beef'
        )

    @patch(
        'archey.entries.wan_ip.check_output',
        return_value='XXX.YY.ZZ.TTT'
    )
    def test_ipv4_only(self, _):
        """Test only public IPv4 detection"""
        self.assertEqual(
            WanIp(ipv6_support=False).value,
            'XXX.YY.ZZ.TTT'
        )

    @patch(
        'archey.entries.wan_ip.check_output',
        side_effect=[
            TimeoutExpired('dig', 1),    # First `check_output` call will fail
            '0123::4567:89a:dead:beef',  # `wget` will "work"
            'XXX.YY.ZZ.TTT'              # The IPv4 address is detected
        ]
    )
    def test_ipv6_timeout(self, _):
        """Test when `dig` call timeout for the IPv6 detection"""
        self.assertEqual(
            WanIp().value,
            'XXX.YY.ZZ.TTT, 0123::4567:89a:dead:beef'
        )

    @patch(
        'archey.entries.wan_ip.check_output',
        side_effect=[
            TimeoutExpired('dig', 1),  # First `check_output` call will fail
            TimeoutExpired('wget', 1)  # Second one too
        ]
    )
    def test_ipv4_timeout_twice(self, _):
        """Test when both `dig` and `wget` trigger timeouts..."""
        self.assertEqual(
            WanIp(ipv6_support=False, no_address='No Address').value,
            'No Address'
        )

    @patch(
        'archey.entries.wan_ip.check_output',
        side_effect=[
            '',  # No address will be returned
            ''
        ]
    )
    def test_no_address(self, _):
        """Test when no address could be retrieved"""
        self.assertEqual(
            WanIp(no_address='No Address').value,
            'No Address'
        )


if __name__ == '__main__':
    unittest.main()
