"""Test module for Archey's LAN IP addresses detection module"""

import unittest
from unittest.mock import MagicMock, call, patch

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
        Additionally check the `output` method behavior.

        IP address "compression" and interface name splitting will also be tested.
        """
        lan_ip = LanIP(options={"max_count": 3})

        output_mock = MagicMock()

        self.assertListEqual(
            lan_ip.value,
            ["192.168.1.55", "2001::45:6789:abcd:6817", "fe80::abcd:ef0:abef:dead"],
        )

        with self.subTest("Single-line combined output."):
            lan_ip.output(output_mock)
            self.assertEqual(
                output_mock.append.call_args[0][1],
                "192.168.1.55, 2001::45:6789:abcd:6817, fe80::abcd:ef0:abef:dead",
            )

        output_mock.reset_mock()

        with self.subTest("Multi-lines output."):
            lan_ip.options["one_line"] = False

            lan_ip.output(output_mock)
            self.assertEqual(output_mock.append.call_count, 3)
            output_mock.append.assert_has_calls(
                [
                    call("LAN IP", "192.168.1.55"),
                    call("LAN IP", "2001::45:6789:abcd:6817"),
                    call("LAN IP", "fe80::abcd:ef0:abef:dead"),
                ]
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
        Additionally check the `output` method behavior.
        """
        lan_ip = LanIP()

        output_mock = MagicMock()
        lan_ip.output(output_mock)

        self.assertListEmpty(lan_ip.value)
        self.assertEqual(
            output_mock.append.call_args[0][1], DEFAULT_CONFIG["default_strings"]["no_address"]
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

        output_mock = MagicMock()
        lan_ip.output(output_mock)

        self.assertListEmpty(lan_ip.value)
        self.assertEqual(
            output_mock.append.call_args[0][1], DEFAULT_CONFIG["default_strings"]["no_address"]
        )

    @patch("archey.entries.lan_ip.netifaces", None)  # Imitate an `ImportError` behavior.
    @HelperMethods.patch_clean_configuration
    def test_netifaces_not_available(self):
        """Check `netifaces` is really acting as a (soft-)dependency"""
        lan_ip = LanIP()

        output_mock = MagicMock()
        lan_ip.output(output_mock)

        self.assertIsNone(lan_ip.value)
        self.assertEqual(
            output_mock.append.call_args[0][1], DEFAULT_CONFIG["default_strings"]["not_detected"]
        )


if __name__ == "__main__":
    unittest.main()
