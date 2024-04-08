"""Test module for Archey's LAN IP addresses detection module"""

import unittest
from unittest.mock import patch

from netifaces import AF_INET, AF_INET6, AF_LINK

from archey.configuration import DEFAULT_CONFIG
from archey.entries.lan_ip import LanIP
from archey.test import CustomAssertions
from archey.test.entries import HelperMethods


class TestLanIPEntry(unittest.TestCase, CustomAssertions):
    """Here, we mock the `netifaces` usages (interfaces and addresses detection calls)"""

    @patch(
        "archey.entries.lan_ip.netifaces.interfaces",
        return_value=["lo", "en0", "wlo1"],
    )
    @patch(
        "archey.entries.lan_ip.netifaces.ifaddresses",
        side_effect=[
            {
                AF_INET: [
                    {
                        "addr": "127.0.0.1",
                        "netmask": "255.0.0.0",
                    },
                ]
            },
            {
                AF_INET: [
                    {
                        "addr": "192.168.0.11",
                        "netmask": "255.255.255.0",
                        "broadcast": "192.168.0.255",
                    },
                    {
                        "addr": "192.168.1.11",
                        "netmask": "255.255.255.0",
                        "broadcast": "192.168.1.255",
                    },
                ]
            },
            {
                AF_INET: [
                    {
                        "addr": "172.16.56.78",
                        "broadcast": "172.16.255.255",
                    },
                ]
            },
        ],
    )
    def test_multiple_interfaces(self, _, __):
        """Test for multiple interfaces, multiple addresses (including a loopback one)"""
        self.assertListEqual(
            LanIP(options={"max_count": False}).value,
            ["192.168.0.11", "192.168.1.11", "172.16.56.78"],
        )

    @patch(
        "archey.entries.lan_ip.netifaces.interfaces",
        return_value=["lo", "en0"],
    )
    @patch(
        "archey.entries.lan_ip.netifaces.ifaddresses",
        side_effect=[
            {
                AF_INET: [
                    {
                        "addr": "127.0.0.1",
                        "netmask": "255.0.0.0",
                        "peer": "127.0.0.1",
                    },
                ],
                AF_INET6: [
                    {
                        "addr": "::1",
                        "netmask": "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128",
                    },
                ],
            },
            {
                AF_INET: [
                    {
                        "addr": "192.168.1.55",
                        "netmask": "255.255.255.0",
                        "broadcast": "192.168.1.255",
                    },
                    {
                        "addr": "123.45.67.89",
                        "netmask": "255.255.0.0",
                        "broadcast": "123.45.255.255",
                    },
                ]
            },
        ],
    )
    def test_show_global(self, _, __):
        """Test public IP addresses forced display"""
        self.assertListEqual(
            LanIP(options={"show_global": True}).value,
            ["192.168.1.55", "123.45.67.89"],
        )

    @patch(
        "archey.entries.lan_ip.netifaces.interfaces",
        return_value=["lo", "en0"],
    )
    @patch(
        "archey.entries.lan_ip.netifaces.ifaddresses",
        side_effect=[
            {
                AF_INET: [
                    {
                        "addr": "127.0.0.1",
                        "netmask": "255.0.0.0",
                        "peer": "127.0.0.1",
                    },
                ],
                AF_INET6: [
                    {
                        "addr": "::1",
                        "netmask": "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128",
                    },
                ],
            },
            {
                AF_INET: [
                    {
                        "addr": "192.168.1.55",
                        "netmask": "255.255.255.0",
                        "broadcast": "192.168.1.255",
                    },
                    {
                        "addr": "169.254.5.6",
                        "netmask": "255.255.0.0",
                        "broadcast": "169.254.255.255",
                    },
                ],
                AF_INET6: [
                    {
                        "addr": "fe80::abcd:ef0:abef:dead",
                        "netmask": "ffff:ffff:ffff:ffff::/64",
                    },
                ],
            },
        ],
    )
    def test_show_link_local(self, _, __):
        """Test link-local IP addresses hiding"""
        self.assertListEqual(
            LanIP(options={"show_link_local": False}).value,
            ["192.168.1.55"],
        )

    @patch(
        "archey.entries.lan_ip.netifaces.interfaces",
        return_value=["lo", "en0"],
    )
    @patch(
        "archey.entries.lan_ip.netifaces.ifaddresses",
        side_effect=[
            {
                AF_LINK: [
                    {
                        "addr": "00:00:00:00:00:00",
                        "peer": "00:00:00:00:00:00",
                    },
                ],
                AF_INET: [
                    {
                        "addr": "127.0.0.1",
                        "netmask": "255.0.0.0",
                        "peer": "127.0.0.1",
                    },
                ],
                AF_INET6: [
                    {
                        "addr": "::1",
                        "netmask": "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128",
                    },
                ],
            },
            {
                AF_LINK: [
                    {
                        "addr": "de:ad:be:ef:de:ad",
                        "broadcast": "ff:ff:ff:ff:ff:ff",
                    },
                ],
                AF_INET: [
                    {
                        "addr": "192.168.1.55",
                        "netmask": "255.255.255.0",
                        "broadcast": "192.168.1.255",
                    }
                ],
                AF_INET6: [
                    {
                        "addr": "2001:0000:0000:0000:0045:6789:abcd:6817",
                        "netmask": "ffff:ffff:ffff:ffff::/64",
                    },
                    {
                        "addr": "2a02::45:6789:abcd:0123",
                        "netmask": "ffff:ffff:ffff:ffff::/64",
                    },
                    {
                        "addr": r"fe80::abcd:ef0:abef:dead%en0",
                        "netmask": "ffff:ffff:ffff:ffff::/64",
                    },
                ],
            },
        ],
    )
    def test_ipv6_and_limit_and_ether(self, _, __):
        """
        Test for IPv6 support, final set length limit and Ethernet interface filtering.
        Additionally check the `pretty_value` property behavior.

        IP address "compression" and interface name splitting will also be tested.
        """
        lan_ip = LanIP(options={"max_count": 3})

        self.assertListEqual(
            lan_ip.value,
            ["192.168.1.55", "2001::45:6789:abcd:6817", "fe80::abcd:ef0:abef:dead"],
        )

        with self.subTest("Normal output."):
            self.assertListEqual(
                list(lan_ip),
                [
                    (lan_ip.name, "192.168.1.55"),
                    (lan_ip.name, "2001::45:6789:abcd:6817"),
                    (lan_ip.name, "fe80::abcd:ef0:abef:dead"),
                ],
            )

    @patch(
        "archey.entries.lan_ip.netifaces.interfaces",
        return_value=["lo", "en0"],
    )
    @patch(
        "archey.entries.lan_ip.netifaces.ifaddresses",
        side_effect=[
            {
                AF_INET: [
                    {
                        "addr": "127.0.0.1",
                        "netmask": "255.0.0.0",
                        "peer": "127.0.0.1",
                    },
                ],
                AF_INET6: [
                    {
                        "addr": "::1",
                        "netmask": "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128",
                    },
                ],
            },
            {
                AF_INET: [
                    {
                        "addr": "192.168.1.55",
                        "netmask": "255.255.255.0",
                        "broadcast": "192.168.1.255",
                    }
                ],
                AF_INET6: [
                    {
                        "addr": "2001::45:6789:abcd:6817",
                        "netmask": "ffff:ffff:ffff:ffff::/64",
                    },
                    {
                        "addr": "2a02::45:6789:abcd:0123",
                        "netmask": "ffff:ffff:ffff:ffff::/64",
                    },
                    {
                        "addr": r"fe80::abcd:ef0:abef:dead%en0",
                        "netmask": "ffff:ffff:ffff:ffff::/64",
                    },
                ],
            },
        ],
    )
    def test_no_ipv6(self, _, __):
        """Test for IPv6 hiding"""
        self.assertListEqual(
            LanIP(options={"ipv6_support": False}).value,
            ["192.168.1.55"],
        )

    @patch(
        "archey.entries.lan_ip.netifaces.interfaces",
        return_value=[],  # No interface returned by `netifaces`.
    )
    def test_no_network_interface(self, _):
        """Test when the device does not have any network interface"""
        self.assertListEmpty(LanIP().value)

    @patch(
        "archey.entries.lan_ip.netifaces.interfaces",
        return_value=["lo", "en0"],
    )
    @patch(
        "archey.entries.lan_ip.netifaces.ifaddresses",
        side_effect=[
            {
                AF_LINK: [
                    {
                        "addr": "00:00:00:00:00:00",
                        "peer": "00:00:00:00:00:00",
                    },
                ],
                AF_INET: [
                    {
                        "addr": "127.0.0.1",
                        "netmask": "255.0.0.0",
                        "peer": "127.0.0.1",
                    },
                ],
                AF_INET6: [
                    {
                        "addr": "0000:0000:0000:0000:0000:0000:0000:0001",
                        "netmask": "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128",
                    }
                ],
            },
            {
                # No address for this one.
            },
        ],
    )
    @HelperMethods.patch_clean_configuration
    def test_no_network_address_output(self, _, __):
        """
        Test when the network interface(s) do not have any IP address.
        Additionally check the `pretty_value` property behavior.
        """
        lan_ip = LanIP()
        self.assertListEmpty(lan_ip.value)
        self.assertListEqual(
            list(lan_ip),
            [(lan_ip.name, DEFAULT_CONFIG["default_strings"]["no_address"])],
        )

    @patch(
        "archey.entries.lan_ip.netifaces.interfaces",
        return_value=["lo", "en0"],
    )
    @patch(
        "archey.entries.lan_ip.netifaces.ifaddresses",
        side_effect=[
            {
                AF_INET: [
                    {
                        "addr": "127.0.0.1",
                        "netmask": "255.0.0.0",
                        "peer": "127.0.0.1",
                    },
                ],
                AF_INET6: [
                    {
                        "addr": "::1",
                        "netmask": "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128",
                    },
                ],
            },
            {
                AF_INET: [
                    {
                        "addr": "192.168.1.55",
                        "netmask": "255.255.255.0",
                        "broadcast": "192.168.1.255",
                    }
                ],
                AF_INET6: [
                    {
                        "addr": "2001::45:6789:abcd:6817",
                        "netmask": "ffff:ffff:ffff:ffff::/64",
                    },
                    {
                        "addr": "2a02::45:6789:abcd:0123",
                        "netmask": "ffff:ffff:ffff:ffff::/64",
                    },
                    {
                        "addr": r"fe80::abcd:ef0:abef:dead%en0",
                        "netmask": "ffff:ffff:ffff:ffff::/64",
                    },
                ],
            },
        ],
    )
    @HelperMethods.patch_clean_configuration
    def test_user_disabled(self, _, __):
        """Check behavior on user inputs edge-cases"""
        lan_ip = LanIP(options={"max_count": 0})
        self.assertListEmpty(lan_ip.value)
        self.assertListEqual(
            list(lan_ip),
            [(lan_ip.name, DEFAULT_CONFIG["default_strings"]["no_address"])],
        )

    @patch("archey.entries.lan_ip.netifaces", None)  # Imitate an `ImportError` behavior.
    @HelperMethods.patch_clean_configuration
    def test_netifaces_not_available(self):
        """Check `netifaces` is really acting as a (soft-)dependency"""
        lan_ip = LanIP()
        self.assertIsNone(lan_ip.value)
        self.assertListEqual(
            list(lan_ip),
            [],
        )


if __name__ == "__main__":
    unittest.main()
