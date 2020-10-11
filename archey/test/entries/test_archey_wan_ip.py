"""Test module for Archey's public IP address detection module"""

import unittest
from unittest.mock import MagicMock, patch

from socket import timeout as SocketTimeoutError
from subprocess import TimeoutExpired

from archey.test import CustomAssertions
from archey.entries.wan_ip import WanIP
from archey.test.entries import HelperMethods
from archey.constants import DEFAULT_CONFIG


class TestWanIPEntry(unittest.TestCase, CustomAssertions):
    """
    Here, we end up mocking calls to `dig` or `urlopen`.
    """
    def setUp(self):
        """We use these mocks so often, it's worth defining them here."""
        self.wan_ip_mock = HelperMethods.entry_mock(WanIP)
        self.output_mock = MagicMock()

    @patch(
        'archey.entries.wan_ip.check_output',
        side_effect=[
            TimeoutExpired('dig', 1),     # `check_output` call will hard-fail.
            '0123::4567:89a:dead:beef\n'  # `check_output` will work.
        ]
    )
    @patch('archey.entries.wan_ip.urlopen')
    def test_ipv4_ko_and_ipv6_ok(self, urlopen_mock, _):
        """Test fallback on HTTP method only when DNS lookup failed"""
        # `urlopen` will hard-fail.
        urlopen_mock.return_value.read.side_effect = SocketTimeoutError(0)

        # IPv4 retrieval failed.
        self.assertFalse(
            WanIP._retrieve_ip_address(self.wan_ip_mock, 4),  # pylint: disable=protected-access
        )

        # IPv6 worked like a (almost !) charm.
        self.assertEqual(
            WanIP._retrieve_ip_address(self.wan_ip_mock, 6),  # pylint: disable=protected-access
            '0123::4567:89a:dead:beef'
        )

    @patch(
        'archey.entries.wan_ip.check_output',
        side_effect=[
            '\n',                     # `check_output` call will soft-fail.
            FileNotFoundError('dig')  # `check_output` call will hard-fail.
        ]
    )
    @patch('archey.entries.wan_ip.urlopen')
    def test_proper_http_fallback(self, urlopen_mock, _):
        """Test fallback on HTTP method only when DNS lookup failed"""
        urlopen_mock.return_value.read.return_value = b'XXX.YY.ZZ.TTT\n'

        # HTTP back-end was not called, we trust DNS lookup tool which failed.
        self.assertFalse(
            WanIP._retrieve_ip_address(self.wan_ip_mock, 4),  # pylint: disable=protected-access
        )

        # New try: HTTP method has been called !
        self.assertEqual(
            WanIP._retrieve_ip_address(self.wan_ip_mock, 4),  # pylint: disable=protected-access
            'XXX.YY.ZZ.TTT'
        )

    def test_retrieval_disabled(self):
        """Test behavior when both IPv4 and IPv6 retrievals are purposely disabled"""
        self.wan_ip_mock.options = {
            'ipv4': False,
            'ipv6': False
        }

        # Both retrievals fail.
        self.assertFalse(
            WanIP._retrieve_ip_address(self.wan_ip_mock, 4)  # pylint: disable=protected-access
        )
        self.assertFalse(
            WanIP._retrieve_ip_address(self.wan_ip_mock, 6)  # pylint: disable=protected-access
        )

    def test_method_disabled(self):
        """Check whether user could disable resolver back-ends from configuration"""
        self.wan_ip_mock.options = {
            'ipv4': {
                'dns_query': False,
                'http_url': False
            }
        }

        # Internal method doesn't return any address.
        self.assertFalse(
            WanIP._retrieve_ip_address(self.wan_ip_mock, 4)  # pylint: disable=protected-access
        )

    def test_two_addresses(self):
        """
        Test when both IPv4 and IPv6 addresses could be retrieved.
        Additionally check the `output` method behavior.
        """
        self.wan_ip_mock.value = ['XXX.YY.ZZ.TTT', '0123::4567:89a:dead:beef']

        WanIP.output(self.wan_ip_mock, self.output_mock)

        self.assertEqual(
            self.output_mock.append.call_args[0][1],
            "XXX.YY.ZZ.TTT, 0123::4567:89a:dead:beef"
        )

    @HelperMethods.patch_clean_configuration
    def test_no_address(self):
        """
        Test when no address could be retrieved.
        Additionally check the `output` method behavior.
        """
        self.wan_ip_mock.value = []

        WanIP.output(self.wan_ip_mock, self.output_mock)

        self.assertListEmpty(self.wan_ip_mock.value)
        self.assertEqual(
            self.output_mock.append.call_args[0][1],
            DEFAULT_CONFIG['default_strings']['no_address']
        )


if __name__ == '__main__':
    unittest.main()
