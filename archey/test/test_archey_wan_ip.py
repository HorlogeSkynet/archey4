"""Test module for Archey's public IP address detection module"""

import unittest
from unittest.mock import patch

from subprocess import TimeoutExpired
from urllib.error import URLError

from archey.entries.wanip import WanIp
from archey.configuration import Configuration
from archey.singleton import Singleton
import archey.default_configuration as DefaultConfig


class TestWanIpEntry(unittest.TestCase):
    """
    Here, we mock calls to `dig` or `urlopen`.
    """

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
        'archey.entries.wanip.check_output',
        side_effect=[
            '0123::4567:89a:dead:beef\n',
            'XXX.YY.ZZ.TTT\n'
        ]
    )
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'entries': {
                'WanIp': {
                    'display_text': 'WAN IP',          # Required KV pair
                    'ipv6_support': True,
                    'ipv4_timeout_secs': float('inf'), # Required KV pair
                    'ipv6_timeout_secs': float('inf')  # Required KV pair
                }
            }
        }
    )
    def test_ipv6_and_ipv4(self, _):
        """[Entry] [WanIp] Test the regular case : Both IPv4 and IPv6 are retrieved"""
        self.assertEqual(
            WanIp().value,
            'XXX.YY.ZZ.TTT, 0123::4567:89a:dead:beef'
        )

    @patch(
        'archey.entries.wanip.check_output',
        return_value='XXX.YY.ZZ.TTT'
    )
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'entries': {
                'WanIp': {
                    'display_text': 'WAN IP',          # Required KV pair
                    'ipv6_support': False,
                    'ipv4_timeout_secs': float('inf'), # Required KV pair
                }
            }
        }
    )
    def test_ipv4_only(self, _):
        """[Entry] [WanIp] Test only public IPv4 detection"""
        self.assertEqual(
            WanIp().value,
            'XXX.YY.ZZ.TTT'
        )

    @patch(
        'archey.entries.wanip.check_output',
        side_effect=[
            TimeoutExpired('dig', 1),  # `check_output` call will fail
            'XXX.YY.ZZ.TTT'            # The IPv4 address is detected
        ]
    )
    @patch(
        'archey.entries.wanip.urlopen',  # `urlopen`'s `getcode` & `read` special mocking.
        **{
            'return_value.getcode.return_value': 200,
            'return_value.read.return_value': b'0123::4567:89a:dead:beef\n'
        }
    )
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'entries': {
                'WanIp': {
                    'display_text': 'WAN IP',          # Required KV pair
                    'ipv6_support': True,
                    'ipv4_timeout_secs': float('inf'), # Required KV pair
                    'ipv6_timeout_secs': float('inf')  # Required KV pair
                }
            }
        }
    )
    def test_ipv6_timeout(self, _, __):
        """[Entry] [WanIp] Test when `dig` call timeout for the IPv6 detection"""
        self.assertEqual(
            WanIp().value,
            'XXX.YY.ZZ.TTT, 0123::4567:89a:dead:beef'
        )

    @patch(
        'archey.entries.wanip.check_output',
        side_effect=TimeoutExpired('dig', 1)  # `check_output` call will fail
    )
    @patch(
        'archey.entries.wanip.urlopen',
        side_effect=URLError('<urlopen error timed out>')  # `urlopen` call will fail
    )
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'entries': {
                'WanIp': {
                    'display_text': 'WAN IP',          # Required KV pair
                    'ipv6_support': False,
                    'ipv4_timeout_secs': float('inf'), # Required KV pair
                    'ipv6_timeout_secs': float('inf')  # Required KV pair
                }
            },
            'default_strings': {
                'no_address': 'No Address'
            }
        }
    )
    def test_ipv4_timeout_twice(self, _, __):
        """[Entry] [WanIp] Test when both `dig` and `URLOpen` trigger timeouts..."""
        self.assertEqual(WanIp().value, 'No Address')

    @patch(
        'archey.entries.wanip.check_output',
        return_value=''  # No address will be returned
    )
    @patch(
        'urllib.request.urlopen',
        return_value=None  # No object will be returned
    )
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'entries': {
                'WanIp': {
                    'display_text': 'WAN IP',          # Required KV pair
                    'ipv6_support': False,
                    'ipv4_timeout_secs': float('inf'), # Required KV pair
                }
            },
            'default_strings': {
                'no_address': 'No Address'
            }
        }
    )
    def test_no_address(self, _, __):
        """[Entry] [WanIp] Test when no address could be retrieved"""
        self.assertEqual(WanIp().value, 'No Address')


if __name__ == '__main__':
    unittest.main()
