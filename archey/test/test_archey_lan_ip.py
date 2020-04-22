"""Test module for Archey's LAN IP addresses detection module"""

import unittest
from unittest.mock import patch

import netifaces

from archey.entries.lanip import LanIp
from archey.configuration import Configuration
from archey.singleton import Singleton
import archey.default_configuration as DefaultConfig


class TestLanIpEntry(unittest.TestCase):
    """Here, we mock the `netifaces` usages (interfaces and addresses detection calls)"""

    def setUp(self):
        """Runs when each test begins"""
        # Set up a default configuration instance.
        config = Configuration()
        config._config = DefaultConfig.CONFIGURATION # pylint: disable=protected-access

    def tearDown(self):
        """Runs when each test finishes testing"""
        # Destroy the singleton configuration instance (if created)
        try:
            del Singleton._instances[Configuration] # pylint: disable=protected-access
        except KeyError:
            pass

    @patch(
        'archey.entries.lanip.netifaces.interfaces',
        return_value=['lo', 'en0', 'wlo1']
    )
    @patch(
        'archey.entries.lanip.netifaces.ifaddresses',
        side_effect=[
            {
                netifaces.AF_INET: [{
                    'addr': '127.0.0.1',
                    'netmask': '255.0.0.0'
                }]
            },
            {
                netifaces.AF_INET: [
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
                netifaces.AF_INET: [{
                    'addr': '172.34.56.78',
                    'broadcast': '172.34.255.255'
                }]
            }
        ]
    )
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'entries': {
                'LanIp': {
                    'display_text': 'LAN IP', # Required KV pair
                    'max_count': False,
                    'ipv6_support': None
                }
            }
        }
    )
    def test_multiple_interfaces(self, _, __):
        """
        [Entry] [LanIp] Test for multiple interfaces, multiple addresses (including a loopback one)
        """
        self.assertEqual(
            LanIp().value,
            '192.168.0.11, 192.168.1.11, 172.34.56.78'
        )

    @patch(
        'archey.entries.lanip.netifaces.interfaces',
        return_value=['lo', 'en0']
    )
    @patch(
        'archey.entries.lanip.netifaces.ifaddresses',
        side_effect=[
            {
                netifaces.AF_LINK: [{
                    'addr': '00:00:00:00:00:00',
                    'peer': '00:00:00:00:00:00'
                }],
                netifaces.AF_INET: [{
                    'addr': '127.0.0.1',
                    'netmask': '255.0.0.0',
                    'peer': '127.0.0.1'
                }],
                netifaces.AF_INET6: [{
                    'addr': '::1',
                    'netmask': 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128'
                }]
            },
            {
                netifaces.AF_LINK: [{
                    'addr': 'de:ad:be:ef:de:ad',
                    'broadcast': 'ff:ff:ff:ff:ff:ff'
                }],
                netifaces.AF_INET: [{
                    'addr': '192.168.1.55',
                    'netmask': '255.255.255.0',
                    'broadcast': '192.168.1.255'
                }],
                netifaces.AF_INET6: [
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
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'entries': {
                'LanIp': {
                    'display_text': 'LAN IP', # Required KV pair
                    'max_count': 2,
                    'ipv6_support': True
                }
            }
        }
    )
    def test_ipv6_and_limit_and_ether(self, _, __):
        """
        [Entry] [LanIp] Test for IPv6 support, final set length limit...
        ...and Ethernet interface filtering
        """
        self.assertEqual(
            LanIp().value,
            '192.168.1.55, 2001::45:6789:abcd:6817'
        )

    @patch(
        'archey.entries.lanip.netifaces.interfaces',
        return_value=['lo', 'en0']
    )
    @patch(
        'archey.entries.lanip.netifaces.ifaddresses',
        side_effect=[
            {
                netifaces.AF_INET: [{
                    'addr': '127.0.0.1',
                    'netmask': '255.0.0.0',
                    'peer': '127.0.0.1'
                }],
                netifaces.AF_INET6: [{
                    'addr': '::1',
                    'netmask': 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128'
                }]
            },
            {
                netifaces.AF_INET: [{
                    'addr': '192.168.1.55',
                    'netmask': '255.255.255.0',
                    'broadcast': '192.168.1.255'
                }],
                netifaces.AF_INET6: [
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
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'entries': {
                'LanIp': {
                    'display_text': 'LAN IP', # Required KV pair
                    'max_count': False,
                    'ipv6_support': None
                }
            }
        }
    )
    def test_no_ipv6(self, _, __):
        """[Entry] [LanIp] Test for IPv6 hiding"""
        self.assertEqual(
            LanIp().value,
            '192.168.1.55'
        )

    @patch(
        'archey.entries.lanip.netifaces.interfaces',
        return_value=[]  # No interface returned by `netifaces`.
    )
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'entries': {
                'LanIp': {
                    'display_text': 'LAN IP', # Required KV pair
                    'max_count': False,       # Required KV pair
                    'ipv6_support': None      # Required KV pair
                }
            },
            'default_strings': {
                'no_address': 'No Address'
            }
        }
    )
    def test_no_network_interface(self, _):
        """[Entry] [LanIp] Test when the device does not have any network interface"""
        self.assertEqual(LanIp().value, 'No Address')

    @patch(
        'archey.entries.lanip.netifaces.interfaces',
        return_value=['lo', 'en0']
    )
    @patch(
        'archey.entries.lanip.netifaces.ifaddresses',
        side_effect=[
            {
                netifaces.AF_LINK: [{
                    'addr': '00:00:00:00:00:00',
                    'peer': '00:00:00:00:00:00'
                }],
                netifaces.AF_INET: [{
                    'addr': '127.0.0.1',
                    'netmask': '255.0.0.0',
                    'peer': '127.0.0.1'
                }],
                netifaces.AF_INET6: [{
                    'addr': '::1',
                    'netmask': 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128'
                }]
            },
            {
                # No address for this one.
            }
        ]
    )
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'entries': {
                'LanIp': {
                    'display_text': 'LAN IP',
                    'max_count': None,
                    'ipv6_support': None
                }
            },
            'default_strings': {
                'no_address': 'No Address'
            }
        }
    )
    def test_no_network_address(self, _, __):
        """[Entry] [LanIp] Test when the network interface(s) do not have any IP address"""
        self.assertEqual(LanIp().value, 'No Address')


if __name__ == '__main__':
    unittest.main()
