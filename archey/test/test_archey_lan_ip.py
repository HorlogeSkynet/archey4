"""Test module for Archey's LAN IP addresses detection module"""

import unittest
from unittest.mock import MagicMock, patch

from netifaces import AF_INET, AF_INET6, AF_LINK

from archey.entries.lan_ip import LanIp


class TestLanIpEntry(unittest.TestCase):
    """Here, we mock the `netifaces` usages (interfaces and addresses detection calls)"""
    @patch(
        'archey.entries.lan_ip.netifaces.interfaces',
        return_value=['lo', 'en0', 'wlo1']
    )
    @patch(
        'archey.entries.lan_ip.netifaces.ifaddresses',
        side_effect=[
            {
                AF_INET: [{
                    'addr': '127.0.0.1',
                    'netmask': '255.0.0.0'
                }]
            },
            {
                AF_INET: [
                    {
                        'addr': '192.168.0.11',
                        'netmask': '255.255.255.0',
                        'broadcast': '192.168.0.255'
                    },
                    {
                        'addr': '192.168.1.11',
                        'netmask': '255.255.255.0',
                        'broadcast': '192.168.1.255'
                    }
                ]
            },
            {
                AF_INET: [{
                    'addr': '172.34.56.78',
                    'broadcast': '172.34.255.255'
                }]
            }
        ]
    )
    @patch(
        'archey.configuration.Configuration.get',
        side_effect=[
            {'lan_ip_v6_support': None},  # Needed key.
            {'lan_ip_max_count': False}
        ]
    )
    def test_multiple_interfaces(self, _, __, ___):
        """Test for multiple interfaces, multiple addresses (including a loopback one)"""
        self.assertListEqual(
            LanIp().value,
            ['192.168.0.11', '192.168.1.11', '172.34.56.78']
        )

    @patch(
        'archey.entries.lan_ip.netifaces.interfaces',
        return_value=['lo', 'en0']
    )
    @patch(
        'archey.entries.lan_ip.netifaces.ifaddresses',
        side_effect=[
            {
                AF_LINK: [{
                    'addr': '00:00:00:00:00:00',
                    'peer': '00:00:00:00:00:00'
                }],
                AF_INET: [{
                    'addr': '127.0.0.1',
                    'netmask': '255.0.0.0',
                    'peer': '127.0.0.1'
                }],
                AF_INET6: [{
                    'addr': '::1',
                    'netmask': 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128'
                }]
            },
            {
                AF_LINK: [{
                    'addr': 'de:ad:be:ef:de:ad',
                    'broadcast': 'ff:ff:ff:ff:ff:ff'
                }],
                AF_INET: [{
                    'addr': '192.168.1.55',
                    'netmask': '255.255.255.0',
                    'broadcast': '192.168.1.255'
                }],
                AF_INET6: [
                    {
                        'addr': '2001::45:6789:abcd:6817',
                        'netmask': 'ffff:ffff:ffff:ffff::/64'
                    },
                    {
                        'addr': '2a02::45:6789:abcd:0123/64',
                        'netmask': 'ffff:ffff:ffff:ffff::/64'
                    },
                    {
                        'addr': r'fe80::abcd:ef0:abef:dead\%en0',
                        'netmask': 'ffff:ffff:ffff:ffff::/64'
                    }
                ]
            }
        ]
    )
    @patch(
        'archey.configuration.Configuration.get',
        side_effect=[
            {'lan_ip_v6_support': True},
            {'lan_ip_max_count': 2}
        ]
    )
    def test_ipv6_and_limit_and_ether(self, _, __, ___):
        """
        Test for IPv6 support, final set length limit and Ethernet interface filtering.
        Additionally check the `output` method behavior.
        """
        lan_ip = LanIp()

        output_mock = MagicMock()
        lan_ip.output(output_mock)

        self.assertListEqual(
            lan_ip.value,
            ['192.168.1.55', '2001::45:6789:abcd:6817']
        )
        self.assertEqual(
            output_mock.append.call_args[0][1],
            '192.168.1.55, 2001::45:6789:abcd:6817'
        )

    @patch(
        'archey.entries.lan_ip.netifaces.interfaces',
        return_value=['lo', 'en0']
    )
    @patch(
        'archey.entries.lan_ip.netifaces.ifaddresses',
        side_effect=[
            {
                AF_INET: [{
                    'addr': '127.0.0.1',
                    'netmask': '255.0.0.0',
                    'peer': '127.0.0.1'
                }],
                AF_INET6: [{
                    'addr': '::1',
                    'netmask': 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128'
                }]
            },
            {
                AF_INET: [{
                    'addr': '192.168.1.55',
                    'netmask': '255.255.255.0',
                    'broadcast': '192.168.1.255'
                }],
                AF_INET6: [
                    {
                        'addr': '2001::45:6789:abcd:6817',
                        'netmask': 'ffff:ffff:ffff:ffff::/64'
                    },
                    {
                        'addr': '2a02::45:6789:abcd:0123/64',
                        'netmask': 'ffff:ffff:ffff:ffff::/64'
                    },
                    {
                        'addr': r'fe80::abcd:ef0:abef:dead\%en0',
                        'netmask': 'ffff:ffff:ffff:ffff::/64'
                    }
                ]
            }
        ]
    )
    @patch(
        'archey.configuration.Configuration.get',
        side_effect=[
            {'lan_ip_v6_support': False},
            {'lan_ip_max_count': None}
        ]
    )
    def test_no_ipv6(self, _, __, ___):
        """Test for IPv6 hiding"""
        self.assertListEqual(
            LanIp().value,
            ['192.168.1.55']
        )

    @patch(
        'archey.entries.lan_ip.netifaces.interfaces',
        return_value=[]  # No interface returned by `netifaces`.
    )
    @patch(
        'archey.configuration.Configuration.get',
        side_effect=[
            {'lan_ip_v6_support': None},  # Needed key.
            {'lan_ip_max_count': None}    # Needed key.
        ]
    )
    def test_no_network_interface(self, _, __):
        """Test when the device does not have any network interface"""
        self.assertFalse(LanIp().value)

    @patch(
        'archey.entries.lan_ip.netifaces.interfaces',
        return_value=['lo', 'en0']
    )
    @patch(
        'archey.entries.lan_ip.netifaces.ifaddresses',
        side_effect=[
            {
                AF_LINK: [{
                    'addr': '00:00:00:00:00:00',
                    'peer': '00:00:00:00:00:00'
                }],
                AF_INET: [{
                    'addr': '127.0.0.1',
                    'netmask': '255.0.0.0',
                    'peer': '127.0.0.1'
                }],
                AF_INET6: [{
                    'addr': '::1',
                    'netmask': 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128'
                }]
            },
            {
                # No address for this one.
            }
        ]
    )
    @patch(
        'archey.configuration.Configuration.get',
        side_effect=[
            {'lan_ip_v6_support': None},  # Needed key.
            {'lan_ip_max_count': None},   # Needed key.
            {'no_address': 'No address'}
        ]
    )
    def test_no_network_address_output(self, _, __, ___):
        """
        Test when the network interface(s) do not have any IP address.
        Additionally check the `output` method behavior.
        """
        lan_ip = LanIp()

        output_mock = MagicMock()
        lan_ip.output(output_mock)

        self.assertFalse(lan_ip.value)
        self.assertEqual(
            output_mock.append.call_args[0][1],
            'No address'
        )


if __name__ == '__main__':
    unittest.main()
